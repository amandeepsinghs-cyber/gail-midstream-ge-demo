"""
Pydantic contracts and data schemas for the GAIL Autonomous Pipeline Grid Agent.
Strict typing across all 5 Acts:
  Act 1: GIS Spatial Infrastructure & IMD Weather Risk
  Act 2: SCADA & Siemens RDS Telemetry
  Act 3: SARIMAX Demand Forecasting & Setpoint Recommendation
  Act 4: Multi-Source Executive Briefing Compilation
  Act 5: RISE with SAP S/4HANA Closed-Loop Work Order
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


# =============================================================================
# ACT 1: GIS SPATIAL & WEATHER SCHEMAS
# =============================================================================

class PipelineCorridorInfo(BaseModel):
    corridor_name: str = Field(..., description="Name of the pipeline network (e.g. HVJ Trunkline)")
    total_network_km: float = Field(default=18700.0, description="Total pipeline network length in km")
    status: str = Field(default="OPERATIONAL", description="Overall corridor operational state")
    key_stations: List[str] = Field(default_factory=list, description="Critical compressor hubs and delivery stations")


class EnvironmentalRiskAlert(BaseModel):
    location_name: str = Field(..., description="Name of critical asset or river crossing")
    asset_class: str = Field(..., description="E.g. SUBMERGED_PIPELINE_CROSSING")
    risk_level: str = Field(..., description="CRITICAL, HIGH, MODERATE, or LOW")
    river_gauge_m: Optional[float] = Field(None, description="Current river water level in meters")
    danger_mark_m: Optional[float] = Field(None, description="Design danger water level in meters")
    imd_rainfall_alert: str = Field(..., description="IMD meteorological rainfall status")
    hydraulic_stress_indicator: str = Field(..., description="SCADA acoustic/vibration stress level")
    action_advisory: str = Field(..., description="Recommended engineering mitigation")


class GridHealthAuditResponse(BaseModel):
    audit_timestamp: str
    network_summary: PipelineCorridorInfo
    environmental_alerts: List[EnvironmentalRiskAlert]
    monitored_corridors: List[str]
    a2ui_map_payload: Dict[str, Any]


# =============================================================================
# ACT 2: SCADA & SIEMENS RDS TELEMETRY SCHEMAS
# =============================================================================

class ScadaTelemetryPoint(BaseModel):
    timestamp: str
    hours_from_start: int
    station: str
    pipeline: str
    linepack_pressure_kg_cm2: float
    gas_flow_mmscmd: float
    ambient_temp_c: float
    siemens_gt_exhaust_temp_c: float


class ScadaHistoryResponse(BaseModel):
    station: str
    pipeline: str
    period_hours: int
    data_points_count: int
    latest_pressure_kg_cm2: float
    average_flow_mmscmd: float
    max_turbine_exhaust_temp_c: float
    telemetry_series: List[ScadaTelemetryPoint]
    a2ui_timeseries_chart: Dict[str, Any]


# =============================================================================
# ACT 3: SARIMAX DEMAND FORECAST & SETPOINT OPTIMIZATION SCHEMAS
# =============================================================================

class ForecastHour(BaseModel):
    hour_ahead: int
    timestamp: str
    predicted_linepack_kg_cm2: float
    lower_ci_95: float
    upper_ci_95: float
    scheduled_offtake_mmscmd: float
    ambient_temp_c: float
    deficit_detected: bool


class SetpointRecommendation(BaseModel):
    target_station: str = "Vijaipur_Compressor_Hub"
    throughput_adjustment_pct: float = Field(default=3.8, description="Recommended adjustment to compressor output")
    action_hour: str = Field(default="14:00 hrs", description="Execution time trigger")
    expected_linepack_stabilization_kg_cm2: float = 78.5
    fuel_gas_savings_scm_day: float = 18500.0
    project_sanchay_daily_savings_inr: float = 462500.0  # Approx Rs 4.62 Lakhs/day (~Rs 16.8 Cr/yr per hub)
    rationale: str


class SarimaxForecastResponse(BaseModel):
    forecast_generated_at: str
    target_station: str
    horizon_hours: int
    model_aic: float
    pressure_deficit_hour_ahead: Optional[int]
    minimum_predicted_pressure_kg_cm2: float
    setpoint_recommendation: SetpointRecommendation
    hourly_forecast: List[ForecastHour]
    a2ui_forecast_chart: Dict[str, Any]


# =============================================================================
# ACT 4: EXECUTIVE REPORT COMPILATION SCHEMAS
# =============================================================================

class ExecutiveBriefingReport(BaseModel):
    report_id: str
    report_title: str
    generated_at: str
    executive_summary: str
    grid_integrity_status: str
    weather_risk_summary: str
    telemetry_summary: Dict[str, Any]
    sarimax_findings: Dict[str, Any]
    project_sanchay_roi: Dict[str, Any]
    compiled_html_path: str
    compiled_pdf_path: Optional[str] = None
    sources_cited: List[str]


# =============================================================================
# ACT 5: RISE WITH SAP S/4HANA CLOSED-LOOP WORK ORDER SCHEMAS
# =============================================================================

class SapWorkOrderRequest(BaseModel):
    station: str = "Vijaipur Compressor Hub"
    maintenance_type: str = "PM01 - Preventive Maintenance / Setpoint Calibration"
    equipment_id: str = "EQ-VIJ-GT-01"
    work_center: str = "MECH-COMP-01"
    priority: str = "2 - High"
    description: str
    fuel_saving_justification: str


class SapWorkOrderResponse(BaseModel):
    status: str = "SUCCESS"
    sap_notification_id: str
    sap_work_order_id: str
    system_target: str = "RISE with SAP S/4HANA Cloud (Project Navodaya)"
    created_timestamp: str
    maintenance_plant: str
    order_status: str = "RELEASED_FOR_EXECUTION"
    assigned_work_center: str
    estimated_roi_project_sanchay_annual_inr: str
    confirmation_message: str


# =============================================================================
# ACT 5: NATURAL LANGUAGE ENTERPRISE Q&A SCHEMAS
# =============================================================================

class EnterpriseQueryRequest(BaseModel):
    query: str


class EnterpriseQueryResponse(BaseModel):
    query: str
    answer: str
    cited_sources: List[str]
    gail_ai_tarang_badge: str = "GAIL AI Tarang Verified Enterprise Insight"
