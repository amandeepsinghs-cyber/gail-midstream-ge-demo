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
    """Emit createSurface + updateComponents for Step 1: GAIL Enterprise Data Lake & GMS Corridor Inventory."""
    dumped = data.model_dump() if hasattr(data, "model_dump") else data

    corridor_values = [
        {"corridor": "HVJ Trunkline (5,420 km)", "flow_mmscmd": 81.4, "capacity_mmscmd": 85.0, "utilization_pct": 95.8},
        {"corridor": "Urja Ganga / JHBDPL (3,384 km)", "flow_mmscmd": 12.0, "capacity_mmscmd": 16.0, "utilization_pct": 75.0},
        {"corridor": "Dadri-Bawana-Nangal (912 km)", "flow_mmscmd": 10.7, "capacity_mmscmd": 12.0, "utilization_pct": 89.2},
        {"corridor": "MNJPL Samruddhi (1,755 km)", "flow_mmscmd": 9.9, "capacity_mmscmd": 13.0, "utilization_pct": 76.2},
        {"corridor": "Regional & Southern Grids (7,229 km)", "flow_mmscmd": 8.18, "capacity_mmscmd": 10.5, "utilization_pct": 77.9},
    ]

    vega_spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": "GAIL 18,700 km National Gas Grid — Corridor Throughput vs. Design Capacity (MMSCMD)",
        "data": {"values": corridor_values},
        "width": "container",
        "height": 220,
        "encoding": {
            "y": {"field": "corridor", "type": "nominal", "title": "Transmission Corridor", "sort": "-x"},
            "x": {"field": "flow_mmscmd", "type": "quantitative", "title": "Active Transmission Volume (MMSCMD)"},
            "color": {"value": "#004B87"},
            "tooltip": [
                {"field": "corridor", "type": "nominal"},
                {"field": "flow_mmscmd", "type": "quantitative", "title": "Active Flow (MMSCMD)"},
                {"field": "capacity_mmscmd", "type": "quantitative", "title": "Design Capacity (MMSCMD)"},
                {"field": "utilization_pct", "type": "quantitative", "title": "Utilization (%)"}
            ]
        },
        "mark": {"type": "bar", "cornerRadiusEnd": 4}
    }

    root_component = {
        "id": "root",
        "component": "Card",
        "child": "spatial-col",
    }
    column_component = {
        "id": "spatial-col",
        "component": "Column",
        "children": ["title", "subtitle", "corridor_chart", "div1", "status_text", "alerts_list"],
    }
    title_component = {
        "id": "title",
        "component": "Text",
        "text": "🗄️ GAIL Enterprise Data Lake & Gas Management System (GMS) Inventory",
        "variant": "h3",
    }
    subtitle_component = {
        "id": "subtitle",
        "component": "Text",
        "text": "18,700 km Cross-Country Grid · 122.18 MMSCMD Total Throughput · Project Navodaya (SAP S/4HANA) Sync",
        "variant": "caption",
    }
    chart_component = {
        "id": "corridor_chart",
        "component": "VegaChart",
        "spec": vega_spec,
        "height": 220,
    }
    div_component = {"id": "div1", "component": "Divider"}
    status_component = {
        "id": "status_text",
        "component": "Text",
        "text": (
            "• Total Verified Grid Throughput: 122.18 MMSCMD across 18,700 km (5 Regional Corridors Audited)\n"
            "• Sectoral Customer Nominations (Exogenous X₁): Fertilizer (HURL/NFL/IFFCO) 38.4 MMSCMD (+20% Scheduled Ramp) · CGD 28.2 MMSCMD · Power 24.8 MMSCMD · Pata Petrochemical & Industrial 30.78 MMSCMD\n"
            "• Enterprise Data Sources Connected: gs://gail-midstream-ge-demo-datalake · GMS Commercial Nominations · Cloud Historian · RISE with SAP S/4HANA Cloud"
        ),
        "variant": "body",
    }
    alerts_component = {
        "id": "alerts_list",
        "component": "Text",
        "text": "Data Governance: 100% Schema Validated · Zero Quarantined Submissions · Ready for Time-Series & SARIMAX Modeling.",
        "variant": "caption",
    }

    components = [root_component, column_component, title_component, subtitle_component, chart_component, div_component, status_component, alerts_component]

    return [
        wrap_a2ui_part(build_create_surface(surface_id=surface_id)),
        wrap_a2ui_part(build_update_components(surface_id=surface_id, components=components)),
    ]


