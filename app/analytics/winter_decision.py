"""
Winter supply decision: Qatar LNG is under force majeure. Lock in replacement cargoes now, or wait?

Joins 🏢 GAIL data (contract book, supply plan, procurement policy) with 🌐 market data
(live prices, winter futures, 5-year history, analyst consensus). All arithmetic is in code;
the LLM only narrates.

1. GAP (deterministic):   demand − (domestic + delivering contracts + planned inventory draw) → cargoes/month
2. PRICING (deterministic, live futures): what our contracts cost vs replacement spot, per winter month
3. STRATEGIES (stochastic): 10,000 seeded TTF paths; 5-year volatility; median path centred on the
   analyst consensus. Lock 100% now / hedge 50% / buy month by month → expected ₹ cost, P5–P95.
4. RECOMMENDATION (GAIL policy): cheapest expected strategy whose worst case (P95) overrun vs the
   board-approved budget stays within the board risk limit.
"""

from __future__ import annotations

import math
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

import numpy as np

PATHS, SEED, FAN_WEEKS = 10_000, 42, 52
STRATEGIES = [
    ("LOCK_ALL", "Lock in 100% now", 1.0),
    ("HEDGE_HALF", "Lock in 50% now, buy 50% at each deadline", 0.5),
    ("WAIT", "Wait: buy each month at its deadline (spot)", 0.0),
]


def _days_in(month: str) -> int:
    y, m = map(int, month.split("-"))
    nxt = date(y + (m == 12), m % 12 + 1, 1)
    return (nxt - date(y, m, 1)).days


def _label(month: str) -> str:
    y, m = map(int, month.split("-"))
    return date(y, m, 1).strftime("%b-%y")


def inr_crore(usd: float, fx: float) -> float:
    return usd * fx / 1e7


# --------------------------------------------------------------------------- 1. gap

def supply_gap(plan: Dict[str, Any], book: Dict[str, Any], usdinr: float) -> Dict[str, Any]:
    k = float(plan["mmbtu_per_mmscm"])
    cargo = float(book["cargo_size_mmbtu"])
    demand = sum(s["mmscmd"] for s in plan["winter_demand_mmscmd"])
    priority = sum(s["mmscmd"] for s in plan["winter_demand_mmscmd"] if s["priority"])
    non_priority = demand - priority
    domestic = float(plan["domestic_gas_allocation_mmscmd"])
    draw_tbtu = float(plan["dahej_inventory"]["planned_winter_drawdown_tbtu_per_month"])

    months = []
    for m in plan["months"]:
        days = _days_in(m)
        to_mmscmd = lambda cargoes: cargoes * cargo / days / k
        lng = sum(to_mmscmd(c["delivered_this_winter_cargoes_per_month"]) for c in book["contracts"])
        lost = sum(c["winter_cargoes_per_month"] - c["delivered_this_winter_cargoes_per_month"] for c in book["contracts"])
        draw = draw_tbtu * 1e6 / days / k
        supply = domestic + lng + draw
        gap = max(0.0, demand - supply)
        gap_mmbtu = gap * k * days
        months.append({
            "month": m, "label": _label(m), "days": days,
            "demand_mmscmd": round(demand, 1), "domestic_mmscmd": round(domestic, 1),
            "contract_lng_mmscmd": round(lng, 2), "inventory_draw_mmscmd": round(draw, 2),
            "supply_mmscmd": round(supply, 2), "gap_mmscmd": round(gap, 2),
            "gap_tbtu": round(gap_mmbtu / 1e6, 2), "cargoes_needed": int(round(gap_mmbtu / cargo)),
            "cargoes_lost_force_majeure": int(lost),
        })
    total_cargoes = sum(x["cargoes_needed"] for x in months)
    avg_gap = sum(x["gap_mmscmd"] for x in months) / len(months)
    fm = [c for c in book["contracts"] if c["status"] == "FORCE_MAJEURE"]
    return {
        "months": months,
        "total_cargoes_needed": total_cargoes,
        "total_gap_tbtu": round(sum(x["gap_tbtu"] for x in months), 1),
        "avg_gap_mmscmd": round(avg_gap, 2),
        "gap_pct_of_demand": round(avg_gap / demand * 100, 1),
        "force_majeure_contracts": [{"id": c["id"], "counterparty": c["counterparty"], "note": c["status_note"],
                                     "cargoes_per_month": c["winter_cargoes_per_month"]} for c in fm],
        "priority_demand_mmscmd": priority,
        "non_priority_demand_mmscmd": non_priority,
        "priority_customers_protected": avg_gap <= non_priority,
        "curtailment_if_not_covered_pct_of_non_priority": round(avg_gap / non_priority * 100, 1),
        "sectors": plan["winter_demand_mmscmd"],
        "exposure_inr_crore_per_usd1": round(inr_crore(total_cargoes * cargo, usdinr), 0),
        "inventory": plan["dahej_inventory"],
    }


