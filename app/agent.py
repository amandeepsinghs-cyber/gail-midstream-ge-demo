"""
Google ADK Agent Definition: GAIL Autonomous Pipeline Grid & Executive Advisory Agent.
Orchestrates the 5-Act demonstration on stage:
  Act 1: Spatial GIS & Weather Overlay (audit_grid_and_weather_risk)
  Weather AI: Google DeepMind WeatherNext 3 Probabilistic Forecast (get_weathernext_forecast)
  Act 2: SCADA & Siemens RDS Telemetry Ingestion (query_scada_telemetry)
  Act 3: Deterministic Econometric SARIMAX Forecasting (run_sarimax_linepack_forecast)
  Act 4: Multi-Source Sovereign Executive Briefing Compilation (compile_executive_briefing)
  Act 5: Closed-Loop SAP S/4HANA Action (stage_sap_maintenance_order) & Enterprise Q&A
"""

from typing import Dict, Any, List
from app.integration.tools import (
    audit_grid_and_weather_risk,
    get_weathernext_forecast,
    query_scada_telemetry,
    run_sarimax_linepack_forecast,
    compile_executive_briefing,
    stage_sap_maintenance_order,
    query_enterprise_knowledge
)
from app.contracts import SapWorkOrderRequest

GAIL_SYSTEM_INSTRUCTION = """
You are the GAIL Autonomous Pipeline Grid, Predictive Analytics & Executive Advisory Agent,
powered by Google Gemini Enterprise.

You act as an agentic operational partner for GAIL (India) Limited's National Gas Management Centre (NGMC),
connecting Yokogawa FAST/TOOLS SCADA, Siemens Remote Diagnostic Services (RDS) turbine telemetry,
Google DeepMind WeatherNext 3 probabilistic weather models, and RISE with SAP S/4HANA Cloud (Project Navodaya).

Your mission across the 5 demonstration acts:
1. Act 1 (Spatial GIS & Weather): Map the 18,700 km grid and flag river swell hazards (e.g. Gauna-Bawana Yamuna crossing).
2. Weather AI (WeatherNext 3): Query 0.05° high-resolution AI ensemble forecasts for any grid coordinate.
3. Act 2 (SCADA Observability): Retrieve real-time 72h telemetry from Chhainsa station and Siemens gas turbines.
4. Act 3 (Econometric SARIMAX): Execute multivariate SARIMAX forecasting integrating customer nominations & ambient heatwaves,
   predict linepack depletion 14 hours ahead, and compute optimal compressor setpoints (+3.8% at Vijaipur) saving 18,500 SCM/day under Project Sanchay.
5. Act 4 (Executive Synthesis): Compile multi-source data into an official sovereign Daily Line-Pack & Grid Integrity Executive Briefing.
6. Act 5 (Closed-Loop SAP & AI Tarang): Stage preventive maintenance orders in RISE with SAP S/4HANA Cloud and answer audience queries with cited facts.

Always communicate with rigorous engineering authority, citing specific stations (Chhainsa, Vijaipur, Dadri),
physical units (kg/cm², MMSCMD, °C), and strategic programs (Project Sanchay, Project Navodaya, GAIL AI Tarang).
"""

