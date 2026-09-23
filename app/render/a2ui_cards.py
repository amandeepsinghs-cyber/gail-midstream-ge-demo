"""
A2UI v0.9 Component Renderer for Gemini Enterprise (GE) & Agent-to-Agent (A2A).
"""

from typing import Dict, Any, List


def build_a2ui_spatial_map_card(gis_data: Dict[str, Any], weathernext_summary: Dict[str, Any] = None) -> Dict[str, Any]:
    alerts = []
    features = gis_data.get("features", [])
    
    for feat in features:
        props = feat.get("properties", {})
        if "environmental_alert" in props or "CRITICAL" in str(props.get("status", "")):
            alerts.append({
                "location_name": props.get("name"),
                "asset_class": props.get("asset_class", "SUBMERGED_CROSSING"),
                "risk_level": "CRITICAL",
                "river_gauge_m": props.get("river_gauge_level_m", 206.4),
                "danger_mark_m": props.get("danger_mark_m", 205.33),
                "imd_rainfall_alert": props.get("imd_rainfall_alert", "HEAVY_TO_VERY_HEAVY (115.6mm)"),
                "hydraulic_stress_indicator": props.get("scada_hydraulic_stress", "ELEVATED_VIBRATION_ALERT"),
                "action_advisory": "Dispatch regional pipeline patrol; activate upstream sectionalizing valve isolation protocol."
            })

    weather_desc = weathernext_summary.get("alert_description") if weathernext_summary else "WeatherNext 3: Active monsoon deluge in Yamuna catchment (115.6mm p90)."

    return {
        "a2ui_version": "v0.9",
        "card_type": "SPATIAL_INFRASTRUCTURE_MONITOR",
        "title": "GAIL National Gas Grid - 18,700 km Spatial Network & WeatherNext 3 Risk Layer",
        "subtitle": "HVJ Trunkline Corridor, Compressor Hubs & Active Yamuna River Crossing Vulnerability Audit",
        "layout": "split_map_and_alerts",
        "theme": "energy_dark",
        "ge_rendering_target": "A2UI_CARD_VIEW",
        "map_layers": {
            "pipeline_geojson": gis_data,
            "corridors": ["Hazira-Vijaipur-Jagdishpur (HVJ)", "MNJPL (Samruddhi Expressway)", "JHBDPL Urja Ganga"],
            "highlighted_assets": [
                {"name": "Vijaipur Compressor Hub", "coords": [77.2941, 24.1627], "type": "COMPRESSOR_HUB"},
                {"name": "Chhainsa Compressor Station", "coords": [77.3412, 28.2711], "type": "PRESSURE_STATION"},
                {"name": "Gauna-Bawana Yamuna Crossing", "coords": [77.0315, 28.7912], "type": "HIGH_RISK_CROSSING"}
            ]
        },
        "weathernext_status": {
            "model": "WeatherNext 3 (Google DeepMind 0.05° Station Ensemble)",
            "risk_category": "CRITICAL_HYDRAULIC_SURGE",
            "narrative": weather_desc
        },
        "active_alerts": alerts,
        "actions": [
            {"label": "Query WeatherNext Forecast", "command": "get_weathernext_forecast location='Gauna_Bawana'"},
            {"label": "Inspect Chhainsa SCADA Telemetry", "command": "query_scada_telemetry station='Chhainsa_CS'"},
            {"label": "Run SARIMAX Demand Forecast", "command": "run_sarimax_linepack_forecast"}
        ]
    }


