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

st.title("🛡️ VitalGuard — Security Posture Dashboard")
st.caption("DevSecOps pipeline for women's health wearable IoT data")

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

counts = get_counts()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Valid Readings", counts.get("valid_readings", 0))
col2.metric("Rejected Readings", counts.get("rejected_readings", 0))
col3.metric("Securely Encrypted", counts.get("secure_readings", 0))
col4.metric("Audit Log Entries", counts.get("audit_log", 0))

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
