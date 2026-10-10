from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from hosn_dashboard_ai import (
    FEATURE_ORDER,
    ModelBundle,
    decision_from_features,
    final_recording_check,
    load_model_bundle,
    load_scenario_summaries,
    recorded_features,
)


ROOT = Path(__file__).resolve().parent

st.set_page_config(
    page_title="HOSN | AI Control Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp { background: #071421; color: #EAF7FF; }
    [data-testid="stSidebar"] { background: #0B1D30; }
    .block-container { max-width: 1500px; padding-top: 1.4rem; }
    h1, h2, h3 { color: #EAF7FF !important; }
    div[data-testid="stMetric"] {
        background: #10263B; border: 1px solid #214760;
        border-radius: 14px; padding: 16px;
    }
    div[data-testid="stMetricLabel"] { color: #8CA9BC; }
    div[data-testid="stMetricValue"] { color: #20D9E8; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_model_bundle() -> ModelBundle:
    return load_model_bundle(ROOT)


@st.cache_data
def get_scenarios() -> dict[str, dict[str, Any]]:
    return load_scenario_summaries(ROOT)


def scenario_title(number: str, summary: dict[str, Any]) -> str:
    title = summary.get("recording_demo", {}).get("scenario_title")
    return title or summary.get("scenario_id", "Recorded scenario " + number)


def scenario_option(number: str) -> str:
    return "S{} · {}".format(number, scenario_title(number, SCENARIOS[number]))


def yes_no(value: Any) -> str:
    return "Yes" if bool(value) else "No"


def controller_result(summary: dict[str, Any]) -> dict[str, Any]:
    check = final_recording_check(summary)
    return check.get("controller_decision", {}).get("controller_result", {})


def recorded_decision(summary: dict[str, Any]) -> dict[str, Any]:
    check = final_recording_check(summary)
    return check.get("controller_decision", summary.get("controller_decision", {}))


def value_at(mapping: dict[str, Any], *keys: str) -> Any:
    value: Any = mapping
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def decision_badge(action: str) -> None:
    if action == "HANDOVER":
        st.warning("HANDOVER")
    elif action == "STAY":
        st.success("STAY")
    else:
        st.info(action)


try:
    MODEL = get_model_bundle()
    MODEL_ERROR = None
except Exception as exc:
    MODEL = None
    MODEL_ERROR = "{}: {}".format(type(exc).__name__, exc)

try:
    SCENARIOS = get_scenarios()
    SCENARIO_ERROR = None
except Exception as exc:
    SCENARIOS = {}
    SCENARIO_ERROR = "{}: {}".format(type(exc).__name__, exc)


with st.sidebar:
    st.title("🛡️ HOSN | حصن")
    st.caption("Rules-first Wi-Fi / emulated 5G handover")
    st.divider()
    if SCENARIOS:
        selected_number = st.selectbox(
            "Recorded Mininet-WiFi scenario",
            options=("1", "2", "3"),
            format_func=scenario_option,
        )
    else:
        selected_number = "1"
    st.divider()
    st.markdown("### Deployment")
    st.write("✅ Streamlit Cloud compatible")
    st.write("✅ No VM or Mininet import")
    st.write("✅ Measured model artifact")
    st.caption("The VM is used to collect experiments; it is not needed for inference.")
    st.divider()
    st.caption("Source branch: hosn-ai-integration")


st.title("HOSN | Network Control Center")
st.caption("Measured AI integration for conflict-only handover decisions")

if MODEL_ERROR:
    st.error("Measured AI model could not be loaded: " + MODEL_ERROR)
else:
    st.success(
        "Accepted measured-data AI loaded: {} | StandardScaler + Logistic Regression".format(
            MODEL.model_path.name
        )
    )

if SCENARIO_ERROR:
    st.error("Recorded scenario data could not be loaded: " + SCENARIO_ERROR)
    st.stop()

selected = SCENARIOS[selected_number]
selected_final = recorded_decision(selected)
selected_result = controller_result(selected)
selected_features = recorded_features(selected)
selected_action = selected.get("action", selected_final.get("action", "UNKNOWN"))
selected_source = selected_final.get("source", "UNKNOWN")
selected_checks = selected.get("checks", {})
selected_path_verified = (
    selected_checks.get("handover_used_both_paths")
    if selected_action == "HANDOVER"
    else selected_checks.get("stay_used_only_wifi")
)
selected_path_label = (
    "Handover path verified"
    if selected_action == "HANDOVER"
    else "Wi-Fi stay path verified"
)

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Measured scenarios", str(len(SCENARIOS)))
with m2:
    st.metric("Selected result", selected_action)
with m3:
    st.metric("Decision source", selected_source)
with m4:
    st.metric("AI called", yes_no(selected_final.get("ai_called")))

st.divider()

tab_scenario, tab_replay, tab_contract = st.tabs(
    ["Recorded Scenario", "Cloud AI Replay", "Training Contract"]
)


with tab_scenario:
    st.subheader(scenario_title(selected_number, selected))
    st.caption(
        "{} · source file: {}".format(
            selected.get("scenario_id", "unknown"),
            selected.get("_dashboard_source_path", "unknown"),
        )
    )

    top_left, top_right = st.columns([1, 2])
    with top_left:
        st.markdown("#### Final controller result")
        decision_badge(selected_action)
        st.write("**Source:** {}".format(selected_source))
        st.write("**Status:** {}".format(selected_final.get("status", "UNKNOWN")))
        st.write("**Rule result:** {} / {}".format(
            selected_result.get("rule_status", "UNKNOWN"),
            selected_result.get("rule_decision", "UNKNOWN"),
        ))
        st.write("**AI called:** {}".format(yes_no(selected_final.get("ai_called"))))
        if selected_final.get("ai_prediction"):
            st.write("**AI prediction:** {}".format(selected_final["ai_prediction"]))
        st.caption(selected_final.get("reason", "No explanation recorded."))

    with top_right:
        st.markdown("#### Recorded decision path")
        if selected_source == "AI":
            st.info(
                "Rule conflict detected → measured AI called → {}.".format(selected_action)
            )
        elif selected_source == "RULES":
            st.success(
                "Clear rule result → {}. The AI was correctly bypassed.".format(selected_action)
            )
        else:
            st.warning(
                "The recorded controller held the connection. Further measurement was required."
            )
        st.write(
            "**{}:** {}  \n**Scenario goal observed:** {}  \n**Checks completed:** {} / 4".format(
                selected_path_label,
                yes_no(selected_path_verified),
                yes_no(selected.get("recording_demo", {}).get("recording_goal_observed")),
                len(selected.get("recording_checks", [])),
            )
        )

    st.markdown("#### Real monitoring checks")
    check_rows = []
    for item in selected.get("recording_checks", []):
        decision = item.get("controller_decision", {})
        result = decision.get("controller_result", {})
        check_rows.append(
            {
                "Check": item.get("number"),
                "Rule": "{} / {}".format(
                    result.get("rule_status", "—"), result.get("rule_decision", "—")
                ),
                "AI called": yes_no(decision.get("ai_called")),
                "Action": item.get("action", decision.get("action", "—")),
                "Source": decision.get("source", "—"),
                "Status": decision.get("status", "—"),
                "Executed handover": yes_no(item.get("executed_handover")),
            }
        )
    st.dataframe(pd.DataFrame(check_rows), use_container_width=True, hide_index=True)

    st.markdown("#### Measured traffic before and after the decision")
    pre = selected.get("pre_decision", {})
    post = selected.get("post_decision", {})
    metric_specs = [
        ("Packet loss (%)", "loss_pct"),
        ("P95 delay (ms)", "p95_one_way_process_delay_ms"),
        ("Max gap (ms)", "max_interarrival_gap_ms"),
        ("Complete frames (%)", "frames", "complete_pct"),
        ("Goodput (Mbps)", "application_goodput_mbps"),
    ]
    metric_rows = []
    for spec in metric_specs:
        metric_rows.append(
            {
                "Metric": spec[0],
                "Before": value_at(pre, *spec[1:]),
                "After": value_at(post, *spec[1:]),
            }
        )
    metrics_df = pd.DataFrame(metric_rows)
    st.dataframe(metrics_df, use_container_width=True, hide_index=True)

    chart = go.Figure()
    chart.add_bar(
        name="Before decision",
        x=metrics_df["Metric"],
        y=metrics_df["Before"],
        marker_color="#8CA9BC",
    )
    chart.add_bar(
        name="After decision",
        x=metrics_df["Metric"],
        y=metrics_df["After"],
        marker_color="#20D9E8",
    )
    chart.update_layout(
        template="plotly_dark",
        barmode="group",
        paper_bgcolor="#10263B",
        plot_bgcolor="#10263B",
        height=360,
        margin=dict(l=20, r=20, t=35, b=90),
        yaxis_title="Measured value",
    )
    st.plotly_chart(chart, use_container_width=True)

    st.markdown("#### Exact normalized feature vector used by HOSN")
    feature_rows = [
        {"Feature": name, "Value": selected_features.get(name)}
        for name in FEATURE_ORDER
    ]
    st.dataframe(pd.DataFrame(feature_rows), use_container_width=True, hide_index=True)

    st.download_button(
        "Download selected real scenario JSON",
        data=json.dumps(selected, indent=2, sort_keys=True),
        file_name="hosn_scenario_{}_recording_summary.json".format(selected_number),
        mime="application/json",
    )


with tab_replay:
    st.subheader("Run the bundled model without the VM")
    st.caption(
        "This deterministic replay uses the selected recording's final measured "
        "feature vector. It does not run Mininet-WiFi or create new experimental results."
    )

    if MODEL is None:
        st.error("The accepted measured model is unavailable, so no replay can run.")
    else:
        replay = decision_from_features(selected_features, MODEL.model)
        r1, r2, r3, r4 = st.columns(4)
        with r1:
            st.metric("Replay decision", replay.decision)
        with r2:
            st.metric("Rule status", replay.rule_status)
        with r3:
            st.metric("AI called", yes_no(replay.ai_called))
        with r4:
            st.metric("AI prediction", replay.ai_prediction or "—")

        matches = (
            replay.decision == selected_action
            and replay.source == selected_source
            and replay.status == selected_final.get("status")
        )
        if matches:
            st.success("Dashboard replay matches the recorded controller result.")
        else:
            st.warning(
                "Dashboard replay differs from the recording. Compare the artifact "
                "version and feature vector before reporting the result."
            )
        st.write("**Explanation:** {}".format(replay.reason))

        if replay.rule_status == "CONFLICT":
            st.markdown("#### Exact model input row")
            st.code(
                repr([[selected_features[name] for name in FEATURE_ORDER]]),
                language="python",
            )
            st.caption(
                "The controller calls model.predict exactly once for this conflict, "
                "using the eight features in the training order."
            )
        else:
            st.info("This snapshot is a clear rule case; the model is bypassed.")

    with st.expander("Local what-if test (software validation only)"):
        st.caption(
            "Change measured-feature values to exercise the same rules-first path. "
            "These values are not added to the experimental results."
        )
        with st.form("what_if_form"):
            inputs: dict[str, float] = {}
            columns = st.columns(2)
            for index, name in enumerate(FEATURE_ORDER):
                default = selected_features.get(name)
                if not isinstance(default, (int, float)):
                    default = 0.0
                if "loss" in name or "trend" in name:
                    step = 0.1
                else:
                    step = 0.5
                with columns[index % 2]:
                    inputs[name] = st.number_input(
                        name,
                        value=float(default),
                        step=step,
                        format="%.4f",
                    )
            submitted = st.form_submit_button("Run local HOSN decision")
        if submitted:
            if MODEL is None:
                st.error("No accepted model is loaded.")
            else:
                test_decision = decision_from_features(inputs, MODEL.model)
                st.write(
                    "**{}** via **{}** · rule status **{}** · AI called **{}**".format(
                        test_decision.decision,
                        test_decision.source,
                        test_decision.rule_status,
                        yes_no(test_decision.ai_called),
                    )
                )
                st.caption(test_decision.reason)


with tab_contract:
    st.subheader("Measured AI training and deployment contract")
    if MODEL is None:
        st.error("The model report is unavailable.")
    else:
        report = MODEL.report
        group = report.get("cross_validation", {}).get("group_metrics", {})
        recall = group.get("recall", {})
        contract_rows = [
            {
                "Item": "Acceptance gate",
                "Value": "PASSED"
                if report.get("acceptance_gate", {}).get("accepted")
                else "FAILED",
            },
            {"Item": "Training data", "Value": "Measured Mininet-WiFi + emulated 5G"},
            {"Item": "Synthetic data", "Value": str(report.get("synthetic_data"))},
            {"Item": "Label source", "Value": report.get("label_source")},
            {"Item": "Model", "Value": report.get("model")},
            {"Item": "Training rows", "Value": report.get("rows")},
            {"Item": "Independent groups", "Value": report.get("independent_scenario_groups")},
            {"Item": "Grouped CV balanced accuracy", "Value": group.get("balanced_accuracy")},
            {"Item": "Grouped CV STAY recall", "Value": recall.get("STAY")},
            {"Item": "Grouped CV HANDOVER recall", "Value": recall.get("HANDOVER")},
            {"Item": "Model SHA-256", "Value": MODEL.sha256},
        ]
        st.dataframe(pd.DataFrame(contract_rows), use_container_width=True, hide_index=True)
        st.markdown("#### Feature order")
        st.code("\n".join(FEATURE_ORDER), language="text")
        st.info(
            "The dashboard contains only the inference dependencies. The VM is still "
            "required for Mininet-WiFi collection and handover experiments, but not "
            "for this Streamlit model replay."
        )

st.divider()
st.caption(
    "HOSN | حصن — Results shown above are the committed measured recordings. "
    "The dashboard does not invent scenario outcomes."
)

