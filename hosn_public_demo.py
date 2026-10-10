
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from dataclasses import dataclass

# PUBLIC DEMO: illustrative decision logic, NOT the private HOSN controller.
@dataclass
class DemoResult:
    decision: str
    source: str
    status: str
    reason: str


# -----------------------------------
# HOSN Dashboard Configuration
# -----------------------------------
st.set_page_config(
    page_title="HOSN | Control Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

NAVY = "#071421"
CARD = "#10263B"
CYAN = "#20D9E8"
WHITE = "#EAF7FF"
MUTED = "#8CA9BC"

st.markdown("""
<style>
.stApp {
    background: #071421;
    color: #EAF7FF;
}
[data-testid="stSidebar"] {
    background: #0B1D30;
}
.block-container {
    padding-top: 1.5rem;
    max-width: 1500px;
}
h1, h2, h3 {
    color: #EAF7FF !important;
}
div[data-testid="stMetric"] {
    background: #10263B;
    border: 1px solid #214760;
    border-radius: 14px;
    padding: 18px;
}
div[data-testid="stMetricLabel"] {
    color: #8CA9BC;
}
div[data-testid="stMetricValue"] {
    color: #20D9E8;
}
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: #214760;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------
# Sidebar
# -----------------------------------
with st.sidebar:
    st.title("🛡️ HOSN | حصن")
    st.caption("Intelligent Handover System")
    st.divider()

    st.subheader("Control Panel")

    scenario = st.selectbox(
        "Select Network Scenario",
        [
            "Stable Wi-Fi",
            "Wi-Fi Degradation",
            "Conflicting Measurements"
        ]
    )

    st.divider()
    st.markdown("### Signal Thresholds")
    st.write("Wi-Fi: -80 dBm")
    st.write("5G: -120 dBm")

    st.divider()
    st.info("DEMO MODE: Illustrative data only.")

# -----------------------------------
# Example Scenario Data
# -----------------------------------
if scenario == "Stable Wi-Fi":
    wifi_signal = -60
    cellular_signal = -105
    rtt = 22
    loss = 0.0
    current_network = "Wi-Fi"
    decision = "STAY"
    decision_mode = "Rule-Based"
    target = "Wi-Fi"

elif scenario == "Wi-Fi Degradation":
    wifi_signal = -88
    cellular_signal = -103
    rtt = 95
    loss = 5.2
    current_network = "Wi-Fi"
    decision = "HANDOVER"
    decision_mode = "Rule-Based"
    target = "5G"

else:
    wifi_signal = -84
    cellular_signal = -90
    rtt = 18
    loss = 0.0
    current_network = "Wi-Fi"
    decision = "AI REVIEW"
    decision_mode = "AI Required"
    target = "Pending"

# -----------------------------------
# Header
# -----------------------------------

# Standalone illustrative demo decisions. No AI model or network execution.
if scenario == "Stable Wi-Fi":
    hosn_result = DemoResult("STAY", "DEMO RULES", "CLEAR", "Illustrative stable Wi-Fi conditions.")
elif scenario == "Wi-Fi Degradation":
    hosn_result = DemoResult("HANDOVER", "DEMO RULES", "CLEAR", "Illustrative Wi-Fi degradation; 5G is the suggested target.")
else:
    hosn_result = DemoResult("STAY", "DEMO HOLD", "AI_UNAVAILABLE", "Conflicting measurements; no trained AI model is connected.")

decision = hosn_result.decision
decision_mode = hosn_result.source
decision_status = hosn_result.status
decision_reason = hosn_result.reason
target = "5G" if decision == "HANDOVER" else current_network

st.title("HOSN | Network Control Center — Public Demo")
st.caption(
    "Public concept demonstration of hybrid Wi-Fi / 5G handover"
)

st.info(
    "PUBLIC DEMO — Values and decisions are "
    "illustrative, not live Mininet-WiFi results."
)

st.divider()

# -----------------------------------
# Network Metrics
# -----------------------------------
st.subheader("Network Monitoring")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Current Connection", current_network)

with c2:
    st.metric("Wi-Fi Signal", f"{wifi_signal} dBm")

with c3:
    st.metric("Latency (RTT)", f"{rtt} ms")

with c4:
    st.metric("Packet Loss", f"{loss:.1f}%")




# -----------------------------------
# HOSN Animated Mobility Demo (single, corrected version)
# -----------------------------------
import json as _hosn_json
import streamlit.components.v1 as components

st.divider()
st.subheader("HOSN | Intelligent Mobility Demo")
st.caption("Illustrative motion and values. Final recommendation follows the selected demo scenario; no private controller, AI model or physical handover is used.")

_hosn_html = r'''

<style>
html, body {
    min-height: 100%;
    overflow-y: auto !important;
}

.panel {
    min-height: 0;
    padding-bottom: 28px !important;
    overflow: visible !important;
}

*{box-sizing:border-box}body{margin:0;background:#071421;color:#eaf7ff;font-family:Segoe UI,Arial,sans-serif}.panel{background:linear-gradient(125deg,#0a2035,#102b3b 65%,#092b35);border:1px solid #23546a;border-radius:18px;padding:20px 24px;overflow:visible}.head{display:flex;align-items:center;justify-content:space-between;gap:12px}.head h2{font-size:20px;margin:0 0 5px}.sub{color:#8ca9bc;font-size:12px}.tag{color:#42e7cf;border:1px solid #276f73;border-radius:20px;padding:6px 12px;font-size:11px;white-space:nowrap}.scene{position:relative;margin-top:12px;height:176px}.scene svg{width:100%;height:100%;display:block;overflow:visible}.base{stroke:#34566a;stroke-width:3;stroke-dasharray:5 7}.active{stroke:#28e5d4;stroke-width:4;stroke-linecap:round;filter:drop-shadow(0 0 5px #20d9e8);transition:all .5s}.node{fill:#102f44;stroke:#277b8b;stroke-width:1.5}.phone{transition:transform .85s cubic-bezier(.2,.7,.2,1)}.pulse{animation:pulse 1.3s ease-in-out infinite}@keyframes pulse{50%{opacity:.35}}.status{display:flex;align-items:center;justify-content:space-between;gap:10px;background:#0a1929;border:1px solid #23465a;border-radius:12px;padding:12px 14px;margin-top:8px}.state{font-weight:700;color:#42e7cf;font-size:13px}.metrics{font-size:12px;color:#b4d2df;margin-top:7px}.actions{display:flex;align-items:center;gap:14px;flex-wrap:wrap;margin-top:14px}.start{background:linear-gradient(100deg,#00a99a,#12c8b6);border:1px solid #46e6d3;border-radius:12px;padding:12px 22px;color:#05232b;font-weight:800;font-size:13px;letter-spacing:.3px;cursor:pointer;box-shadow:0 4px 20px #00a99a44;transition:transform .15s,box-shadow .15s}.start:hover{transform:translateY(-2px);box-shadow:0 6px 24px #00d8bd70}.start:disabled{opacity:.6;cursor:wait;transform:none}.foot{color:#87a8b7;font-size:11px}.progress{height:4px;border-radius:6px;background:#193a4c;margin-top:14px;overflow:hidden}.fill{height:100%;width:0;background:linear-gradient(90deg,#20d9e8,#00ffa3);transition:width .85s}@media(max-width:500px){.panel{padding:14px}.head h2{font-size:16px}.tag{font-size:9px}.status{align-items:flex-start;flex-direction:column}.scene{height:148px}}
/* Keep the primary action visible at the top of the demo card. */
.actions{margin:16px 0 4px;gap:12px}
.start{background:linear-gradient(110deg,#08e1b0,#20d9e8);border:1px solid #79ffe4;border-radius:999px;padding:13px 26px;box-shadow:0 0 0 1px #16d8b733,0 8px 28px #00d5bb44;min-height:46px}
.start:focus-visible{outline:3px solid #eaf7ff;outline-offset:3px}
@media(max-width:500px){.actions{align-items:stretch}.start{width:100%}}
</style>
<div class="panel">
 <div class="head"><div><h2>🛡️ HOSN | Smart Mobility Control</h2><div class="sub">Intelligent Wi-Fi / 5G Handover • Interactive Prototype</div></div><span class="tag">● DEMO MODE</span></div>
 <div class="actions"><button id="start" class="start" type="button">▶ LAUNCH HOSN SIMULATION</button><span class="foot">Conceptual motion only. No physical network switching.</span></div>
 <div class="scene"><svg viewBox="0 0 800 175" role="img" aria-label="Phone moving from Wi-Fi coverage toward 5G coverage">
  <line x1="108" y1="88" x2="692" y2="88" class="base"/><line id="beam" x1="108" y1="88" x2="148" y2="88" class="active"/>
  <rect x="12" y="42" width="130" height="96" rx="16" class="node"/><rect x="658" y="42" width="130" height="96" rx="16" class="node"/>
  <g fill="none" stroke="#28e5d4" stroke-width="3" stroke-linecap="round"><path d="M43 75 Q77 45 111 75 M54 85 Q77 65 100 85"/><circle cx="77" cy="93" r="3" fill="#28e5d4"/><path d="M723 64 V98 M710 98 H736 M723 64 L710 77 M723 64 L736 77"/></g>
  <g fill="#eaf7ff" font-family="Segoe UI,Arial" font-size="14" text-anchor="middle"><text x="77" y="119">Wi-Fi AP1</text><text x="723" y="119">5G</text></g>
  <g id="movingPhone" class="phone" transform="translate(0 0)"><circle cx="154" cy="88" r="29" fill="#20d9e8" opacity=".12" class="pulse"/><rect x="140" y="62" width="28" height="51" rx="6" fill="#b9fbf1" stroke="#21d9c6" stroke-width="2"/><rect x="144" y="69" width="20" height="35" rx="2" fill="#10364b"/><circle cx="154" cy="108" r="2" fill="#0c4252"/></g>
 </svg></div>
 <div class="status"><span id="state" class="state" aria-live="polite">READY · Connected to Wi-Fi</span><span id="stepLabel" class="sub">STAGE 0 / 5</span></div>
 <div id="metrics" class="metrics">Wi-Fi Signal: -60 dBm &nbsp; | &nbsp; RTT: 22 ms &nbsp; | &nbsp; Packet Loss: 0%</div>

<div class="progress"><div id="fill" class="fill"></div></div>
</div>
<script>
const controllerDecision=__DECISION__;
const controllerSource=__SOURCE__;
const controllerStatus=__STATUS__;
const stages=[
 {x:154,text:'VIDEO CALL ACTIVE · Wi-Fi connected',signal:-60,rtt:22,loss:0},
 {x:270,text:'USER MOVING · Network monitoring',signal:-70,rtt:35,loss:0.3},
 {x:390,text:'WI-Fi DEGRADING · Signal weakening',signal:-79,rtt:55,loss:1.2},
 {x:525,text:'HOSN ANALYSIS · Evaluating candidate network',signal:-85,rtt:78,loss:3.0},
 {x:680,text:'HOSN DECISION · '+(controllerDecision==='HANDOVER'?'5G recommended':controllerDecision==='STAY'?'Stay on Wi-Fi':'Hold current connection'),signal:-88,rtt:95,loss:5.2}
];
let running=false;
const btn=document.getElementById('start');
const phone=document.getElementById('movingPhone');
const beam=document.getElementById('beam');
const state=document.getElementById('state');
const stepLabel=document.getElementById('stepLabel');
const metrics=document.getElementById('metrics');
const fill=document.getElementById('fill');
const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));
function reset(){phone.style.transform='translate(0px,0px)';beam.setAttribute('x2','154');fill.style.width='0%';state.textContent='READY · Connected to Wi-Fi';stepLabel.textContent='STAGE 0 / 5';metrics.textContent='Wi-Fi Signal: -60 dBm | RTT: 22 ms | Packet Loss: 0%';}
btn.addEventListener('click',async()=>{
 if(running)return;
 running=true;btn.disabled=true;btn.textContent='SIMULATION RUNNING…';reset();
 for(let i=0;i<stages.length;i++){
  const s=stages[i];
  const position=(i===stages.length-1 && controllerDecision!=='HANDOVER')?390:s.x;
   phone.style.transform='translate('+(position-154)+'px,0px)';
  beam.setAttribute('x2',String(position));
  state.textContent=s.text;
  stepLabel.textContent='STAGE '+(i+1)+' / 5';
  metrics.textContent='Wi-Fi Signal: '+s.signal+' dBm | RTT: '+s.rtt+' ms | Packet Loss: '+s.loss+'%';
  fill.style.width=((i+1)*20)+'%';
  await sleep(1450);
 }
 state.textContent='DEMO DECISION: '+controllerDecision+' · '+controllerSource+' · '+controllerStatus;
 btn.disabled=false;btn.textContent='↻ REPLAY SIMULATION';running=false;
});
</script>
'''
_hosn_html = (_hosn_html
    .replace("__DECISION__", _hosn_json.dumps(str(decision)))
    .replace("__SOURCE__", _hosn_json.dumps(str(decision_mode)))
    .replace("__STATUS__", _hosn_json.dumps(str(decision_status))))
components.html(_hosn_html, height=620, scrolling=True)

# -----------------------------------
# Network Visualization
# -----------------------------------
st.divider()
st.subheader("Network Status")

left, right = st.columns(2)

with left:
    with st.container(border=True):
        st.markdown("### 📶 Wi-Fi | AP1")
        st.metric("Signal Strength", f"{wifi_signal} dBm")
        st.write("Threshold: -80 dBm")

        if wifi_signal < -80:
            st.error("Signal below configured threshold")
        else:
            st.success("Signal above configured threshold")

with right:
    with st.container(border=True):
        st.markdown("### 📡 5G | Cellular")
        st.metric(
            "Simulated Signal Strength",
            f"{cellular_signal} dBm"
        )
        st.write("Threshold: -120 dBm")

        if cellular_signal < -120:
            st.error("Signal below configured threshold")
        else:
            st.success("Signal above configured threshold")

# -----------------------------------
# HOSN Decision Engine
# -----------------------------------
st.divider()
st.subheader("HOSN Decision Engine")

d1, d2 = st.columns(2)

with d1:
    with st.container(border=True):
        st.markdown("### Decision Analysis")
        st.write(f"**Decision Mode:** {decision_mode}")
        
        st.write(f"**Decision Status:** {decision_status}")
        st.caption(f"Reason: {decision_reason}")

        st.write(f"**Current Network:** {current_network}")

        if decision == "HANDOVER":
            st.warning("HANDOVER recommended")
        elif decision == "STAY":
            st.success("STAY connected")
        else:
            st.info("AI prediction required")

with d2:
    with st.container(border=True):
        st.markdown("### Network Selection")
        st.write(f"**Target Network:** {target}")
        st.write(f"**Decision:** {decision}")
        st.caption(
            "Illustrative decision. No physical "
            "network switching is performed."
        )

# -----------------------------------
# Interactive Measurement Graphs
# -----------------------------------
st.divider()
st.subheader("Network Measurements Over Time")

times = list(range(0, 61, 5))

if scenario == "Stable Wi-Fi":
    signals = [-58, -59, -60, -61, -60, -62,
               -61, -60, -59, -60, -61, -60, -60]
    delays = [20, 21, 22, 21, 23, 22,
              21, 22, 20, 21, 22, 22, 22]
    losses = [0.0] * 13

elif scenario == "Wi-Fi Degradation":
    signals = [-58, -61, -64, -68, -72, -76,
               -80, -83, -85, -87, -88, -88, -88]
    delays = [20, 24, 28, 35, 42, 50,
              60, 68, 75, 82, 90, 93, 95]
    losses = [0, 0, 0.1, 0.3, 0.5, 0.8,
              1.2, 1.8, 2.5, 3.1, 4.0, 4.7, 5.2]

else:
    signals = [-68, -70, -72, -74, -77, -79,
               -81, -82, -83, -84, -84, -84, -84]
    delays = [35, 32, 30, 28, 26, 24,
              22, 21, 20, 19, 18, 18, 18]
    losses = [0.0] * 13

data = pd.DataFrame({
    "Time (s)": times,
    "Wi-Fi Signal (dBm)": signals,
    "RTT (ms)": delays,
    "Packet Loss (%)": losses
})

def make_chart(column, color, threshold=None):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=data["Time (s)"],
        y=data[column],
        mode="lines+markers",
        line=dict(color=color, width=3),
        marker=dict(size=6),
        name=column
    ))

    if threshold is not None:
        fig.add_hline(
            y=threshold,
            line_dash="dash",
            line_color="#FFB454",
            annotation_text="Threshold"
        )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=CARD,
        plot_bgcolor=CARD,
        font=dict(color=WHITE),
        height=310,
        margin=dict(l=20, r=20, t=25, b=20),
        xaxis_title="Time (seconds)",
        yaxis_title=column
    )

    return fig

g1, g2 = st.columns(2)

with g1:
    st.plotly_chart(
        make_chart("Wi-Fi Signal (dBm)", CYAN, -80),
        use_container_width=True
    )

with g2:
    st.plotly_chart(
        make_chart("RTT (ms)", "#A78BFA"),
        use_container_width=True
    )

st.plotly_chart(
    make_chart("Packet Loss (%)", "#FF718B"),
    use_container_width=True
)

# -----------------------------------
# Handover Event Log
# -----------------------------------
st.divider()
st.subheader("Handover Event Log")

if decision == "HANDOVER":
    events = pd.DataFrame([{
        "Time": "Demo scenario",
        "From": "Wi-Fi",
        "To": "5G",
        "Decision Mode": decision_mode,
        "Status": "Recommended only"
    }])
    st.dataframe(events, use_container_width=True,
                 hide_index=True)
else:
    st.info(
        "No executed handover events in this demo. "
        "No live network executor is connected."
    )

# -----------------------------------
# Export
# -----------------------------------
st.divider()
st.subheader("Export Scenario Measurements")

st.download_button(
    "Download Demo CSV",
    data=data.to_csv(index=False),
    file_name="hosn_demo_measurements.csv",
    mime="text/csv"
)

st.caption(
    "HOSN | حصن — ATP Prototype. "
    "Demo data must not be reported as experimental results."
)



# -----------------------------------
# HOSN Handover Process Timeline
# -----------------------------------
st.divider()
st.subheader("HOSN | Handover Process")

st.caption(
    "Conceptual process visualization — "
    "not an executed network handover."
)

steps = [
    ("01", "VIDEO CALL", "Application traffic is active"),
    ("02", "MONITOR", "Collect network measurements"),
    ("03", "ANALYZE", "Rules evaluate both networks"),
    ("04", "DECIDE", f"{decision_mode}: {decision}"),
    ("05", "NEXT ACTION",
     "Recommend 5G handover"
     if decision == "HANDOVER"
     else "Maintain current connection")
]

columns = st.columns(5)

for col, (number, title, description) in zip(columns, steps):
    with col:
        with st.container(border=True):
            st.markdown(f"### {number}")
            st.markdown(f"**{title}**")
            st.caption(description)

if decision == "HANDOVER":
    st.warning(
        "Handover recommended: Wi-Fi → 5G. "
        "Execution is not connected in this dashboard."
    )
elif decision_mode == "HOLD":
    st.info(
        "Decision on hold: continue measuring "
        "until AI or sufficient data is available."
    )
else:
    st.success(
        "Stay connected: no handover recommended."
    )

# -----------------------------------
# Final Experimental Comparison
# -----------------------------------
from pathlib import Path
import json

st.divider()
st.subheader("Experimental Comparison")

st.caption(
    "RSSI Baseline vs HOSN Rules-Only vs HOSN Full AI"
)

results_root = Path(__file__).resolve().parent / "results"

reports = sorted(
    results_root.glob(
        "final_three_arm_comparison_*/final_comparison_report.json"
    ),
    reverse=True
)

if not reports:
    st.info(
        "Final experimental results are not available yet. "
        "Waiting for the team's validated Mininet-WiFi comparison."
    )
else:
    try:
        report = json.loads(
            reports[0].read_text(encoding="utf-8")
        )

        if report.get("completed_replays") != 48:
            st.warning(
                "Comparison report is incomplete. "
                "Results are not displayed as final."
            )
        elif not report.get("mechanical_checks_pass", False):
            st.warning(
                "Experimental checks did not pass. "
                "Results require review."
            )
        elif not report.get("ai_used_only_for_conflicts", False):
            st.warning(
                "AI routing checks did not pass. "
                "Results require review."
            )
        else:
            summary = report["aggregate_by_strategy"]

            rows = []

            for strategy, values in summary.items():
                rows.append({
                    "Strategy": strategy,
                    "Decision Accuracy (%)":
                        values["decision_accuracy_pct"],
                    "Packet Loss (%)":
                        values["mean_post_loss_pct"],
                    "Max Gap (ms)":
                        values["mean_post_max_gap_ms"],
                    "Complete Frames (%)":
                        values["mean_post_complete_frames_pct"]
                })

            comparison_df = pd.DataFrame(rows)

            st.success(
                "Validated comparison report loaded."
            )

            st.dataframe(
                comparison_df,
                use_container_width=True,
                hide_index=True
            )

            metric = st.selectbox(
                "Compare Performance Metric",
                [
                    "Decision Accuracy (%)",
                    "Packet Loss (%)",
                    "Max Gap (ms)",
                    "Complete Frames (%)"
                ]
            )

            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=comparison_df["Strategy"],
                y=comparison_df[metric],
                marker_color="#20D9E8"
            ))

            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="#10263B",
                plot_bgcolor="#10263B",
                title=metric,
                xaxis_title="Strategy",
                yaxis_title=metric
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    except (OSError, ValueError, KeyError, TypeError) as error:
        st.error(
            "Could not read the experimental report: "
            + str(error)
        )



# -----------------------------------
# HOSN System Architecture
# -----------------------------------
st.divider()
st.subheader("HOSN | System Architecture")

st.caption(
    "Conceptual architecture of the hybrid "
    "rule-based and AI-assisted handover system."
)

a, b, c, d = st.columns(4)

with a:
    with st.container(border=True):
        st.markdown("### 01 | NETWORK")
        st.write("Wi-Fi AP1")
        st.write("5G-like Cellular")
        st.caption("Emulated network environment")

with b:
    with st.container(border=True):
        st.markdown("### 02 | MONITOR")
        st.write("Signal Strength")
        st.write("RTT / Latency")
        st.write("Packet Loss")
        st.caption("Network measurements")

with c:
    with st.container(border=True):
        st.markdown("### 03 | DECIDE")
        st.write("Rules First")
        st.write("AI for Conflicts")
        st.caption("Hybrid HOSN controller")

with d:
    with st.container(border=True):
        st.markdown("### 04 | ACTION")
        st.write("STAY")
        st.write("HANDOVER")
        st.caption("Network decision output")

st.info(
    "Rules handle clear cases. AI is intended "
    "for conflicting measurements only."
)

# -----------------------------------
# AI Training & Validation
# -----------------------------------
st.divider()
st.subheader("AI Training & Validation")

st.caption(
    "Research methodology — not a live "
    "model performance report."
)

m1, m2, m3 = st.columns(3)

with m1:
    st.metric("Reported Samples", "128")

with m2:
    st.metric("Scenario Groups", "32")

with m3:
    st.metric("AI Input Features", "8")

st.caption(
    "Sample and group counts are project-reported "
    "figures pending final dataset verification."
)

st.markdown("### Machine Learning Pipeline")

pipeline = [
    "1. Mininet-WiFi measurements",
    "2. Reviewed experimental dataset",
    "3. Scenario-grouped validation",
    "4. StandardScaler + Logistic Regression",
    "5. Model acceptance checks",
    "6. AI inference for rule conflicts"
]

for step in pipeline:
    st.write(step)

st.warning(
    "This public demo does not include a trained AI model or private training files."
)

st.markdown("### Validation Safeguards")

st.write(
    "Scenario replays are grouped during validation "
    "to reduce training/testing leakage."
)

st.write(
    "Only pre-decision features are permitted "
    "as model inputs."
)

st.write(
    "A production model must pass accuracy and per-class "
    "recall acceptance checks before deployment."
)



# -----------------------------------
# HOSN Video Call Quality Monitoring
# -----------------------------------
st.divider()
st.subheader("Video Call | Quality Monitoring")

st.caption(
    "Illustrative video-call risk indicators based on "
    "simulated RTT and packet loss. "
    "Not an actual video-call quality measurement."
)

# Demo-only quality classification
if loss >= 3.0 or rtt >= 100:
    call_status = "HIGH RISK"
    call_message = (
        "Network conditions may cause interruptions "
        "during a video call."
    )
elif loss >= 1.0 or rtt >= 60:
    call_status = "DEGRADING"
    call_message = (
        "Network quality is deteriorating. "
        "Video-call performance may be affected."
    )
else:
    call_status = "STABLE"
    call_message = (
        "Current network measurements indicate "
        "a relatively stable connection."
    )

v1, v2, v3 = st.columns(3)

with v1:
    st.metric("Video Call Status", call_status)

with v2:
    st.metric("Network RTT", f"{rtt} ms")

with v3:
    st.metric("Packet Loss", f"{loss:.1f}%")

with st.container(border=True):
    st.markdown("### Video Call Assessment")

    if call_status == "STABLE":
        st.success(call_message)
    elif call_status == "DEGRADING":
        st.warning(call_message)
    else:
        st.error(call_message)

    st.write(f"**Current Network:** {current_network}")
    st.write(f"**HOSN Decision:** {decision}")
    st.write(f"**Decision Source:** {decision_mode}")

    if decision == "HANDOVER":
        st.info(
            "HOSN recommends switching to the "
            "candidate network. The actual handover "
            "and video-call continuity are not measured here."
        )
    elif decision_mode == "HOLD":
        st.warning(
            "HOSN is holding the current connection "
            "because the AI model is unavailable "
            "or further decision support is required."
        )
    else:
        st.success(
            "HOSN recommends maintaining "
            "the current connection."
        )

st.caption(
    "Demo risk thresholds: RTT >= 60 ms or "
    "loss >= 1% indicates degradation; "
    "RTT >= 100 ms or loss >= 3% indicates high risk. "
    "These are illustrative dashboard settings, "
    "not experimentally validated video-call thresholds."
)



# -----------------------------------
# HOSN Network Switching Visualization
# -----------------------------------
st.divider()
st.subheader("Wi-Fi ↔ 5G | Network Switching")

st.caption(
    "Interactive decision visualization using demo "
    "measurements and illustrative demo logic. "
    "No physical handover is executed."
)

net_left, net_center, net_right = st.columns([2, 1, 2])

with net_left:
    with st.container(border=True):
        st.markdown("### 📶 Wi-Fi | AP1")
        st.metric("Signal", f"{wifi_signal} dBm")
        st.write("Service Floor: -80 dBm")

        if current_network == "Wi-Fi":
            st.success("CURRENT CONNECTION")
        else:
            st.info("AVAILABLE NETWORK")

with net_center:
    st.markdown("### ⇄")
    st.markdown("**HOSN**")

    if decision == "HANDOVER":
        st.warning("SWITCH")
    elif decision_mode == "HOLD":
        st.info("HOLD")
    else:
        st.success("STAY")

with net_right:
    with st.container(border=True):
        st.markdown("### 📡 5G | Cellular")
        st.metric("Signal", f"{cellular_signal} dBm")
        st.write("Service Floor: -120 dBm")

        if decision == "HANDOVER":
            st.warning("RECOMMENDED TARGET")
        else:
            st.info("CANDIDATE NETWORK")

st.divider()

st.markdown("### HOSN Switching Decision")

if decision == "HANDOVER":
    st.warning(
        "Wi-Fi → 5G handover recommended. "
        "The network connection has not actually switched."
    )
elif decision_mode == "HOLD":
    st.info(
        "HOSN detected a decision conflict. "
        "The current Wi-Fi connection is maintained "
        "because no accepted AI model is connected in this public demo."
    )
else:
    st.success(
        "STAY on Wi-Fi. HOSN does not recommend "
        "a network change under these measurements."
    )

st.write(f"**Decision Source:** {decision_mode}")
st.write(f"**Decision Status:** {decision_status}")
st.caption(f"Demo explanation: {decision_reason}")
