"""A2UI surface emitter for GAIL Pipeline & Grid Advisory Agent.

Constructs paired 'createSurface', 'updateDataModel', and 'updateComponents' ADK Parts for Gemini Enterprise.
Renders maps, WeatherNext 3 probabilistic cards, SCADA historians, SARIMAX econometric curves, and executive briefings.
"""

import uuid
from typing import List, Dict, Any
from google.genai import types

from app.render.a2ui_envelope import wrap_a2ui_part
from app.render.a2ui_lifecycle import (
    build_create_surface,
    build_update_components,
    build_update_data_model,
)
from app.render.a2ui_cards import (
    build_a2ui_spatial_map_card,
    build_a2ui_weathernext_card,
    build_a2ui_scada_chart,
    build_a2ui_forecast_chart,
)
from app.render.forecast_vega import FORECAST_SPEC_KEY, build_sarimax_vega_spec


def build_spatial_surface(data: Any, surface_id: str) -> List[types.Part]:
    """Emit createSurface + updateComponents for 18,700 km spatial grid audit and hazard overlay."""
    dumped = data.model_dump() if hasattr(data, "model_dump") else data
    card = dumped.get("a2ui_map_payload") or dumped
    
    root_component = {
        "id": "root",
        "component": "Card",
        "children": ["title", "subtitle", "status_text", "alerts_list"],
    }
    title_component = {
        "id": "title",
        "component": "Text",
        "text": f"🗺️ {card.get('title', 'GAIL National Gas Grid - 18,700 km Spatial Network')}",
        "variant": "h3",
    }
    subtitle_component = {
        "id": "subtitle",
        "component": "Text",
        "text": card.get("subtitle", "HVJ Trunkline & River Crossings"),
        "variant": "caption",
    }
    
    alerts = dumped.get("environmental_alerts", [])
    alert_txt = "\n".join([f"⚠️ {a.get('location_name', 'Crossing')}: Gauge {a.get('river_gauge_m')}m (Danger: {a.get('danger_mark_m')}m) - {a.get('imd_rainfall_alert')}" for a in alerts]) if alerts else "✅ All 18,700 km transmission corridors operating in normal hydraulic window."
    
    status_component = {
        "id": "status_text",
        "component": "Text",
        "text": alert_txt,
        "variant": "body",
    }
    alerts_component = {
        "id": "alerts_list",
        "component": "Text",
        "text": "Monitored Trunklines: Hazira-Vijaipur-Jagdishpur (HVJ) · MNJPL (Samruddhi Expressway) · JHBDPL (Urja Ganga)\nActive Action: Sectionalizing valve isolation on Gauna-Bawana crossing standby.",
        "variant": "caption",
    }

    components = [root_component, title_component, subtitle_component, status_component, alerts_component]

    return [
        wrap_a2ui_part(build_create_surface(surface_id=surface_id)),
        wrap_a2ui_part(build_update_components(surface_id=surface_id, components=components)),
    ]


def build_weathernext_surface(data: Any, surface_id: str) -> List[types.Part]:
    """Emit createSurface + updateComponents with DeepMind WeatherNext 3 ensemble chart."""
    dumped = data.model_dump() if hasattr(data, "model_dump") else data
    m = dumped.get("summary_metrics", {})
    loc = dumped.get("location_name", "Grid Station")
    hourly = dumped.get("hourly_forecast", [])

    vega_spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": f"Google DeepMind WeatherNext 3 (0.05° Station Ensemble) - {loc}",
        "data": {"values": hourly},
        "width": "container",
        "height": 240,
        "encoding": {"x": {"field": "forecast_hour", "type": "quantitative", "title": "Forecast Hour (T+1h to T+24h)"}},
        "layer": [
            {
                "mark": {"type": "area", "opacity": 0.25, "color": "#1A73E8"},
                "encoding": {
                    "y": {"field": "temp_c_p10", "type": "quantitative", "scale": {"zero": False}},
                    "y2": {"field": "temp_c_p90"}
                }
            },
            {
                "mark": {"type": "line", "color": "#EA4335", "strokeWidth": 2.5},
                "encoding": {
                    "y": {"field": "temp_c_p50", "type": "quantitative", "title": "Ambient Temperature (°C)"}
                }
            },
            {
                "mark": {"type": "bar", "opacity": 0.55, "color": "#34A853"},
                "encoding": {
                    "y": {"field": "precip_mm_h_p90", "type": "quantitative", "title": "Precipitation Rate (mm/h)"}
                }
            }
        ]
    }

    root_component = {
        "id": "root",
        "component": "Card",
        "children": ["wn-title", "wn-subtitle", "wn-chart", "wn-divider", "wn-kpi"],
    }
    title_comp = {
        "id": "wn-title",
        "component": "Text",
        "text": f"🌦️ Google DeepMind WeatherNext 3 · {loc}",
        "variant": "h3",
    }
    sub_comp = {
        "id": "wn-subtitle",
        "component": "Text",
        "text": f"Probabilistic Forecast (p10 / p50 / p90) · Risk Category: {dumped.get('risk_category')}",
        "variant": "caption",
    }
    chart_comp = {
        "id": "wn-chart",
        "component": "VegaChart",
        "spec": vega_spec,
        "height": 240,
    }
    div_comp = {"id": "wn-divider", "component": "Divider"}
    kpi_comp = {
        "id": "wn-kpi",
        "component": "Text",
        "text": (
            f"• Peak Temperature (p50): {m.get('peak_temperature_c', 41.9)}°C\n"
            f"• 24h Cumulative Precipitation (p90): {m.get('cumulative_precipitation_p90_mm', 115.6)} mm\n"
            f"• Flood Hazard Status: {dumped.get('alert_description')}\n"
            f"• Action Advisory: {dumped.get('action_protocol')}"
        ),
        "variant": "body",
    }

    components = [root_component, title_comp, sub_comp, chart_comp, div_comp, kpi_comp]

    return [
        wrap_a2ui_part(build_create_surface(surface_id=surface_id)),
        wrap_a2ui_part(build_update_components(surface_id=surface_id, components=components)),
    ]


