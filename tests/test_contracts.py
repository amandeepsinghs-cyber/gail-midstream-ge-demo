"""Test Pydantic schemas for GAIL Pipeline Agent."""

from app.contracts import (
    PipelineCorridorInfo,
    EnvironmentalRiskAlert,
    GridHealthAuditResponse,
    ScadaTelemetryPoint,
    ScadaHistoryResponse,
    SarimaxForecastResponse,
    SetpointRecommendation,
    ExecutiveBriefingReport,
    SapWorkOrderRequest,
    SapWorkOrderResponse,
    EnterpriseQueryResponse
)

def test_pipeline_corridor_contract():
    info = PipelineCorridorInfo(
        corridor_name="HVJ Trunkline",
        total_network_km=18700.0,
        status="OPERATIONAL",
        key_stations=["Vijaipur", "Chhainsa"]
    )
    assert info.total_network_km == 18700.0
    assert len(info.key_stations) == 2

def test_environmental_alert_contract():
    alert = EnvironmentalRiskAlert(
        location_name="Gauna-Bawana Yamuna Crossing",
        asset_class="SUBMERGED_PIPELINE_CROSSING",
        risk_level="CRITICAL",
        river_gauge_m=206.4,
        danger_mark_m=205.33,
        imd_rainfall_alert="HEAVY (115.6mm)",
        hydraulic_stress_indicator="ELEVATED",
        action_advisory="Deploy patrol"
    )
    assert alert.risk_level == "CRITICAL"
    assert alert.river_gauge_m > alert.danger_mark_m

def test_sap_work_order_contracts():
    req = SapWorkOrderRequest(
        station="Vijaipur",
        equipment_id="EQ-VIJ-GT-01",
        description="Setpoint adjustment",
        fuel_saving_justification="Project Sanchay"
    )
    assert req.priority == "2 - High"
