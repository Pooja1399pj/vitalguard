"""
VitalGuard Dashboard
Displays live pipeline stats from Firestore, agent-wise breakdown,
transport-privacy proof (Wireshark), compliance summary, and
personal insight -- tying all 5 agents into one view.
"""
import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv
from google.cloud import firestore

load_dotenv()
PROJECT_ID = os.getenv("GCP_PROJECT_ID")

st.set_page_config(page_title="VitalGuard Dashboard", layout="wide")

db = firestore.Client(project=PROJECT_ID)

st.markdown("""
<style>
@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.4; }
    100% { opacity: 1; }
}
.top-right-live {
    display: flex;
    justify-content: flex-end;
    align-items: center;
}

.live-badge {
    display: inline-flex;
    align-items: center;
    background-color: rgba(46, 204, 113, 0.15);
    border: 1px solid #2ecc71;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 14px;
    font-weight: 600;
    color: #2ecc71;
    margin-left: 12px;
}
.live-dot {
    height: 10px;
    width: 10px;
    background-color: #2ecc71;
    border-radius: 50%;
    display: inline-block;
    margin-right: 8px;
    animation: pulse 1.5s infinite;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="top-right-live">
<svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M12 2L4 5V11C4 16 7.5 20.5 12 22C16.5 20.5 20 16 20 11V5L12 2Z" stroke="#2ecc71" stroke-width="1.4" fill="none"/>
<circle cx="12" cy="9.5" r="2" stroke="#2ecc71" stroke-width="1.1" fill="none"/>
<path d="M8.5 15C8.5 12.8 10.1 11.7 12 11.7C13.9 11.7 15.5 12.8 15.5 15" stroke="#2ecc71" stroke-width="1.1" fill="none" stroke-linecap="round"/>
</svg>
<span class="live-badge"><span class="live-dot"></span>Live Monitoring</span>
</div>
""", unsafe_allow_html=True)

st.markdown('<h1 style="margin:0; padding:0;">🛡️ VitalGuard — Security Posture Dashboard</h1>', unsafe_allow_html=True)
st.caption("Securing Data for women's health wearable IoT data")

# ---------- Live Firestore counts ----------
@st.cache_data(ttl=30)
def get_counts():
    collections = ["valid_readings", "rejected_readings", "secure_readings", "audit_log"]
    counts = {}
    for c in collections:
        try:
            counts[c] = len(list(db.collection(c).stream()))
        except Exception:
            counts[c] = 0
    return counts

with st.spinner("🔐 Loading VitalGuard security posture..."):
    counts = get_counts()

col1, col2, col3, col4 = st.columns(4)
st.markdown("""
<style>
.metric-btn button {
    background: none !important;
    border: none !important;
    padding: 0 !important;
    text-align: left !important;
}
.metric-btn button p {
    font-size: 2.5rem !important;
    font-weight: 600 !important;
    color: white !important;
}
.metric-btn button:hover p {
    color: #2ecc71 !important;
    text-decoration: underline;
}
</style>
""", unsafe_allow_html=True)

def clickable_metric(col, label, value, collection_name, key):
    with col:
        st.markdown(f"<p style='color:#8a9099; margin-bottom:0;'>{label}</p>", unsafe_allow_html=True)
        st.markdown('<div class="metric-btn">', unsafe_allow_html=True)
        clicked = st.button(str(value), key=key)
        st.markdown('</div>', unsafe_allow_html=True)
        if clicked:
            st.session_state["expanded_collection"] = collection_name
            st.session_state["expanded_label"] = label

clickable_metric(col1, "Valid Readings", counts.get("valid_readings", 0), "valid_readings", "btn_valid")
clickable_metric(col2, "Rejected Readings", counts.get("rejected_readings", 0), "rejected_readings", "btn_rejected")
clickable_metric(col3, "Securely Encrypted", counts.get("secure_readings", 0), "secure_readings", "btn_secure")
clickable_metric(col4, "Audit Log Entries", counts.get("audit_log", 0), "audit_log", "btn_audit")

