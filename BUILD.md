# Engineering Build Guide & Presenter Runbook
## GAIL Autonomous Pipeline Grid, Predictive Analytics & Executive Advisory Agent
### Document ID: `BUILD-GAIL-GRID-ADVISOR-V1.0`

---

## 1. Overview & Project Structure

This document outlines the step-by-step engineering build, test harness execution, and live demonstration runbook for the **GAIL Pipeline Grid & Executive Advisory Agent**.

```
agents/gail_pipeline_agent/
├── SDD.md                           # System Design Document
├── BUILD.md                         # This build & execution runbook
├── CHECKLIST.md                     # Formal Phase-Gate Verification Scorecard
├── blueprint.md                     # 5-Act Demonstration Blueprint
├── some_relevant comments.md        # Technical explanation of SARIMAX Physics
├── pyproject.toml                   # Python dependencies & build config
├── Dockerfile                       # Container definition for Cloud Run
├── agents-cli-manifest.yaml         # Enterprise agent registry manifest
├── README.md                        # Documentation
├── app/
│   ├── contracts.py                 # Pydantic schemas across all 5 acts
│   ├── agent.py                     # Google ADK agent orchestrator
│   ├── fast_api_app.py              # A2A JSON-RPC & REST endpoints
│   ├── analytics/
│   │   └── sarimax_linepack.py      # SARIMAX(1,1,0)(1,0,0)24 forecasting engine
│   ├── render/
│   │   └── a2ui_cards.py            # A2UI v0.9 Vega-Lite visualization cards
│   ├── synthesis/
│   │   └── executive_report_compiler.py # Multi-source HTML/PDF compiler
│   └── integration/
│       └── tools.py                 # 6 callable ADK agent tools
├── fixtures/
│   ├── gail_hvj_scada_telemetry_72h.csv # Verified 72-hour SCADA & turbine dataset
│   ├── river_crossings_gis.geojson      # HVJ corridor & Yamuna flood alert layer
│   ├── customer_nominations_24h.json    # 24h leading exogenous demand & temp feeds
│   ├── sap_order_template.json          # S/4HANA Work Order schema
│   └── generate_fixtures.py             # Deterministic fixture generator
└── tests/
    ├── test_contracts.py            # Pydantic schema validation
    ├── test_sarimax_analytics.py    # Time-series model convergence & setpoint tests
    └── test_tools_agent.py          # End-to-end multi-act prompt execution tests
```

---

## 2. Environment Setup & Dependency Installation

The package requires Python 3.11+ and standard scientific/web libraries:

```bash
# 1. Navigate to the agent workspace
cd "Oil & Gas Agent Portfolio/agents/gail_pipeline_agent"

# 2. Activate or link virtual environment
source ../ppac_reporting_engine/ppac_reporting_engine/.venv/bin/activate

# 3. Verify core libraries
python -c "import pandas, statsmodels, pydantic, fastapi, jinja2; print('All core libraries verified!')"
```

---

## 3. Step-by-Step Build Validation

### Step 1: Verify & Regenerate Fixtures
```bash
python fixtures/generate_fixtures.py
```
*Expected Output:*
* `fixtures/river_crossings_gis.geojson` (4 spatial features, Yamuna crossing flood alert)
* `fixtures/customer_nominations_24h.json` (24 hourly leading exogenous data points)
* `fixtures/sap_order_template.json` (Project Navodaya SAP schema)

### Step 2: Run Full Automated Test Suite
```bash
PYTHONPATH=. pytest tests/ -v
```
*Expected Output:*
* 13 tests passed across contracts, analytics, and tools in under 3 seconds.

---

## 4. Live Demonstration Stage Runbook (The 5 Acts)

Use this runbook when presenting live to GAIL executives or at industry briefings:

### Starting the Live Server
```bash
uvicorn app.fast_api_app:app --host 0.0.0.0 --port 8080 --reload
```

---

### ACT 1: Spatial GIS Infrastructure & IMD Weather
* **Presenter Action:** Submit Act 1 prompt via API or UI:
  ```bash
  curl -X POST http://localhost:8080/api/v1/prompt \
    -H "Content-Type: application/json" \
    -d '{"prompt": "Gemini, initialize a grid health and risk audit across the HVJ and MNJPL pipeline corridors for the next 24 hours."}'
  ```
* **What Renders:**
  * Spatial map of ~18,700 km grid.
  * Active IMD hazard alert: **Gauna-Bawana Yamuna River Crossing** at 206.4m gauge (Danger Mark: 205.33m).
* **Presenter Script:**
  > *"Notice how Gemini doesn't just show a static drawing. It actively fuses IMD meteorological radar data directly with our physical right-of-use asset map. Following incidents like the Gauna-Bawana river flood leakage, GE automatically flags river crossings under hydraulic stress before physical damage occurs."*