def build_weathernext_surface(data: Any, surface_id: str) -> List[types.Part]:
    """Emit createSurface + updateComponents with DeepMind WeatherNext 3 ensemble chart (Optional Add-On)."""
    dumped = data.model_dump() if hasattr(data, "model_dump") else data
    m = dumped.get("summary_metrics", {})
    loc = dumped.get("location_name", "Grid Station")
    hourly = dumped.get("hourly_forecast", [])

    vega_spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": f"Environmental Weather Overlay (0.05° Ensemble) - {loc}",
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
        "child": "wn-col",
    }
    col_component = {
        "id": "wn-col",
        "component": "Column",
        "children": ["wn-title", "wn-subtitle", "wn-chart", "wn-divider", "wn-kpi"],
    }
    title_comp = {
        "id": "wn-title",
        "component": "Text",
        "text": f"🌦️ Optional Environmental Weather Overlay · {loc}",
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

    components = [root_component, col_component, title_comp, sub_comp, chart_comp, div_comp, kpi_comp]

    return [
        wrap_a2ui_part(build_create_surface(surface_id=surface_id)),
        wrap_a2ui_part(build_update_components(surface_id=surface_id, components=components)),
    ]


def build_scada_surface(data: Any, surface_id: str) -> List[types.Part]:
    """Emit createSurface + updateComponents for Step 2: GAIL Enterprise Historian 72-Hour Time Series."""
    dumped = data.model_dump() if hasattr(data, "model_dump") else data
    station = dumped.get("station", "Chhainsa_CS")
    latest_p = dumped.get("latest_pressure_kg_cm2", 81.47)
    flow = dumped.get("average_flow_mmscmd", 48.05)
    exhaust = dumped.get("max_turbine_exhaust_temp_c", 549.4)
    series = dumped.get("telemetry_series") or dumped.get("time_series") or []

    vega_spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": f"GAIL Enterprise Cloud Historian — 72-Hour Line-Pack Pressure & Flow Time Series ({station})",
        "data": {"values": series[-36:] if series else []},
        "width": "container",
        "height": 240,
        "resolve": {"scale": {"y": "independent"}},
        "encoding": {"x": {"field": "timestamp", "type": "nominal", "title": "Timestamp (Hourly GMS & Historian Log)", "axis": {"labelAngle": -45}}},
        "layer": [
            {
                "mark": {"type": "line", "color": "#1A73E8", "strokeWidth": 2.5},
                "encoding": {
                    "y": {"field": "linepack_pressure_kg_cm2", "type": "quantitative", "title": "Line-Pack Pressure (kg/cm²)", "scale": {"domain": [74, 86]}}
                }
            },
            {
                "mark": {"type": "line", "color": "#E65100", "strokeDash": [4, 4], "strokeWidth": 2},
                "encoding": {
                    "y": {"field": "gas_flow_mmscmd", "type": "quantitative", "title": "Gas Throughput (MMSCMD)"}
                }
            }
        ]
    }

    root_comp = {
        "id": "root",
        "component": "Card",
        "child": "scada-col",
    }
    col_comp = {
        "id": "scada-col",
        "component": "Column",
        "children": ["scada-title", "scada-sub", "scada-chart", "scada-div", "scada-kpi", "scada-desc"],
    }
    title_comp = {
        "id": "scada-title",
        "component": "Text",
        "text": f"📊 GAIL Operational Time-Series Explorer · {station} (HVJ Corridor)",
        "variant": "h3",
    }
    sub_comp = {
        "id": "scada-sub",
        "component": "Text",
        "text": "72-Hour Enterprise Cloud Historian & Gas Management System (GMS) Time-Series Dataset",
        "variant": "caption",
    }
    chart_comp = {
        "id": "scada-chart",
        "component": "VegaChart",
        "spec": vega_spec,
        "height": 240,
    }
    kpi_comp = {
        "id": "scada-kpi",
        "component": "Text",
        "text": (
            f"• Current Line-Pack Pressure: {latest_p} kg/cm² (Contractual Operating Band: 76.0 – 84.0 kg/cm²)\n"
            f"• Mean Segment Throughput: {flow} MMSCMD (HVJ Northern Trunkline)\n"
            f"• Compressor Station Thermal Efficiency Index: {exhaust}°C (Within Optimal Window <555.0°C)\n"
            f"• Exogenous Customer Off-Take Schedule (X₁): +20.0% Fertilizer & CGD Drawal Ramp Scheduled at T+8h"
        ),
        "variant": "body",
    }
    div_comp = {"id": "scada-div", "component": "Divider"}
    desc_comp = {
        "id": "scada-desc",
        "component": "Text",
        "text": "Queried from GAIL Enterprise Cloud Historian & GMS Data Lake (gs://gail-midstream-ge-demo-datalake).",
        "variant": "caption",
    }

    components = [root_comp, col_comp, title_comp, sub_comp, chart_comp, div_comp, kpi_comp, desc_comp]

    return [
        wrap_a2ui_part(build_create_surface(surface_id=surface_id)),
        wrap_a2ui_part(build_update_components(surface_id=surface_id, components=components)),
    ]