# --------------------------------------------------------------------------- 2. pricing

def contract_economics(live: Dict[str, Any], book: Dict[str, Any], pol: Dict[str, Any], gap: Dict[str, Any]) -> Dict[str, Any]:
    regas = float(book["dahej_regas_usd_mmbtu"])
    prem = float(pol["india_spot_premium_to_ttf_usd_mmbtu"])
    cargo = float(book["cargo_size_mmbtu"])
    fx = float(live["usdinr"])
    by_id = {c["id"]: c for c in book["contracts"]}
    us, qa = by_id["LT-US-01"], by_id["LT-QATAR-01"]
    rows = []
    for fut in live["winter_futures"]:
        spot = fut["TTF_usd_mmbtu"] + prem + regas
        us_landed = (us["price_formula"]["hh_multiplier"] * fut["HENRY_HUB"] + us["price_formula"]["liquefaction_fee_usd_mmbtu"]
                     + us["freight_usd_mmbtu"] + regas)
        qa_landed = qa["price_formula"]["brent_slope"] * fut["BRENT"] + qa["price_formula"]["constant_usd_mmbtu"] + qa["freight_usd_mmbtu"] + regas
        rows.append({"month": fut["month"], "label": fut["label"],
                     "ttf_eur_mwh": fut["TTF"], "henry_hub": fut["HENRY_HUB"], "brent": fut["BRENT"],
                     "spot_replacement_usd_mmbtu": round(spot, 2), "us_contract_landed_usd_mmbtu": round(us_landed, 2),
                     "qatar_contract_landed_usd_mmbtu": round(qa_landed, 2),
                     "sources": {b: fut.get(f"{b}_source") for b in ("TTF", "HENRY_HUB", "BRENT")}})
    avg = lambda key: sum(r[key] for r in rows) / len(rows)
    lost_cargoes = sum(m["cargoes_lost_force_majeure"] for m in gap["months"])
    us_cargoes = us["delivered_this_winter_cargoes_per_month"] * len(rows)
    outage_cost_usd = sum((r["spot_replacement_usd_mmbtu"] - r["qatar_contract_landed_usd_mmbtu"]) * cargo
                          * qa["winter_cargoes_per_month"] for r in rows)
    us_value_usd = sum((r["spot_replacement_usd_mmbtu"] - r["us_contract_landed_usd_mmbtu"]) * cargo
                       * us["delivered_this_winter_cargoes_per_month"] for r in rows)
    return {
        "months": rows,
        "avg_spot_replacement_usd_mmbtu": round(avg("spot_replacement_usd_mmbtu"), 2),
        "avg_us_contract_landed_usd_mmbtu": round(avg("us_contract_landed_usd_mmbtu"), 2),
        "avg_qatar_contract_landed_usd_mmbtu": round(avg("qatar_contract_landed_usd_mmbtu"), 2),
        "qatar_outage_extra_cost_inr_crore": round(inr_crore(outage_cost_usd, fx), 0),
        "qatar_lost_cargoes": lost_cargoes,
        "us_cargoes_winter": us_cargoes,
        "us_cargoes_value_vs_spot_inr_crore": round(inr_crore(us_value_usd, fx), 0),
        "us_cargo_value_each_inr_crore": round(inr_crore(us_value_usd, fx) / max(us_cargoes, 1), 0),
        "formulas": {
            "spot_replacement": f"TTF + ${prem:.2f} (India premium, JKM proxy) + ${regas:.2f} regas",
            "us_contract": f"{us['price_formula']['text']} + ${us['freight_usd_mmbtu']:.2f} freight + ${regas:.2f} regas",
            "qatar_contract": f"{qa['price_formula']['text']} + ${qa['freight_usd_mmbtu']:.2f} freight + ${regas:.2f} regas",
        },
    }


