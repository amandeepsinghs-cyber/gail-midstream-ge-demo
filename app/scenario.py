"""
Single source of truth for the "One Morning at GAIL" demo storyline.

Every tool, A2UI card and the executive report read their numbers from here, so the
shortfall, the LNG decision, the forecast and the savings always agree across all four beats:

    Problem (shortfall) -> Decision (LNG option) -> Proof (SARIMAX scenarios) -> Action (brief + SAP)
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict

from app.analytics.lng_landed_cost import evaluate_options
from app.analytics.sarimax_linepack import (
    CONTRACT_FLOOR_KG_CM2,
    SarimaxLinepackEngine,
    cached_scenarios,
)

SEGMENT = "HVJ North (Vijaipur → Chhainsa)"
MMBTU_PER_MMSCM = 37300.0  # approx. energy content of 1 MMSCM of pipeline gas


@lru_cache(maxsize=1)
def shortfall() -> Dict[str, Any]:
    """Tomorrow's shortfall = revised nominations − baseline nominations over the surge window."""
    df, meta = SarimaxLinepackEngine().load_exogenous_forecast()
    surge = df[df["demand_surge_flag"]]
    fert_delta = float((surge["fertilizer_hurl_nfl_mmscmd"] - surge["baseline_fertilizer_mmscmd"]).mean())
    cgd_delta = float((surge["cgd_delhi_haryana_mmscmd"] - surge["baseline_cgd_mmscmd"]).mean())
    total = round(fert_delta + cgd_delta, 1)
    return {
        "segment": SEGMENT,
        "shortfall_mmscmd": total,
        "fertilizer_delta_mmscmd": round(fert_delta, 2),
        "cgd_delta_mmscmd": round(cgd_delta, 2),
        "fertilizer_change_pct": 20.0,
        "cgd_change_pct": 12.0,
        "starts_hour_ahead": int(meta["metadata"].get("surge_from_hour_ahead", 3)),
        "starts_at": str(surge["timestamp"].iloc[0]),
        "reason": meta["metadata"].get("revision_reason", ""),
        "baseline_daily_offtake_mmscmd": round(float(df["baseline_offtake_mmscmd"].mean()), 2),
        "revised_daily_offtake_mmscmd": round(float(df["scheduled_offtake_mmscmd"].mean()), 2),
    }


@lru_cache(maxsize=1)
def lng_decision() -> Dict[str, Any]:
    gap = shortfall()["shortfall_mmscmd"]
    res = evaluate_options()
    days_covered = res["cargo_size_mmbtu"] / (gap * MMBTU_PER_MMSCM)
    res.update({
        "shortfall_mmscmd": gap,
        "dahej_sendout_increase_mmscmd": gap,
        "sendout_effective_hour_ahead": 6,
        "cargo_covers_days": round(days_covered, 0),
        "execution_plan": (
            f"Raise Dahej send-out by +{gap} MMSCMD from terminal inventory at T+6h; "
            f"inventory is replenished by the {res['recommended_option_label']} arriving in "
            f"{next(o['arrival_days'] for o in res['options'] if o['recommended'])} days."
        ),
    })
    return res


def forecast() -> Dict[str, Any]:
    return cached_scenarios(24)


def storyline() -> Dict[str, Any]:
    """Everything the decision brief needs, in one dict."""
    s = shortfall()
    d = lng_decision()
    f = forecast()
    sp = f["setpoint_recommendation"]
    return {
        "shortfall": s,
        "lng": d,
        "forecast": f,
        "contract_floor_kg_cm2": CONTRACT_FLOOR_KG_CM2,
        "headline": (
            f"{s['shortfall_mmscmd']} MMSCMD shortfall covered by {d['recommended_option_label']} "
            f"(₹{d['saving_vs_spot_inr_crore']} Cr cheaper than spot); line-pack held at "
            f"{f['with_swap_minimum_kg_cm2']} kg/cm² vs breach at T+{f['pressure_deficit_hour_ahead']}h "
            f"without action; Vijaipur +{sp['throughput_adjustment_pct']}%."
        ),
    }
