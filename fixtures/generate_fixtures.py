"""
Fixture generator for GAIL Pipeline Grid & Advisory Agent.
Generates:
  1. river_crossings_gis.geojson - HVJ pipeline geospatial coordinates & IMD flood alert overlay.
  2. gail_hvj_scada_telemetry_72h.csv - 72h Chhainsa history (pressure driven by supply-demand balance).
  3. customer_nominations_24h.json - Baseline vs revised customer nominations for the next 24h.
  4. lng_market_snapshot.json - Illustrative LNG benchmarks, freight and sourcing options.
  5. sap_order_template.json - S/4HANA Plant Maintenance notification & work order schema.
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

# -----------------------------------------------------------------------------
# V3 "One Morning at GAIL" scenario fixtures
# -----------------------------------------------------------------------------
# Physics used for the synthetic Chhainsa history (HVJ North segment):
#   line-pack inventory integrates the segment's supply-minus-demand balance
#       L_t = L_{t-1} + K_LINEPACK * net_balance_t
#   observed pressure = L_t + u_t,  u_t = 0.8 u_{t-1} + N(0, 0.25)  (sensor / flow noise)
# Compressors deliver a flat day-ahead schedule while demand swings with the day, so the
# line packs overnight and drafts in the daytime: a visible 24h cycle in the history.
# The SARIMAX model in app/analytics/sarimax_linepack.py re-learns K and the noise from
# this history, so the forecast (and its widening confidence cone) is fitted, not drawn.

import math
import random

K_LINEPACK = 0.125          # kg/cm² change per hour per 1 MMSCMD of imbalance
HISTORY_START = "2026-09-20 06:00:00"
FORECAST_START_HOUR = 6     # T+1 = 06:00 IST on 2026-09-23 ("It's 6 AM")
SURGE_FROM_HOUR_AHEAD = 3   # revised nominations bite from 08:00 (T+3)
SCHEDULED_SUPPLY_MMSCMD = 48.0   # flat day-ahead compressor schedule = mean baseline demand
INITIAL_LINEPACK_KG_CM2 = 83.5
NOISE_SIGMA, NOISE_PHI = 0.25, 0.8


def _baseline_demand(hod: int) -> dict:
    """Baseline sector off-take (MMSCMD) downstream of Chhainsa for hour-of-day."""
    fert = 15.0
    cgd = 8.35 + 1.2 * math.sin(2 * math.pi * (hod - 8) / 24)
    power = 14.0 + 2.0 * math.sin(2 * math.pi * (hod - 9) / 24)
    industrial = 10.65
    return {"fertilizer": fert, "cgd": cgd, "power": power, "industrial": industrial}


def generate_scada_history():
    """72h Chhainsa history where pressure is driven by the supply/demand balance."""
    rng = random.Random(42)
    rng_aux = random.Random(7)   # ambient / exhaust noise kept separate from the pressure series
    rows = []
    linepack = INITIAL_LINEPACK_KG_CM2
    noise = 0.0
    start_day, start_hod = 20, 6
    for i in range(72):
        hod = (start_hod + i) % 24
        day = start_day + (start_hod + i) // 24
        demand = sum(_baseline_demand(hod).values()) + rng.gauss(0, 0.3)
        # Compressors run a flat day-ahead schedule; demand swings with the day, so the
        # line packs overnight and drafts during the day.
        supply = SCHEDULED_SUPPLY_MMSCMD + rng.gauss(0, 0.3)
        net = round(supply - demand, 2)
        linepack = linepack + K_LINEPACK * (supply - demand)
        noise = NOISE_PHI * noise + rng.gauss(0, NOISE_SIGMA)
        pressure = linepack + noise
        ambient = 31.0 + 5.5 * math.sin(2 * math.pi * (hod - 9) / 24) + rng_aux.gauss(0, 0.4)
        exhaust = 538.0 + 0.9 * (supply - 48.0) + 0.6 * (ambient - 31.0) + rng_aux.gauss(0, 1.2)
        rows.append({
            "timestamp": f"2026-09-{day:02d} {hod:02d}:00:00",
            "hours_from_start": i,
            "station": "Chhainsa_CS",
            "pipeline": "HVJ_Trunkline",
            "linepack_pressure_kg_cm2": round(pressure, 2),
            "gas_flow_mmscmd": round(supply, 2),
            "segment_demand_mmscmd": round(demand, 2),
            "net_balance_mmscmd": round(net, 2),
            "ambient_temp_c": round(ambient, 1),
            "siemens_gt_exhaust_temp_c": round(exhaust, 1),
        })
    path = FIXTURES_DIR / "gail_hvj_scada_telemetry_72h.csv"
    cols = list(rows[0].keys())
    with open(path, "w", encoding="utf-8") as f:
        f.write(",".join(cols) + "\n")
        for r in rows:
            f.write(",".join(str(r[c]) for c in cols) + "\n")
    print(f"Generated {path} (last pressure {rows[-1]['linepack_pressure_kg_cm2']})")


def generate_customer_nominations():
    """Next 24h: baseline vs revised nominations (+20% Fertilizer, +12% CGD)."""
    feed = []
    for i in range(24):
        hod = (FORECAST_START_HOUR + i) % 24
        base = _baseline_demand(hod)
        surge = (i + 1) >= SURGE_FROM_HOUR_AHEAD
        rev = dict(base)
        if surge:
            rev["fertilizer"] = base["fertilizer"] * 1.20
            rev["cgd"] = base["cgd"] * 1.12
        ambient = 31.0 + 5.5 * math.sin(2 * math.pi * (hod - 9) / 24)
        day = 23 + (FORECAST_START_HOUR + i) // 24
        feed.append({
            "hour_ahead": i + 1,
            "timestamp": f"2026-09-{day:02d} {hod:02d}:00:00",
            "baseline_offtake_mmscmd": round(sum(base.values()), 3),
            "scheduled_supply_mmscmd": SCHEDULED_SUPPLY_MMSCMD,
            "scheduled_offtake_mmscmd": round(sum(rev.values()), 3),
            "fertilizer_hurl_nfl_mmscmd": round(rev["fertilizer"], 3),
            "cgd_delhi_haryana_mmscmd": round(rev["cgd"], 3),
            "power_plants_mmscmd": round(rev["power"], 3),
            "industrial_petchem_mmscmd": round(rev["industrial"], 3),
            "baseline_fertilizer_mmscmd": round(base["fertilizer"], 3),
            "baseline_cgd_mmscmd": round(base["cgd"], 3),
            "predicted_ambient_temp_c": round(ambient, 1),
            "demand_surge_flag": surge,
        })
    nominations = {
        "metadata": {
            "forecast_window_hours": 24,
            "start_timestamp": feed[0]["timestamp"],
            "end_timestamp": feed[-1]["timestamp"],
            "target_station": "Chhainsa_CS",
            "segment": "HVJ North (Vijaipur -> Chhainsa)",
            "revision_reason": "Rabi-season urea ramp at HURL/NFL (+20%) and CGD winter uptick (+12%)",
            "surge_from_hour_ahead": SURGE_FROM_HOUR_AHEAD,
            "linepack_sensitivity_kg_cm2_per_mmscmd_h": K_LINEPACK,
        },
        "hourly_exogenous_feed": feed,
    }
    path = FIXTURES_DIR / "customer_nominations_24h.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nominations, f, indent=2)
    print(f"Generated {path}")


def generate_lng_market_snapshot():
    """Illustrative LNG market & logistics inputs. NOT GAIL contract terms."""
    snapshot = {
        "disclaimer": "ILLUSTRATIVE DEMO VALUES - not GAIL contract terms or live market quotes.",
        "as_of": "2026-09-23 06:00 IST",
        "fx_inr_per_usd": 84.0,
        "cargo_size_mmbtu": 3200000,
        "delivery_terminal": "Dahej LNG Terminal",
        "regas_tariff_usd_mmbtu": 0.60,
        "benchmarks_usd_mmbtu": {"JKM": 13.60, "HENRY_HUB": 3.10, "BRENT_USD_BBL": 78.0, "TTF": 12.40},
        "options": [
            {
                "id": "SPOT_JKM",
                "label": "Spot cargo (JKM)",
                "formula": "JKM + premium + regas",
                "components": {"JKM": 13.60, "spot_premium": 0.25},
                "arrival_days": 5,
            },
            {
                "id": "US_HH_REROUTE",
                "label": "US Henry Hub re-route",
                "formula": "1.15 x HH + liquefaction + freight + regas",
                "components": {"HH_x_1.15": round(1.15 * 3.10, 3), "liquefaction": 2.75, "freight_cape_route": 3.10},
                "arrival_days": 34,
            },
            {
                "id": "QATAR_TIME_SWAP",
                "label": "Qatar time-swap",
                "formula": "12.67% x Brent + 0.50 + swap fee + freight + regas",
                "components": {"brent_slope_12.67pct": round(0.1267 * 78.0, 3), "constant": 0.50, "swap_fee": 0.40, "freight": 0.45},
                "arrival_days": 4,
            },
        ],
        "terminal_inventory_cover_days": 7,
    }
    path = FIXTURES_DIR / "lng_market_snapshot.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2)
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
    generate_scada_history()
    generate_customer_nominations()
    generate_lng_market_snapshot()
    generate_sap_order_template()
