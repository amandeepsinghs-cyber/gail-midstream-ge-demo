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
        "text": "🗄️ Grid Flows & Tomorrow's Customer Nominations",
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
    sf = dumped.get("demand_shortfall") or {}
    if not sf:
        from app import scenario
        sf = scenario.shortfall()
    status_component = {
        "id": "status_text",
        "component": "Text",
        "text": (
            f"⚠️ **Tomorrow's shortfall on {sf.get('segment', 'HVJ North')}: {sf.get('shortfall_mmscmd', 4.0)} MMSCMD** "
            f"from {str(sf.get('starts_at', ''))[11:16]} IST\n"
            f"• Revised nominations: Fertilizer (HURL/NFL) +{sf.get('fertilizer_change_pct', 20):.0f}% "
            f"(+{sf.get('fertilizer_delta_mmscmd', 3.0)} MMSCMD) · CGD +{sf.get('cgd_change_pct', 12):.0f}% "
            f"(+{sf.get('cgd_delta_mmscmd', 1.0)} MMSCMD)\n"
            f"• Segment off-take: {sf.get('baseline_daily_offtake_mmscmd')} → {sf.get('revised_daily_offtake_mmscmd')} MMSCMD (baseline → revised)\n"
            f"• Reason: {sf.get('reason', '')}"
        ),
        "variant": "body",
    }
    alerts_component = {
        "id": "alerts_list",
        "component": "Text",
        "text": "Sources: GMS customer nominations · Enterprise Cloud Historian · gs://gail-midstream-ge-demo-datalake. Next: evaluate LNG supply options.",
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
        "text": f"📈 Can the grid carry it? · {dumped.get('target_station', station)}",
        "variant": "h3",
    }
    sub_comp = {
        "id": "sm-sub",
        "component": "Text",
        "text": (
            f"① Loaded {dumped.get('fitted_on_hours', 72)}h historian data  ② Detected daily cycle "
            f"(~{dumped.get('daily_cycle_amplitude_kg_cm2')} kg/cm² swing)  ③ Fitted {dumped.get('model_type')} "
            f"(β = {dumped.get('linepack_sensitivity_beta')})  ④ Back-tested on last {dumped.get('backtest_holdout_hours')}h: "
            f"{dumped.get('backtest_mape_pct')}% error  ⑤ Forecast two futures with 80% / 95% cones"
        ),
        "variant": "caption",
    }
    chart_comp = {
        "id": "sm-chart",
        "component": "VegaChart",
        "spec": spec,
        "height": 340,
    }
    div_comp = {"id": "sm-div", "component": "Divider"}
    breach_h = dumped.get("pressure_deficit_hour_ahead")
    breach_ts = str(dumped.get("pressure_deficit_timestamp") or "")[11:16]
    floor = dumped.get("critical_pressure_threshold_kg_cm2", 76.0)
    rec_comp = {
        "id": "sm-rec",
        "component": "Text",
        "text": (
            f"🔴 **Without action:** breaches the {floor:.1f} kg/cm² floor at **T+{breach_h}h ({breach_ts} IST)**, "
            f"falling to {dumped.get('minimum_predicted_pressure_kg_cm2')} kg/cm².\n"
            f"🟢 **With LNG swap (+{dumped.get('extra_supply_mmscmd')} MMSCMD from T+{dumped.get('extra_supply_from_hour')}h):** "
            f"stays at or above **{dumped.get('with_swap_minimum_kg_cm2')} kg/cm²** — no breach "
            f"(95% lower bound {dumped.get('with_swap_min_lower95_kg_cm2')} kg/cm², still above the floor).\n"
            f"⚙️ **Setpoint:** Vijaipur throughput +{setpoint.get('throughput_adjustment_pct')}% "
            f"({setpoint.get('current_vijaipur_throughput_mmscmd')} → {setpoint.get('recommended_vijaipur_throughput_mmscmd')} MMSCMD) "
            f"to carry the extra Dahej gas north.\n"
            f"Same fitted model, two supply inputs: the forecast shows what happens **if we act**."
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


def build_lng_surface(data: Any, surface_id: str) -> List[types.Part]:
    """Beat 2 (Decision): landed-cost comparison of LNG supply options."""
    d = data.model_dump() if hasattr(data, "model_dump") else data
    rows = []
    for o in d.get("options", []):
        status = "Recommended" if o.get("recommended") else ("Too late" if not o.get("feasible") else "Dearer")
        rows.append({
            "option": o["label"],
            "usd_mmbtu": o["delivered_cost_usd_mmbtu"],
            "label": f"${o['delivered_cost_usd_mmbtu']:.2f}" + ("  (too late)" if not o.get("feasible") else ""),
            "status": status,
            "arrival": f"{o['arrival_days']} days",
            "formula": o["formula"],
        })
    enc_y = {"field": "option", "type": "nominal", "title": None, "sort": {"field": "usd_mmbtu", "order": "ascending"}}
    spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": {
            "text": f"Delivered cost at {d.get('delivery_terminal', 'Dahej')} (USD/MMBtu)",
            "subtitle": "Fixed formulas · illustrative prices",
            "anchor": "start",
        },
        "width": "container",
        "height": 170,
        "data": {"values": rows},
        "encoding": {"y": enc_y},
        "layer": [
            {
                "mark": {"type": "bar", "cornerRadiusEnd": 4, "height": 30},
                "encoding": {
                    "x": {"field": "usd_mmbtu", "type": "quantitative", "title": "USD/MMBtu", "scale": {"domain": [0, 16]}},
                    "color": {
                        "field": "status", "type": "nominal", "title": None,
                        "scale": {"domain": ["Recommended", "Dearer", "Too late"], "range": ["#008751", "#E65100", "#CBD5E1"]},
                        "legend": {"orient": "bottom"},
                    },
                    "tooltip": [
                        {"field": "option", "title": "Option"},
                        {"field": "formula", "title": "Formula"},
                        {"field": "usd_mmbtu", "title": "USD/MMBtu", "format": ".2f"},
                        {"field": "arrival", "title": "Arrival"},
                    ],
                },
            },
            {
                "mark": {"type": "text", "align": "left", "dx": 6, "fontWeight": "bold", "fontSize": 13},
                "encoding": {
                    "x": {"field": "usd_mmbtu", "type": "quantitative"},
                    "text": {"field": "label"},
                },
            },
        ],
    }
    lines = []
    for o in sorted(d.get("options", []), key=lambda x: x["delivered_cost_usd_mmbtu"]):
        mark = "✅" if o.get("recommended") else ("⏱️" if not o.get("feasible") else "•")
        lines.append(f"{mark} {o['label']}: ${o['delivered_cost_usd_mmbtu']:.2f}/MMBtu · arrives in {o['arrival_days']} days"
                     + ("" if o.get("feasible") else " — too late"))
    comps = [
        {"id": "root", "component": "Card", "child": "lng-col"},
        {"id": "lng-col", "component": "Column",
         "children": ["lng-title", "lng-sub", "lng-chart", "lng-div", "lng-rec", "lng-opts", "lng-note"]},
        {"id": "lng-title", "component": "Text", "variant": "h3",
         "text": f"💱 Cheapest way to cover the {d.get('shortfall_mmscmd')} MMSCMD shortfall"},
        {"id": "lng-sub", "component": "Text", "variant": "caption",
         "text": f"Landed-cost engine (fixed formulas) · FX ₹{d.get('fx_inr_per_usd')}/USD · cargo {d.get('cargo_size_mmbtu', 0)/1e6:.1f} TBtu · {d.get('as_of')}"},
        {"id": "lng-chart", "component": "VegaChart", "spec": spec, "height": 170},
        {"id": "lng-div", "component": "Divider"},
        {"id": "lng-rec", "component": "Text", "variant": "body",
         "text": (f"**Recommended: {d.get('recommended_option_label')}** at ${d.get('recommended_delivered_cost_usd_mmbtu'):.2f}/MMBtu — "
                  f"**₹{d.get('saving_vs_spot_inr_crore')} Cr cheaper** than a spot cargo (saves ${d.get('saving_vs_spot_usd_mmbtu'):.2f}/MMBtu).\n"
                  f"{d.get('execution_plan')}")},
        {"id": "lng-opts", "component": "Text", "variant": "body", "text": "\n".join(lines)},
        {"id": "lng-note", "component": "Text", "variant": "caption", "text": d.get("disclaimer", "")},
    ]
    return [
        wrap_a2ui_part(build_create_surface(surface_id=surface_id)),
        wrap_a2ui_part(build_update_components(surface_id=surface_id, components=comps)),
    ]


