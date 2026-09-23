# Engineering Build Guide & Presenter Runbook
## GAIL Autonomous Pipeline Grid, Predictive Analytics & Executive Advisory Agent
### Document ID: `BUILD-GAIL-GRID-ADVISOR-V2.0`
**Status:** Approved Sovereign Build | **Target Runtime:** Google Gemini Enterprise / Cloud Run  
**Governing Entity:** GAIL (India) Limited

---

## 1. Overview & Project Structure

This document outlines the step-by-step engineering build, test harness execution, and live demonstration runbook for the **GAIL Pipeline Grid & Executive Advisory Agent**.

```
agents/gail_pipeline_agent/
├── SDD.md                           # System Design Document (v2.0)
├── BUILD.md                         # This build & execution runbook (v2.0)
├── CHECKLIST.md                     # Formal Phase-Gate Verification Scorecard
├── README.md                        # Complete demonstration playbook
├── pyproject.toml                   # Python dependencies & build config
├── Dockerfile                       # Container definition for Cloud Run
├── agents-cli-manifest.yaml         # Enterprise agent registry manifest
├── app/
│   ├── contracts.py                 # Pydantic schemas across all 5 acts & WeatherNext
│   ├── agent.py                     # Google ADK agent orchestrator & prompt router
│   ├── fast_api_app.py              # A2A JSON-RPC & REST endpoints
│   ├── analytics/
│   │   ├── sarimax_linepack.py      # Econometric SARIMAX(1,1,0)(1,0,0)24 forecasting engine
│   │   └── weathernext_engine.py    # Google DeepMind WeatherNext 3 probabilistic engine
│   ├── render/
│   │   └── a2ui_cards.py            # A2UI v0.9 Vega-Lite visualization cards
│   ├── synthesis/
│   │   └── executive_report_compiler.py # PPAC-grade sovereign HTML/PDF compiler
│   └── integration/
│       ├── tools.py                 # 7 callable ADK agent tools
│       └── gcs_connector.py         # GCS Medallion Data Lake connector
├── fixtures/
│   ├── gail_hvj_scada_telemetry_72h.csv # Verified 72-hour SCADA & turbine dataset
│   ├── river_crossings_gis.geojson      # HVJ corridor & Yamuna flood alert layer
│   ├── customer_nominations_24h.json    # 24h leading exogenous demand & temp feeds
│   └── sap_order_template.json          # S/4HANA Work Order schema
└── tests/
    ├── test_contracts.py            # Pydantic schema validation
    ├── test_sarimax_analytics.py    # Time-series model convergence & setpoint tests
    └── test_tools_agent.py          # End-to-end multi-act prompt execution tests
```

---

## 2. Verbatim 5-Act Live Presenter Runbook

### Act 1: Spatial GIS Grid Infrastructure & Environmental Weather Layer
- **Presenter Prompt:** `"Gemini, initialize a grid health and risk audit across the HVJ and MNJPL pipeline corridors for the next 24 hours."`
- **Agent Output:** A2UI Spatial GIS map card rendering the 18,700 km transmission network, highlighting Hazira, Vijaipur, Chhainsa, and Dadri. Flags critical alert at Gauna-Bawana Yamuna crossing (206.4m gauge > 205.33m danger mark).
- **Weather AI Expansion:** `"Gemini, what is the WeatherNext 3 probabilistic weather forecast for the Yamuna River crossing?"`
- **Agent Output:** WeatherNext 3 card with 64-member ensemble bounds ($p_{10}, p_{50}, p_{90}$), forecasting 115.6mm deluge and scour velocity exceedance ($v > 3.2\text{ m/s}$).

### Act 2: SCADA Telemetry Ingestion & Turbine Observability
- **Presenter Prompt:** `"Access live telemetry for Chhainsa Compressor Station and plot 72-hour historical trends for line-pack pressure, gas flow rate, and Siemens turbine exhaust temperatures."`
- **Agent Output:** Interactive A2UI dual-axis chart showing 72-hour pressure ($81.47\text{ kg/cm}^2$), flow ($48.05\text{ MMSCMD}$), and Siemens turbine exhaust temperature peaking at $549.4^\circ\text{C}$.

### Act 3: Deterministic Econometric SARIMAX Demand Forecasting
- **Presenter Prompt:** `"Execute a 24-hour predictive SARIMAX demand forecast for Chhainsa station considering downstream fertilizer plant off-takes, and calculate optimal compressor setpoints at Vijaipur."`
- **Agent Output:** SARIMAX model (AIC: 98.73, MAPE: 1.42%) projects pressure depletion to $74.2\text{ kg/cm}^2$ at Hour 14 ahead. Accounts for 8-hour hydraulic transit delay ($380\text{ km} @ 35\text{ km/h}$) and advises $+3.8\%$ Vijaipur setpoint increase at 14:00 hrs, saving $18,500\text{ SCM/day}$ of fuel gas (₹16.88 Crore/year) under Project Sanchay.

### Act 4: Sovereign Multi-Source Executive Briefing Compilation
- **Presenter Prompt:** `"Compile this grid audit, weather assessment, SARIMAX forecast, and fuel-saving calculations into an official Daily Line-Pack & Integrity Executive Briefing."`
- **Agent Output:** Synthesizes Yokogawa SCADA, Siemens RDS, WeatherNext 3, and Project Sanchay balance sheets into a sovereign executive briefing matching the MoPNG/PPAC format with interactive Save Edits and Print/PDF buttons. Uploads to `gs://gail-midstream-ge-demo-datalake/curated/executive_reports/`.

### Act 5: Closed-Loop SAP S/4HANA Work Order Staging & AI Tarang
- **Presenter Prompt:** `"Log this optimization advisory and stage a preventive work order directly into RISE with SAP S/4HANA Cloud."`
- **Agent Output:** Stages Work Order `WO-481918` for Unit `EQ-VIJ-GT-01` under Project Navodaya at Plant 1102 (Vijaipur). Zero human manual entry delay.
- **Presenter Prompt:** `"What was our total natural gas transmission volume last fiscal year, and what is our Net Zero Scope-1 target timeline?"`
- **Agent Output:** GAIL AI Tarang answers with cited BRSR disclosures: 122.18 MMSCMD volume across 18,700 km and 100% Net Zero Scope 1 & 2 emissions by 2035.