def build_a2ui_weathernext_card(weathernext_data: Dict[str, Any]) -> Dict[str, Any]:
    metrics = weathernext_data.get("summary_metrics", {})
    hourly = weathernext_data.get("hourly_forecast", [])

    vega_spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": f"WeatherNext 3 Probabilistic Forecast (p10 / p50 / p90) - {weathernext_data.get('location_name')}",
        "data": {"values": hourly},
        "width": 420,
        "height": 220,
        "encoding": {"x": {"field": "forecast_hour", "type": "quantitative", "title": "Forecast Hour Ahead (T+1h to T+24h)"}},
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
                "mark": {"type": "bar", "opacity": 0.5, "color": "#34A853"},
                "encoding": {
                    "y": {"field": "precip_mm_h_p90", "type": "quantitative", "title": "Precipitation Rate (mm/h)"}
                }
            }
        ]
    }

    return {
        "a2ui_version": "v0.9",
        "card_type": "PROBABILISTIC_WEATHER_OBSERVABILITY",
        "title": f"Google DeepMind WeatherNext 3 · {weathernext_data.get('location_name')}",
        "subtitle": f"High-Resolution 0.05° Station Ensemble ({weathernext_data.get('corridor')})",
        "theme": "energy_dark",
        "summary_kpis": [
            {"label": "Peak Temp (p50)", "value": f"{metrics.get('peak_temperature_c')} °C"},
            {"label": "24h Precip (p90)", "value": f"{metrics.get('cumulative_precipitation_p90_mm')} mm"},
            {"label": "Max Hourly Rate", "value": f"{metrics.get('max_hourly_intensity_mm_h')} mm/h"},
            {"label": "Wind Vector", "value": metrics.get('dominant_wind_vector')},
            {"label": "Risk Envelope", "value": weathernext_data.get('risk_category')}
        ],
        "vega_lite_spec": vega_spec,
        "action_advisory": weathernext_data.get("action_protocol")
    }


def build_a2ui_scada_chart(telemetry_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": "Chhainsa Station 72h Telemetry: Linepack Pressure & Siemens GT Exhaust Temp",
        "data": {"values": telemetry_records},
        "width": 440,
        "height": 220,
        "encoding": {"x": {"field": "hour_index", "type": "quantitative", "title": "Historical Hours (-72h to Present)"}},
        "layer": [
            {
                "mark": {"type": "line", "color": "#58a6ff", "strokeWidth": 2.5},
                "encoding": {
                    "y": {
                        "field": "linepack_pressure_kg_cm2",
                        "type": "quantitative",
                        "title": "Linepack Pressure (kg/cm²)",
                        "scale": {"domain": [70, 85]}
                    }
                }
            },
            {
                "mark": {"type": "line", "color": "#f85149", "strokeDash": [5, 5], "strokeWidth": 1.8},
                "encoding": {
                    "y": {
                        "field": "siemens_gt_exhaust_temp_c",
                        "type": "quantitative",
                        "title": "Siemens GT Exhaust Temp (°C)",
                        "scale": {"domain": [520, 560]}
                    }
                }
            }
        ]
    }


def build_a2ui_forecast_chart(forecast_data: Dict[str, Any]) -> Dict[str, Any]:
    records = forecast_data.get("forecast_records", [])
    setpoint = forecast_data.get("setpoint_recommendation", {})
    
    return {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "card_type": "SARIMAX_PREDICTIVE_ADVISORY",
        "title": f"{forecast_data.get('model_type')} 24-Hour Predictive Line-Pack Trajectory",
        "data": {"values": records},
        "width": 440,
        "height": 220,
        "encoding": {"x": {"field": "hour_ahead", "type": "quantitative", "title": "Forecast Horizon (Hours Ahead)"}},
        "layer": [
            {
                "mark": {"type": "area", "opacity": 0.3, "color": "#238636"},
                "encoding": {
                    "y": {
                        "field": "conf_interval_95_lower",
                        "type": "quantitative",
                        "scale": {"domain": [68, 88]}
                    },
                    "y2": {"field": "conf_interval_95_upper"}
                }
            },
            {
                "mark": {"type": "line", "color": "#2ea043", "strokeWidth": 2.5},
                "encoding": {
                    "y": {
                        "field": "predicted_linepack_kg_cm2",
                        "type": "quantitative",
                        "title": "Predicted Linepack (kg/cm²)"
                    }
                }
            },
            {
                "mark": {"type": "rule", "color": "#f85149", "strokeWidth": 2, "strokeDash": [4, 4]},
                "encoding": {
                    "y": {"datum": forecast_data.get("critical_pressure_threshold_kg_cm2", 75.0)}
                }
            }
        ],
        "metadata": {
            "aic": forecast_data.get("aic"),
            "mape": forecast_data.get("mape_backtest_pct"),
            "recommended_setpoint": f"+{setpoint.get('throughput_adjustment_pct')}% at {setpoint.get('source_station')}",
            "annualized_savings": f"₹{setpoint.get('annualized_sanchay_inr_crores')} Crore / year"
        }
    }