def build_decision_surface(data: Any, surface_id: str) -> List[types.Part]:
    """Beat 4 (Action): decision brief link + SAP order on one card."""
    d = data.model_dump() if hasattr(data, "model_dump") else data
    comps = [
        {"id": "root", "component": "Card", "child": "dec-col"},
        {"id": "dec-col", "component": "Column",
         "children": ["dec-title", "dec-sub", "dec-story", "dec-div", "dec-sap", "dec-link"]},
        {"id": "dec-title", "component": "Text", "variant": "h3", "text": "✅ Decision briefed and actioned"},
        {"id": "dec-sub", "component": "Text", "variant": "caption",
         "text": f"Report {d.get('report_id')} · {d.get('sap_system')}"},
        {"id": "dec-story", "component": "Text", "variant": "body",
         "text": (f"1️⃣ **Problem:** {d.get('shortfall_mmscmd')} MMSCMD shortfall on HVJ North\n"
                  f"2️⃣ **Decision:** {d.get('chosen_option')} — ₹{d.get('saving_vs_spot_inr_crore')} Cr cheaper than spot\n"
                  f"3️⃣ **Proof:** breach at T+{d.get('breach_hour_without_action')}h avoided; line-pack held ≥ {d.get('min_pressure_with_action_kg_cm2')} kg/cm²\n"
                  f"4️⃣ **Action:** SAP order **{d.get('sap_work_order_id')}** · {d.get('sap_order_status')}")},
        {"id": "dec-div", "component": "Divider"},
        {"id": "dec-sap", "component": "Text", "variant": "body",
         "text": "\n".join(f"• {a}" for a in d.get("sap_actions", [])) + f"\n• Audit hash: {d.get('audit_hash')}"},
        {"id": "dec-link", "component": "Text", "variant": "body",
         "text": f"📑 [Open the executive decision brief]({d.get('report_url')})"},
    ]
    return [
        wrap_a2ui_part(build_create_surface(surface_id=surface_id)),
        wrap_a2ui_part(build_update_components(surface_id=surface_id, components=comps)),
    ]
