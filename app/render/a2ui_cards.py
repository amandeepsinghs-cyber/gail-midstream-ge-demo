"""
A2UI v0.9 Component Renderer for GAIL Pipeline Grid & Advisory Agent.
Generates structured A2UI payloads with embedded Vega-Lite chart specifications:
  - Spatial GIS Map Card (HVJ Corridor & IMD Weather Alerts)
  - SCADA 72h Multi-variable Telemetry Chart
  - SARIMAX Predictive Demand & Deficit Forecast Chart
  - Executive KPI & Project Sanchay Savings Card
"""

from typing import Dict, Any, List

def build_a2ui_spatial_map_card(geojson_data: Dict[str, Any], alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Renders A2UI v0.9 card for Act 1: Spatial Grid & Environmental Weather Overlay."""
    return {
        "a2ui_version": "v0.9",
        "card_type": "SPATIAL_INFRASTRUCTURE_MONITOR",
        "title": "GAIL National Gas Grid - 18,700 km Spatial Network & IMD Risk Layer",
        "subtitle": "HVJ Trunkline Corridor & Active River Crossing Vulnerability Audit",
        "layout": "split_map_and_alerts",
        "theme": "energy_dark",
        "map_layers": {
            "pipeline_geojson": geojson_data,
            "corridors": ["Hazira-Vijaipur-Jagdishpur (HVJ)", "MNJPL (Samruddhi Expressway)"],
            "highlighted_assets": [
                {"name": "Vijaipur Compressor Hub", "coords": [77.2941, 24.1627], "type": "COMPRESSOR_HUB"},
                {"name": "Chhainsa Compressor Station", "coords": [77.3412, 28.2711], "type": "PRESSURE_STATION"},
                {"name": "Gauna-Bawana Yamuna Crossing", "coords": [77.0315, 28.7912], "type": "HIGH_RISK_CROSSING"}
            ]
        },
        "active_alerts": alerts,
        "actions": [
            {"label": "Inspect Chhainsa Telemetry", "command": "query_scada_telemetry station='Chhainsa_CS'"},
            {"label": "Run SARIMAX Demand Forecast", "command": "run_sarimax_linepack_forecast"}
        ]
    }


def build_a2ui_scada_chart(telemetry_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Renders A2UI v0.9 Vega-Lite chart for Act 2: 72h Multi-Variable SCADA Telemetry."""
    return {
        "a2ui_version": "v0.9",
        "card_type": "TELEMETRY_MULTI_TIMESERIES",
        "title": "Chhainsa Compressor Station - 72-Hour SCADA & Turbine Telemetry",
        "subtitle": "Yokogawa FAST/TOOLS SCADA & Siemens RDS Turbine Exhaust Feeds",
        "vega_lite_spec": {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "width": 680,
            "height": 280,
            "data": {"values": telemetry_data},
            "encoding": {
                "x": {"field": "timestamp", "type": "temporal", "title": "Timestamp (Hourly)"}
            },
            "layer": [
                {
                    "mark": {"type": "line", "color": "#1a73e8", "strokeWidth": 2.5},
                    "encoding": {
                        "y": {
                            "field": "linepack_pressure_kg_cm2",
                            "type": "quantitative",
                            "scale": {"domain": [70, 85]},
                            "title": "Linepack Pressure (kg/cm²)"
                        },
                        "tooltip": [
                            {"field": "timestamp", "type": "temporal"},
                            {"field": "linepack_pressure_kg_cm2", "title": "Pressure (kg/cm²)"},
                            {"field": "gas_flow_mmscmd", "title": "Flow (MMSCMD)"},
                            {"field": "siemens_gt_exhaust_temp_c", "title": "Turbine Exhaust (°C)"}
                        ]
                    }
                },
                {
                    "mark": {"type": "line", "color": "#ea4335", "strokeDash": [4, 4], "strokeWidth": 1.5},
                    "encoding": {
                        "y": {
                            "field": "gas_flow_mmscmd",
                            "type": "quantitative",
                            "title": "Flow Throughput (MMSCMD)"
                        }
                    }
                }
            ]
        },
        "kpis": [
            {"label": "Latest Line-Pack Pressure", "value": "81.47 kg/cm²", "status": "NORMAL"},
            {"label": "Average Throughput", "value": "48.05 MMSCMD", "status": "OPTIMAL"},
            {"label": "Max Turbine Exhaust Temp", "value": "549.4 °C", "status": "ELEVATED_HEAVY_LOAD"}
        ]
    }


def build_a2ui_forecast_chart(forecast_data: Dict[str, Any]) -> Dict[str, Any]:
    """Renders A2UI v0.9 Vega-Lite chart for Act 3: SARIMAX Forecast with 95% Confidence Interval & Setpoint trigger."""
    hourly_records = forecast_data.get("hourly_forecast", [])
    setpoint = forecast_data.get("setpoint_recommendation", {})
    
    return {
        "a2ui_version": "v0.9",
        "card_type": "SARIMAX_PREDICTIVE_ADVISORY",
        "title": "SARIMAX 24-Hour Predictive Line-Pack Demand Forecast",
        "subtitle": "Chhainsa Station | Exogenous Customer Off-take Surge & Ambient Thermal Regressors",
        "vega_lite_spec": {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "width": 680,
            "height": 280,
            "data": {"values": hourly_records},
            "layer": [
                {
                    "mark": {"type": "area", "opacity": 0.2, "color": "#34a853"},
                    "encoding": {
                        "x": {"field": "timestamp", "type": "temporal", "title": "Forecast Horizon (Hours Ahead)"},
                        "y": {"field": "lower_ci_95", "type": "quantitative", "title": "Line-Pack Pressure (kg/cm²)"},
                        "y2": {"field": "upper_ci_95"}
                    }
                },
                {
                    "mark": {"type": "line", "color": "#188038", "strokeWidth": 3},
                    "encoding": {
                        "x": {"field": "timestamp", "type": "temporal"},
                        "y": {"field": "predicted_linepack_kg_cm2", "type": "quantitative"},
                        "tooltip": [
                            {"field": "hour_ahead", "title": "Hour Ahead"},
                            {"field": "predicted_linepack_kg_cm2", "title": "Predicted Pressure (kg/cm²)"},
                            {"field": "scheduled_offtake_mmscmd", "title": "Offtake (MMSCMD)"},
                            {"field": "ambient_temp_c", "title": "Ambient Temp (°C)"}
                        ]
                    }
                },
                {
                    "mark": {"type": "rule", "color": "#d93025", "strokeWidth": 2, "strokeDash": [5, 5]},
                    "encoding": {
                        "y": {"datum": 76.0}
                    }
                }
            ]
        },
        "advisory_box": {
            "flag": "PREDICTED DEFICIT AT HOUR 14 AHEAD",
            "recommended_action": f"Increase {setpoint.get('target_station')} throughput by +{setpoint.get('throughput_adjustment_pct')}% at {setpoint.get('action_hour')}",
            "fuel_savings": f"{setpoint.get('fuel_gas_savings_scm_day'):,.0f} SCM/day",
            "project_sanchay_annual_roi": "₹16.8 Crore / year"
        }
    }
