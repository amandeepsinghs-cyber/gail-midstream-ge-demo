"""
V4 agent tools: "Qatar is under force majeure. Lock in winter cargoes now, or wait?"

Each tool answers one business question, joins 🏢 GAIL data with 🌐 market data, returns a SHORT
summary to the model (numbers to narrate) and stashes the full payload for the A2UI card.

    DATA      Q1 assess_winter_supply_gap      🏢 contract book, GMS nominations  (+ 🌐 news sub-agent)
    DATA      Q2 check_gail_position           🏢 Dahej inventory, customer commitments, SAP open POs & budget, deadlines
    DATA      Q3 get_live_gas_market           🌐 live prices + winter futures  × 🏢 contract formulas, SAP budget
    ANALYSIS  Q4 get_gas_price_history         🌐 5-year weekly history
    ANALYSIS  Q5 get_analyst_price_outlook     �� dated, sourced analyst forecasts
    DECISION  Q6 evaluate_winter_procurement   Monte Carlo: 🌐 futures, volatility, consensus × 🏢 all of the above
    ACTION    Q7 prepare_procurement_approval  🏢 SAP purchase requisition + approval memo (human approves)
"""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime
from typing import Any, Dict, Optional

try:
    from google.adk.tools import ToolContext
except ImportError:  # pragma: no cover
    ToolContext = Any

from app.analytics import winter_decision as wd
from app.integration import gail_data
from app.market import yahoo_feed
from app.market.analyst_outlook import outlook as analyst_outlook

logger = logging.getLogger(__name__)

PENDING_GAP_KEY = "pending_v4_gap"
PENDING_MARKET_KEY = "pending_v4_market"
PENDING_HISTORY_KEY = "pending_v4_history"
PENDING_OUTLOOK_KEY = "pending_v4_outlook"
PENDING_STRATEGY_KEY = "pending_v4_strategy"
PENDING_POSITION_KEY = "pending_v4_position"
PENDING_APPROVAL_KEY = "pending_v4_approval"
V4_PENDING_KEYS = [PENDING_APPROVAL_KEY, PENDING_STRATEGY_KEY, PENDING_POSITION_KEY, PENDING_OUTLOOK_KEY,
                   PENDING_HISTORY_KEY, PENDING_MARKET_KEY, PENDING_GAP_KEY]  # card priority order

SRC_BOOK = "🏢 GAIL contract book (sample)"
SRC_GMS = "🏢 GAIL GMS nominations & Dahej inventory (sample)"
SRC_POLICY = "🏢 GAIL procurement policy: budget & board risk limit (sample)"
SRC_SAP = "🏢 RISE with SAP S/4HANA (Project Navodaya)"
SRC_SAP_POS = "🏢 SAP open purchase orders & LNG budget (sample)"
SRC_INV = "🏢 Dahej terminal inventory (sample)"
SRC_ANALYSTS = "🌐 Published analyst forecasts (dated, sourced)"
SAMPLE_NOTE = "GAIL figures are sample data; your systems plug in here."

_session: Dict[str, Any] = {}


def _stash(tool_context: Any, key: str, value: Dict[str, Any]) -> None:
    if tool_context is not None and getattr(tool_context, "state", None) is not None:
        try:
            tool_context.state[key] = value
        except Exception:
            pass


def _market_src(live: Dict[str, Any]) -> str:
    return f"🌐 {live.get('source_label', 'Yahoo Finance')}"


# --------------------------------------------------------------------------- shared context