# --------------------------------------------------------------------------- 3. strategies (Monte Carlo)

def ttf_stats(history_rows: List[Dict[str, Any]]) -> Dict[str, float]:
    x = np.array([r["ttf_usd_mmbtu"] for r in history_rows], dtype=float)
    lr = np.diff(np.log(x))
    return {"annual_vol": float(lr.std(ddof=1) * math.sqrt(52)), "weeks": int(len(x))}


def simulate_ttf(s0: float, consensus_12m: Optional[float], vol: float, n: int = PATHS, weeks: int = FAN_WEEKS,
                 seed: int = SEED) -> np.ndarray:
    """Log-price paths (n, weeks); median path reaches the consensus at 12 months."""
    mu = math.log(consensus_12m / s0) if consensus_12m else 0.0
    dt = 1.0 / 52
    z = np.random.default_rng(seed).standard_normal((n, weeks))
    return math.log(s0) + np.cumsum(mu * dt + vol * math.sqrt(dt) * z, axis=1)


def _at_day(log_paths: np.ndarray, days: float) -> np.ndarray:
    w = days / 7.0
    i = max(int(math.floor(w)) - 1, 0)
    f = min(max(w - math.floor(w), 0.0), 1.0)
    return np.exp((1 - f) * log_paths[:, i] + f * log_paths[:, min(i + 1, log_paths.shape[1] - 1)])


