# System Design Document (SDD)
## GAIL Autonomous Pipeline Grid, Predictive Analytics & Executive Advisory Agent
### Document ID: `SDD-GAIL-GRID-ADVISOR-V2.0`
**Status:** Approved Sovereign Architecture | **Target Runtime:** Google Gemini Enterprise / Cloud Run  
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
│ 1. OT SENSOR TELEMETRY        │ 2. AI METEOROLOGICAL ENGINE   │ 3. ENTERPRISE IT & ERP                      │
│ • Yokogawa FAST/TOOLS SCADA   │ • Google DeepMind WeatherNext │ • RISE with SAP S/4HANA (Project Navodaya)  │
│   (Chhainsa & Vijaipur hubs)  │   (0.05° Station Ensemble)    │ • Customer Nominations (HURL, NFL, CGD)     │
│ • Siemens RDS Gas Turbines    │ • Hydrological Gauges (Yamuna)│ • GAIL BRSR & ESG Disclosures               │
│ • Submerged Acoustic Scour    │ • IMD Doppler Weather Radar   │ • GCS Medallion Data Lake                   │
└───────────────┬───────────────┴───────────────┬───────────────┴──────────────────────┬──────────────────────┘
                │                               │                                      │
                ▼                               ▼                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                     GEMINI ENTERPRISE AGENT ORCHESTRATOR                                    │
│                                           (Google ADK / Python 3.11)                                        │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ • Multivariate Econometric SARIMAX Engine (s=24 diurnal seasonality, AIC grid search, MAPE backtest)       │
│ • Transient Hydraulic Transit Delay Estimator (380 km Vijaipur -> Chhainsa wave propagation @ 35 km/h)     │
│ • A2UI v0.9 Vega-Lite Component Renderer (Spatial GIS corridors, WeatherNext cards, confidence bands)       │
│ • Sovereign Multi-Source Executive Briefing HTML/PDF Synthesis Compiler                                     │
└──────────────────────────────────────────────────────┬──────────────────────────────────────────────────────┘
                                                       │
                                ▼                       ▼                       ▼
                     ┌───────────────────┬───────────────────────────┬───────────────────┐
                     │ A2A & A2UI Card   │ Sovereign Executive Brief │ SAP Work Order    │
                     │ Gemini Enterprise │ PPAC-Grade HTML/PDF       │ PM01 Notification │
                     └───────────────────┴───────────────────────────┴───────────────────┘
```

---

## 3. Mathematical & Data Science Foundations

### 3.1 PPAC-Grade SARIMAX Line-Pack Formulation
Standard univariate time-series models (like basic ARIMA) fail to predict sudden pressure collapses when past pressure logs look flat. The GAIL agent implements a **Multivariate Seasonal AutoRegressive Integrated Moving Average with eXogenous regressors**:

$$\text{SARIMAX}(p, d, q) \times (P, D, Q)_s \text{ with exogenous matrix } \mathbf{X}$$

- **Target Variable ($Y_t$):** Chhainsa compressor station linepack pressure ($\text{kg/cm}^2$).
- **Exogenous Regressors ($\mathbf{X}_t$):**
  1. $X_{1,t}$: Scheduled downstream customer nominations (MMSCMD) from anchor fertilizer units.
  2. $X_{2,t}$: Real-time ambient temperature ($^\circ\text{C}$) from Google DeepMind WeatherNext 3.
- **Seasonality ($s=24$):** Diurnal 24-hour cycle corresponding to daily industrial dispatch and ambient temperature shifts.
- **Hyperparameter Optimization:** Automatic bounded AIC grid search over Box-Jenkins space:
  - Non-seasonal orders: $p \in [0, 2]$, $d = 1$, $q \in [0, 2]$
  - Seasonal orders: $P \in [0, 1]$, $D \in [0, 1]$, $Q \in [0, 1]$
- **Backtesting Verification:** 6-hour out-of-sample holdout validation measuring Mean Absolute Percentage Error ($\text{MAPE} < 2.0\%$).

### 3.2 Transient Hydraulic Delay Physics
Natural gas is a compressible fluid. Pressure waves generated at upstream compressor stations do not travel at the speed of light or sound in open air, but at the sonic velocity in high-pressure methane ($\approx 380\text{--}420\text{ m/s}$) moderated by pipeline friction, resulting in bulk hydraulic wave propagation velocities of:

$$v_{\text{wave}} \approx 30\text{--}40\text{ km/h}$$

For the critical transmission leg from **Vijaipur Compressor Hub** to **Chhainsa Station** ($\Delta x \approx 380\text{ km}$):

$$\Delta t_{\text{transit}} = \frac{380\text{ km}}{35\text{ km/h}} \approx 8\text{--}10\text{ hours}$$

**Operational Significance:** If customer offtake surges at $T+14\text{h}$, waiting until the pressure drops at Chhainsa before ramping Vijaipur causes an unavoidable line-pack collapse. The agent identifies the deficit $14$ hours in advance and issues the setpoint increase at $T+6\text{h}$ to $T+8\text{h}$ (8 hours ahead), ensuring the gas wave arrives exactly as the industrial demand spikes.

---

## 4. Google DeepMind WeatherNext 3 Model Integration

The agent queries the operational WeatherNext 3 AI model (0.05° station ensemble):
- **Resolution:** 0.05° high-resolution station calibration (~5 km spatial resolution).
- **Ensemble Sampling:** 64-member probabilistic ensemble statistics ($p_{10}, p_{25}, p_{50}\text{ median}, p_{75}, p_{90}$).
- **Hydrological Coupling:** Couples hourly precipitation intensity ($\text{mm/h}$) and catchment saturation to river gauge heights, flagging scour velocity thresholds ($v > 3.2\text{ m/s}$) at pipeline submerged crossings (e.g. Gauna-Bawana Yamuna crossing).

---

## 5. Project Sanchay ROI & Decarbonization Formulation

Under Project Sanchay, compressor fuel gas optimization yields direct financial and ESG returns:

$$\text{Daily Savings (INR)} = \Delta V_{\text{fuel}} \times P_{\text{gas}} = 18,500\text{ SCM/day} \times ₹25/\text{SCM} = ₹4,62,500/\text{day}$$
$$\text{Annualized Savings} = ₹4,62,500 \times 365 = ₹16.88\text{ Crore/year}$$
$$\text{CO}_2\text{e Avoided} = 18,500\text{ SCM/day} \times 2.0\text{ kg CO}_2/\text{SCM} \times 365 = 13,500\text{ MT CO}_2\text{e/year}$$
