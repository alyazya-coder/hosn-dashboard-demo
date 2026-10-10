from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

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

# Visual-only mobility story. The decision label comes from the selected recording.
st.subheader("HOSN | Intelligent Mobility")
st.caption("Animated explanation of the selected recorded decision — not a live network switch.")
_demo_action = str(selected_action)
_demo_source = str(selected_source)
_demo_ai = bool(selected_final.get("ai_called"))
_demo_html = r"""
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"/>
<style>
*{box-sizing:border-box}html,body{margin:0;padding:0;background:#071421;color:#eaf7ff;font-family:Segoe UI,Arial,sans-serif}
.panel{border:1px solid #23556b;border-radius:18px;background:linear-gradient(125deg,#0b2337,#10303b);padding:16px;min-height:355px}
.top{display:flex;align-items:center;justify-content:space-between;gap:8px;flex-wrap:wrap}.top strong{font-size:17px}.pill{border:1px solid #287a79;border-radius:30px;color:#53e8d5;padding:5px 11px;font-size:11px}
button{display:inline-block;background:linear-gradient(100deg,#0dd8c4,#41f0b7);color:#062b31;border:0;border-radius:12px;padding:12px 18px;font-weight:800;cursor:pointer;box-shadow:0 0 17px #14d7bf66;max-width:100%;margin:12px 0 8px}button:disabled{opacity:.6;cursor:wait}
svg{width:100%;height:166px;display:block;overflow:visible}.line{stroke:#375d70;stroke-width:4;stroke-dasharray:7 8}.beam{stroke:#36ead4;stroke-width:5;stroke-linecap:round;filter:drop-shadow(0 0 5px #2cf4c6)}.node{fill:#123449;stroke:#2d9c9b;stroke-width:2}.phone{transition:transform .8s ease-in-out}
.info{display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;border:1px solid #285165;background:#0a1d2d;border-radius:10px;padding:11px;font-size:12px}.status{color:#53e8d5;font-weight:700}.foot{color:#a3beca;font-size:11px}.track{height:5px;border-radius:5px;background:#183c4c;overflow:hidden}.fill{height:100%;width:0;background:linear-gradient(90deg,#1ad9ee,#4ef0b7);transition:width .7s}
</style></head><body><div class="panel">
<div class="top"><strong>🛡️ HOSN · Mobility Command</strong><span class="pill">RECORDED SCENARIO · VISUAL REPLAY</span></div>
<button id="go">▶ LAUNCH MOBILITY DEMO</button>
<svg viewBox="0 0 800 165" aria-label="Illustration of Wi-Fi and emulated 5G connectivity">
<line x1="120" y1="83" x2="680" y2="83" class="line"/><line id="beam" x1="120" y1="83" x2="165" y2="83" class="beam"/>
<rect x="10" y="40" width="140" height="92" rx="16" class="node"/><rect x="650" y="40" width="140" height="92" rx="16" class="node"/>
<g fill="none" stroke="#41ead7" stroke-width="3"><path d="M42 73 Q80 38 118 73 M56 85 Q80 63 104 85"/><path d="M720 59 V99 M704 99 H736 M720 59 L706 74 M720 59 L734 74"/></g>
<g fill="#eaf7ff" font-size="15" text-anchor="middle"><text x="80" y="115">Wi-Fi AP1</text><text x="720" y="115">5G-like</text></g>
<g id="phone" class="phone"><circle cx="165" cy="82" r="28" fill="#21d9e8" opacity=".18"/><rect x="151" y="55" width="28" height="51" rx="6" fill="#c6fff6"/><rect x="155" y="62" width="20" height="34" rx="2" fill="#0c3446"/></g>
</svg>
<div class="info"><span id="stage" class="status">READY · Wi-Fi connected</span><span id="detail">Controller: __SOURCE__ · __ACTION__</span></div>
<p class="foot">Decision is read from the recorded VM scenario. Movement is an illustration, not an executed handover.</p>
<div class="track"><div id="fill" class="fill"></div></div>
</div>
<script>
const action=__ACTION_JSON__, source=__SOURCE_JSON__, ai=__AI_JSON__;
const btn=document.getElementById('go'),phone=document.getElementById('phone'),beam=document.getElementById('beam'),stage=document.getElementById('stage'),detail=document.getElementById('detail'),fill=document.getElementById('fill');
let busy=false;const sleep=ms=>new Promise(r=>setTimeout(r,ms));
btn.onclick=async()=>{if(busy)return;busy=true;btn.disabled=true;btn.textContent='SIMULATION RUNNING…';
const isHandover=action==='HANDOVER';
const frames=[{x:165,t:'VIDEO CALL ACTIVE · Wi-Fi connected'},{x:265,t:'USER MOVING · Monitoring quality'},{x:380,t:'HOSN RULES · Evaluating networks'},{x:isHandover?525:405,t:ai?'RULE CONFLICT · AI consulted':'RULES · Clear decision'},{x:isHandover?680:405,t:'FINAL DECISION · '+action}];
phone.style.transform='translate(0px,0px)';beam.setAttribute('x2','165');fill.style.width='0%';
for(let i=0;i<frames.length;i++){const f=frames[i];phone.style.transform='translate('+(f.x-165)+'px,0px)';beam.setAttribute('x2',String(f.x));stage.textContent=f.t;detail.textContent='Controller: '+source+' · '+action;fill.style.width=((i+1)*20)+'%';await sleep(1100)}
btn.textContent='↻ REPLAY MOBILITY DEMO';btn.disabled=false;busy=false};
</script></body></html>
"""
_demo_html = (_demo_html.replace("__ACTION_JSON__", json.dumps(_demo_action))
    .replace("__SOURCE_JSON__", json.dumps(_demo_source))
    .replace("__AI_JSON__", json.dumps(_demo_ai))
    .replace("__ACTION__", _demo_action).replace("__SOURCE__", _demo_source))
