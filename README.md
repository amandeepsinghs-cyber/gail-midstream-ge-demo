# GAIL (India) Limited · Enterprise Data Lifecycle & Sovereign Advisory Agent
## "Access Data · Show Time-Series · Run Deterministic SARIMAX · Compile Exhaustive Report"

An enterprise-grade autonomous operational and executive advisory agent designed for **GAIL (India) Limited**, powered by **Google Gemini Enterprise** and the **Agent Development Kit (ADK)**.

---

## 1. Executive Summary: What We Demonstrate

This demonstration showcases Gemini Enterprise executing the complete **Enterprise Data Lifecycle**:
1. **Access Any Enterprise Data from Anywhere:** Dynamically query across structured and unstructured repositories—**GAIL Enterprise Data Lake (`gs://gail-midstream-ge-demo-datalake`)**, **Commercial Gas Management System (GMS)**, and **RISE with SAP S/4HANA Cloud (Project Navodaya)**.
2. **Show & Visualize Multi-Variable Operational Time Series:** Ingest 72-hour operational logs from the **Enterprise Cloud Historian** (Line-Pack Pressure `kg/cm²`, Throughput `MMSCMD`, and Station Thermal Efficiency `°C`) and render interactive dual-layer time-series charts in seconds without manual CSV handling.
3. **Run Deterministic Mathematical & Statistical Models:** Execute multivariate **Box-Jenkins SARIMAX $(1,1,1)\times(1,1,1)_{24}$** forecasting driven by **24-Hour Diurnal Seasonality ($S=24$)** and **Exogenous Customer Off-Take Nominations ($X_1$)** to predict line-pack deficits 14 hours ahead and compute optimal compressor setpoints saving **18,500 SCM/day (₹16.88 Crore/yr)** under **Project Sanchay (₹600 Crore NPV target)**.
4. **Compile Exhaustive Executive Ready Reckoners:** Synthesize all audited datasets, historical time series, forecasting tables, and financial economics into a publication-ready **6-Part GAIL Executive HTML Report** with the official GAIL crest and audited tables in seconds.

> **Architecture Note on OT / SCADA & Weather:**
> To eliminate air-gap controversies during executive presentations, all operational telemetry is sourced cleanly from GAIL's **Enterprise Cloud Historian & GMS Data Lake** rather than claiming direct live penetration into air-gapped Level 1/Level 2 OT networks. Environmental weather models are parked as an optional add-on feature and kept out of the core data narrative.

---

## 2. Canonical 4-Step On-Stage Demonstration Flow

```
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                        GEMINI ENTERPRISE DATA LIFECYCLE DEMONSTRATION                             │
├──────────────────────────┬──────────────────────────┬─────────────────────────┬───────────────────┤
│ STEP 1: ACCESS DATA      │ STEP 2: SHOW TIME-SERIES │ STEP 3: RUN SARIMAX     │ STEP 4: REPORT    │
│ Enterprise Data Lake     │ Enterprise Cloud         │ Box-Jenkins (S=24 + X₁) │ Exhaustive 6-Part │
│ GMS Corridor Volumes     │ Historian 72h Series     │ T+14h Deficit (73.8 kg) │ Ready Reckoner    │
│ 18,700 km Grid Inventory │ Dual-Layer VegaChart     │ +3.8% Vijaipur Setpoint │ Official GAIL     │
│ Sectoral Nominations     │ Linepack & Throughput    │ Saves ₹16.88 Cr/yr      │ HTML / Cloud URI  │
└──────────────────────────┴──────────────────────────┴─────────────────────────┴───────────────────┘
```

---

### Step 1: Universal Enterprise Data Access
* **Presenter Prompt:**
  > *"Access the GAIL Enterprise Data Lake and show regional pipeline transmission volumes and sectoral customer off-take nominations."*
* **Live Agent Output:**
  * **Visual Surface:** Interactive **VegaChart Bar Card** comparing active throughput vs. design capacity across GAIL's 5 principal corridors (`122.18 MMSCMD` total transmission across `18,700 km` network: HVJ `81.4 MMSCMD`, Urja Ganga `12.0 MMSCMD`, DBNPL `10.7 MMSCMD`, MNJPL `9.9 MMSCMD`, Regional `8.18 MMSCMD`).
  * **Audited Nominations:** Displays commercial off-take allocations across Fertilizer anchors (`38.4 MMSCMD` with +20% scheduled ramp), City Gas Distribution (`28.2 MMSCMD`), Power (`24.8 MMSCMD`), and Pata Petrochemicals (`30.78 MMSCMD`).
* **The "SO WHAT?" Business Value:**
  * **Unified Data Access:** Replaces manual spreadsheet consolidation across commercial GMS, regional logbooks, and ERP with a single, governed conversational interface.

---

### Step 2: Show Data & Interactive 72-Hour Operational Time-Series Plot
* **Presenter Prompt:**
  > *"Show the 72-hour operational time series for Chhainsa station from the Enterprise Cloud Historian and plot line-pack pressure and gas throughput."*
* **Live Agent Output:**
  * **Visual Surface:** Interactive **Dual-Layer 72-Hour VegaChart** plotting hourly Line-Pack Pressure (`kg/cm²` in blue) against Gas Transmission Throughput (`MMSCMD` in saffron dashed line).
  * **KPI Summary:** Current line-pack pressure (`81.47 kg/cm²`), average corridor flow (`48.05 MMSCMD`), compressor thermal efficiency (`549.4 °C`), and baseline fuel burn rate (`1.41%`).