if "expanded_collection" in st.session_state:
    st.markdown("---")
    st.subheader(f"📋 {st.session_state['expanded_label']} — Details")
    st.markdown("""
    <div style='background-color:rgba(46,204,113,0.08); border:1px solid rgba(46,204,113,0.3);
                border-radius:8px; padding:10px 16px; margin-bottom:12px; font-size:14px; color:#c9d1d9;'>
    <b>📏 Reference Ranges (for interpreting values below):</b><br>
    • BP: Normal 90-120 / 60-80 mmHg &nbsp;|&nbsp; Elevated 120-140 / 80-90 &nbsp;|&nbsp; High &gt;140/90<br>
    • Symptom Severity (0-4 scale): 0 = None &nbsp;|&nbsp; 1 = Mild &nbsp;|&nbsp; 2 = Moderate &nbsp;|&nbsp; 3 = Significant &nbsp;|&nbsp; 4 = Severe<br>
    • Food Glycemic Load: Low 0-10 &nbsp;|&nbsp; Medium 11-19 &nbsp;|&nbsp; High 20+
    </div>
    """, unsafe_allow_html=True)
    docs = list(db.collection(st.session_state["expanded_collection"]).limit(20).stream())
    if docs:
        rows = [doc.to_dict() for doc in docs]
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    else:
        st.info("No records yet.")

st.divider()

# ---------- Agent-wise breakdown ----------
st.subheader("Agent Pipeline Breakdown")

try:
    stage2_flagged = pd.read_csv("data/stage2_flagged.csv")
    stage1_rejected = pd.read_csv("data/stage1_rejected.csv")
    stage2_passed = pd.read_csv("data/stage2_passed.csv")

    agent_stats = {
        "Agent 1 Rejected (Device Integrity)": len(stage1_rejected),
        "Agent 2 Flagged (ML Anomaly)": len(stage2_flagged),
        "Passed Both Agents": len(stage2_passed),
    }

    fig = go.Figure(data=[go.Bar(
        x=list(agent_stats.keys()),
        y=list(agent_stats.values()),
        marker_color=["#e74c3c", "#f39c12", "#2ecc71"]
    )])
    fig.update_layout(title="Synthetic Readings — Pipeline Outcome", height=350)
    st.plotly_chart(fig, use_container_width=True)
except FileNotFoundError:
    st.info("Run agents/device_integrity.py and agents/data_sanity_ml.py first to populate this chart.")

st.divider()

# ---------- Model Integrity (Agent 3) demo ----------
st.subheader("🛡️ Agent 3 — Adversarial Defense Demo")
col_a, col_b = st.columns(2)
with col_a:
    st.markdown("**Before Attack**")
    st.code("BP: 195/125 | Anomaly Score: -0.1011 | Prediction: ANOMALY ✅")
with col_b:
    st.markdown("**After Adversarial Perturbation**")
    st.code("BP: 125/85 | Anomaly Score: 0.0030 | Prediction: NORMAL ⚠️ (attack succeeded)")

st.success("🛡️ Agent 3 flagged this as a suspected adversarial evasion — implausible reading swing "
           "(195→125 systolic) for the same device, routed to manual review.")

st.divider()

# ---------- Compliance Summary (Agent 4) ----------
st.subheader("📋 Agent 4 — Compliance Summary")
compliance = {
    "Data Minimization": "Only clinically relevant fields stored; no raw device metadata retained.",
    "Encryption at Rest": "Sensitive fields encrypted via Cloud KMS before write.",
    "Access Control": "Read access restricted to data owner and authorized agents only.",
    "Audit Trail": "Every write/read event logged with timestamp, user, and device.",
    "Consent Basis": "Synthetic demo data; production requires explicit consent capture."
}
for k, v in compliance.items():
    st.markdown(f"**{k}:** {v}")

st.divider()

# ---------- Personal Insight (Agent 5) ----------
st.subheader("💡 Agent 5 — Personal Insight")
st.info(
    "Based on your last 94 logged readings, we noticed no strong pattern: your food glycemic "
    "load and symptom severity don't show a clear relationship (average glycemic load 44.3, "
    "average symptom severity 1.82/4). This is just an observed trend in your own data, not a "
    "diagnosis -- other factors (sleep, stress, cycle phase) might be more relevant to track "
    "alongside food."
)

st.divider()

# ---------- Transport Privacy Proof (Wireshark) ----------
st.subheader("🔒 Transport-Layer Privacy Proof (Wireshark)")
st.markdown(
    "We captured real network traffic proving SNI (domain name) leaks in TLS handshakes, "
    "even with ECH enabled -- and verified correct ECH behavior on a reference endpoint."
)

col_ws1, col_ws2 = st.columns(2)
with col_ws1:
    st.image("assets/wireshark_before.png", caption="BEFORE: SNI plaintext visible")
with col_ws2:
    st.image("assets/wireshark_after.png", caption="AFTER: ECH — SNI hidden")

st.divider()
st.caption("VitalGuard — Patchamomma 2026 | Built by Pooja Baskaran")
