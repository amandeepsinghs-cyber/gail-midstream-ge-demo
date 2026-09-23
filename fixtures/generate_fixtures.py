"""
Fixture generator for GAIL Pipeline Grid & Advisory Agent.
Generates:
  1. river_crossings_gis.geojson - HVJ pipeline geospatial coordinates & IMD flood alert overlay.
  2. customer_nominations_24h.json - Leading exogenous demand off-take and IMD temperature forecasts.
  3. sap_order_template.json - S/4HANA Plant Maintenance notification & work order schema.
"""

import json
from pathlib import Path

FIXTURES_DIR = Path(__file__).resolve().parent

def generate_gis_geojson():
    geojson_data = {
        "type": "FeatureCollection",
        "metadata": {
            "network": "GAIL National Gas Grid - HVJ Trunkline",
            "total_km": 18700,
            "generated_for": "Act 1: Spatial GIS & Weather Overlay"
        },
        "features": [
            {
                "type": "Feature",
                "id": "PIPE-HVJ-01",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [72.7311, 21.1702],  # Hazira Terminal
                        [75.8577, 22.7196],  # Indore Spur
                        [77.2941, 24.1627],  # Vijaipur Compressor Hub
                        [77.3412, 28.2711],  # Chhainsa Compressor Station
                        [77.5539, 28.5516],  # Dadri Delivery Station
                        [77.0315, 28.7912],  # Bawana / Yamuna River Crossing
                        [76.8512, 29.3909]   # Nangal Extension
                    ]
                },
                "properties": {
                    "name": "Hazira-Vijaipur-Jagdishpur (HVJ) Trunkline",
                    "diameter_inches": 36,
                    "design_pressure_kg_cm2": 85.0,
                    "operating_status": "NORMAL_TRANSMISSION"
                }
            },
            {
                "type": "Feature",
                "id": "STN-VIJAIPUR",
                "geometry": {
                    "type": "Point",
                    "coordinates": [77.2941, 24.1627]
                },
                "properties": {
                    "name": "Vijaipur Compressor Hub",
                    "station_type": "PRIMARY_COMPRESSION_HUB",
                    "active_turbines": 8,
                    "siemens_gt_units": ["GT-01", "GT-02", "GT-03", "GT-04"],
                    "current_throughput_mmscmd": 48.5,
                    "status": "OPERATIONAL"
                }
            },
            {
                "type": "Feature",
                "id": "STN-CHHAINSA",
                "geometry": {
                    "type": "Point",
                    "coordinates": [77.3412, 28.2711]
                },
                "properties": {
                    "name": "Chhainsa Compressor Station",
                    "station_type": "SECONDARY_PRESSURE_BOOST",
                    "current_linepack_kg_cm2": 81.47,
                    "siemens_gt_units": ["GT-CH-1", "GT-CH-2"],
                    "status": "OPERATIONAL"
                }
            },
            {
                "type": "Feature",
                "id": "RISK-YAMUNA-CROSSING",
                "geometry": {
                    "type": "Point",
                    "coordinates": [77.0315, 28.7912]
                },
                "properties": {
                    "name": "Gauna-Bawana Yamuna River Crossing",
                    "asset_class": "SUBMERGED_PIPELINE_CROSSING",
                    "environmental_alert": "HIGH_RISK_FLASH_FLOOD_WARNING",
                    "river_gauge_level_m": 206.4,
                    "danger_mark_m": 205.33,
                    "imd_rainfall_alert": "HEAVY_TO_VERY_HEAVY (115.6mm)",
                    "scada_hydraulic_stress": "ELEVATED_VIBRATION_ALERT",
                    "incident_reference": "Preemptive monitoring post Gauna-Bawana Yamuna flash flood breach"
                }
            }
        ]
    }
    path = FIXTURES_DIR / "river_crossings_gis.geojson"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(geojson_data, f, indent=2)
    print(f"Generated {path}")

def generate_customer_nominations():
    """Generates the next 24 hours of leading exogenous variables (X)."""
    nominations = {
        "metadata": {
            "forecast_window_hours": 24,
            "start_timestamp": "2026-09-23 00:00:00",
            "end_timestamp": "2026-09-23 23:00:00",
            "target_station": "Chhainsa_CS"
        },
        "hourly_exogenous_feed": []
    }
    
    # 24 hours ahead
    # At hour 10-14 (10:00 to 14:00), downstream fertilizer plants (HURL/NFL) surge draw
    # Ambient temp peaks at 42.1 C
    for h in range(24):
        time_str = f"2026-09-23 {h:02d}:00:00"
        if 8 <= h <= 17:
            # Daytime peak demand
            fert_demand = 18.5 + (2.5 if 10 <= h <= 15 else 0.5)
            cgd_demand = 14.0 + (3.0 if 8 <= h <= 12 else 1.0)
            power_demand = 19.5 + (4.0 if 12 <= h <= 16 else 1.5)
            ambient_temp = 36.5 + (5.5 if 12 <= h <= 16 else 2.0)
        else:
            # Night off-peak
            fert_demand = 15.0
            cgd_demand = 8.5
            power_demand = 14.0
            ambient_temp = 31.0 + (1.5 if h >= 20 else -1.0)
            
        total_offtake = round(fert_demand + cgd_demand + power_demand, 2)
        
        nominations["hourly_exogenous_feed"].append({
            "hour_ahead": h + 1,
            "timestamp": time_str,
            "scheduled_offtake_mmscmd": total_offtake,
            "fertilizer_hurl_nfl_mmscmd": fert_demand,
            "cgd_delhi_haryana_mmscmd": cgd_demand,
            "power_plants_mmscmd": power_demand,
            "predicted_ambient_temp_c": round(ambient_temp, 1),
            "demand_surge_flag": total_offtake > 52.0
        })
        
    path = FIXTURES_DIR / "customer_nominations_24h.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nominations, f, indent=2)
    print(f"Generated {path}")

def generate_sap_order_template():
    sap_template = {
        "system": "RISE with SAP S/4HANA Cloud (Project Navodaya)",
        "maintenance_notification_type": "M2 - Breakdown/Preventive Calibration",
        "plant": "1102 - GAIL Vijaipur Compressor Station",
        "work_center": "MECH-COMP-01",
        "order_type": "PM01 - Preventive Maintenance",
        "default_priority": "2 - High",
        "default_activity_type": "CALIB",
        "gl_account": "0000421000 - Plant Maintenance Expenses",
        "cost_center": "GAIL-VIJ-OPS"
    }
    path = FIXTURES_DIR / "sap_order_template.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(sap_template, f, indent=2)
    print(f"Generated {path}")

if __name__ == "__main__":
    generate_gis_geojson()
    generate_customer_nominations()
    generate_sap_order_template()
