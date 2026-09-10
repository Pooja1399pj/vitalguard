# 🛡️ VitalGuard

**A DevSecOps Pipeline & Adversarial-Resilient Security Layer for Women's Health Wearable IoT Data**

*Built for Patchamomma 2026 — Open Innovation Challenge*

🔗 **Live Dashboard:** [https://shebuilds.cloud]

---

## 📋 Table of Contents

- [Problem Statement](#problem-statement)
- [Solution Overview](#solution-overview)
- [Architecture](#architecture)
- [The 5 Agents](#the-5-agents)
- [Tech Stack](#tech-stack)
- [Key Research Findings](#key-research-findings)
- [Setup & Installation](#setup--installation)
- [Running the Pipeline](#running-the-pipeline)
- [Project Structure](#project-structure)
- [Screenshots](#screenshots)
- [Future Work](#future-work)
- [Author](#author)

---

## Problem Statement

Consumer health wearables (BP monitors, cycle trackers, symptom logs) largely fall outside HIPAA-equivalent regulation, leaving sensitive reproductive/hormonal health data exposed at multiple layers:

- **Network layer:** Plaintext DNS queries and visible TLS SNI fields leak *which* health app a device is talking to — revealing a medical condition (e.g., PCOD tracking) without even breaking encryption.
- **AI/ML layer:** ML models used for health anomaly detection are themselves vulnerable to adversarial evasion and data poisoning attacks — a gap flagged in FDA's 2025 AI-medical-device guidance and the updated Feb 2026 HIPAA Security Rule.
- **Data layer:** A majority of leading wearable manufacturers show transparency issues in data handling practices, and this data sits in a regulatory gray zone.

Existing hackathon/consumer solutions (PCOS/PCOD predictors) focus almost entirely on diagnostic accuracy, already exceeding 95–98% in academic literature.Almost none treat security and data integrity as the core product.

What our VitalGuard does?

---

## Solution Overview

VitalGuard is a 5-agent DevSecOps pipeline that treats health data like production code — every reading passes through security gates before it's trusted, stored, or interpreted.

Rather than competing on diagnostic accuracy, VitalGuard competes on trust it defends the transport layer, the data layer, and uniquely the ML model itself.

---

## Architecture

```
[Wearable Device]
       │  DoH + ECH (encrypted transport)
       ▼
[Cloud Pub/Sub] → ingestion
       │
       ▼
┌─────────────────────────────────────────┐
│   ADK Multi-Agent Pipeline (Cloud Run)   │
│                                           │
│   Agent 1: Device Integrity              │
│         ↓                                │
│   Agent 2: Data Sanity (ML anomaly)      │
│         ↓                                │
│   Agent 3: Model Integrity (adversarial) │
│         ↓                                │
│   Agent 4: Privacy/Compliance (KMS+IAM)  │
│         ↓                                │
│   Agent 5: Personal Insight              │
└─────────────────────────────────────────┘
       │
       ▼
[Cloud KMS | Firestore | BigQuery] → storage
       │
       ▼
[Streamlit Dashboard on Cloud Run] → live stats, proofs, insights
```

---

## The 5 Agents

Agent 1 Device Integrity - Validates device signature/auth token; rejects spoofed or cloned devices.
Agent 2. Data Sanity (ML) - Isolation Forest–based personalized anomaly detection on BP, symptom, and food-glycemic-load data.
Agent 3. Model Integrity  - Defends the ML model itself against adversarial evasion attacks — detects implausible reading swings and anomaly-score manipulation designed to fool Agent 2 
Agent 4. Privacy/Compliance - Cloud KMS field-level encryption, IAM-based least-privilege access control, audit logging, auto-generated HIPAA-equivalent compliance reports.
Agent 5. Personal Insight -  Statistical correlation + plain-language trend explanation (e.g., food–symptom patterns) — never a diagnosis.

### Agent 3 in detail — why it matters

Most anomaly-detection pipelines stop at Agent 2. We went further: we **attacked our own model**. We crafted an adversarial perturbation that took a genuinely dangerous reading (BP 195/125) and nudged it just enough to flip the Isolation Forest's classification from `ANOMALY` to `NORMAL` — a real evasion attack succeeding on an undefended pipeline. Agent 3 then catches this exact attack using rate-of-change monitoring: a BP swing of 70+ points between consecutive readings from the same device is physiologically implausible and gets flagged for manual review, regardless of what the ML model says.

---

## Tech Stack

**Google Cloud:** Pub/Sub · Cloud Run · Cloud KMS · Firestore · BigQuery · IAM · Cloud Build · Artifact Registry

**ML/Security:** scikit-learn (Isolation Forest) · Adversarial Robustness Toolbox (ART) concepts

**Dashboard:** Streamlit · Plotly

**Transport Security Research:** DoH (DNS over HTTPS) · ECH (Encrypted Client Hello) · Wireshark · Cloudflare

**Infra:** Docker · Cloudflare (custom domain + ECH) · GitHub

---

## Key Research Findings

VitalGuard isn't just built on security *theory* — every claim in this project was **empirically tested and captured on video/screenshot** using Wireshark, across multiple real environments (Google Cloud, Cloudflare, a dedicated ECH test service, and our own deployed domain).

### 1. Our own backend leaks metadata
We captured our own backend url domain traffic which is given in touch point 2 is exposed in wiresharkfound the SNI field exposing `https://vitalguard-dashboard-321428319627.asia-south1.run.app/` in plaintext — meaning a network observer could infer "this device talks to a Google Cloud health backend" without ever decrypting the payload.

### 2. ECH deployment is inconsistent in the real world
We tested ECH (Encrypted Client Hello) against Google services, Cloudflare's own domains, and a dedicated ECH test endpoint. Despite the ECH extension being present in the handshake, several of these failed to properly mask the real SNI — the "cover name" mechanism that ECH is supposed to provide was frequently just the real hostname, not a generic decoy.

### 3. **DoH is a hard prerequisite for ECH — not an independent feature**
This is our most original finding. We discovered that **ECH will not function correctly unless Secure DNS (DoH) is explicitly enabled in-browser.** With Chrome's DNS setting left at "OS default," SNI leaked in plaintext even on ECH-capable domains. Switching Secure DNS to a provider like Cloudflare immediately enabled correct ECH behavior — outer SNI became a generic cover name (`cloudflare-ech.com`) with the real destination encrypted inside.

**This validates the core premise of our project:** transport-layer privacy for health data cannot rely on a single control. DNS encryption and TLS/SNI encryption are coupled — and most consumer devices, left at default settings, get neither.

### 4. We proved this on our own live deployment
We purchased a custom domain, deployed VitalGuard's dashboard behind Cloudflare with ECH enabled, and captured before/after Wireshark proof on our *own* production traffic — not just third-party test sites.

---

## Setup & Installation

### Prerequisites
- Python 3.12+
- Google Cloud SDK (`gcloud`)
- A GCP project with billing enabled
- Docker (for Cloud Run deployment)

### 1. Clone and set up environment
```bash
git clone <this-repo-url>
cd vitalguard
python3 -m venv env
source env/bin/activate       # Windows: env\Scripts\activate
pip install -r requirements.txt
```

### 2. GCP setup
```bash
gcloud config set project YOUR_PROJECT_ID

gcloud services enable pubsub.googleapis.com \
  firestore.googleapis.com \
  cloudkms.googleapis.com \
  run.googleapis.com \
  logging.googleapis.com

gcloud firestore databases create --location=YOUR_REGION --type=firestore-native

gcloud kms keyrings create vitalguard-keyring --location=YOUR_REGION
gcloud kms keys create vitalguard-key \
  --location=YOUR_REGION \
  --keyring=vitalguard-keyring \
  --purpose=encryption
```

### 3. Environment variables
Create a `.env` file:
```
GCP_PROJECT_ID=your-project-id
GEMINI_API_KEY=your-gemini-key   # optional, Agent 5 has a rule-based fallback
```

### 4. Pub/Sub setup
```bash
gcloud pubsub topics create vitals-ingest
gcloud pubsub subscriptions create vitals-ingest-sub --topic=vitals-ingest
```

---

## Running the Pipeline

### Generate synthetic data
```bash
python data/synthetic_generator.py
```

### Run each agent (sequential regression test)
```bash
python agents/device_integrity.py        # Agent 1
python agents/data_sanity_ml.py          # Agent 2
python agents/model_integrity_art.py     # Agent 3 — adversarial attack + defense demo
python agents/privacy_compliance.py      # Agent 4 — KMS encryption + audit
python agents/personal_insight_gemini.py # Agent 5 — insight generation
```

### Run the live end-to-end pipeline
Terminal A:
```bash
python data/subscriber.py
```
Terminal B:
```bash
python data/publisher.py
```

### Launch the dashboard locally
```bash
streamlit run dashboard.py
```

### Deploy to Cloud Run
```bash
gcloud run deploy vitalguard-dashboard \
  --source . \
  --region YOUR_REGION \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=YOUR_PROJECT_ID
```

---

## Project Structure

```
vitalguard/
├── agents/
│   ├── device_integrity.py         # Agent 1
│   ├── data_sanity_ml.py           # Agent 2
│   ├── model_integrity_art.py      # Agent 3
│   ├── privacy_compliance.py       # Agent 4
│   └── personal_insight_gemini.py  # Agent 5
├── data/
│   ├── synthetic_generator.py      # Synthetic dataset generator
│   ├── publisher.py                # Pub/Sub publisher (simulated device)
│   └── subscriber.py               # Pub/Sub subscriber → pipeline runner
├── assets/
│   ├── wireshark_before.png        # SNI leak proof
│   └── wireshark_after.png         # ECH success proof
├── dashboard.py                    # Streamlit dashboard
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Screenshots

Live security proofs and dashboard views are embedded directly in the deployed dashboard at [shebuilds.cloud](https://shebuilds.cloud), including:
- Real-time pipeline statistics pulled from Firestore
- Agent 1/2 rejection and anomaly breakdown chart
- Agent 3 adversarial attack-vs-defense demonstration
- Agent 4 compliance summary
- Agent 5 personal insight output
- Wireshark before/after transport-privacy proof

---

## Future Work

- Live Gemini API integration for Agent 5 (currently a tested rule-based fallback with an identical input/output contract).
- Full production integration path with Samsung Health / Google Health Connect / MyFitnessPal-style APIs (our synthetic schema is designed to mirror this exactly).
- DNSSEC exploration as a complementary control alongside DoH + ECH.
- Expanded adversarial testing using the IBM Adversarial Robustness Toolbox's full attack suite.

---

## Author

**Pooja Baskaran** — Solo builder, Patchamomma 2026

Built end-to-end: infrastructure, all 5 agents, dashboard, deployment, and original transport-security research.