def evaluate_strategies(live: Dict[str, Any], history_rows: List[Dict[str, Any]], consensus_ttf_usd: Optional[float],
                        gap: Dict[str, Any], book: Dict[str, Any], pol: Dict[str, Any],
                        today: Optional[date] = None) -> Dict[str, Any]:
    today = today or date.today()
    fx = float(live["usdinr"])
    cargo = float(book["cargo_size_mmbtu"])
    adders = float(pol["india_spot_premium_to_ttf_usd_mmbtu"]) + float(book["dahej_regas_usd_mmbtu"])
    stats = ttf_stats(history_rows)
    logp = simulate_ttf(live["ttf_usd_mmbtu"], consensus_ttf_usd, stats["annual_vol"])
    fut = {f["month"]: f for f in live["winter_futures"]}
    lead = int(pol.get("cargo_procurement_lead_time_days", 45))

    lock_usd = 0.0
    forced_usd = 0.0                      # months past their deadline: must be locked in every strategy
    spot_usd = np.zeros(logp.shape[0])
    month_rows = []
    for m in gap["months"]:
        y, mo = map(int, m["month"].split("-"))
        decide_by = date(y, mo, 1) - timedelta(days=lead)
        days = (decide_by - today).days   # HARD RULE: waiting ends at the decision deadline
        vol_mmbtu = m["cargoes_needed"] * cargo
        lock_px = fut[m["month"]]["TTF_usd_mmbtu"] + adders
        forced = days <= 0
        if forced:
            forced_usd += lock_px * vol_mmbtu
            spot_px = np.full(logp.shape[0], lock_px)
        else:
            lock_usd += lock_px * vol_mmbtu
            spot_px = _at_day(logp, days) + adders
            spot_usd += spot_px * vol_mmbtu
        month_rows.append({"month": m["month"], "label": m["label"], "cargoes": m["cargoes_needed"],
                           "decide_by": decide_by.isoformat(), "decide_by_label": decide_by.strftime("%d %b %Y"),
                           "days_to_decide": days, "forced_lock": forced,
                           "days_ahead": days, "lock_in_usd_mmbtu": round(lock_px, 2),
                           "spot_p5": round(float(np.percentile(spot_px, 5)), 2),
                           "spot_p50": round(float(np.percentile(spot_px, 50)), 2),
                           "spot_p95": round(float(np.percentile(spot_px, 95)), 2)})

    total_mmbtu = gap["total_cargoes_needed"] * cargo
    budget_cr = inr_crore(float(pol["winter_budget_delivered_usd_mmbtu"]) * total_mmbtu, fx)
    limit = float(pol["risk_limit_p95_overrun_inr_crore"])
    out = []
    for sid, label, locked in STRATEGIES:
        cost = inr_crore(forced_usd + locked * lock_usd + (1 - locked) * spot_usd, fx)
        p = lambda q: float(np.percentile(cost, q))
        p95_overrun = p(95) - budget_cr
        out.append({"id": sid, "label": label, "locked_share": locked,
                    "expected_inr_crore": round(float(cost.mean()), 0), "p5_inr_crore": round(p(5), 0),
                    "p50_inr_crore": round(p(50), 0), "p95_inr_crore": round(p(95), 0),
                    "p95_overrun_vs_budget_inr_crore": round(p95_overrun, 0),
                    "within_risk_limit": bool(p95_overrun <= limit)})
    ok = [s for s in out if s["within_risk_limit"]]
    chosen = min(ok, key=lambda s: s["expected_inr_crore"]) if ok else min(out, key=lambda s: s["p95_inr_crore"])
    lock_all = next(s for s in out if s["id"] == "LOCK_ALL")
    wait = next(s for s in out if s["id"] == "WAIT")
    wait_cost = inr_crore(forced_usd + spot_usd, fx)
    lock_cost = inr_crore(forced_usd + lock_usd, fx)

    # Minimum share (of the cargoes still open) to lock so that P95 cost <= budget + limit. Lock-in cost is
    # certain, so P95(F + s*L + (1-s)*S) = F + s*L + (1-s)*P95(S) exactly -> solve for s, round up.
    ceiling = budget_cr + limit
    p95_wait = wait["p95_inr_crore"]
    if lock_cost > ceiling:
        min_share = None
    elif p95_wait <= ceiling:
        min_share = 0.0
    else:
        min_share = (p95_wait - ceiling) / (p95_wait - lock_cost)
    n_forced = sum(r["cargoes"] for r in month_rows if r["forced_lock"])
    n_open = gap["total_cargoes_needed"] - n_forced
    min_cargoes = None if min_share is None else n_forced + int(math.ceil(min_share * n_open - 1e-9))

    fan = []
    for k in range(logp.shape[1]):
        col = np.exp(logp[:, k])
        fan.append({"date": (today + timedelta(days=7 * (k + 1))).isoformat(),
                    **{f"p{q}": round(float(np.percentile(col, q)), 2) for q in (5, 25, 50, 75, 95)}})

    return {
        "paths": PATHS, "seed": SEED, "history_weeks": stats["weeks"],
        "ttf_annual_vol_pct": round(stats["annual_vol"] * 100, 0),
        "centred_on_consensus_ttf_usd_mmbtu": consensus_ttf_usd,
        "ttf_today_usd_mmbtu": live["ttf_usd_mmbtu"],
        "months": month_rows,
        "lead_time_days": lead,
        "cargoes_forced_lock": n_forced,
        "next_decision_deadline": next(({"month": r["label"], "decide_by": r["decide_by_label"], "days": r["days_to_decide"]}
                                        for r in month_rows if not r["forced_lock"]), None),
        "total_cargoes": gap["total_cargoes_needed"],
        "budget_inr_crore": round(budget_cr, 0),
        "budget_usd_mmbtu": pol["winter_budget_delivered_usd_mmbtu"],
        "risk_limit_inr_crore": limit,
        "strategies": out,
        "recommended_id": chosen["id"],
        "recommended_label": chosen["label"],
        "recommended_within_limit": chosen["within_risk_limit"],
        "prob_wait_cheaper_than_lock_pct": round(float((wait_cost < lock_cost).mean() * 100), 0),
        "expected_saving_if_wait_inr_crore": round(lock_all["expected_inr_crore"] - wait["expected_inr_crore"], 0),
        "min_share_to_lock_pct": None if min_share is None else round(min_share * 100, 0),
        "min_cargoes_to_lock": min_cargoes,
        "expected_saving_vs_lock_all_inr_crore": round(lock_all["expected_inr_crore"] - chosen["expected_inr_crore"], 0),
        "p95_protection_vs_wait_inr_crore": round(wait["p95_inr_crore"] - chosen["p95_inr_crore"], 0),
        "ttf_fan_12m": fan,
    }