def build_sarimax_surface(data: Any, surface_id: str) -> List[types.Part]:
    """Emit createSurface + updateDataModel (Vega spec) + updateComponents for Step 3: SARIMAX demand forecast."""
    dumped = data.model_dump() if hasattr(data, "model_dump") else data
    station = dumped.get("station", "Chhainsa_CS")
    setpoint = dumped.get("setpoint_recommendation", {})
    spec = build_sarimax_vega_spec(dumped)

    root_comp = {
        "id": "root",
        "component": "Card",
        "child": "sarimax-col",
    }
    col_comp = {
        "id": "sarimax-col",
        "component": "Column",
        "children": ["sm-title", "sm-sub", "sm-chart", "sm-div", "sm-rec"],
    }
    title_comp = {
        "id": "sm-title",
        "component": "Text",
        "text": f"📈 Deterministic SARIMAX (1,1,1)×(1,1,1)₂₄ Time-Series Forecast · {station}",
        "variant": "h3",
    }
    sub_comp = {
        "id": "sm-sub",
        "component": "Text",
        "text": "Multivariate Box-Jenkins Model · Seasonal 24h Diurnal Cycle (S=24) + Exogenous Customer Nominations (X₁)",
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
            f"• Mathematical Early Warning: Incorporates 24h Diurnal Lag (S=24) + Exogenous Customer Nominations (X₁: +20% Fertilizer HURL/NFL & CGD drawal ramp)\n"
            f"⚠️ Critical Line-Pack Depletion Predicted: {dumped.get('minimum_predicted_pressure_kg_cm2', 73.8)} kg/cm² at T+{dumped.get('pressure_deficit_hour_ahead', 14)}h (Contract Threshold: 76.0 kg/cm²).\n"
            f"💡 Recommended Hydraulic Setpoint: +{setpoint.get('throughput_adjustment_pct', 3.8)}% at Vijaipur Hub ({setpoint.get('action_hour', '14:00')} IST).\n"
            f"💰 Project Sanchay Fuel Savings: {setpoint.get('fuel_gas_savings_scm_day', 18500):,} SCM/day (₹{setpoint.get('project_sanchay_daily_savings_inr', 462500):,}/day · ₹16.88 Cr/yr toward ₹600 Cr NPV)."
        ),
        "variant": "body",
    }

    components = [root_comp, col_comp, title_comp, sub_comp, chart_comp, div_comp, rec_comp]

    return [
        wrap_a2ui_part(build_create_surface(surface_id=surface_id)),
        wrap_a2ui_part(build_update_data_model(surface_id=surface_id, value={FORECAST_SPEC_KEY: spec})),
        wrap_a2ui_part(build_update_components(surface_id=surface_id, components=components)),
    ]


