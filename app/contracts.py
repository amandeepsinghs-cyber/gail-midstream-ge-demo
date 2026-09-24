"""
Pydantic Data Contracts for GAIL Autonomous Pipeline Grid Agent.
Strict validation across all 5 demonstration acts, WeatherNext 3 models,
and A2UI v0.9 component specifications. Supports both v1.0 and v2.0 field aliases.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# =============================================================================
# A2UI FRONTEND MESSAGE CONTRACTS (GEMINI ENTERPRISE)
# =============================================================================

class A2uiCatalogVersion(str, Enum):
    """Gemini Enterprise A2UI catalog version."""
    V0_8 = "v0.8"   # Legacy Lit renderer
    V0_9 = "v0.9"   # Active Angular renderer (VegaChart, Canvas, Material 3)


ACTIVE_A2UI_CATALOG_VERSION: A2uiCatalogVersion = A2uiCatalogVersion.V0_9
A2UI_MIME_TYPE: str = "application/json+a2ui"
DEFAULT_GE_CATALOG_ID: str = (
    "https://www.gstatic.com/vertexaisearch/a2ui/v0_9/gemini_enterprise_composite_catalog.json"
)


class A2uiMessage(BaseModel):
    """A single protocol message emitted to the Gemini Enterprise A2UI surface.
    
    Each lifecycle message is serialized into an independent A2A DataPart envelope.
    """
    message_type: str                  # e.g. "createSurface", "updateComponents", "updateDataModel"
    surface_id: str                    # Unique surface identifier per conversation turn
    payload: Dict[str, Any]            # Version-specific message contents
    catalog_version: A2uiCatalogVersion = ACTIVE_A2UI_CATALOG_VERSION


# =============================================================================
# ACT 1 & WEATHER: SPATIAL GIS, IMD & WEATHERNEXT 3 CONTRACTS
# =============================================================================

class PipelineCorridorInfo(BaseModel):
    corridor_name: str
    total_network_km: float
    status: str
    key_stations: List[str]


class EnvironmentalRiskAlert(BaseModel):
    location_name: str
    asset_class: str
    risk_level: str
    river_gauge_m: float
    danger_mark_m: float
    imd_rainfall_alert: str
    hydraulic_stress_indicator: str
    action_advisory: str

# Backward compatibility alias
EnvironmentalAlert = EnvironmentalRiskAlert


class WeatherNextForecastResponse(BaseModel):
    model: str
    provider: str
    resolution: str
    ensemble_members: int
    location_name: str
    corridor: str
    coordinates: Dict[str, float]
    elevation_m: float
    generated_at: str
    risk_category: str
    alert_description: str
    action_protocol: str
    summary_metrics: Dict[str, Any]
    hourly_forecast: List[Dict[str, Any]]
    a2ui_card: Optional[Dict[str, Any]] = None


class GridHealthAuditResponse(BaseModel):
    audit_timestamp: str
    network_summary: PipelineCorridorInfo
    environmental_alerts: List[EnvironmentalRiskAlert]
    monitored_corridors: List[str]
    weathernext_summary: Optional[Dict[str, Any]] = None
    demand_shortfall: Optional[Dict[str, Any]] = None
    a2ui_map_payload: Dict[str, Any]


# =============================================================================
# ACT 2: SCADA & SIEMENS RDS TELEMETRY
# =============================================================================

class ScadaTelemetryPoint(BaseModel):
    timestamp: str
    linepack_pressure_kg_cm2: float
    gas_flow_mmscmd: float
    siemens_gt_exhaust_temp_c: float
    ambient_temp_c: float
    status: str


class ScadaHistoryResponse(BaseModel):
    station: str
    pipeline: str
    period_hours: int
    data_points_count: int
    latest_pressure_kg_cm2: float
    average_flow_mmscmd: float
    max_turbine_exhaust_temp_c: float
    telemetry_series: List[Dict[str, Any]]
    a2ui_timeseries_chart: Optional[Dict[str, Any]] = None


# =============================================================================
# ACT 3: PPAC-GRADE DETERMINISTIC SARIMAX DEMAND FORECAST
# =============================================================================

class SetpointRecommendation(BaseModel):
    source_station: str = "Vijaipur Compressor Hub"
    target_station: str = "Vijaipur Compressor Hub"
    action_hour: str = "14:00"
    lead_time_hours: int = 8
    hydraulic_wave_speed_km_h: float = 35.0
    transit_distance_km: float = 380.0
    throughput_adjustment_pct: float = 3.8
    current_vijaipur_throughput_mmscmd: float = 105.3
    recommended_vijaipur_throughput_mmscmd: float = 109.3
    current_vijaipur_discharge_kg_cm2: float = 82.5
    recommended_vijaipur_discharge_kg_cm2: float = 85.6
    fuel_gas_savings_scm_day: float = 18500.0
    project_sanchay_daily_savings_inr: float = 462500.0
    annualized_sanchay_inr_crores: float = 16.88
    decarbonization_co2e_reduction_mt_yr: float = 13500.0


class SarimaxForecastResponse(BaseModel):
    model_type: str = "SARIMAX(1,1,0)×(1,0,0)₂₄"
    target_station: str = "Chhainsa_CS"
    fitted_on_hours: int = 72
    aic: float = 0.0
    model_aic: float = 0.0
    mape_backtest_pct: float = 0.0
    linepack_sensitivity_beta: Optional[float] = None
    model_params: Dict[str, float] = Field(default_factory=dict)
    horizon_hours: int = 24
    last_observed_pressure_kg_cm2: Optional[float] = None
    pressure_deficit_hour_ahead: Optional[int] = None
    pressure_deficit_timestamp: Optional[str] = None
    critical_pressure_threshold_kg_cm2: float = 76.0
    projected_tadir_minimum_kg_cm2: float = 0.0
    minimum_predicted_pressure_kg_cm2: float = 0.0
    with_swap_minimum_kg_cm2: Optional[float] = None
    with_swap_breach: bool = False
    extra_supply_mmscmd: float = 0.0
    extra_supply_from_hour: int = 6
    forecast_records: List[Dict[str, Any]] = Field(default_factory=list)
    hourly_forecast: List[Dict[str, Any]] = Field(default_factory=list)
    # PPAC-style evidence: history on the chart, honest hold-out validation, detected daily cycle
    history: List[Dict[str, Any]] = Field(default_factory=list)
    last_observed_timestamp: Optional[str] = None
    with_swap_min_lower95_kg_cm2: Optional[float] = None
    band_halfwidth_95_t1: Optional[float] = None
    band_halfwidth_95_t24: Optional[float] = None
    backtest_train_hours: Optional[int] = None
    backtest_holdout_hours: Optional[int] = None
    backtest_mape_pct: Optional[float] = None
    backtest_max_abs_error_kg_cm2: Optional[float] = None
    daily_cycle_amplitude_kg_cm2: Optional[float] = None
    daily_peak_hour: Optional[int] = None
    daily_trough_hour: Optional[int] = None
    setpoint_recommendation: SetpointRecommendation
    a2ui_forecast_chart: Optional[Dict[str, Any]] = None


# =============================================================================
# BEAT 2: COMMERCIAL DECISION - LNG SUPPLY OPTIONS (deterministic landed cost)
# =============================================================================

class LngSupplyOptionsResponse(BaseModel):
    as_of: str
    disclaimer: str
    delivery_terminal: str
    shortfall_mmscmd: float
    benchmarks_usd_mmbtu: Dict[str, float]
    fx_inr_per_usd: float
    cargo_size_mmbtu: float
    terminal_inventory_cover_days: int
    options: List[Dict[str, Any]]
    recommended_option_id: str
    recommended_option_label: str
    recommended_delivered_cost_usd_mmbtu: float
    benchmark_option_label: str
    saving_vs_spot_usd_mmbtu: float
    saving_vs_spot_usd_mn: float
    saving_vs_spot_inr_crore: float
    dahej_sendout_increase_mmscmd: float
    sendout_effective_hour_ahead: int
    cargo_covers_days: float
    execution_plan: str


# =============================================================================
# BEAT 4: ACTION - DECISION BRIEF + SAP ORDER (one card)
# =============================================================================

class DecisionBriefResponse(BaseModel):
    headline: str
    shortfall_mmscmd: float
    chosen_option: str
    saving_vs_spot_inr_crore: float
    breach_hour_without_action: Optional[int] = None
    min_pressure_without_action_kg_cm2: float
    min_pressure_with_action_kg_cm2: float
    vijaipur_throughput_adjustment_pct: float
    report_url: str
    report_id: str
    sap_work_order_id: str
    sap_system: str
    sap_order_status: str
    sap_actions: List[str]
    audit_hash: str


# =============================================================================
# ACT 4: SOVEREIGN MULTI-SOURCE EXECUTIVE BRIEFING REPORT
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
    sources_cited: List[str]


# =============================================================================
# ACT 5: RISE WITH SAP S/4HANA & GAIL AI TARANG
# =============================================================================

class SapWorkOrderRequest(BaseModel):
    station: Optional[str] = "Vijaipur"
    equipment_id: str = "EQ-VIJ-GT-01"
    plant: str = "1102"
    order_type: str = "PM01"
    description: str = "Setpoint Calibration"
    priority: str = "2 - High"
    setpoint_increase_pct: float = 3.8
    fuel_saving_justification: Optional[str] = "Project Sanchay 18,500 SCM/day fuel gas"
    action_hour: str = "14:00"


class SapWorkOrderResponse(BaseModel):
    work_order_id: str = "WO-481918"
    sap_work_order_id: str = "WO-481918"
    equipment_id: str = "EQ-VIJ-GT-01"
    order_type: str = "PM01"
    status: str = "SUCCESS"
    order_status: str = "RELEASED_FOR_EXECUTION"
    sap_system: str = "RISE with SAP S/4HANA Cloud (Project Navodaya)"
    execution_plant: str = "1102 - Vijaipur Compressor Complex"
    scheduled_action_time: str = "14:00:00"
    throughput_calibration: str = "+3.8% (Target: 49.3 MMSCMD, Fuel Burn Reduction)"
    project_alignment: str = "Project Sanchay Fuel Gas Minimization Mandate (₹600 Cr NPV Target)"
    audit_hash: str = "7a3f9e4b81c2d0e7"


from pydantic import BaseModel, Field, model_validator

class EnterpriseQueryResponse(BaseModel):
    query: str
    answer: str
    source_attribution: List[str] = Field(default_factory=list)
    cited_sources: List[str] = Field(default_factory=list)
    confidence_score: float = 0.98

    @model_validator(mode="after")
    def sync_sources(self):
        if not self.cited_sources and self.source_attribution:
            self.cited_sources = list(self.source_attribution)
        elif not self.source_attribution and self.cited_sources:
            self.source_attribution = list(self.cited_sources)
        return self