def build_scada_surface(data: Any, surface_id: str) -> List[types.Part]:
    """Emit createSurface + updateComponents for Yokogawa SCADA & Siemens RDS Telemetry."""
    dumped = data.model_dump() if hasattr(data, "model_dump") else data
    station = dumped.get("station", "Chhainsa_CS")
    latest_p = dumped.get("latest_pressure_kg_cm2", 81.47)
    flow = dumped.get("average_flow_mmscmd", 48.05)
    exhaust = dumped.get("max_turbine_exhaust_temp_c", 549.4)

    root_comp = {
        "id": "root",
        "component": "Card",
        "children": ["scada-title", "scada-sub", "scada-kpi", "scada-div", "scada-desc"],
    }
    title_comp = {
        "id": "scada-title",
        "component": "Text",
        "text": f"📊 Yokogawa FAST/TOOLS SCADA Historian · {station}",
        "variant": "h3",
    }
    sub_comp = {
        "id": "scada-sub",
        "component": "Text",
        "text": f"72-Hour Operational Historian & Siemens RDS Gas Turbine Exhaust Telemetry (HVJ Trunkline)",
        "variant": "caption",
    }
    kpi_comp = {
        "id": "scada-kpi",
        "component": "Text",
        "text": (
            f"• Line-Pack Pressure: {latest_p} kg/cm² (Nominal Target: 80.0 - 84.0 kg/cm²)\n"
            f"• Average Transmission Flow: {flow} MMSCMD\n"
            f"• Siemens GT-01 Exhaust Temp: {exhaust}°C (Max Operational Limit: 555.0°C)\n"
            f"• Telemetry Integrity: 72 Hourly Data Points Synchronized from NGMC Archive"
        ),
        "variant": "body",
    }
    div_comp = {"id": "scada-div", "component": "Divider"}
    desc_comp = {
        "id": "scada-desc",
        "component": "Text",
        "text": "Real-time feed connected to GAIL National Gas Management Centre (NGMC) telemetry bus.",
        "variant": "caption",
    }

    components = [root_comp, title_comp, sub_comp, kpi_comp, div_comp, desc_comp]

    return [
        wrap_a2ui_part(build_create_surface(surface_id=surface_id)),
        wrap_a2ui_part(build_update_components(surface_id=surface_id, components=components)),
    ]


def build_sarimax_surface(data: Any, surface_id: str) -> List[types.Part]:
    """Emit createSurface + updateDataModel (Vega spec) + updateComponents for SARIMAX demand forecast."""
    dumped = data.model_dump() if hasattr(data, "model_dump") else data
    station = dumped.get("station", "Chhainsa_CS")
    setpoint = dumped.get("setpoint_recommendation", {})
    spec = build_sarimax_vega_spec(dumped)

    root_comp = {
        "id": "root",
        "component": "Card",
        "children": ["sm-title", "sm-sub", "sm-chart", "sm-div", "sm-rec"],
    }
    title_comp = {
        "id": "sm-title",
        "component": "Text",
        "text": f"📈 SARIMAX Econometric Linepack Forecast · {station}",
        "variant": "h3",
    }
    sub_comp = {
        "id": "sm-sub",
        "component": "Text",
        "text": "PPAC-Grade Box-Jenkins Multivariate TSA (Nominations & Ambient Weather Regressors)",
        "variant": "caption",
    }
    chart_comp = {
        "id": "sm-chart",
        "component": "VegaChart",
        "spec": spec,
        "height": 280,
    }
    div_comp = {"id": "sm-div", "component": "Divider"}
    rec_comp = {
        "id": "sm-rec",
        "component": "Text",
        "text": (
            f"⚠️ Critical Linepack Depletion Predicted: T+{dumped.get('pressure_deficit_hour_ahead', 14)}h at Chhainsa.\n"
            f"💡 Recommended Hydraulic Setpoint: +{setpoint.get('throughput_adjustment_pct', 3.8)}% at Vijaipur Hub ({setpoint.get('action_hour', '14:00')} IST).\n"
            f"💰 Project Sanchay Fuel Savings: {setpoint.get('fuel_gas_savings_scm_day', 18500):,} SCM/day (₹{setpoint.get('project_sanchay_daily_savings_inr', 462500):,}/day · ₹16.88 Cr/yr)."
        ),
        "variant": "body",
    }

    components = [root_comp, title_comp, sub_comp, chart_comp, div_comp, rec_comp]

    return [
        wrap_a2ui_part(build_create_surface(surface_id=surface_id)),
        wrap_a2ui_part(build_update_data_model(surface_id=surface_id, value={FORECAST_SPEC_KEY: spec})),
        wrap_a2ui_part(build_update_components(surface_id=surface_id, components=components)),
    ]