components.html(_demo_html, height=385, scrolling=False)

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
    with st.expander("View all four monitoring checks"):
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
    st.markdown("#### Performance snapshots")
    for first in range(0, len(metric_rows), 3):
        cols = st.columns(min(3, len(metric_rows) - first))
        for col, item in zip(cols, metric_rows[first:first+3]):
            with col:
                before, after = item["Before"], item["After"]
                fmt = lambda v: f"{v:.2f}" if isinstance(v, (int, float)) else str(v if v is not None else "N/A")
                st.markdown(f"**{item['Metric']}**")
                st.metric("After decision", fmt(after), delta=(f"Before: {fmt(before)}"), delta_color="off")
    with st.expander("Full measured values (before / after)"):
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
        template=None,
        barmode="group",
        paper_bgcolor="#10263B",
        plot_bgcolor="#10263B",
        height=360,
        margin=dict(l=20, r=20, t=35, b=90),
        yaxis_title="Measured value",
    )
    st.plotly_chart(chart, use_container_width=True, theme=None)

    st.markdown("#### Exact normalized feature vector used by HOSN")
    feature_rows = [
        {"Feature": name, "Value": selected_features.get(name)}
        for name in FEATURE_ORDER
    ]
    friendly_features = [
        ("Wi-Fi signal margin", "current_signal_margin_db", "dB"),
        ("Candidate signal margin", "candidate_signal_margin_db", "dB"),
        ("Wi-Fi latency", "current_latency_ms", "ms"),
        ("Candidate latency", "candidate_latency_ms", "ms"),
        ("Wi-Fi packet loss", "current_loss_pct", "%"),
        ("Candidate packet loss", "candidate_loss_pct", "%"),
    ]
    for offset in range(0, len(friendly_features), 3):
        feature_cols = st.columns(3)
        for col, (label, key, unit) in zip(feature_cols, friendly_features[offset:offset+3]):
            value = selected_features.get(key)
            display = f"{value:.2f} {unit}" if isinstance(value, (int, float)) else "N/A"
            with col:
                st.metric(label, display)
    with st.expander("Show all eight exact AI features (technical details)"):
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
        with st.expander("View complete training contract and validation metrics"):
            st.dataframe(pd.DataFrame(contract_rows), use_container_width=True, hide_index=True)
        with st.expander("🧠 View AI Input Features"):
            cols = st.columns(2)
            for i, feature in enumerate(FEATURE_ORDER):
                with cols[i % 2]:
                    st.info(f"🔹 {i + 1:02d} | {feature}")
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