---

### ACT 2: SCADA Telemetry & Turbine Diagnostic Status
* **Presenter Action:** Submit Act 2 prompt:
  ```bash
  curl -X POST http://localhost:8080/api/v1/prompt \
    -H "Content-Type: application/json" \
    -d '{"prompt": "Access live telemetry for Chhainsa Compressor Station and plot 72-hour historical trends for line-pack pressure, gas flow rate, and Siemens turbine exhaust temperatures."}'
  ```
* **What Renders:**
  * Multi-variable time-series chart from Yokogawa SCADA and Siemens RDS.
  * Latest Chhainsa linepack: **81.47 kg/cm²**, throughput: **48.05 MMSCMD**, turbine exhaust: **549.4 °C**.
* **Presenter Script:**
  > *"Control room engineers typically spend 45 minutes exporting raw SCADA logs and cleaning CSVs. Gemini Enterprise ingests multi-system telemetry—Yokogawa SCADA and Siemens RDS turbine feeds—and renders an interactive, multi-variable plot in seconds."*

---

### ACT 3: Deterministic SARIMAX Forecasting & Optimal Setpoint
* **Presenter Action:** Submit Act 3 prompt:
  ```bash
  curl -X POST http://localhost:8080/api/v1/prompt \
    -H "Content-Type: application/json" \
    -d '{"prompt": "Execute a 24-hour predictive SARIMAX demand forecast for Chhainsa station considering downstream fertilizer plant off-takes, and calculate optimal compressor setpoints at Vijaipur."}'
  ```
* **What Renders:**
  * 24-hour predictive line-pack curve with 95% confidence bands.
  * Pressure deficit flagged at **Hour 14 ahead**.
  * Setpoint Recommendation: **Increase Vijaipur throughput by +3.8% at 14:00 hrs**, saving **18,500 SCM/day** of fuel gas (**₹4.62 Lakhs/day** / **₹16.88 Cr/year**).
* **Presenter Script:**
  > *"This is where Gemini Enterprise transforms into an Agentic Decision Partner. It ingests leading customer nominations (HURL/NFL off-take surges) and ambient heatwave forecasts into a SARIMAX model, predicting the line-pack deficit 14 hours ahead—matching the physical gas transit delay from Vijaipur. Adjusting Vijaipur throughput by +3.8% directly accelerates GAIL's Project Sanchay."*

---

### ACT 4: Automated Executive Briefing (The Point-Scoring Deliverable)
* **Presenter Action:** Submit Act 4 prompt:
  ```bash
  curl -X POST http://localhost:8080/api/v1/prompt \
    -H "Content-Type: application/json" \
    -d '{"prompt": "Compile this grid audit, weather assessment, SARIMAX forecast, and fuel-saving calculations into an official Daily Line-Pack & Integrity Executive Briefing."}'
  ```
* **Presenter Action (Browser):** Open `http://localhost:8080/api/v1/report/latest`
* **What Renders:**
  * Official styled Executive Briefing with GAIL branding, grid KPIs, alert cards, turbine health table, and Project Sanchay ROI table.
* **Presenter Script:**
  > *"Look at this report. What normally takes shift engineers and plant managers 3 to 4 hours of tedious document preparation is compiled autonomously in 6 seconds. It is publication-ready and fully audited across 4 distinct enterprise data sources."*

---

### ACT 5: Closed-Loop SAP S/4HANA Action & GAIL AI Tarang Q&A
* **Presenter Action (Part 1: SAP):**
  ```bash
  curl -X POST http://localhost:8080/api/v1/prompt \
    -H "Content-Type: application/json" \
    -d '{"prompt": "Log this optimization advisory and stage a preventive work order directly into RISE with SAP S/4HANA Cloud."}'
  ```
  * Output: Confirmation of Work Order `#WO-48xxxx` created under Project Navodaya at Plant 1102.
* **Presenter Action (Part 2: Audience Q&A):** Invite an attendee from HR or Finance:
  ```bash
  curl -X POST http://localhost:8080/api/v1/prompt \
    -H "Content-Type: application/json" \
    -d '{"prompt": "What was our total natural gas transmission volume last fiscal year, and what is our Net Zero Scope-1 target timeline?"}'
  ```
  * Output: **122.18 MMSCMD** and **100% Net Zero by 2035**, cited from GAIL's official BRSR report.

---

## 5. Containerization & Deployment

To deploy to Cloud Run or Vertex AI Reasoning Engine:

```bash
# Build Docker image
docker build -t asia-south1-docker.pkg.dev/og-agentic-ecosystem/agents/gail-grid-advisor:v1 .

# Run locally
docker run -p 8080:8080 asia-south1-docker.pkg.dev/og-agentic-ecosystem/agents/gail-grid-advisor:v1
```
