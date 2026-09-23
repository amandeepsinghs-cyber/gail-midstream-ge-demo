"""
Google ADK Agent Definition: GAIL Autonomous Pipeline Grid & Executive Advisory Agent.
Orchestrates the 5-Act demonstration on stage:
  Act 1: Spatial GIS & Weather Overlay (audit_grid_and_weather_risk)
  Act 2: SCADA & Siemens RDS Telemetry Ingestion (query_scada_telemetry)
  Act 3: Deterministic SARIMAX Forecasting (run_sarimax_linepack_forecast)
  Act 4: Multi-Source Executive Briefing Compilation (compile_executive_briefing)
  Act 5: Closed-Loop SAP S/4HANA Action (stage_sap_maintenance_order) & Enterprise Q&A
"""

from typing import Dict, Any, List
from app.integration.tools import (
    audit_grid_and_weather_risk,
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
Indian Meteorological Department (IMD) environmental radar, and RISE with SAP S/4HANA Cloud (Project Navodaya).

Your mission across the 5 demonstration acts:
1. Act 1 (Spatial GIS & Weather): Map the 18,700 km grid and flag river swell hazards (e.g. Gauna-Bawana Yamuna crossing).
2. Act 2 (SCADA Observability): Retrieve real-time 72h telemetry from Chhainsa station and Siemens gas turbines.
3. Act 3 (SARIMAX Analytics): Execute multivariate SARIMAX forecasting integrating customer nominations & ambient heatwaves,
   predict linepack depletion 14 hours ahead, and compute optimal compressor setpoints (+3.8% at Vijaipur) saving 18,500 SCM/day under Project Sanchay.
4. Act 4 (Executive Synthesis): Compile multi-source data into an official Daily Line-Pack & Grid Integrity Executive Briefing.
5. Act 5 (Closed-Loop SAP & AI Tarang): Stage preventive maintenance orders in RISE with SAP S/4HANA Cloud and answer audience queries with cited facts.

Always communicate with rigorous engineering authority, citing specific stations (Chhainsa, Vijaipur, Dadri),
physical units (kg/cm², MMSCMD, °C), and strategic programs (Project Sanchay, Project Navodaya, GAIL AI Tarang).
"""

class GailPipelineAgent:
    """Agent orchestrator for interactive command execution and API integration."""
    
    def __init__(self):
        self.system_prompt = GAIL_SYSTEM_INSTRUCTION
        self.available_tools = {
            "audit_grid_and_weather_risk": audit_grid_and_weather_risk,
            "query_scada_telemetry": query_scada_telemetry,
            "run_sarimax_linepack_forecast": run_sarimax_linepack_forecast,
            "compile_executive_briefing": compile_executive_briefing,
            "stage_sap_maintenance_order": stage_sap_maintenance_order,
            "query_enterprise_knowledge": query_enterprise_knowledge
        }

    def execute_prompt(self, user_prompt: str) -> Dict[str, Any]:
        """Routes conversational user prompts to appropriate tool execution and narrative responses."""
        p_lower = user_prompt.lower()
        
        # ACT 4: Executive PDF/HTML briefing report (checked first to avoid keyword collision with weather/sarimax)
        if "report" in p_lower or "briefing" in p_lower or "compile" in p_lower:
            report = compile_executive_briefing()
            return {
                "act": "ACT 4: Multi-Source Executive Briefing",
                "narrative": (
                    f"Synthesized data from Yokogawa SCADA, Siemens RDS, IMD radar, and Project Sanchay ROI. "
                    f"Official briefing compiled in 6 seconds: '{report.report_title}'. "
                    f"Output available at {report.compiled_html_path}."
                ),
                "data": report.model_dump(),
                "artifact_path": report.compiled_html_path
            }

        # ACT 1: Grid audit / GIS / weather
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

        # ACT 3: SARIMAX demand forecast / compressor setpoint
        elif "sarimax" in p_lower or "forecast" in p_lower or "setpoint" in p_lower or "demand" in p_lower:
            forecast = run_sarimax_linepack_forecast(station="Chhainsa_CS", horizon_hours=24)
            rec = forecast.setpoint_recommendation
            return {
                "act": "ACT 3: Deterministic SARIMAX Forecasting & Optimal Setpoint",
                "narrative": (
                    f"Multivariate SARIMAX model (AIC: {forecast.model_aic}) predicts a line-pack deficit "
                    f"at Chhainsa station starting at Hour {forecast.pressure_deficit_hour_ahead} ahead, "
                    f"driven by customer nomination surges (+25% fertilizer off-take) and ambient heat (41.9 °C). "
                    f"Recommended Action: Increase {rec.target_station} throughput by +{rec.throughput_adjustment_pct}% "
                    f"at {rec.action_hour}. Saves {rec.fuel_gas_savings_scm_day:,.0f} SCM/day of fuel gas (~₹4.62 Lakhs/day), "
                    f"accelerating GAIL's Project Sanchay (₹600 Cr NPV target)."
                ),
                "data": forecast.model_dump(),
                "a2ui_card": forecast.a2ui_forecast_chart
            }
            
        # ACT 5: SAP S/4HANA Work Order
        elif "sap" in p_lower or "work order" in p_lower or "navodaya" in p_lower:
            req = SapWorkOrderRequest(
                station="Vijaipur Compressor Hub",
                equipment_id="EQ-VIJ-GT-01",
                description="Calibrate Vijaipur compressor setpoints for +3.8% throughput to preempt downstream linepack deficit",
                fuel_saving_justification="Saves 18,500 SCM/day fuel gas under Project Sanchay"
            )
            order_res = stage_sap_maintenance_order(req)
            return {
                "act": "ACT 5: Closed-Loop SAP S/4HANA Action",
                "narrative": (
                    f"{order_res.confirmation_message} Work order staged with High Priority (2) "
                    f"under Project Navodaya at Plant 1102 (Vijaipur). Zero human data entry delay."
                ),
                "data": order_res.model_dump()
            }
            
        # ACT 5: Audience Q&A / GAIL AI Tarang
        else:
            q_res = query_enterprise_knowledge(user_prompt)
            return {
                "act": "ACT 5: GAIL AI Tarang Natural Language Query",
                "narrative": q_res.answer,
                "data": q_res.model_dump()
            }