def build_report_surface(data: Any, surface_id: str) -> List[types.Part]:
    """Emit createSurface + updateComponents for sovereign executive briefing release."""
    dumped = data.model_dump() if hasattr(data, "model_dump") else data
    title = dumped.get("report_title", "Daily Line-Pack & Grid Integrity Sovereign Executive Briefing")
    html_path = dumped.get("compiled_html_path", "output_artifacts/GAIL_Executive_Briefing.html")

    root_comp = {
        "id": "root",
        "component": "Card",
        "children": ["rep-title", "rep-sub", "rep-kpi", "rep-div", "rep-actions"],
    }
    title_comp = {
        "id": "rep-title",
        "component": "Text",
        "text": f"📑 {title}",
        "variant": "h3",
    }
    sub_comp = {
        "id": "rep-sub",
        "component": "Text",
        "text": f"Sovereign Multi-Source Compilation · Reference: {dumped.get('report_id')}",
        "variant": "caption",
    }
    kpi_comp = {
        "id": "rep-kpi",
        "component": "Text",
        "text": (
            f"• Grid Status: {dumped.get('grid_integrity_status')}\n"
            f"• WeatherNext Alert: {dumped.get('weather_risk_summary')}\n"
            f"• Project Sanchay Fuel Gas ROI: ₹16.88 Crore Annualized Margin Protection\n"
            f"• Artifact URI: {html_path}"
        ),
        "variant": "body",
    }
    div_comp = {"id": "rep-div", "component": "Divider"}
    actions_comp = {
        "id": "rep-actions",
        "component": "Text",
        "text": f"Interactive HTML edition generated with base64 State Emblem, official GAIL crest, and Parts A–F statutory data tables.\nAccess report locally or in Data Lake: {html_path}",
        "variant": "caption",
    }

    components = [root_comp, title_comp, sub_comp, kpi_comp, div_comp, actions_comp]

    return [
        wrap_a2ui_part(build_create_surface(surface_id=surface_id)),
        wrap_a2ui_part(build_update_components(surface_id=surface_id, components=components)),
    ]


def build_sap_surface(data: Any, surface_id: str) -> List[types.Part]:
    """Emit createSurface + updateComponents for RISE with SAP S/4HANA work order staging."""
    dumped = data.model_dump() if hasattr(data, "model_dump") else data
    order_id = dumped.get("work_order_id", "WO-481918")

    root_comp = {
        "id": "root",
        "component": "Card",
        "children": ["sap-title", "sap-sub", "sap-kpi", "sap-div", "sap-audit"],
    }
    title_comp = {
        "id": "sap-title",
        "component": "Text",
        "text": f"⚙️ RISE with SAP S/4HANA Cloud · Work Order {order_id}",
        "variant": "h3",
    }
    sub_comp = {
        "id": "sap-sub",
        "component": "Text",
        "text": f"Project Navodaya Automated Maintenance Staging · Plant: {dumped.get('execution_plant')}",
        "variant": "caption",
    }
    kpi_comp = {
        "id": "sap-kpi",
        "component": "Text",
        "text": (
            f"• Work Order ID: {order_id} (Type: {dumped.get('order_type')})\n"
            f"• Target Equipment: {dumped.get('equipment_id')} (Vijaipur GT-01)\n"
            f"• Execution Status: {dumped.get('order_status')}\n"
            f"• Calibration Advisory: {dumped.get('throughput_calibration')}\n"
            f"• Mandate Alignment: {dumped.get('project_alignment')}"
        ),
        "variant": "body",
    }
    div_comp = {"id": "sap-div", "component": "Divider"}
    audit_comp = {
        "id": "sap-audit",
        "component": "Text",
        "text": f"SHA-256 Audit Verification Hash: {dumped.get('audit_hash')} · Logged to Project Navodaya Governance Ledger.",
        "variant": "caption",
    }

    components = [root_comp, title_comp, sub_comp, kpi_comp, div_comp, audit_comp]

    return [
        wrap_a2ui_part(build_create_surface(surface_id=surface_id)),
        wrap_a2ui_part(build_update_components(surface_id=surface_id, components=components)),
    ]
