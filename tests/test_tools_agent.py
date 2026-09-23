"""Test concrete agent tools and multi-act prompt execution."""

from app.integration.tools import (
    audit_grid_and_weather_risk,
    query_scada_telemetry,
    run_sarimax_linepack_forecast,
    compile_executive_briefing,
    stage_sap_maintenance_order,
    query_enterprise_knowledge
)
from app.contracts import SapWorkOrderRequest
from app.agent import GailPipelineAgent

def test_tool_act1_grid_audit():
    res = audit_grid_and_weather_risk()
    assert res.network_summary.total_network_km == 18700.0
    assert len(res.environmental_alerts) >= 1
    assert "Gauna-Bawana" in res.environmental_alerts[0].location_name
    assert "a2ui_version" in res.a2ui_map_payload

def test_tool_act2_scada():
    res = query_scada_telemetry("Chhainsa_CS", 72)
    assert res.station == "Chhainsa_CS"
    assert res.data_points_count == 72
    assert res.latest_pressure_kg_cm2 > 70.0
    assert res.max_turbine_exhaust_temp_c > 500.0

def test_tool_act3_sarimax():
    res = run_sarimax_linepack_forecast("Chhainsa_CS", 24)
    assert res.setpoint_recommendation.fuel_gas_savings_scm_day == 18500.0
    assert res.setpoint_recommendation.throughput_adjustment_pct == 3.8
    assert res.a2ui_forecast_chart["card_type"] == "SARIMAX_PREDICTIVE_ADVISORY"

def test_tool_act4_executive_report():
    report = compile_executive_briefing()
    assert "Daily Line-Pack" in report.report_title
    assert report.compiled_html_path.endswith(".html")
    assert report.project_sanchay_roi["annualized_inr_crores"] == 16.88

def test_tool_act5_sap_order():
    req = SapWorkOrderRequest(
        station="Vijaipur",
        equipment_id="EQ-VIJ-GT-01",
        description="Setpoint Calibration",
        fuel_saving_justification="18,500 SCM/day fuel gas"
    )
    res = stage_sap_maintenance_order(req)
    assert res.status == "SUCCESS"
    assert "WO-" in res.sap_work_order_id
    assert res.order_status == "RELEASED_FOR_EXECUTION"

def test_tool_act5_enterprise_qa():
    res = query_enterprise_knowledge("What is our Net Zero Scope-1 target timeline?")
    assert "2035" in res.answer
    assert "BRSR" in str(res.cited_sources)

def test_agent_orchestrator_all_acts():
    agent = GailPipelineAgent()
    
    # Act 1
    r1 = agent.execute_prompt("Gemini, initialize a grid health and risk audit across HVJ")
    assert "ACT 1" in r1["act"]
    assert "Gauna-Bawana" in r1["narrative"]
    
    # Act 2
    r2 = agent.execute_prompt("Access live telemetry for Chhainsa Compressor Station")
    assert "ACT 2" in r2["act"]
    assert "Yokogawa" in r2["narrative"]
    
    # Act 3
    r3 = agent.execute_prompt("Execute a 24-hour predictive SARIMAX demand forecast for Chhainsa")
    assert "ACT 3" in r3["act"]
    assert "+3.8%" in r3["narrative"]
    
    # Act 4
    r4 = agent.execute_prompt("Compile this grid audit and SARIMAX forecast into an official Executive Briefing")
    assert "ACT 4" in r4["act"]
    assert "compiled_html_path" in r4["data"]
    
    # Act 5: SAP
    r5 = agent.execute_prompt("Stage a preventive work order directly into RISE with SAP S/4HANA Cloud")
    assert "ACT 5: Closed-Loop SAP" in r5["act"]
    
    # Act 5: Q&A
    r6 = agent.execute_prompt("What was our total natural gas transmission volume last fiscal year?")
    assert "ACT 5: GAIL AI Tarang" in r6["act"]
    assert "122.18 MMSCMD" in r6["narrative"]