def analysts_inside_fan(fan: List[Dict[str, Any]], forecasts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Sanity check: TTF analyst forecasts vs the simulated P5–P95 fan at their period."""
    inside, total, detail = 0, 0, []
    dates = [date.fromisoformat(f["date"]) for f in fan]
    for r in forecasts:
        if r["benchmark"] != "TTF":
            continue
        d = date.fromisoformat(r["period_mid"])
        i = min(range(len(dates)), key=lambda j: abs(dates[j] - d))
        if abs(dates[i] - d).days > 45:
            continue
        total += 1
        ok = fan[i]["p5"] <= r["value_usd_mmbtu"] <= fan[i]["p95"]
        inside += int(ok)
        detail.append({"institution": r["institution"], "period": r["period"], "inside": ok})
    return {"inside": inside, "total": total, "detail": detail}


# --------------------------------------------------------------------------- 5. GAIL's own position

def approver_for(value_inr_crore: float, pol: Dict[str, Any]) -> str:
    """Delegation of financial powers: who must sign for a purchase of this value."""
    for band in pol.get("delegation_of_authority", []):
        if band["up_to_inr_crore"] is None or value_inr_crore <= band["up_to_inr_crore"]:
            return band["approver"]
    return pol.get("approver", "Director (Marketing)")


def internal_position(plan: Dict[str, Any], book: Dict[str, Any], pol: Dict[str, Any], sap: Dict[str, Any],
                      gap: Dict[str, Any], strat: Dict[str, Any], usdinr: float) -> Dict[str, Any]:
    """🏢 Everything GAIL's own systems say about the decision: tanks, customers, SAP, budget, deadlines."""
    cargo_tbtu = float(book["cargo_size_mmbtu"]) / 1e6
    inv = plan["dahej_inventory"]
    usable = float(inv["current_tbtu"]) - float(inv["minimum_operating_tbtu"])
    month_gap_tbtu = max(m["gap_tbtu"] for m in gap["months"])
    comp = float(plan.get("firm_gsa_shortfall_compensation_usd_mmbtu", 0.0))
    comp_per_cargo = inr_crore(comp * float(book["cargo_size_mmbtu"]), usdinr)
    pos = sap.get("open_purchase_orders_winter", [])
    covering = sum(p["cargoes"] for p in pos if p.get("covers_gap"))
    blocked = [p for p in pos if "block" in p.get("status", "").lower()]
    committed = float(sap.get("replacement_budget_committed_inr_crore", 0.0))
    lock_all = next(s for s in strat["strategies"] if s["id"] == "LOCK_ALL")
    lock_cost = lock_all["expected_inr_crore"]
    return {
        "inventory": {
            "current_tbtu": inv["current_tbtu"], "minimum_tbtu": inv["minimum_operating_tbtu"],
            "usable_tbtu": round(usable, 1), "usable_cargo_equivalent": round(usable / cargo_tbtu, 1),
            "cover_days": inv["cover_days_at_current_sendout"],
            "one_month_gap_tbtu": round(month_gap_tbtu, 1),
            "can_absorb_a_missed_month": usable >= month_gap_tbtu,
        },
        "customers": {
            "must_supply_mmscmd": gap["priority_demand_mmscmd"],
            "total_demand_mmscmd": gap["priority_demand_mmscmd"] + gap["non_priority_demand_mmscmd"],
            "must_supply_sectors": [s["sector"] for s in plan["winter_demand_mmscmd"] if s["priority"]],
            "curtailment_if_uncovered_pct": gap["curtailment_if_not_covered_pct_of_non_priority"],
            "compensation_per_missed_cargo_inr_crore": round(comp_per_cargo, 0),
        },
        "sap": {
            "open_pos": pos, "cargoes_already_covering_gap": covering,
            "gap_still_open_cargoes": gap["total_cargoes_needed"] - covering,
            "blocked_pos": blocked,
            "budget_inr_crore": strat["budget_inr_crore"], "committed_inr_crore": committed,
            "available_inr_crore": round(strat["budget_inr_crore"] - committed, 0),
            "lock_all_cost_inr_crore": lock_cost,
            "lock_all_vs_budget_inr_crore": round(lock_cost - strat["budget_inr_crore"], 0),
            "funds_centre": sap.get("funds_centre"),
        },
        "deadlines": [{"month": r["label"], "cargoes": r["cargoes"], "decide_by": r["decide_by_label"],
                       "days_left": r["days_to_decide"], "forced_lock": r["forced_lock"]} for r in strat["months"]],
        "lead_time_days": strat["lead_time_days"],
        "next_deadline": strat["next_decision_deadline"],
        "approver_for_lock_all": approver_for(lock_cost, pol),
        "risk_limit_inr_crore": strat["risk_limit_inr_crore"],
    }
