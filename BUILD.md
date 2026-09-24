# Engineering Build Guide & Presenter Runbook
## GAIL (India) Limited · Enterprise Data Lifecycle & Sovereign Advisory Agent
### Document ID: `BUILD-GAIL-DATA-LIFECYCLE-V2.1`
**Status:** Approved Sovereign Build | **Target Runtime:** Google Gemini Enterprise / Vertex AI Agent Runtime  
**Governing Entity:** GAIL (India) Limited (National Gas Management Centre & Project Navodaya)

---

## 1. Overview & Project Structure

This document outlines the engineering build, test harness verification, and live demonstration runbook for the **GAIL Enterprise Data Lifecycle Agent**, demonstrating:
1. **Universal Enterprise Data Access:** Querying GAIL's Enterprise Data Lake (`gs://gail-midstream-ge-demo-datalake`), Commercial Gas Management System (GMS), and SAP S/4HANA (Project Navodaya).
2. **Operational Time-Series Observability:** Visualizing 72-hour operational logs from the Enterprise Cloud Historian (Line-Pack Pressure `kg/cm²` and Throughput `MMSCMD`) in an interactive dual-layer chart.
3. **Deterministic Econometric Modeling:** Executing multivariate Box-Jenkins SARIMAX $(1,1,1)\times(1,1,1)_{24}$ forecasting driven by $S=24$ diurnal cycles and exogenous customer nominations ($X_1$), computing optimal compressor setpoints saving 18,500 SCM/day under Project Sanchay (₹600 Cr NPV).
4. **Exhaustive Executive Report Synthesis:** Compiling a publication-grade 6-part HTML Ready Reckoner with the official GAIL crest and audited tables in seconds.

```
agents/gail_pipeline_agent/
├── SDD.md                           # System Design Document (Architecture & Math)
├── BUILD.md                         # This build & execution runbook
├── CHECKLIST.md                     # Phase-Gate Verification Checklist
├── README.md                        # Complete demonstration playbook
├── blueprint.md                     # 4-Step Demonstration Master Blueprint
├── pyproject.toml                   # Python dependencies & build config
├── Dockerfile                       # Container definition for Agent Runtime
├── agents-cli-manifest.yaml         # Enterprise agent registry manifest
├── app/
│   ├── contracts.py                 # Pydantic schemas across data lifecycle
│   ├── agent.py                     # Google ADK agent orchestrator & prompt router
│   ├── fast_api_app.py              # A2A JSON-RPC & REST endpoints
│   ├── analytics/
│   │   └── sarimax_linepack.py      # Multivariate SARIMAX forecasting engine
│   ├── render/
│   │   └── a2ui_emit.py             # A2UI v0.9 Vega-Lite visualization cards
│   ├── synthesis/
│   │   └── executive_report_compiler.py # 6-Part GAIL Ready Reckoner compiler
│   └── integration/
│       ├── tools.py                 # Callable ADK agent tools
│       └── gcs_connector.py         # GCS Medallion Data Lake connector
├── fixtures/
│   ├── gail_hvj_scada_telemetry_72h.csv # Verified 72-hour operational time-series dataset
│   ├── customer_nominations_24h.json    # Commercial customer nomination schedules
│   ├── gail_logo.svg / .png             # Official GAIL corporate crest
│   └── sap_order_template.json          # S/4HANA Work Order schema
└── tests/
    ├── test_contracts.py            # Pydantic schema validation
    ├── test_sarimax_analytics.py    # Time-series model convergence & setpoint tests
    └── test_tools_agent.py          # End-to-end prompt execution tests
```

---

## 2. Verbatim 4-Step Live Presenter Runbook

### Step 1: Universal Enterprise Data Access
- **Presenter Prompt:**
  > *"Access the GAIL Enterprise Data Lake and show regional pipeline transmission volumes and sectoral customer off-take nominations."*
- **Agent Output:**
  - **A2UI Visual:** Interactive VegaChart Bar Card comparing active transmission vs. capacity across 5 corridors (`122.18 MMSCMD` across `18,700 km`: HVJ `81.4 MMSCMD`, Urja Ganga `12.0 MMSCMD`, DBNPL `10.7 MMSCMD`, MNJPL `9.9 MMSCMD`, Regional `8.18 MMSCMD`).
  - **Reconciliation Table:** Audited commercial off-take allocations across Fertilizer anchors (`38.4 MMSCMD` with +20% scheduled ramp), City Gas Distribution (`28.2 MMSCMD`), Power (`24.8 MMSCMD`), and Pata Petrochemicals (`30.78 MMSCMD`).
