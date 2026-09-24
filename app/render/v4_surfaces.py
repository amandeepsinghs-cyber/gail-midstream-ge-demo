"""A2UI v0.9 cards for the V4 flow. One card per business question; every card ends with a
🏢 GAIL data / 🌐 market data sources line (the Gemini Enterprise point: both, in one answer)."""

from __future__ import annotations

from typing import Any, Dict, List

from google.genai import types

from app.analytics import winter_decision as wd
from app.render import v4_charts as ch
from app.render.a2ui_envelope import wrap_a2ui_part
from app.render.a2ui_lifecycle import build_create_surface, build_update_components


def _card(surface_id: str, prefix: str, title: str, subtitle: str, charts: List[Dict[str, Any]],
          body: str, sources: List[str], note: str = "", link: str = "") -> List[types.Part]:
    ids: List[str] = [f"{prefix}-title", f"{prefix}-sub"]
    comps: List[Dict[str, Any]] = [
        {"id": f"{prefix}-title", "component": "Text", "variant": "h3", "text": title},
        {"id": f"{prefix}-sub", "component": "Text", "variant": "caption", "text": subtitle},
    ]
    for i, spec in enumerate(charts):
        cid = f"{prefix}-chart{i}"
        ids.append(cid)
        comps.append({"id": cid, "component": "VegaChart", "spec": spec, "height": spec.get("height", 240) + 40})
    ids += [f"{prefix}-div", f"{prefix}-body"]
    comps += [{"id": f"{prefix}-div", "component": "Divider"},
              {"id": f"{prefix}-body", "component": "Text", "variant": "body", "text": body}]
    if link:
        ids.append(f"{prefix}-link")
        comps.append({"id": f"{prefix}-link", "component": "Text", "variant": "body", "text": link})
    ids.append(f"{prefix}-src")
    comps.append({"id": f"{prefix}-src", "component": "Text", "variant": "caption",
                  "text": "Sources: " + " · ".join(sources) + (f"\n{note}" if note else "")})
    comps = [{"id": "root", "component": "Card", "child": f"{prefix}-col"},
             {"id": f"{prefix}-col", "component": "Column", "children": ids}] + comps
    return [wrap_a2ui_part(build_create_surface(surface_id=surface_id)),
            wrap_a2ui_part(build_update_components(surface_id=surface_id, components=comps))]


def build_gap_surface(p: Dict[str, Any], surface_id: str) -> List[types.Part]:
    g = p["gap"]
    fm = "; ".join(f"{f['counterparty']}: {f['cargoes_per_month']} cargoes/month" for f in g["force_majeure_contracts"])
    body = (f"⚠️ **Winter gap: {g['total_cargoes_needed']} cargoes ({g['total_gap_tbtu']} TBtu), about {g['avg_gap_mmscmd']} MMSCMD "
            f"({g['gap_pct_of_demand']}% of demand), Dec–Feb.**\n"
            f"• Force majeure: {fm}\n"
            f"• Priority customers (fertilizer, city gas): {'protected' if g['priority_customers_protected'] else 'AT RISK'}. "
            f"If uncovered: {g['curtailment_if_not_covered_pct_of_non_priority']}% cut to refinery, power and other industrial.\n"
            f"• **Every $1/MMBtu move = ₹{g['exposure_inr_crore_per_usd1']:,.0f} Cr** on the replacement volume.")
    return _card(surface_id, "gap", "🧭 Impact of the Qatar force majeure on our winter supply",
                 "GAIL contract book × winter nominations × Dahej inventory", [ch.gap_chart(g)], body, p["sources"], p.get("note", ""))


def build_market_surface(p: Dict[str, Any], surface_id: str) -> List[types.Part]:
    live, e = p["live"], p["econ"]
    dc = live.get("day_change_pct", {})
    fmt = lambda v: "" if v is None else f" ({v:+.1f}% d/d)"
    body = (f"• Henry Hub **${live['henry_hub_usd_mmbtu']:.2f}**{fmt(dc.get('HENRY_HUB'))} · TTF **€{live['ttf_eur_mwh']:.1f}/MWh = "
            f"${live['ttf_usd_mmbtu']:.2f}**{fmt(dc.get('TTF'))} · Brent **${live['brent_usd_bbl']:.1f}**{fmt(dc.get('BRENT'))} · "
            f"₹{live['usdinr']:.2f}/$\n"
            f"• Europe pays **{live['ttf_usd_mmbtu'] / live['henry_hub_usd_mmbtu']:.1f}×** the US price.\n"
            f"• 🏢 Our US contract cargo lands at **${e['avg_us_contract_landed_usd_mmbtu']:.2f}** vs spot replacement "
            f"**${e['avg_spot_replacement_usd_mmbtu']:.2f}**, so each US cargo is worth **₹{e['us_cargo_value_each_inr_crore']:,.0f} Cr** vs spot. Keep all of them coming to Dahej.\n"
            f"• 🏢 Replacing the lost Qatar volume at spot costs **₹{e['qatar_outage_extra_cost_inr_crore']:,.0f} Cr more** this winter.\n"
            + (f"• 💰 🏢 {p['budget_line']}" if p.get("budget_line") else ""))
    return _card(surface_id, "mkt", "💹 What gas costs today, and what it means for our contracts and budget",
                 live.get("source_label", ""), [ch.market_chart(live, e)], body, p["sources"],
                 "JKM is licensed (Platts): India spot estimated as TTF + premium. " + p.get("note", ""))