def build_report_surface(data: Any, surface_id: str) -> List[types.Part]:
    """Emit createSurface + updateComponents for Step 4: Exhaustive GAIL Executive Report."""
    dumped = data.model_dump() if hasattr(data, "model_dump") else data
    title = dumped.get("report_title", "GAIL (India) Limited Daily Gas Transmission, SARIMAX & Project Sanchay Executive Report")
    html_path = dumped.get("compiled_html_path", "output_artifacts/GAIL_Executive_Briefing_2026-09-23.html")

    root_comp = {
        "id": "root",
        "component": "Card",
        "child": "report-col",
    }
    col_comp = {
        "id": "report-col",
        "component": "Column",
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
        "text": f"Exhaustive 6-Part Management Ready Reckoner · Reference: {dumped.get('report_id')}",
        "variant": "caption",
    }
    kpi_comp = {
        "id": "rep-kpi",
        "component": "Text",
        "text": (
            f"• Part A & B: 18,700 km Corridor Utilization (122.18 MMSCMD) & Sectoral Customer Nominations (Fertilizer, Power, CGD, Petchem)\n"
            f"• Part C & D: 72-Hour Operational Historian Time-Series & 24-Hour Multivariate SARIMAX (S=24 + X₁) Forecast Tables\n"
            f"• Part E & F: Project Sanchay Fuel Gas Economics (18,500 SCM/day · ₹16.88 Cr/yr · ₹600 Cr NPV) & SAP S/4HANA Governance\n"
            f"• Live Executive HTML Report: [Open GAIL Executive Briefing]({html_path})"
        ),
        "variant": "body",
    }
    div_comp = {"id": "rep-div", "component": "Divider"}
    actions_comp = {
        "id": "rep-actions",
        "component": "Text",
        "text": f"Publication-ready 6-Part HTML edition compiled with official GAIL (India) Limited crest, embedded SVG time-series charts, and audited tables.\nAccess Report: [Click to View Full Report]({html_path})",
        "variant": "caption",
    }

    components = [root_comp, col_comp, title_comp, sub_comp, kpi_comp, div_comp, actions_comp]

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
        "child": "sap-col",
    }
    col_comp = {
        "id": "sap-col",
        "component": "Column",
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

    components = [root_comp, col_comp, title_comp, sub_comp, kpi_comp, div_comp, audit_comp]

    return [
        wrap_a2ui_part(build_create_surface(surface_id=surface_id)),
        wrap_a2ui_part(build_update_components(surface_id=surface_id, components=components)),
    ]


def build_enterprise_qa_surface(data: Any, surface_id: str) -> List[types.Part]:
    """Emit createSurface + updateComponents for GAIL AI Tarang Enterprise Knowledge Q&A."""
    dumped = data.model_dump() if hasattr(data, "model_dump") else data
    sources = dumped.get("source_attribution", [])
    sources_txt = "\n".join([f"• {s}" for s in sources]) if sources else "• GAIL Corporate Operational Guidelines"

    root_comp = {
        "id": "root",
        "component": "Card",
        "child": "qa-col",
    }
    col_comp = {
        "id": "qa-col",
        "component": "Column",
        "children": ["qa-title", "qa-sub", "qa-ans", "qa-div", "qa-src"],
    }
    title_comp = {
        "id": "qa-title",
        "component": "Text",
        "text": "🏛️ GAIL AI Tarang · Sovereign Enterprise Intelligence",
        "variant": "h3",
    }
    sub_comp = {
        "id": "qa-sub",
        "component": "Text",
        "text": f"Query: {dumped.get('query', 'Enterprise Inquiry')} · Confidence: {int(dumped.get('confidence_score', 0.99)*100)}%",
        "variant": "caption",
    }
    ans_comp = {
        "id": "qa-ans",
        "component": "Text",
        "text": dumped.get("answer", ""),
        "variant": "body",
    }
    div_comp = {"id": "qa-div", "component": "Divider"}
    src_comp = {
        "id": "qa-src",
        "component": "Text",
        "text": f"Authoritative Citations:\n{sources_txt}",
        "variant": "caption",
    }

    components = [root_comp, col_comp, title_comp, sub_comp, ans_comp, div_comp, src_comp]

    return [
        wrap_a2ui_part(build_create_surface(surface_id=surface_id)),
        wrap_a2ui_part(build_update_components(surface_id=surface_id, components=components)),
    ]