- **Presenter Key Takeaway:**
  > *"Notice how Gemini Enterprise instantly bridges commercial GMS nomination schedules, regional logbooks, and cloud data lake records without requiring any manual spreadsheet consolidation or CSV export."*

---

### Step 2: Show Data & Interactive 72-Hour Operational Time Series
- **Presenter Prompt:**
  > *"Show the 72-hour operational time series for Chhainsa station from the Enterprise Cloud Historian and plot line-pack pressure and gas throughput."*
- **Agent Output:**
  - **A2UI Visual:** Dual-Layer 72-Hour VegaChart plotting hourly Line-Pack Pressure (`kg/cm²` in blue) against Gas Transmission Throughput (`MMSCMD` in saffron dashed line).
  - **Operational KPIs:** Line-pack pressure (`81.47 kg/cm²`), throughput (`48.05 MMSCMD`), and compressor thermal efficiency index (`549.4 °C`).
- **Presenter Key Takeaway:**
  > *"Shift engineers typically lose 45 minutes every shift pulling CSVs and wrestling with charting tools. GE pulls verified operational history directly from the Enterprise Cloud Historian and plots a multi-variable series in seconds—with zero OT air-gap friction."*

---

### Step 3: Deterministic SARIMAX Forecasting & Optimal Compressor Setpoint
- **Presenter Prompt:**
  > *"Run the deterministic 24-hour SARIMAX forecast for Chhainsa considering scheduled fertilizer and CGD customer nominations, and calculate the Project Sanchay setpoint."*
- **Agent Output:**
  - **A2UI Visual:** 24-Hour Predictive Line-Pack Forecast Band with 95% confidence intervals, contract floor line (`76.0 kg/cm²`), and T+14h deficit warning (`73.8 kg/cm²`).
  - **The Math Explainer:** Explains why SARIMAX predicts the drop on a flat trend: **24-Hour Diurnal Seasonality ($S=24$)** combined with **Exogenous Leading Customer Off-Take Regressors ($X_1$: +20% Fertilizer HURL/NFL surge)**.
  - **Hydraulic Optimization:** Recommends increasing Vijaipur Hub compressor throughput by **+3.8% at 14:00 IST**, saving **18,500 SCM/day (₹16.88 Crore/year)** under **Project Sanchay (₹600 Crore NPV mandate)**.
- **Presenter Key Takeaway:**
  > *"This is physics-informed, deterministic enterprise AI. It calculates the wave delay across our 18,700 km grid and alerts operators 14 hours before pressure drops below contract threshold, saving ₹16.88 Crore annually in fuel gas."*

---

### Step 4: Multi-Source Automated Executive Ready Reckoner Report
- **Presenter Prompt:**
  > *"Compile the exhaustive 6-Part GAIL Daily Gas Transmission, SARIMAX & Project Sanchay Executive Report."*
- **Agent Output:**
  - **A2UI Visual:** Interactive Report Surface linking to the 6-Part HTML Ready Reckoner (`GAIL_Executive_Briefing_2026-09-23.html`) with official GAIL branding, corridor loading tables, sectoral nomination reconciliation, 72h time-series plots, SARIMAX forecast intervals, and Project Sanchay ROI economics.
- **Presenter Key Takeaway:**
  > *"What normally takes shift engineers and commercial managers 3 to 4 hours of document formatting and manual spreadsheet reconciliation is compiled autonomously in 6 seconds into a publication-ready management ready reckoner."*

---

### Optional Follow-Up Integrations
1. **RISE with SAP S/4HANA Cloud (Project Navodaya):**
   - *Prompt:* `"Stage this advisory into RISE with SAP S/4HANA Cloud under Project Navodaya."`
   - *Output:* Work Order `#480291` staged for Vijaipur GT-01 calibration with SHA-256 audit hash.
2. **Enterprise Q&A (GAIL AI Tarang):**
   - *Prompt:* `"Under GAIL AI Tarang, what was our total transmission volume last fiscal year and our Net Zero target?"`
   - *Output:* Cites verified corporate records: **122.18 MMSCMD** average transmission volume and **Net Zero Scope 1 & 2 emissions by 2035**.

---

## 3. Test Suite & Local Verification

```bash
# Run full unit & integration test suite
PYTHONPATH=. pytest tests/ -v

# Run local FastAPI & A2A development server
uvicorn app.fast_api_app:app --host 0.0.0.0 --port 8080 --reload
```