* **The "SO WHAT?" Business Value:**
  * **Zero Data Prep Latency:** Saves **45 minutes per shift** typically spent exporting CSVs and formatting Excel charts. Data is pulled directly from the Enterprise Cloud Historian with zero OT air-gap friction.

---

### Step 3: Run Deterministic Multivariate SARIMAX $(1,1,1)\times(1,1,1)_{24}$ Model
* **Presenter Prompt:**
  > *"Run the deterministic 24-hour SARIMAX forecast for Chhainsa considering scheduled fertilizer and CGD customer nominations, and calculate the Project Sanchay setpoint."*
* **Live Agent Output:**
  * **Visual Surface:** Interactive **24-Hour Forecast Band VegaChart** with 95% confidence intervals, contract floor line (`76.0 kg/cm²`), and T+14h deficit callout (`73.8 kg/cm²`).
  * **Mathematical Early-Warning Mechanism Explained:**
    * A basic univariate model (ARIMA) only extrapolates past pressure ($Y_t$) and fails to predict drops when current trends look flat.
    * GAIL's multivariate SARIMAX combines **24-Hour Diurnal Seasonality ($S=24$)** with **Exogenous Leading Customer Off-Take Regressors ($X_1$)**—specifically scheduled +20% Fertilizer (HURL/NFL) and +12% CGD morning off-take surges.
    * Because hydraulic wave propagation across the 18,700 km grid takes hours, the model calculates the pressure deficit **14 hours before** the physical drop manifests in the pipe.
  * **Hydraulic Recommendation & Financial ROI:**
    * **Action:** Adjust Vijaipur Hub compressor discharge by **+3.8% at 14:00 IST**.
    * **Financial Impact:** Saves **18,500 SCM/day** of internal fuel gas (**₹16.88 Crore/year**), directly driving GAIL's **Project Sanchay ₹600 Crore NPV mandate**.
* **The "SO WHAT?" Business Value:**
  * **Proactive vs. Reactive Balancing:** Eliminates downstream supply penalties and prevents firing costly auxiliary standby turbines.

---

### Step 4: Compile Exhaustive 6-Part GAIL Executive Ready Reckoner Report
* **Presenter Prompt:**
  > *"Compile the exhaustive 6-Part GAIL Daily Gas Transmission, SARIMAX & Project Sanchay Executive Report."*
* **Live Agent Output:**
  * **Visual Surface:** Interactive A2UI Report Surface with summary KPIs and direct link to the publication-ready HTML Ready Reckoner (`output_artifacts/GAIL_Executive_Briefing_2026-09-23.html` / `gs://gail-midstream-ge-demo-datalake/curated/executive_reports/...`).
  * **Exhaustive Report Structure:**
    * **Part A:** National Transmission Grid Corridor Loading (`18,700 km`, `122.18 MMSCMD`, 5 Corridors).
    * **Part B:** Sectoral Demand & Customer Off-Take Reconciliation ($X_1$ Schedule for Fertilizer, CGD, Power, Petchem).
    * **Part C:** Enterprise Cloud Historian 72-Hour Operational Time-Series Tables.
    * **Part D:** Multivariate SARIMAX Forecast Band Table (24-Hour lookahead with 95% Confidence Intervals).
    * **Part E:** Project Sanchay Fuel-Gas Economics & ₹600 Crore NPV Portfolio Tracker.
    * **Part F:** Closed-Loop RISE with SAP S/4HANA Cloud (Project Navodaya) Governance Ledger.
* **The "SO WHAT?" Business Value:**
  * **Administrative Latency Zeroed:** Replaces 3 to 4 hours of tedious manual shift paperwork per station with an instant, publication-grade executive deliverable.

---

## 3. Optional Follow-Up Integrations

1. **Closed-Loop SAP S/4HANA Action (Project Navodaya):**
   * *Prompt:* `"Stage this advisory into RISE with SAP S/4HANA Cloud under Project Navodaya."`
   * *Output:* Stages preventive maintenance work order `#480291` for Vijaipur GT-01 calibration with SHA-256 audit hash.
2. **Enterprise Natural Language Q&A (GAIL AI Tarang):**
   * *Prompt:* `"Under GAIL AI Tarang, what was our total transmission volume last fiscal year and our Net Zero target?"`
   * *Output:* Cites verified corporate records: **122.18 MMSCMD** average transmission volume and **Net Zero Scope 1 & 2 emissions by 2035**.

---

## 4. Deployment & Infrastructure Reference

* **GCP Project:** `og-agentic-ecosystem` (`349946979746`, region `asia-south1`)
* **Dedicated Service Account:** `gail-grid-agent@og-agentic-ecosystem.iam.gserviceaccount.com`
* **Reasoning Engine ID:** `projects/349946979746/locations/asia-south1/reasoningEngines/6842313636208181248`
* **Agent Card URL:** `https://asia-south1-aiplatform.googleapis.com/reasoningEngines/v1/projects/349946979746/locations/asia-south1/reasoningEngines/6842313636208181248/api/a2a/app/.well-known/agent-card.json`
* **Gemini Enterprise Registered Agent:** `projects/349946979746/locations/global/collections/default_collection/engines/oil-and-gas-agentic-transf_1788683272432/assistants/default_assistant/agents/13029231145782247335`
* **Data Lake Bucket:** `gs://gail-midstream-ge-demo-datalake`
