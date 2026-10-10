+# HOSN dashboard demo

Streamlit dashboard for the HOSN rules-first Wi-Fi / emulated-5G handover system.

## What is included

- The accepted measured-data model: `results/measured_dataset_campaign_20261003T145634_501377Z/hosn_conflict_ai_model.joblib`
- Its acceptance report and SHA-256 integrity check
- Three real Mininet-WiFi/emulated-5G recording summaries
- The normalized HOSN controller contract and exact eight-feature order
- A cloud-safe dashboard entrypoint: `hosn_public_demo.py`

The dashboard loads the model with joblib and uses the embedded StandardScaler + Logistic Regression pipeline. It calls the model only when the rules return a complete `CONFLICT`. Clear `STAY` and `HANDOVER` cases bypass AI.

The VM is required to collect new Mininet-WiFi experiments and execute handovers. It is not required to run this dashboard or replay the recorded decisions.

Run locally:

```bash
pip install -r requirements.txt
streamlit run hosn_public_demo.py
```