def build_history_surface(p: Dict[str, Any], surface_id: str) -> List[types.Part]:
    s = p["summary"]
    body = (f"• 2022 crisis peak: **{s['ttf_peak']}** · 5-year low ${s['ttf_5y_low_usd_mmbtu']:.2f}\n"
            f"• Today TTF **${s['ttf_today_usd_mmbtu']:.2f}** vs Henry Hub ${s['henry_hub_today']:.2f}: spread "
            f"**${s['spread_today_usd_mmbtu']:.2f}** (5-year average ${s['spread_5y_average_usd_mmbtu']:.2f})\n"
            f"• Measured TTF volatility **{s['ttf_annual_volatility_pct']:.0f}% a year**. That is the risk we simulate next.")
    return _card(surface_id, "hist", "📉 5 years of gas prices and what moved them", s["period"],
                 [ch.history_chart(p["rows"])], body, p["sources"])


def build_outlook_surface(p: Dict[str, Any], surface_id: str) -> List[types.Part]:
    o, live = p["outlook"], p["live"]
    lines = [f"• {r['institution']} ({r['published']}): {r['period']} **{r['value']} {r['unit']}** ≈ ${r['value_usd_mmbtu']:.1f}"
             for r in o["forecasts"] if r["benchmark"] == "TTF"]
    body = ("**TTF (European gas):**\n" + "\n".join(lines) +
            f"\n• **2027 consensus €{o['consensus_ttf_eur_mwh']}/MWh (${o['consensus_usd_mmbtu']['TTF']:.1f})** vs winter futures "
            f"€{live['winter_futures'][0]['TTF']:.1f}/MWh today. The experts disagree, and the market prices winter well above 2027.\n"
            f"• Henry Hub 2027: ${o['consensus_usd_mmbtu']['HENRY_HUB']:.2f} (EIA, Enverus) · Brent 2027: ${o['consensus_brent_usd_bbl']:.0f}/bbl (EIA, Fitch)")
    return _card(surface_id, "outl", "🔭 What do the experts expect?", f"Published forecasts collected {o.get('collected_on')}",
                 [ch.outlook_chart(o, live)], body, p["sources"], "Verify each source link before external use.")


def build_position_surface(p: Dict[str, Any], surface_id: str) -> List[types.Part]:
    pos = p["position"]
    inv, cu, sp, nd = pos["inventory"], pos["customers"], pos["sap"], pos["next_deadline"]
    pos_lines = "\n".join(f"  – PO {o['po']} · {o['vendor']} · {o['cargoes']} cargoes · {o['status']}" for o in sp["open_pos"])
    body = ((f"⏱️ **Decision deadline: the {nd['month']} cargoes must be contracted by {nd['decide_by']}, {nd['days']} days from today.**\n"
             if nd else "⏱️ **All contracting deadlines have passed: remaining cargoes must be locked now.**\n") +
            f"• 🛢️ **Dahej tanks:** {inv['current_tbtu']} TBtu, of which **{inv['usable_tbtu']} TBtu usable** (≈{inv['usable_cargo_equivalent']} cargoes, "
            f"{inv['cover_days']} days of cover). "
            + ("**Not enough to absorb a missed month** " if not inv["can_absorb_a_missed_month"] else "Enough to absorb a missed month ")
            + f"({inv['one_month_gap_tbtu']} TBtu).\n"
            f"• 👥 **Customers:** {', '.join(cu['must_supply_sectors'])} are must-supply ({cu['must_supply_mmscmd']:.0f} of {cu['total_demand_mmscmd']:.0f} MMSCMD). "
            f"A missed cargo means a {cu['curtailment_if_uncovered_pct']}% cut to other customers and ≈ ₹{cu['compensation_per_missed_cargo_inr_crore']:,.0f} Cr compensation.\n"
            f"• 📄 **SAP open orders (winter):** {sp['gap_still_open_cargoes']} of the gap cargoes have no purchase order yet.\n{pos_lines}\n"
            f"• 💰 **SAP budget:** replacement budget ₹{sp['budget_inr_crore']:,.0f} Cr, committed ₹{sp['committed_inr_crore']:,.0f} Cr, "
            f"available ₹{sp['available_inr_crore']:,.0f} Cr · board risk limit ₹{pos['risk_limit_inr_crore']:,.0f} Cr.\n"
            f"• ✍️ **Approver** under the delegation of authority: **{pos['approver_for_lock_all']}**.")
    return _card(surface_id, "pos", "🏢 Our own position: inventory, customers, SAP",
                 "Dahej inventory × customer commitments × SAP orders and budget × contracting deadlines",
                 [ch.deadline_chart(pos)], body, p["sources"], p.get("note", ""))


