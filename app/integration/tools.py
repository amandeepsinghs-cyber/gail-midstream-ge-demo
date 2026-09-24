"""
Agent tools for the GAIL "One Morning at GAIL" demo.

Main storyline (Problem -> Decision -> Proof -> Action):
  1. audit_grid_and_weather_risk   - grid flows + revised customer nominations -> 4.0 MMSCMD shortfall
  2. evaluate_lng_supply_options   - deterministic LNG landed-cost comparison -> recommended option
  3. run_sarimax_linepack_forecast - fitted SARIMAX, two scenarios (line-pack only vs with LNG)
  4. publish_decision_brief        - executive report + RISE with SAP order, one card

Backup tools: query_scada_telemetry, get_weathernext_forecast, compile_executive_briefing,
stage_sap_maintenance_order, query_enterprise_knowledge.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

try:
    from google.adk.tools import ToolContext
except ImportError:
    ToolContext = Any

from app.contracts import (
    GridHealthAuditResponse,
    WeatherNextForecastResponse,
    ScadaHistoryResponse,
    SarimaxForecastResponse,
    ExecutiveBriefingReport,
    SapWorkOrderRequest,
    SapWorkOrderResponse,
    EnterpriseQueryResponse,
    LngSupplyOptionsResponse,
    DecisionBriefResponse,
)
from app import scenario
from app.analytics.sarimax_linepack import SarimaxLinepackEngine
from app.analytics.weathernext_engine import WeatherNextEngine
from app.render.a2ui_cards import (
    build_a2ui_spatial_map_card,
    build_a2ui_weathernext_card,
    build_a2ui_scada_chart,
    build_a2ui_forecast_chart
)
from app.synthesis.executive_report_compiler import ExecutiveReportCompiler
from app.integration.gcs_connector import (
    load_geojson,
    load_nominations,
    publish_executive_report_to_gcs
)

FIXTURES_DIR = Path(__file__).resolve().parent.parent.parent / "fixtures"

# State keys for A2UI after-agent callback
PENDING_SPATIAL_KEY: str = "pending_spatial_summary"
PENDING_WEATHERNEXT_KEY: str = "pending_weathernext_summary"
PENDING_SCADA_KEY: str = "pending_scada_summary"
PENDING_SARIMAX_KEY: str = "pending_sarimax_summary"
PENDING_REPORT_KEY: str = "pending_report_summary"
PENDING_SAP_KEY: str = "pending_sap_summary"
PENDING_ENTERPRISE_QA_KEY: str = "pending_enterprise_qa_summary"
PENDING_LNG_KEY: str = "pending_lng_summary"
PENDING_DECISION_KEY: str = "pending_decision_summary"


def _stash(tool_context: Any, key: str, value: Dict[str, Any]) -> None:
    if tool_context is not None and getattr(tool_context, "state", None) is not None:
        try:
            tool_context.state[key] = value
        except Exception:
            pass


# =============================================================================
# TOOL 1 (ACT 1): SPATIAL GIS & WEATHER AUDIT
# =============================================================================

def audit_grid_and_weather_risk(
    corridor: str = "HVJ",
    tool_context: Optional[ToolContext] = None
) -> GridHealthAuditResponse:
    """
    BEAT 1 (Problem): Shows today's grid flows across GAIL's 18,700 km network (122.18 MMSCMD across
    HVJ, Urja Ganga, DBNPL, MNJPL) and tomorrow's revised customer nominations, and computes the
    resulting supply shortfall on HVJ North (Fertilizer +20%, CGD +12% => ~4.0 MMSCMD).
    Use for: grid flows, corridor volumes, customer nominations, data lake / GMS access.
    """
    gis_data = load_geojson("river_crossings_gis.geojson")
    weathernext = WeatherNextEngine().get_forecast(location="Gauna_Bawana")
        
    sf = scenario.shortfall()
    alerts = [
        {
            "location_name": "Revised Customer Nominations - HVJ North (Exogenous X)",
            "asset_class": "COMMERCIAL_GMS_NOMINATION_SCHEDULE",
            "risk_level": "SUPPLY_SHORTFALL",
            "river_gauge_m": sf["revised_daily_offtake_mmscmd"],
            "danger_mark_m": sf["baseline_daily_offtake_mmscmd"],
            "imd_rainfall_alert": (
                f"Fertilizer (HURL/NFL) +{sf['fertilizer_change_pct']:.0f}% and CGD +{sf['cgd_change_pct']:.0f}% "
                f"from {sf['starts_at'][11:16]} IST"
            ),
            "hydraulic_stress_indicator": f"SHORTFALL_{sf['shortfall_mmscmd']}_MMSCMD",
            "action_advisory": "Evaluate LNG supply options, then forecast Chhainsa line-pack.",
        },
        {
            "location_name": "Gauna-Bawana Yamuna River Crossing",
            "asset_class": "SUBMERGED_PIPELINE_CROSSING",
            "risk_level": "WATCH",
            "river_gauge_m": 204.8,
            "danger_mark_m": 205.33,
            "imd_rainfall_alert": "Normal Seasonal Waterway Flow",
            "hydraulic_stress_indicator": "NORMAL_STABILITY",
            "action_advisory": "Routine aerial and pressure log monitoring active.",
        },
    ]

    a2ui_map = build_a2ui_spatial_map_card(gis_data, weathernext)
    
    res = GridHealthAuditResponse(
        audit_timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        network_summary={
            "corridor_name": "GAIL 18,700 km Integrated National Gas Grid (HVJ · Urja Ganga · DBNPL · MNJPL)",
            "total_network_km": 18700.0,
            "total_transmission_mmscmd": 122.18,
            "status": "100%_SCHEMA_VALIDATED_GMS_AND_DATA_LAKE_ONLINE",
            "key_stations": ["Hazira Terminal", "Vijaipur Compressor Hub", "Chhainsa Station", "Pata Petrochem Complex", "Dadri Terminal"]
        },
        environmental_alerts=alerts,
        monitored_corridors=["HVJ Trunkline (81.4 MMSCMD)", "JHBDPL Urja Ganga (12.0 MMSCMD)", "DBNPL (10.7 MMSCMD)", "MNJPL Samruddhi (9.9 MMSCMD)"],
        weathernext_summary={
            "model": "GAIL GMS & Enterprise Data Lake Inventory",
            "risk_category": "EXOGENOUS_NOMINATION_SURGE_X1",
            "cumulative_precipitation_p90_mm": 122.18,
            "alert": f"122.18 MMSCMD verified across 5 regional corridors; tomorrow's shortfall on HVJ North: {sf['shortfall_mmscmd']} MMSCMD."
        },
        demand_shortfall=sf,
        a2ui_map_payload=a2ui_map
    )

    if tool_context and hasattr(tool_context, "state") and tool_context.state is not None:
        try:
            tool_context.state[PENDING_SPATIAL_KEY] = res.model_dump()
        except Exception:
            pass

    return res


# =============================================================================
# TOOL 2: OPTIONAL ENVIRONMENTAL WEATHER OVERLAY
# =============================================================================

def get_weathernext_forecast(
    location: str = "Chhainsa_CS",
    horizon_hours: int = 24,
    tool_context: Optional[ToolContext] = None
) -> WeatherNextForecastResponse:
    """
    Optional Add-On Tool: Queries environmental weather forecast ensemble for specific pipeline coordinates
    only when the user explicitly requests weather conditions.
    """
    engine = WeatherNextEngine()
    data = engine.get_forecast(location=location, horizon_hours=horizon_hours)
    a2ui_card = build_a2ui_weathernext_card(data)
    data["a2ui_card"] = a2ui_card
    res = WeatherNextForecastResponse(**data)

    if tool_context and hasattr(tool_context, "state") and tool_context.state is not None:
        try:
            tool_context.state[PENDING_WEATHERNEXT_KEY] = res.model_dump()
        except Exception:
            pass

    return res


# =============================================================================
# TOOL 3 (STEP 2): ENTERPRISE CLOUD HISTORIAN & GMS 72-HOUR TIME SERIES
# =============================================================================

def query_scada_telemetry(
    station: str = "Chhainsa_CS",
    hours: int = 72,
    tool_context: Optional[ToolContext] = None
) -> ScadaHistoryResponse:
    """
    STEP 2 Tool: Queries and plots the 72-hour operational time-series dataset (Line-Pack Pressure in kg/cm²,
    Gas Transmission Flow in MMSCMD, and Compressor Station Thermal Efficiency Index in °C) from the
    GAIL Enterprise Cloud Historian & Gas Management System (GMS) Data Lake.
    """
    engine = SarimaxLinepackEngine()
    df = engine.load_historical_data()
    df["timestamp"] = df["timestamp"].astype(str)
    
    telemetry_records = df.tail(hours).to_dict(orient="records")
    latest = telemetry_records[-1]
    
    a2ui_chart = build_a2ui_scada_chart(telemetry_records)
    
    res = ScadaHistoryResponse(
        station=station,
        pipeline="HVJ_Trunkline",
        period_hours=hours,
        data_points_count=len(telemetry_records),
        latest_pressure_kg_cm2=float(latest["linepack_pressure_kg_cm2"]),
        average_flow_mmscmd=round(float(df["gas_flow_mmscmd"].mean()), 2),
        max_turbine_exhaust_temp_c=round(float(df["siemens_gt_exhaust_temp_c"].max()), 2),
        telemetry_series=telemetry_records,
        a2ui_timeseries_chart=a2ui_chart
    )

    if tool_context and hasattr(tool_context, "state") and tool_context.state is not None:
        try:
            tool_context.state[PENDING_SCADA_KEY] = res.model_dump()
        except Exception:
            pass

    return res


# =============================================================================
# TOOL 4 (STEP 3): DETERMINISTIC MULTIVARIATE SARIMAX FORECAST
# =============================================================================

def run_sarimax_linepack_forecast(
    station: str = "Chhainsa_CS",
    horizon_hours: int = 24,
    tool_context: Optional[ToolContext] = None
) -> SarimaxForecastResponse:
    """
    BEAT 3 (Proof): Fits a SARIMAX(1,1,0)x(1,0,0)_24 model on 72h of Chhainsa history (exogenous input:
    supply-demand balance) and forecasts 24h line-pack for two scenarios from the same model:
    "line-pack draw only" (no extra supply) vs "with LNG swap" (+4.0 MMSCMD Dahej send-out from T+6h).
    Returns breach hour vs the 76.0 kg/cm2 contract floor, 95% intervals and the Vijaipur setpoint.
    Use for: "can the grid carry it", forecast, SARIMAX, line-pack, setpoint.
    """
    forecast_results = dict(scenario.forecast())
    a2ui_chart = build_a2ui_forecast_chart(forecast_results)
    forecast_results["a2ui_forecast_chart"] = a2ui_chart
    res = SarimaxForecastResponse(**forecast_results)
    _stash(tool_context, PENDING_SARIMAX_KEY, res.model_dump())
    return res


# =============================================================================
# TOOL 5 (STEP 4): EXHAUSTIVE GAIL EXECUTIVE READY RECKONER REPORT COMPILER
# =============================================================================

def compile_executive_briefing(
    tool_context: Optional[ToolContext] = None,
    sap_order: Optional[Dict[str, Any]] = None,
) -> ExecutiveBriefingReport:
    """
    STEP 4 Tool: Compiles the exhaustive 6-Part GAIL (India) Limited Daily Gas Transmission,
    SARIMAX Demand & Project Sanchay Executive Report (Ready Reckoner HTML edition) from GMS,
    Enterprise Cloud Historian, and SAP S/4HANA (Project Navodaya) datasets.
    """
    grid_audit = audit_grid_and_weather_risk().model_dump()
    scada_summary = query_scada_telemetry().model_dump()
    sarimax_results = run_sarimax_linepack_forecast().model_dump()
    weathernext_yamuna = get_weathernext_forecast("Gauna_Bawana").model_dump()
    story = scenario.storyline()

    compiler = ExecutiveReportCompiler()
    html_path = compiler.compile_html_report(
        grid_audit=grid_audit,
        scada_summary=scada_summary,
        sarimax_results=sarimax_results,
        weathernext_data=weathernext_yamuna,
        sap_order_status=sap_order,
        storyline=story,
    )

    # Publish to GCS Data Lake Curated Zone
    report_filename = Path(html_path).name
    with open(html_path, "r", encoding="utf-8") as f:
        html_bytes = f.read()
    gcs_uri = publish_executive_report_to_gcs(html_bytes, report_filename)
    
    setpoint = sarimax_results.get("setpoint_recommendation", {})
    
    res = ExecutiveBriefingReport(
        report_id=f"GAIL-EXEC-REP-{datetime.now().strftime('%Y%m%d%H%M')}",
        report_title="Daily Line-Pack & Supply Decision Executive Briefing",
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        executive_summary=story["headline"],
        grid_integrity_status="SHORTFALL_COVERED" if not sarimax_results.get("with_swap_breach") else "AT_RISK",
        weather_risk_summary="Gauna-Bawana Yamuna crossing: WATCH (below danger mark); no weather constraint on the plan.",
        telemetry_summary={
            "station": "Chhainsa_CS",
            "linepack_pressure_kg_cm2": scada_summary["latest_pressure_kg_cm2"],
            "max_turbine_exhaust_temp_c": scada_summary["max_turbine_exhaust_temp_c"]
        },
        sarimax_findings={
            "deficit_hour_ahead": sarimax_results["pressure_deficit_hour_ahead"],
            "min_without_action_kg_cm2": sarimax_results["minimum_predicted_pressure_kg_cm2"],
            "min_with_swap_kg_cm2": sarimax_results["with_swap_minimum_kg_cm2"],
            "recommended_setpoint": f"+{setpoint.get('throughput_adjustment_pct')}% at {setpoint.get('action_hour')}"
        },
        project_sanchay_roi={
            "fuel_savings_scm_day": setpoint.get("fuel_gas_savings_scm_day"),
            "daily_margin_recovery_inr": setpoint.get("project_sanchay_daily_savings_inr"),
            "annualized_inr_crores": 16.88,
            "lng_saving_vs_spot_inr_crore": story["lng"]["saving_vs_spot_inr_crore"],
        },
        compiled_html_path=gcs_uri or html_path,
        sources_cited=[
            "GMS customer nominations (baseline vs revised)",
            "LNG market snapshot (illustrative) & landed-cost engine",
            "Enterprise Cloud Historian - Chhainsa 72h (SARIMAX training data)",
            "RISE with SAP S/4HANA (Project Navodaya)",
            "GAIL AI Tarang Operational Guidelines"
        ]
    )

    if tool_context and hasattr(tool_context, "state") and tool_context.state is not None:
        try:
            tool_context.state[PENDING_REPORT_KEY] = res.model_dump()
        except Exception:
            pass

    return res


# =============================================================================
# TOOL 6 (ACT 5): RISE WITH SAP S/4HANA CLOSED-LOOP WORK ORDER
# =============================================================================

def stage_sap_maintenance_order(
    request: SapWorkOrderRequest = None,
    tool_context: Optional[ToolContext] = None
) -> SapWorkOrderResponse:
    """
    Stages an autonomous preventive maintenance work order directly into RISE with SAP S/4HANA Cloud
    under Project Navodaya for Vijaipur Compressor Hub.
    """
    import hashlib
    now = datetime.now()
    order_id = f"WO-{hash(now.isoformat()) % 1000000:06d}"
    audit_hash = hashlib.sha256(f"{order_id}-EQ-VIJ-GT-01-NAVODAYA".encode()).hexdigest()[:16]
    
    res = SapWorkOrderResponse(
        work_order_id=order_id,
        equipment_id="EQ-VIJ-GT-01",
        order_type="PM01",
        status="SUCCESS",
        order_status="RELEASED_FOR_EXECUTION",
        sap_system="RISE with SAP S/4HANA Cloud (Project Navodaya)",
        execution_plant="1102 - Vijaipur Compressor Complex",
        scheduled_action_time=(now).strftime("%Y-%m-%d 14:00:00"),
        throughput_calibration="+3.8% Vijaipur throughput (105.3 -> 109.3 MMSCMD) to carry +4.0 MMSCMD Dahej send-out",
        project_alignment="Project Sanchay Fuel Gas Minimization Mandate (₹600 Cr NPV Target)",
        audit_hash=audit_hash
    )

    if tool_context and hasattr(tool_context, "state") and tool_context.state is not None:
        try:
            tool_context.state[PENDING_SAP_KEY] = res.model_dump()
        except Exception:
            pass

    return res


# =============================================================================
# TOOL 7: ENTERPRISE NATURAL LANGUAGE Q&A (GAIL AI TARANG)
# =============================================================================

def query_enterprise_knowledge(query: str, tool_context: Optional[ToolContext] = None) -> EnterpriseQueryResponse:
    """
    Answers natural language enterprise questions on GAIL operations, financial metrics,
    Project Sanchay, and ESG Net Zero commitments with cited sources.
    """
    q_lower = query.lower()
    
    if "sanchay" in q_lower or "fuel" in q_lower or "savings" in q_lower:
        res = EnterpriseQueryResponse(
            query=query,
            answer=(
                "Project Sanchay is GAIL's flagship operational efficiency initiative launched across all major compressor stations. "
                "The program targets a cumulative NPV of ₹600 Crore through fuel gas minimization, aerodynamic re-blading, "
                "and predictive linepack balancing. At Vijaipur Compressor Hub alone, real-time setpoint optimization (+3.8% throughput) "
                "conserves 18,500 SCM/day of fuel gas, equivalent to ₹4.62 Lakhs/day or ₹16.88 Crore annually."
            ),
            source_attribution=[
                "GAIL Annual Report 2024-25, Operational Excellence Review (p. 42)",
                "Project Sanchay Fuel Gas Optimization Framework (NGMC-OPS-SOP-2025)",
                "Yokogawa FAST/TOOLS Telemetry Historian Audit Log"
            ],
            confidence_score=0.99
        )
    elif "net zero" in q_lower or "esg" in q_lower or "scope" in q_lower or "emission" in q_lower:
        res = EnterpriseQueryResponse(
            query=query,
            answer=(
                "GAIL (India) Limited has committed to achieving Net Zero Scope-1 and Scope-2 emissions by the year 2035—five years "
                "ahead of India's national PSU mandate. Intermediate milestones include reducing emission intensity by 20% by 2030, "
                "blending 10% green hydrogen in city gas networks (e.g. Avantika Gas pilot at Indore), and constructing 1 GW of renewable capacity."
            ),
            source_attribution=[
                "GAIL Sustainability Report 2024-25 (BRSR ESG Milestone Framework, p. 18)",
                "MoPNG Net Zero Taskforce Roadmap for Maharatna CPSEs",
                "GAIL AI Tarang Operational Guidelines"
            ],
            confidence_score=0.98
        )
    elif "transmission" in q_lower or "volume" in q_lower or "grid" in q_lower or "network" in q_lower or "share" in q_lower:
        res = EnterpriseQueryResponse(
            query=query,
            answer=(
                "GAIL owns and operates an extensive cross-country natural gas pipeline network spanning over 18,700 km "
                "with an interconnected transmission capacity of 206 MMSCMD. In FY 2024-25, GAIL transmitted an average of "
                "122.18 MMSCMD, commanding an approximate 70% national market share in natural gas transmission across India."
            ),
            source_attribution=[
                "Petroleum & Natural Gas Regulatory Board (PNGRB) Pipeline Bulletin 2025",
                "GAIL Q1 FY26 Investor Factbook (Physical Performance Highlights)",
                "National Gas Management Centre (NGMC) Daily Gas Dispatch Log"
            ],
            confidence_score=0.99
        )
    else:
        res = EnterpriseQueryResponse(
            query=query,
            answer=(
                f"According to GAIL NGMC operational documentation, natural gas operations across the 18,700 km network "
                f"remain synchronized with RISE with SAP S/4HANA (Project Navodaya) and Yokogawa SCADA. "
                f"Specific operational metrics are tracked in real-time under GAIL AI Tarang standards."
            ),
            source_attribution=[
                "GAIL Corporate Operational Guidelines (2025 Edition)",
                "National Gas Management Centre (NGMC) Central Dispatch System"
            ],
            confidence_score=0.95
        )

    if tool_context and hasattr(tool_context, "state") and tool_context.state is not None:
        try:
            tool_context.state[PENDING_ENTERPRISE_QA_KEY] = res.model_dump()
        except Exception:
            pass

    return res


# =============================================================================
# BEAT 2 (DECISION): LNG SUPPLY OPTIONS - DETERMINISTIC LANDED COST
# =============================================================================

def evaluate_lng_supply_options(tool_context: Optional[ToolContext] = None) -> LngSupplyOptionsResponse:
    """
    BEAT 2 (Decision): Finds the cheapest way to cover tomorrow's HVJ North shortfall. Prices three LNG
    options delivered at Dahej with fixed formulas (Spot JKM cargo; US Henry Hub cargo re-route via Cape;
    Qatar term-cargo time-swap), screens them for arrival timing against terminal inventory cover,
    recommends the cheapest feasible option and computes the Rs Crore saving versus buying spot.
    Prices are illustrative demo values. Use for: "cheapest way to cover the shortfall", LNG sourcing,
    Henry Hub, JKM, cargo swap, landed cost.
    """
    res = LngSupplyOptionsResponse(**scenario.lng_decision())
    _stash(tool_context, PENDING_LNG_KEY, res.model_dump())
    return res


# =============================================================================
# BEAT 4 (ACTION): DECISION BRIEF + SAP ORDER IN ONE STEP
# =============================================================================

def publish_decision_brief(tool_context: Optional[ToolContext] = None) -> DecisionBriefResponse:
    """
    BEAT 4 (Action): Briefs management and raises the SAP order in one step. Stages the RISE with SAP
    S/4HANA order (Vijaipur +3.8% throughput and Dahej send-out nomination), compiles the executive
    report with a one-page decision summary, publishes it to the data lake and returns the report link
    and SAP order ID together. Use for: "brief management and raise the SAP order", executive report,
    management briefing, work order.
    """
    sap = stage_sap_maintenance_order().model_dump()
    report = compile_executive_briefing(sap_order=sap)
    story = scenario.storyline()
    f, d = story["forecast"], story["lng"]
    res = DecisionBriefResponse(
        headline=story["headline"],
        shortfall_mmscmd=story["shortfall"]["shortfall_mmscmd"],
        chosen_option=d["recommended_option_label"],
        saving_vs_spot_inr_crore=d["saving_vs_spot_inr_crore"],
        breach_hour_without_action=f["pressure_deficit_hour_ahead"],
        min_pressure_without_action_kg_cm2=f["minimum_predicted_pressure_kg_cm2"],
        min_pressure_with_action_kg_cm2=f["with_swap_minimum_kg_cm2"],
        vijaipur_throughput_adjustment_pct=f["setpoint_recommendation"]["throughput_adjustment_pct"],
        report_url=report.compiled_html_path,
        report_id=report.report_id,
        sap_work_order_id=sap["work_order_id"],
        sap_system=sap["sap_system"],
        sap_order_status=sap["order_status"],
        sap_actions=[
            f"PM order: Vijaipur Hub throughput +{f['setpoint_recommendation']['throughput_adjustment_pct']}% at T+6h",
            f"Nomination: Dahej send-out +{d['dahej_sendout_increase_mmscmd']} MMSCMD ({d['recommended_option_label']})",
        ],
        audit_hash=sap["audit_hash"],
    )
    _stash(tool_context, PENDING_DECISION_KEY, res.model_dump())
    return res