def context() -> Dict[str, Any]:
    """Everything the tools need, computed once per live-price refresh (15 min)."""
    live = yahoo_feed.live_snapshot()
    key = live.get("as_of_ist")
    if _session.get("key") == key:
        return _session["ctx"]
    hist = yahoo_feed.price_history(5)
    book, plan, pol, sap = gail_data.contract_book(), gail_data.supply_plan(), gail_data.policy(), gail_data.sap_position()
    outl = analyst_outlook(live["eurusd"])
    gap = wd.supply_gap(plan, book, live["usdinr"])
    econ = wd.contract_economics(live, book, pol, gap)
    strat = wd.evaluate_strategies(live, hist["rows"], outl["consensus_usd_mmbtu"]["TTF"], gap, book, pol)
    strat["analyst_check"] = wd.analysts_inside_fan(strat["ttf_fan_12m"], outl["forecasts"])
    position = wd.internal_position(plan, book, pol, sap, gap, strat, live["usdinr"])
    ctx = {"live": live, "hist": hist, "book": book, "plan": plan, "policy": pol, "sap": sap,
           "outlook": outl, "gap": gap, "econ": econ, "strategy": strat, "position": position}
    _session.update(key=key, ctx=ctx)
    return ctx


# --------------------------------------------------------------------------- Q1

