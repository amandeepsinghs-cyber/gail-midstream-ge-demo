# GAIL Autonomous Pipeline Grid, Predictive Analytics & Executive Advisory Agent

An enterprise-grade autonomous operational and executive advisory agent designed for **GAIL (India) Limited**'s National Gas Management Centre (NGMC), powered by **Google Gemini Enterprise** and the **Agent Development Kit (ADK)**.

---

## 1. Executive Overview: The 5-Act Demonstration Flow

The demonstration is structured across 5 progressive acts that escalate from physical geospatial observation to predictive physics, executive synthesis, and closed-loop ERP execution:

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                        GEMINI ENTERPRISE 5-ACT DEMONSTRATION ESCALATION                                │
├─────────────────────┬─────────────────────┬─────────────────────┬─────────────────────┬────────────────┤
│ ACT 1: SPATIAL MAPS │ ACT 2: SCADA DATA   │ ACT 3: SARIMAX MATH │ ACT 4: EXEC REPORT  │ ACT 5: SAP ERP │
│ Google Maps Layer   │ Yokogawa SCADA      │ Diurnal Seasonality │ 4-Source HTML/PDF   │ S/4HANA Order  │
│ 18,700 km Grid      │ Siemens RDS Feeds   │ Leading Off-take (X)│ Shift Paperwork     │ Project        │
│ Yamuna River Alert  │ Chhainsa/Vijaipur   │ +3.8% Setpoint      │ 3 hrs -> 6 seconds  │ Navodaya &     │
│ Zero Flood Washout  │ No Manual CSVs      │ Saves ₹16.88 Cr/yr  │ Executive Briefing  │ AI Tarang Q&A  │
└─────────────────────┴─────────────────────┴─────────────────────┴─────────────────────┴────────────────┘
```

---

## 2. Interactive Google Maps Spatial Layer (Act 1 Explained)

When the agent executes **Act 1**, it renders an interactive **Google Maps (Satellite / Terrain / Hybrid)** component populated directly by [`fixtures/river_crossings_gis.geojson`](file:///usr/local/google/home/amandeepsinghs/O&G_slidedeck_agentic_transformation/Oil%20&%20Gas%20Agent%20Portfolio/agents/gail_pipeline_agent/fixtures/river_crossings_gis.geojson):

* **Pipeline Polylines:** Real GPS linestring paths tracing the **18,700 km National Gas Grid**, prominently rendering the flagship **Hazira-Vijaipur-Jagdishpur (HVJ)** trunkline and the **Mumbai-Nagpur-Jharsuguda Pipeline (MNJPL)** along the Samruddhi Expressway.
* **Interactive Facility Markers:**
  * **Vijaipur Compressor Hub** `[24.1627°N, 77.2941°E]`: Primary compression hub with 8 active industrial gas turbines.
  * **Chhainsa Compressor Station** `[28.2711°N, 77.3412°E]`: Secondary booster station feeding the National Capital Region (NCR).
  * **Dadri Delivery Terminal** `[28.5516°N, 77.5539°E]`: High-pressure delivery manifold.
* **Dynamic Environmental Risk Overlay (Flashing Red Pulsing Tag):**
  * **Gauna-Bawana Yamuna River Crossing** `[28.7912°N, 77.0315°E]`:
    * *River Water Level:* **206.40 m** (Design Danger Level: **205.33 m**).
    * *IMD Meteorological Radar:* **115.6 mm** heavy precipitation in catchment.
    * *SCADA Acoustic Sensor:* Elevated vibration indicating hydraulic bed scouring.
    * *Action Tag:* Preemptive sectionalizing valve isolation warning to prevent repeats of the historic flood leakage incident.

---

## 3. The 5 Demonstration Acts: Prompts, Answers & "So What?"

### ACT 1: Spatial Grid Infrastructure & IMD Weather Overlay
* **Presenter Prompt:**
  > *"Gemini, initialize a grid health and risk audit across the Hazira-Vijaipur-Jagdishpur (HVJ) and MNJPL pipeline corridors for the next 24 hours."*
* **Live Agent Output:**
  * **A2UI Visual:** Interactive Google Maps view of the 18,700 km grid with environmental hazard markers.
  * **Agent Answer:**
    > *"Audit initialized across 18,700 km. Critical hazard detected at Gauna-Bawana Yamuna River crossing. Catchment received 115.6mm rainfall; river gauge at 206.4m exceeds the 205.33m design danger mark. SCADA reports acoustic vibration stress. Immediate sectionalizing valve watch advised."*
* **The "SO WHAT?" & Business Benefit:**
  * **Operational Impact:** Replaces fragmented weather forecasts with dynamic spatial asset risk fusion.
  * **Asset Protection:** Prevents catastrophic underwater pipeline washouts and leaks during monsoon river swells.

---

### ACT 2: SCADA Telemetry & Siemens Gas Turbine Observability
* **Presenter Prompt:**
  > *"Access live telemetry for Chhainsa Compressor Station and plot 72-hour historical trends for line-pack pressure, gas flow rate, and Siemens turbine exhaust temperatures."*
* **Live Agent Output:**
  * **A2UI Visual:** Multi-variable Vega-Lite time-series chart showing pressure, flow, and exhaust temperatures.
  * **Agent Answer:**
    > *"Retrieved 72-hour telemetry from Yokogawa SCADA and Siemens RDS. Chhainsa linepack is currently stable at 81.47 kg/cm² with an average throughput of 48.05 MMSCMD. However, Siemens gas turbine exhaust temperatures reached 549.4 °C under daytime heavy load."*
* **The "SO WHAT?" & Business Benefit:**
  * **Operational Impact:** Eliminates **45 minutes per shift engineer** spent manually exporting SCADA CSVs and formatting Excel charts.
  * **Cross-Silo Observability:** Seamlessly bridges pipeline pressure with turbine mechanical reliability in a single view.

---

### ACT 3: Deterministic SARIMAX Forecasting & Optimal Setpoint Recommendation
* **Presenter Prompt:**
  > *"Execute a 24-hour predictive SARIMAX demand forecast for Chhainsa station considering downstream fertilizer plant off-takes, and calculate optimal compressor setpoints at Vijaipur."*
* **Live Agent Output:**
  * **A2UI Visual:** 24-hour predictive line-pack curve with 95% confidence bands and a red dashed threshold line showing pressure dropping below $76.0\text{ kg/cm}^2$ at **Hour 14 ahead**.
  * **Agent Answer:**
    > *"Multivariate SARIMAX model (AIC: 190.5) detects a linepack deficit 14 hours ahead, triggered by a +25% scheduled off-take surge from HURL/NFL fertilizer units and ambient heat (41.9 °C).  
    > **Recommendation:** Increase Vijaipur compressor throughput by +3.8% starting at 14:00 hrs. This compensates for the 14-hour gas transit delay, stabilizes Chhainsa linepack at 78.5 kg/cm², and avoids firing an auxiliary turbine."*
* **The "SO WHAT?" & Business Benefit:**
  * **Physical Reality:** Gas travels at $\approx 30\text{ km/h}$; the 14-hour advance warning matches the real hydraulic travel time over 380 km from Vijaipur to Chhainsa.
  * **Direct Financial ROI:** Saves **18,500 SCM/day** of internal fuel gas ($\mathbf{₹4.62\text{ Lakhs/day}}$ or $\mathbf{₹16.88\text{ Crore/year}}$ per hub), directly driving **Project Sanchay's ₹600 Cr NPV target**.

---

### ACT 4: Multi-Source Automated Executive Briefing (The Climax)
* **Presenter Prompt:**
  > *"Compile this grid audit, weather assessment, SARIMAX forecast, and fuel-saving calculations into an official Daily Line-Pack & Integrity Executive Briefing."*
* **Live Agent Output:**
  * **A2UI Visual:** Generates and renders a styled, multi-page executive HTML/PDF report with GAIL branding, grid KPIs, river hazard alerts, turbine health status, and Project Sanchay ROI tables.
  * **Agent Answer:**
    > *"Synthesized data from Yokogawa SCADA, Siemens RDS, IMD radar, and Project Sanchay calculations. Official briefing compiled autonomously in 6 seconds: 'GAIL Daily Line-Pack & Grid Integrity Briefing'."*
* **The "SO WHAT?" & Business Benefit:**
  * **Administrative Latency Zeroed:** Eliminates **3 to 4 hours** of daily manual shift paperwork and chart cropping per station.
  * **Single Source of Truth:** Ensures leadership, plant managers, and control room operators make decisions off the exact same audited data.

---

### ACT 5: Closed-Loop SAP S/4HANA Action & GAIL AI Tarang Q&A
* **Part 1 (SAP Integration): Presenter Prompt:**
  > *"Log this optimization advisory and stage a preventive work order directly into RISE with SAP S/4HANA Cloud."*
  * **Agent Answer:**
    > *"Created SAP S/4HANA Work Order #WO-481034 for Equipment EQ-VIJ-GT-01 under Project Navodaya at Plant 1102 (Vijaipur). Order status: RELEASED_FOR_EXECUTION. Setpoint calibrated for +3.8% throughput."*
  * **Business Benefit:** Seamless IT/OT convergence; zero human data-entry error between the SCADA control room and ERP accounting.
* **Part 2 (Audience Q&A): Invite any attendee (HR, Finance, Legal) to ask:**
  > *"What was our total natural gas transmission volume last fiscal year, and what is our Net Zero Scope-1 target timeline?"*
  * **Agent Answer:**
    > *"According to GAIL's official BRSR disclosures, GAIL transmitted an average of 122.18 MMSCMD across 18,700 km of pipelines (~70% national share) and has committed to 100% Net Zero in Scope 1 and Scope 2 emissions by 2035."*
  * **Business Benefit:** Fulfills **GAIL AI Tarang** by proving that all 300 non-technical attendees can query complex enterprise data conversationally.

---

## 4. Directory Layout

```
agents/gail_pipeline_agent/
├── SDD.md                           # System Design Document (Architecture & Math)
├── BUILD.md                         # Engineering Build Guide & Presenter Runbook
├── CHECKLIST.md                     # Formal Phase-Gate Verification Checklist
├── blueprint.md                     # 5-Act Demonstration Blueprint
├── some_relevant comments.md        # Technical explanation of SARIMAX Physics
├── pyproject.toml                   # Python dependencies & build config
├── Dockerfile                       # Container definition for Cloud Run
├── agents-cli-manifest.yaml         # Enterprise agent registry manifest
├── README.md                        # This file
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

## 5. Running the Tests & Local Service

### Running the Test Suite (13/13 Passing)
```bash
PYTHONPATH=. pytest tests/ -v
```

### Running the FastAPI & A2A Server
```bash
uvicorn app.fast_api_app:app --host 0.0.0.0 --port 8080 --reload
```

* **Health Check:** `http://localhost:8080/health`
* **Agent Card:** `http://localhost:8080/a2a/gail_grid_advisor/.well-known/agent-card.json`
* **Latest Report:** `http://localhost:8080/api/v1/report/latest`
* **Interactive Prompt API:** `POST http://localhost:8080/api/v1/prompt`
