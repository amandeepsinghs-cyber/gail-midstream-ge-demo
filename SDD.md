# System Design Document (SDD)
## GAIL Autonomous Pipeline Grid, Predictive Analytics & Executive Advisory Agent
### Document ID: `SDD-GAIL-GRID-ADVISOR-V1.0`
**Status:** Approved Architecture | **Target Runtime:** Google Cloud Agent Runtime / Cloud Run  
**Author:** Oil & Gas Enterprise Agentic Ecosystem | **Governing Entity:** GAIL (India) Limited

---

## 1. Executive Summary & Enterprise Context

GAIL (India) Limited stands as India’s Maharatna natural gas transmission leader, operating approximately **18,700 km of cross-country natural gas pipelines** (~70% of India's transmission infrastructure) with an average daily volume of **122.18 MMSCMD**. 

### 1.1 Strategic Alignment
This agentic system directly operationalizes three flagship GAIL digital mandates:
1. **Project Sanchay / Sanchay-II:** Targets **₹600 Crore ($72M) Net Present Value (NPV) gains** by 2028 through autonomous process optimization, line-pack balancing, and internal fuel gas burn reduction across compressor hubs.
2. **Project Navodaya (RISE with SAP S/4HANA Cloud):** Winner of the SAP ACE Award for core digital ERP operations. This agent executes closed-loop Plant Maintenance (PM) work orders directly into SAP Cloud without human administrative delay.
3. **GAIL AI Tarang:** Enterprise-wide AI upskilling engaging 5,000+ employees. The agent democratizes natural language access to complex transmission telemetry, ESG BRSR disclosures, and 2035 Net Zero metrics for non-technical stakeholders.

---

## 2. System Architecture & OT/IT Convergence

The agent functions as a real-time autonomous operational partner connecting physical field telemetry, meteorological radar, time-series forecasting, and cloud ERP:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                  GAIL AGENT OT/IT CONVERGENCE TOPOLOGY                                      │
├───────────────────────────────┬───────────────────────────────┬─────────────────────────────────────────────┤
│ 1. OT SENSOR TELEMETRY        │ 2. METEOROLOGICAL RADAR       │ 3. ENTERPRISE IT & ERP                      │
│ • Yokogawa FAST/TOOLS SCADA   │ • IMD Doppler Weather Radar   │ • RISE with SAP S/4HANA (Project Navodaya)  │
│   (Chhainsa & Vijaipur hubs)  │ • River Catchment Gauges      │ • Customer Nominations (HURL, NFL, CGD)     │
│ • Siemens RDS Gas Turbines    │ • Gauna-Bawana Yamuna Warning │ • GAIL BRSR & ESG Disclosures               │
└───────────────┬───────────────┴───────────────┬───────────────┴──────────────────────┬──────────────────────┘
                │                               │                                      │
                ▼                               ▼                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                     GEMINI ENTERPRISE AGENT ORCHESTRATOR                                    │
│                                           (Google ADK / Python 3.11)                                        │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ • Multivariate SARIMAX Engine (s=24 diurnal seasonality, exogenous nominations & ambient heatwave)          │
│ • Transient Hydraulic Transit Delay Estimator (350 km Vijaipur -> Chhainsa wave propagation)                │
│ • A2UI v0.9 Vega-Lite Component Renderer (Spatial GIS corridors, telemetry charts, confidence bands)        │
│ • Multi-Source Executive Briefing HTML/PDF Synthesis Compiler                                               │
└──────────────────────────────────────────────────────┬──────────────────────────────────────────────────────┘
                                                       │
                               ▼                       ▼                       ▼
                     ┌───────────────────┬───────────────────────────┬───────────────────┐
                     │ A2A Endpoint      │ Executive HTML Briefing   │ SAP Work Order    │
                     │ JSON-RPC 0.3/1.0  │ 4-Source PDF Deliverable  │ PM01 Notification │
                     └───────────────────┴───────────────────────────┴───────────────────┘
```

---

## 3. Mathematical & Data Science Foundations

### 3.1 SARIMAX Line-Pack Formulation
Standard univariate time-series models (like basic ARIMA) fail to predict sudden pressure collapses when past pressure logs look flat. The GAIL agent implements a **Multivariate Seasonal AutoRegressive Integrated Moving Average with eXogenous regressors**:

$$\text{SARIMAX}(p, d, q) \times (P, D, Q)_s \text{ with exogenous matrix } \mathbf{X}$$

* **Target Variable ($Y_t$):** Chhainsa compressor station line-pack pressure ($\text{kg/cm}^2$).
* **Model Orders:** $(p=1, d=1, q=0) \times (P=1, D=0, Q=0)_{s=24}$
* **Exogenous Variables ($\mathbf{X}$):**
  1. $X_{1,t}$: Scheduled downstream customer off-take nominations from fertilizer units (HURL, NFL) and power stations (MMSCMD).
  2. $X_{2,t}$: IMD ambient temperature forecasts ($^\circ\text{C}$), accounting for gas turbine thermal derating and daytime electrical air-conditioning surges.

### 3.2 Physical Justification of Early Warning (Hydraulic Wave Propagation)
Natural gas travels through cross-country trunklines at approximately **$25 \text{ to } 40\text{ km/h}$**. 
* The distance between the **Vijaipur Compressor Hub** and the **Chhainsa Station** is approximately **$380\text{ km}$**.
* A hydraulic line-pack pressure wave initiated at Vijaipur requires **$10 \text{ to } 14\text{ hours}$** of physical transit time to manifest at Chhainsa.
* By ingesting advance nominations ($X_{1}$) at $T=0$, the SARIMAX model predicts line-pack depletion at $T+14\text{ hours}$, allowing the operator to adjust Vijaipur setpoints (+3.8%) at $T=0$, so the physical gas pack arrives exactly as the fertilizer plant off-take ramps up.

### 3.3 Project Sanchay Fuel Gas Quantification
* **Auxiliary Peaking Turbine Burn:** Starting an additional Siemens SGT gas turbine at Chhainsa consumes $\approx 22,000\text{ SCM/day}$ of internal fuel gas.
* **Proactive Line-Pack Stabilization:** Boosting Vijaipur baseline throughput by $+3.8\%$ eliminates auxiliary turbine starts, resulting in net fuel savings of **$18,500\text{ SCM/day}$**.
* **Daily Margin Recovery:** $18,500\text{ SCM} \times ₹25/\text{SCM} = \mathbf{₹4,62,500/\text{day}}$.
* **Annualized Asset Impact:** $\mathbf{₹16.88\text{ Crore / year}}$ in direct fuel gas savings per compressor hub.

---

## 4. Component Specification & Tool Contracts

The agent implements 6 concrete callable tools conforming to Pydantic v2 schemas in `app/contracts.py`:

| Tool Name | Act | Inputs | Primary Output | A2UI Visual Artifact |
| :--- | :--- | :--- | :--- | :--- |
| `audit_grid_and_weather_risk` | Act 1 | `corridor: str` | `GridHealthAuditResponse` | GeoJSON Pipeline Map + IMD Flash Flood Alert Card |
| `query_scada_telemetry` | Act 2 | `station: str, hours: int` | `ScadaHistoryResponse` | 72h Multi-variable Vega-Lite Time-Series Chart |
| `run_sarimax_linepack_forecast` | Act 3 | `station: str, horizon: int` | `SarimaxForecastResponse` | 24h Predictive Confidence Band & Setpoint Card |
| `compile_executive_briefing` | Act 4 | None | `ExecutiveBriefingReport` | Multi-Source Styled HTML/PDF Briefing Document |
| `stage_sap_maintenance_order` | Act 5 | `SapWorkOrderRequest` | `SapWorkOrderResponse` | SAP S/4HANA Work Order Confirmation Badge |
| `query_enterprise_knowledge` | Act 5 | `query: str` | `EnterpriseQueryResponse` | Cited Fact Card (GAIL AI Tarang Verified) |

---

## 5. Security, IAM & Data Governance

1. **Service Account Identity:** `gail-grid-agent@og-agentic-ecosystem.iam.gserviceaccount.com`
2. **GCS Storage Scope:** `gs://og-agentic-gail-data-asia-south1/`
   * Read: `SCADA Telemetry/`, `Siemens RDS Logs/`, `IMD Weather Feeds/`
   * Write: `Executive Briefings/`, `Optimized Setpoint Advisories/`
3. **ERP Authentication:** Mutual TLS (mTLS) with OAuth 2.0 Client Credentials targeting RISE with SAP S/4HANA Cloud OData v4 endpoints (`/sap/opu/odata4/sap/api_maintorder/`).
4. **Air-Gap Telemetry Isolation:** SCADA telemetry is processed via read-only replication from Yokogawa FAST/TOOLS OPC-UA Historian into GCS Medallion landing zones, preventing write-back risks to safety-critical safety instrumented systems (SIS).

---

## 6. Verification & Test Architecture

The service includes an automated pytest suite validating all 5 acts:
* `tests/test_contracts.py`: Strict schema typing and validation.
* `tests/test_sarimax_analytics.py`: Model convergence, AIC computation, and setpoint logic.
* `tests/test_tools_agent.py`: End-to-end execution of all 6 tools and conversational routing.