def build_strategy_surface(p: Dict[str, Any], surface_id: str) -> List[types.Part]:
    s, g = p["strategy"], p["gap"]
    rec = s["recommended_label"]
    budget_ttf = s["budget_usd_mmbtu"] - (s["months"][0]["lock_in_usd_mmbtu"] - p["live"]["winter_futures"][0]["TTF_usd_mmbtu"])
    lines = [f"{'✅' if x['id'] == s['recommended_id'] else ('🟢' if x['within_risk_limit'] else '🔴')} "
             f"{wd.strategy_line(x, s['risk_limit_inr_crore'])}" for x in s["strategies"]]
    body = (f"**Recommendation: {rec}** ({s['total_cargoes']} cargoes).\n"
            f"• {wd.risk_statement(s)}\n"
            + "\n".join(lines) +
            f"\n• Minimum to lock within the risk limit: **{s['min_cargoes_to_lock']} of {s['total_cargoes']} cargoes**. "
            f"Priority customers covered: {'yes' if g['priority_customers_protected'] else 'no'}.\n"
            + (f"• 🏢 Checked against GAIL's position: tanks {'cannot' if not p['position']['inventory']['can_absorb_a_missed_month'] else 'can'} absorb a missed month · "
               f"waiting ends {p['position']['next_deadline']['decide_by']} for {p['position']['next_deadline']['month']} · "
               f"lock-in {p['position']['sap']['lock_all_vs_budget_inr_crore']:+,.0f} Cr vs SAP budget · approver {p['position']['approver_for_lock_all']}.\n"
               if p.get("position") and p["position"].get("next_deadline") else "") +
            f"• Sanity check: {s['analyst_check']['inside']} of {s['analyst_check']['total']} analyst forecasts sit inside the simulated range.\n"
            f"_Method: {s['paths']:,} paths · {s['history_weeks']} weeks of history · TTF volatility {s['ttf_annual_vol_pct']:.0f}%/yr · "
            f"centred on analyst consensus · waiting priced at each month's contracting deadline · seed {s['seed']}. The agent frames the risk; the approver decides._")
    return _card(surface_id, "strat", "🎯 Monte Carlo: lock in now, or wait?", "�� Live futures + 10,000-path Monte Carlo × 🏢 GAIL position, budget and risk limit",
                 [ch.fan_chart(s, p["hist_rows"], p["outlook"], p["live"], budget_ttf), ch.strategy_chart(s)],
                 body, p["sources"], p.get("note", ""))


def build_approval_surface(p: Dict[str, Any], surface_id: str) -> List[types.Part]:
    pr, memo, s = p["pr"], p["memo"], p["strategy"]
    items = "\n".join(f"• {li['item']} · {li['description']} · {li['quantity']} · ~₹{li['indicative_inr_crore']:,.0f} Cr" for li in pr["lines"])
    body = (f"**SAP purchase requisition {pr['pr_number']}**: {pr['status']}\n{items}\n"
            f"• Total indicative value **₹{pr['total_indicative_inr_crore']:,.0f} Cr** · {pr['document_type']} · plant {pr['plant']}\n"
            f"• Nothing is executed until the {p.get('approver', 'Director (Marketing)')} approves. Audit hash {pr['audit_hash']}.")
    return _card(surface_id, "appr", "✅ Approval prepared and staged", f"{pr['system']} · {s['recommended_label']}",
                 [], body, p["sources"], link=f"📑 [Open the approval memo]({memo['url']})")


V4_BUILDERS = {
    "pending_v4_gap": build_gap_surface,
    "pending_v4_market": build_market_surface,
    "pending_v4_history": build_history_surface,
    "pending_v4_outlook": build_outlook_surface,
    "pending_v4_position": build_position_surface,
    "pending_v4_strategy": build_strategy_surface,
    "pending_v4_approval": build_approval_surface,
}