def assess_winter_supply_gap(tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    """
    Q1 (Problem): How exposed is GAIL this winter? Reads GAIL's contract book (Qatar long-term
    contract under force majeure), winter customer nominations by sector, domestic allocation and
    Dahej inventory, and computes the Dec–Feb supply gap in cargoes, which customers are exposed
    (fertilizer and CGD have priority), and the ₹ exposure to every $1/MMBtu price move.
    Use for: impact of the Qatar force majeure on our winter supply, winter gap, exposure, what's hitting supply.
    """
    c = context()
    g, live = c["gap"], c["live"]
    payload = {"gap": g, "live_fx": live["usdinr"], "sources": [SRC_BOOK, SRC_GMS], "note": SAMPLE_NOTE}
    _stash(tool_context, PENDING_GAP_KEY, payload)
    return {
        "force_majeure": [f"{f['counterparty']}: {f['cargoes_per_month']} cargoes/month lost" for f in g["force_majeure_contracts"]],
        "winter_gap_by_month": {m["label"]: f"{m['cargoes_needed']} cargoes ({m['gap_mmscmd']} MMSCMD)" for m in g["months"]},
        "total_cargoes_needed": g["total_cargoes_needed"],
        "total_gap_tbtu": g["total_gap_tbtu"],
        "gap_pct_of_demand": g["gap_pct_of_demand"],
        "priority_customers_protected": g["priority_customers_protected"],
        "if_not_covered": f"{g['curtailment_if_not_covered_pct_of_non_priority']}% cut to refinery, power and other industrial customers; fertilizer and CGD protected",
        "exposure_inr_crore_per_usd1_mmbtu": g["exposure_inr_crore_per_usd1"],
        "sources": [SRC_BOOK, SRC_GMS],
        "data_note": SAMPLE_NOTE,
    }


# --------------------------------------------------------------------------- Q2

def get_live_gas_market(tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    """
    Q3 (Data, market today): Live Henry Hub, TTF, Brent, ₹/$ and winter futures from Yahoo Finance, all in
    USD/MMBtu, joined with GAIL's contract formulas and SAP budget: what our US contract cargo lands at vs
    the replacement spot price, what the Qatar outage costs GAIL this winter, and what locking in all
    replacement cargoes at today's futures would cost vs the replacement budget in SAP.
    Use for: gas prices today, market prices, Henry Hub, TTF, Brent, what it means for our contracts and budget.
    """
    c = context()
    live, econ = c["live"], c["econ"]
    sap = c["position"]["sap"]
    budget_line = (f"Locking in all {c['gap']['total_cargoes_needed']} replacement cargoes at today's futures costs ₹{sap['lock_all_cost_inr_crore']:,.0f} Cr, "
                   f"₹{abs(sap['lock_all_vs_budget_inr_crore']):,.0f} Cr {'over' if sap['lock_all_vs_budget_inr_crore'] > 0 else 'under'} "
                   f"the ₹{sap['budget_inr_crore']:,.0f} Cr replacement budget in SAP.")
    payload = {"live": live, "econ": econ, "budget_line": budget_line,
               "sources": [_market_src(live), SRC_BOOK, SRC_SAP_POS], "note": SAMPLE_NOTE}
    _stash(tool_context, PENDING_MARKET_KEY, payload)
    return {
        "as_of": live["source_label"],
        "henry_hub_usd_mmbtu": live["henry_hub_usd_mmbtu"],
        "ttf": f"€{live['ttf_eur_mwh']}/MWh = ${live['ttf_usd_mmbtu']}/MMBtu",
        "brent_usd_bbl": live["brent_usd_bbl"],
        "usdinr": live["usdinr"],
        "europe_vs_us_multiple": round(live["ttf_usd_mmbtu"] / live["henry_hub_usd_mmbtu"], 1),
        "winter_spot_replacement_usd_mmbtu": econ["avg_spot_replacement_usd_mmbtu"],
        "our_us_contract_landed_usd_mmbtu": econ["avg_us_contract_landed_usd_mmbtu"],
        "our_qatar_contract_would_have_landed_usd_mmbtu": econ["avg_qatar_contract_landed_usd_mmbtu"],
        "qatar_outage_extra_cost_this_winter_inr_crore": econ["qatar_outage_extra_cost_inr_crore"],
        "each_us_cargo_worth_vs_spot_inr_crore": econ["us_cargo_value_each_inr_crore"],
        "lock_in_cost_vs_sap_budget": budget_line,
        "note": "JKM is licensed (Platts); India spot estimated as TTF + premium. " + SAMPLE_NOTE,
        "sources": payload["sources"],
    }


# --------------------------------------------------------------------------- Q3

def get_gas_price_history(tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    """
    Q4 (Analysis, history): 5 years of weekly TTF (Europe) vs Henry Hub (US) vs Brent oil-parity prices from
    Yahoo Finance, in USD/MMBtu: the 2022 crisis spike, today's spike, the Europe–US spread and the
    measured volatility (which drives the risk simulation).
    Use for: price history, 5 years, trend, 2022, spread, volatility.
    """
    c = context()
    rows, live = c["hist"]["rows"], c["live"]
    peak = max(rows, key=lambda r: r["ttf_usd_mmbtu"])
    spreads = [r["ttf_usd_mmbtu"] - r["henry_hub"] for r in rows]
    stats = wd.ttf_stats(rows)
    summary = {
        "period": f"{rows[0]['date']} to {rows[-1]['date']} ({len(rows)} weeks)",
        "ttf_peak": f"${peak['ttf_usd_mmbtu']}/MMBtu (€{peak['ttf_eur_mwh']}/MWh) in week of {peak['date']}",
        "ttf_today_usd_mmbtu": rows[-1]["ttf_usd_mmbtu"],
        "ttf_5y_low_usd_mmbtu": min(r["ttf_usd_mmbtu"] for r in rows),
        "henry_hub_today": rows[-1]["henry_hub"],
        "spread_today_usd_mmbtu": round(spreads[-1], 2),
        "spread_5y_average_usd_mmbtu": round(sum(spreads) / len(spreads), 2),
        "ttf_annual_volatility_pct": round(stats["annual_vol"] * 100, 0),
        "sources": [_market_src(c["hist"])],
    }
    _stash(tool_context, PENDING_HISTORY_KEY, {"rows": rows, "summary": summary, "sources": summary["sources"]})
    return summary


# --------------------------------------------------------------------------- Q4

def get_analyst_price_outlook(tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    """
    Q5 (Analysis, outlook): What do the experts expect? Published, dated TTF, Henry Hub and Brent forecasts from
    named institutions (BofA, Goldman Sachs, Fitch, US EIA, Enverus), converted to USD/MMBtu, with the
    consensus (median of 2027 forecasts), the spread of views, and today's winter futures for comparison.
    Use for: analyst forecasts, outlook, what do experts expect, consensus, next 12 months.
    """
    c = context()
    o, live = c["outlook"], c["live"]
    payload = {"outlook": o, "live": live, "sources": [SRC_ANALYSTS, _market_src(live)]}
    _stash(tool_context, PENDING_OUTLOOK_KEY, payload)
    ttf = [r for r in o["forecasts"] if r["benchmark"] == "TTF"]
    return {
        "ttf_forecasts": [f"{r['institution']} (published {r['published']}): {r['period']} = {r['value']} {r['unit']} "
                          f"(= ${r['value_usd_mmbtu']:.2f}/MMBtu)" for r in ttf],
        "ttf_consensus_2027": f"€{o['consensus_ttf_eur_mwh']}/MWh (${o['consensus_usd_mmbtu']['TTF']}/MMBtu)",
        "ttf_winter_futures_today": f"€{live['winter_futures'][0]['TTF']}/MWh (Dec)",
        "henry_hub_consensus_2027": o["consensus_usd_mmbtu"]["HENRY_HUB"],
        "brent_consensus_2027_usd_bbl": o["consensus_brent_usd_bbl"],
        "institutions": o["institutions"],
        "collected_on": o["collected_on"],
        "message": "Analysts disagree widely; the market (futures) prices winter far above the 2027 consensus.",
        "sources": [SRC_ANALYSTS],
    }


# --------------------------------------------------------------------------- Q5

def check_gail_position(tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    """
    Q2 (Data, our own position, GAIL internal data only): checks GAIL's own systems: Dahej terminal
    inventory (usable stock, days of cover, can it absorb a missed month?), customer commitments
    (must-supply fertilizer and city gas, compensation owed to firm customers per missed cargo),
    SAP open purchase orders for the winter (what already covers the gap; the blocked Qatar order),
    the replacement budget in SAP (approved and committed), the latest date each month's cargoes
    must be contracted (procurement lead time), and who must approve under the delegation of authority.
    Use for: check our position, inventory, tanks, stock, customer commitments, SAP, open orders,
    budget, deadline, how long can we wait, before we decide.
    """
    c = context()
    p = c["position"]
    inv, cust, sap = p["inventory"], p["customers"], p["sap"]
    sources = [SRC_INV, SRC_GMS, SRC_SAP_POS, SRC_POLICY]
    _stash(tool_context, PENDING_POSITION_KEY, {"position": p, "gap": c["gap"], "sources": sources, "note": SAMPLE_NOTE})
    nd = p["next_deadline"]
    return {
        "dahej_inventory": f"{inv['current_tbtu']} TBtu in tanks, {inv['usable_tbtu']} TBtu usable above the minimum "
                           f"(≈{inv['usable_cargo_equivalent']} cargoes), {inv['cover_days']} days of cover",
        "can_inventory_absorb_a_missed_month": inv["can_absorb_a_missed_month"],
        "one_month_gap_tbtu": inv["one_month_gap_tbtu"],
        "must_supply_customers": f"{', '.join(cust['must_supply_sectors'])}: {cust['must_supply_mmscmd']:.0f} of {cust['total_demand_mmscmd']:.0f} MMSCMD",
        "if_gap_uncovered": f"{cust['curtailment_if_uncovered_pct']}% cut to non-priority customers; compensation ≈ ₹{cust['compensation_per_missed_cargo_inr_crore']:.0f} Cr per missed cargo",
        "sap_open_orders": [f"PO {o['po']} {o['vendor']}: {o['cargoes']} cargoes, {o['status']}" for o in sap["open_pos"]],
        "sap_gap_still_open_cargoes": sap["gap_still_open_cargoes"],
        "sap_replacement_budget_inr_crore": sap["budget_inr_crore"],
        "sap_budget_committed_inr_crore": sap["committed_inr_crore"],
        "board_risk_limit_inr_crore": p["risk_limit_inr_crore"],
        "decision_deadlines": [f"{d['month']} cargoes ({d['cargoes']}): contract by {d['decide_by']} ({d['days_left']} days)" for d in p["deadlines"]],
        "next_deadline": f"{nd['month']} cargoes must be contracted by {nd['decide_by']}, {nd['days']} days from today" if nd else "all deadlines passed",
        "procurement_lead_time_days": p["lead_time_days"],
        "approver_under_delegation_of_authority": p["approver_for_lock_all"],
        "sources": sources,
        "data_note": SAMPLE_NOTE,
    }


# --------------------------------------------------------------------------- Q6

def evaluate_winter_procurement(tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    """
    Q6 (Analysis -> decision): Runs the Monte Carlo simulation and recommends: lock in the winter
    replacement cargoes now, or wait? Combines the market (live
    futures, 5-year volatility, analyst consensus) with GAIL's own position (gap, Dahej inventory,
    must-supply customers, SAP budget, contracting deadlines, board risk limit). Prices three strategies
    (lock 100% now / lock 50% / wait and buy each month at its contracting deadline) with a 10,000-path
    Monte Carlo and recommends the cheapest one whose worst realistic case (P95) stays within GAIL's
    board risk limit. Waiting can never run past a month's contracting deadline (hard rule).
    Use for: run a Monte Carlo / simulation, test the options, lock in or wait, should we buy now, hedge,
    risk, what do you recommend, what should we do.
    """
    c = context()
    s, g, p = c["strategy"], c["gap"], c["position"]
    payload = {"strategy": s, "hist_rows": c["hist"]["rows"][-52:], "outlook": c["outlook"], "gap": g, "position": p,
               "live": c["live"], "sources": [_market_src(c["live"]), SRC_ANALYSTS, SRC_BOOK, SRC_INV, SRC_SAP_POS, SRC_POLICY],
               "note": SAMPLE_NOTE}
    _stash(tool_context, PENDING_STRATEGY_KEY, payload)
    nd = p["next_deadline"]
    return {
        "method_statement": (f"I simulated {s['paths']:,} winter price paths from live TTF futures, {s['ttf_annual_vol_pct']:.0f}% volatility "
                             f"measured over {s['history_weeks']} weeks, and the analyst consensus, then tested three options "
                             f"(lock in now, lock in half, wait until each contracting deadline) against GAIL's ₹{s['risk_limit_inr_crore']:,.0f} Cr risk limit."),
        "cargoes": s["total_cargoes"],
        "strategies": [wd.strategy_line(x, s["risk_limit_inr_crore"]) for x in s["strategies"]],
        "prob_waiting_is_cheaper_pct": s["prob_wait_cheaper_than_lock_pct"],
        "expected_saving_if_wait_inr_crore": s["expected_saving_if_wait_inr_crore"],
        "worst_case_statement": wd.risk_statement(s),
        "budget_inr_crore": s["budget_inr_crore"],
        "board_risk_limit_p95_overrun_inr_crore": s["risk_limit_inr_crore"],
        "recommendation": s["recommended_label"],
        "min_cargoes_to_lock_within_risk_limit": s["min_cargoes_to_lock"],
        "checked_against_gail_position": {
            "inventory": f"only {p['inventory']['usable_tbtu']} TBtu usable, cannot absorb a missed month"
                         if not p["inventory"]["can_absorb_a_missed_month"] else f"{p['inventory']['usable_tbtu']} TBtu usable, can absorb a missed month",
            "must_supply_customers_covered": g["priority_customers_protected"],
            "deadline": f"waiting ends {nd['decide_by']} for {nd['month']} ({nd['days']} days)" if nd else "all deadlines passed",
            "sap_budget": f"lock-in is ₹{p['sap']['lock_all_vs_budget_inr_crore']:,.0f} Cr vs the ₹{p['sap']['budget_inr_crore']:,.0f} Cr budget, within the ₹{s['risk_limit_inr_crore']:,.0f} Cr risk limit",
            "approver": p["approver_for_lock_all"],
        },
        "analysts_inside_simulated_range": f"{s['analyst_check']['inside']} of {s['analyst_check']['total']}",
        "method": f"{s['paths']:,} paths · {s['history_weeks']} weeks of history · TTF volatility {s['ttf_annual_vol_pct']}%/yr · centred on analyst consensus · waiting priced at each month's contracting deadline · seed {s['seed']}",
        "sources": payload["sources"],
        "data_note": SAMPLE_NOTE,
    }


# --------------------------------------------------------------------------- Q7

def _stage_purchase_requisition(c: Dict[str, Any]) -> Dict[str, Any]:
    s, pol, live, book = c["strategy"], c["policy"], c["live"], c["book"]
    n_lock = s["total_cargoes"] if s["recommended_id"] == "LOCK_ALL" or s["min_cargoes_to_lock"] is None \
        else max(s["min_cargoes_to_lock"], 0)
    lines, remaining = [], n_lock
    for m in s["months"]:
        take = min(m["cargoes"], remaining)
        remaining -= take
        if take:
            value = wd.inr_crore(take * book["cargo_size_mmbtu"] * m["lock_in_usd_mmbtu"], live["usdinr"])
            lines.append({"item": f"{len(lines) + 1:02d}0", "material": pol["sap"]["material"],
                          "description": f"LNG cargo DES Dahej, {m['label']} delivery",
                          "quantity": f"{take} × {book['cargo_size_mmbtu'] / 1e6:.1f} TBtu",
                          "price_basis": f"TTF {m['label']} futures + ${pol['india_spot_premium_to_ttf_usd_mmbtu']:.2f} + regas",
                          "indicative_usd_mmbtu": m["lock_in_usd_mmbtu"], "indicative_inr_crore": round(value, 0)})
    now = datetime.now()
    pr = f"PR-{int(hashlib.sha1(now.isoformat().encode()).hexdigest(), 16) % 10**8:08d}"
    total = round(sum(li["indicative_inr_crore"] for li in lines), 0)
    approver = wd.approver_for(total, pol)
    return {
        "pr_number": pr, "system": pol["sap"]["system"], "document_type": pol["sap"]["document_type"],
        "purchasing_org": pol["sap"]["purchasing_org"], "plant": pol["sap"]["plant"],
        "gl_account": pol["sap"]["gl_account"], "cost_center": pol["sap"]["cost_center"],
        "lines": lines, "cargoes": n_lock, "total_indicative_inr_crore": total,
        "status": f"AWAITING APPROVAL · {approver}",
        "approver": approver,
        "approval_required": total >= pol["approval_threshold_inr_crore"],
        "created_at": now.strftime("%Y-%m-%d %H:%M"),
        "audit_hash": hashlib.sha256(f"{pr}|{total}|{live['as_of_ist']}".encode()).hexdigest()[:16],
    }


def prepare_procurement_approval(tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    """
    Q7 (Action): Prepares the one-page approval memo for the approver set by GAIL's delegation of
    authority (by value) with the live
    numbers, charts and sources, publishes it to the data lake, and stages a RISE with SAP S/4HANA
    purchase requisition for the recommended cargoes, status AWAITING APPROVAL (a human approves;
    nothing is executed). Returns the memo link and the SAP PR number.
    Use for: prepare the approval, brief the Director / MD, raise the SAP order / purchase request, stage it.
    """
    from app.synthesis.approval_memo import build_and_publish_memo
    c = context()
    pr = _stage_purchase_requisition(c)
    memo = build_and_publish_memo(c, pr)
    s = c["strategy"]
    payload = {"pr": pr, "memo": memo, "strategy": s, "gap": c["gap"], "econ": c["econ"], "live": c["live"],
               "position": c["position"], "approver": pr["approver"], "sources": [SRC_SAP, SRC_POLICY, _market_src(c["live"])]}
    _stash(tool_context, PENDING_APPROVAL_KEY, payload)
    return {
        "memo_url": memo["url"],
        "sap_purchase_requisition": pr["pr_number"],
        "sap_status": pr["status"],
        "cargoes": pr["cargoes"],
        "indicative_value_inr_crore": pr["total_indicative_inr_crore"],
        "recommendation": s["recommended_label"],
        "approver": pr["approver"],
        "approver_rule": "delegation of authority, by value",
        "audit_hash": pr["audit_hash"],
        "sources": payload["sources"],
    }