class GailPipelineAgent:
    """Agent orchestrator for interactive command execution and API integration."""
    
    def __init__(self):
        self.system_prompt = GAIL_SYSTEM_INSTRUCTION
        self.available_tools = {
            "audit_grid_and_weather_risk": audit_grid_and_weather_risk,
            "get_weathernext_forecast": get_weathernext_forecast,
            "query_scada_telemetry": query_scada_telemetry,
            "run_sarimax_linepack_forecast": run_sarimax_linepack_forecast,
            "compile_executive_briefing": compile_executive_briefing,
            "stage_sap_maintenance_order": stage_sap_maintenance_order,
            "query_enterprise_knowledge": query_enterprise_knowledge
        }

    def execute_prompt(self, user_prompt: str) -> Dict[str, Any]:
        """Routes conversational user prompts to appropriate tool execution and narrative responses."""
        p_lower = user_prompt.lower()
        
        # ACT 4: Executive PDF/HTML briefing report
        if "report" in p_lower or "briefing" in p_lower or "compile" in p_lower:
            report = compile_executive_briefing()
            return {
                "act": "ACT 4: Multi-Source Executive Briefing",
                "narrative": (
                    f"Synthesized data from Yokogawa SCADA, Siemens RDS, Google DeepMind WeatherNext 3, and Project Sanchay ROI. "
                    f"Official sovereign briefing compiled in 6 seconds: '{report.report_title}'. "
                    f"Output published at {report.compiled_html_path}."
                ),
                "data": report.model_dump(),
                "artifact_path": report.compiled_html_path
            }

        # WEATHER AI: Specific WeatherNext query (e.g. "weather in Chhainsa", "Yamuna catchment rainfall")
        elif "weathernext" in p_lower or ("weather" in p_lower and ("in" in p_lower or "at" in p_lower or "forecast" in p_lower or "temperature" in p_lower or "rain" in p_lower)):
            loc = "Gauna_Bawana" if ("yamuna" in p_lower or "river" in p_lower or "crossing" in p_lower) else ("Vijaipur_Hub" if "vijaipur" in p_lower else "Chhainsa_CS")
            w_res = get_weathernext_forecast(location=loc)
            m = w_res.summary_metrics
            return {
                "act": "WEATHER AI: Google DeepMind WeatherNext 3",
                "narrative": (
                    f"WeatherNext 3 (0.05° Station Ensemble) processed for {w_res.location_name}: "
                    f"Peak ambient temperature {m.get('peak_temperature_c')}°C, 24h cumulative precipitation {m.get('cumulative_precipitation_p90_mm')}mm (p90). "
                    f"Risk Envelope: {w_res.risk_category}. {w_res.action_protocol}"
                ),
                "data": w_res.model_dump(),
                "a2ui_card": w_res.a2ui_card
            }

        # ACT 1: Grid audit / GIS / weather overlay
        elif "grid health" in p_lower or "spatial" in p_lower or ("weather" in p_lower and "audit" in p_lower) or ("hvj" in p_lower and "risk" in p_lower) or "corridor" in p_lower:
            audit = audit_grid_and_weather_risk()
            return {
                "act": "ACT 1: Spatial GIS & Weather Overlay",
                "narrative": (
                    "Audit initialized across the 18,700 km transmission network. "
                    "Active environmental hazard flagged at the Gauna-Bawana Yamuna River crossing "
                    "due to 115.6mm rainfall in catchment. River gauge level (206.4m) exceeds danger mark (205.33m). "
                    "A2UI spatial layer loaded with real-time sectionalizing valve alerts."
                ),
                "data": audit.model_dump(),
                "a2ui_card": audit.a2ui_map_payload
            }
            
        # ACT 2: SCADA telemetry / Chhainsa / trends
        elif "telemetry" in p_lower or "scada" in p_lower or "72-hour" in p_lower:
            history = query_scada_telemetry(station="Chhainsa_CS", hours=72)
            return {
                "act": "ACT 2: SCADA & Siemens RDS Telemetry",
                "narrative": (
                    "Retrieved 72-hour telemetry from Yokogawa FAST/TOOLS SCADA and Siemens RDS. "
                    "Current linepack pressure at Chhainsa is 81.47 kg/cm², average throughput is 48.05 MMSCMD. "
                    "Siemens gas turbine exhaust temperature reached 549.4 °C under daytime heavy load."
                ),
                "data": history.model_dump(),
                "a2ui_card": history.a2ui_timeseries_chart
            }
            
        # ACT 3: SARIMAX forecasting / optimal setpoint / Project Sanchay
        elif "sarimax" in p_lower or "forecast" in p_lower or "setpoint" in p_lower or "sanchay" in p_lower or "deficit" in p_lower:
            forecast = run_sarimax_linepack_forecast(station="Chhainsa_CS", horizon_hours=24)
            sp = forecast.setpoint_recommendation
            return {
                "act": "ACT 3: Deterministic SARIMAX Forecasting & Optimal Setpoint",
                "narrative": (
                    f"Multivariate SARIMAX model (AIC: {forecast.aic}, MAPE: {forecast.mape_backtest_pct}%) predicts a line-pack deficit "
                    f"at Chhainsa station starting at Hour {forecast.pressure_deficit_hour_ahead} ahead, driven by customer nomination surges "
                    f"(+25% fertilizer off-take) and ambient heat (41.9 °C). "
                    f"Recommended Action: Increase Vijaipur Compressor Hub throughput by +{sp.throughput_adjustment_pct}% at {sp.action_hour[-8:-3]} hrs. "
                    f"Saves {int(sp.fuel_gas_savings_scm_day):,} SCM/day of fuel gas (~₹{sp.project_sanchay_daily_savings_inr/100000:.2f} Lakhs/day), "
                    f"accelerating GAIL's Project Sanchay (₹{sp.annualized_sanchay_inr_crores} Cr/yr NPV target)."
                ),
                "data": forecast.model_dump(),
                "a2ui_card": forecast.a2ui_forecast_chart
            }
            
        # ACT 5: RISE with SAP S/4HANA Work Order
        elif "sap" in p_lower or "work order" in p_lower or "navodaya" in p_lower or "stage" in p_lower:
            wo_req = SapWorkOrderRequest(
                description="Project Navodaya Preemptive Calibration: Unit GT-01 +3.8% Setpoint Increase",
                action_hour="14:00"
            )
            order_res = stage_sap_maintenance_order(wo_req)
            return {
                "act": "ACT 5: Closed-Loop SAP S/4HANA Action",
                "narrative": (
                    f"Successfully created SAP S/4HANA Work Order {order_res.work_order_id} for {order_res.equipment_id} "
                    f"under Project Navodaya. Setpoint adjustment calibrated for +3.8% throughput to optimize fuel gas burn. "
                    f"Work order staged with High Priority (2) under Project Navodaya at Plant 1102 (Vijaipur). Zero human data entry delay."
                ),
                "data": order_res.model_dump(),
                "a2ui_card": {
                    "a2ui_version": "v0.9",
                    "card_type": "ERP_WORK_ORDER_STATUS",
                    "title": f"RISE with SAP S/4HANA Cloud · {order_res.work_order_id}",
                    "status": "STAGED",
                    "equipment": order_res.equipment_id,
                    "plant": order_res.execution_plant,
                    "target_time": order_res.scheduled_action_time,
                    "audit_hash": order_res.audit_hash
                }
            }
            
        # ACT 5.5: GAIL AI Tarang Enterprise Q&A
        else:
            q_res = query_enterprise_knowledge(user_prompt)
            return {
                "act": "ACT 5: GAIL AI Tarang Natural Language Query",
                "narrative": q_res.answer,
                "data": q_res.model_dump()
            }
