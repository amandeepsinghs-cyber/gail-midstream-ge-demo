"""One-page approval memo for the Director (Marketing): the decision, the numbers, the charts, the sources."""

from __future__ import annotations

import html
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from app.analytics import winter_decision as wd
from app.integration.gcs_connector import publish_executive_report_to_gcs
from app.render import v4_charts as ch

ROOT = Path(__file__).resolve().parent.parent.parent
OUT_DIR = ROOT / "output_artifacts"


def _logo() -> str:
    try:
        return (ROOT / "fixtures" / "gail_logo_base64.txt").read_text().strip()
    except Exception:
        return ""


def _money(v: float) -> str:
    return f"₹{v:,.0f} Cr"


def render_memo_html(c: Dict[str, Any], pr: Dict[str, Any]) -> str:
    s, g, e, live, o, pol = c["strategy"], c["gap"], c["econ"], c["live"], c["outlook"], c["policy"]
    budget_ttf = s["budget_usd_mmbtu"] - (s["months"][0]["lock_in_usd_mmbtu"] - live["winter_futures"][0]["TTF_usd_mmbtu"])
    charts = {
        "gap": ch.gap_chart(g),
        "fan": ch.fan_chart(s, c["hist"]["rows"][-52:], o, live, budget_ttf),
        "strat": ch.strategy_chart(s),
        "market": ch.market_chart(live, e),
    }
    rows = "".join(
        f"<tr class='{'rec' if x['id'] == s['recommended_id'] else ''}'><td>{html.escape(x['label'])}</td>"
        f"<td>{_money(x['expected_inr_crore'])}</td><td>{_money(x['p5_inr_crore'])} – {_money(x['p95_inr_crore'])}</td>"
        f"<td>{_money(x['p95_overrun_vs_budget_inr_crore'])}</td><td>{'✅ within' if x['within_risk_limit'] else '❌ breaches'}</td></tr>"
        for x in s["strategies"])
    pr_rows = "".join(f"<tr><td>{li['item']}</td><td>{html.escape(li['description'])}</td><td>{li['quantity']}</td>"
                      f"<td>${li['indicative_usd_mmbtu']:.2f}</td><td>{_money(li['indicative_inr_crore'])}</td></tr>" for li in pr["lines"])
    analysts = "".join(f"<li>{html.escape(r['institution'])} ({r['published']}): {r['period']} {r['value']} {r['unit']}</li>"
                       for r in o["forecasts"])
    now = datetime.now().strftime("%d %b %Y %H:%M")
    approver = pr.get("approver", pol["approver"])
    pos = c.get("position")
    checks = ""
    if pos:
        inv, cu, sp = pos["inventory"], pos["customers"], pos["sap"]
        dl = "".join(f"<li>{d['month']} ({d['cargoes']} cargoes): contract by <b>{d['decide_by']}</b> ({d['days_left']} days)</li>" for d in pos["deadlines"])
        checks = (f"<h2>5. Checked against GAIL's own position (🏢)</h2><ul>"
                  f"<li><b>Dahej inventory:</b> {inv['current_tbtu']} TBtu, {inv['usable_tbtu']} TBtu usable ({inv['cover_days']} days of cover). "
                  f"{'Cannot' if not inv['can_absorb_a_missed_month'] else 'Can'} absorb a missed month ({inv['one_month_gap_tbtu']} TBtu).</li>"
                  f"<li><b>Customers:</b> {html.escape(', '.join(cu['must_supply_sectors']))} must be supplied ({cu['must_supply_mmscmd']:.0f} of {cu['total_demand_mmscmd']:.0f} MMSCMD). "
                  f"A missed cargo means a {cu['curtailment_if_uncovered_pct']}% cut to other customers and about {_money(cu['compensation_per_missed_cargo_inr_crore'])} compensation.</li>"
                  f"<li><b>SAP:</b> {sp['gap_still_open_cargoes']} gap cargoes have no purchase order; the Qatar order is blocked (force majeure). "
                  f"Replacement budget {_money(sp['budget_inr_crore'])}, committed {_money(sp['committed_inr_crore'])}.</li>"
                  f"<li><b>Contracting deadlines</b> ({pos['lead_time_days']}-day lead time):<ul>{dl}</ul></li>"
                  f"<li><b>Approver</b> under the delegation of authority: {html.escape(approver)}.</li></ul>")
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>GAIL Winter LNG Procurement – Approval Memo</title>
<script src="https://cdn.jsdelivr.net/npm/vega@5"></script><script src="https://cdn.jsdelivr.net/npm/vega-lite@5"></script>
<script src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>
<style>body{{font-family:Arial,Helvetica,sans-serif;max-width:980px;margin:24px auto;color:#0F172A;line-height:1.45}}
header{{display:flex;align-items:center;gap:16px;border-bottom:3px solid #1B365D;padding-bottom:10px}}header img{{height:54px}}
h1{{font-size:22px;margin:0}}h2{{font-size:16px;color:#1B365D;border-bottom:1px solid #CBD5E1;padding-bottom:4px;margin-top:26px}}
.bluf{{background:#ECFDF5;border-left:5px solid #008751;padding:12px 16px;font-size:15px}}.warn{{background:#FEF2F2;border-left:5px solid #DC2626;padding:10px 14px}}
table{{border-collapse:collapse;width:100%;font-size:13px}}td,th{{border:1px solid #E2E8F0;padding:6px 8px;text-align:left}}th{{background:#F1F5F9}}
tr.rec{{background:#ECFDF5;font-weight:bold}}.chart{{width:100%;margin:8px 0}}.meta{{color:#64748B;font-size:12px}}
.sig{{display:flex;gap:40px;margin-top:20px}}.sig div{{flex:1;border-top:1px solid #0F172A;padding-top:6px;font-size:13px}}</style></head><body>
<header><img src="{_logo()}" alt="GAIL"><div><h1>Winter LNG Procurement – Decision for Approval</h1>
<div class="meta">To: {html.escape(approver)} · Prepared by Gemini Enterprise decision agent · {now} IST · SAP PR {pr['pr_number']}</div></div></header>

<h2>1. Decision requested</h2>
<div class="bluf"><b>Approve: {html.escape(s['recommended_label'])} for {pr['cargoes']} replacement cargoes (Dec–Feb), indicative {_money(pr['total_indicative_inr_crore'])}.</b><br>
{html.escape(wd.risk_statement(s))}
Priority customers (fertilizer, city gas) stay covered.</div>

<h2>2. The problem (🏢 GAIL data)</h2>
<p>{html.escape('; '.join(f"{f['counterparty']}: {f['note']}" for f in g['force_majeure_contracts']))}
Winter gap: <b>{g['total_cargoes_needed']} cargoes ({g['total_gap_tbtu']} TBtu)</b>, {g['gap_pct_of_demand']}% of demand.
Exposure: <b>₹{g['exposure_inr_crore_per_usd1']:,.0f} Cr per $1/MMBtu</b>. Replacing Qatar at spot costs {_money(e['qatar_outage_extra_cost_inr_crore'])} more this winter.</p>
<div id="gap" class="chart"></div>

<h2>3. The market (🌐 live)</h2>
<p>{html.escape(live.get('source_label', ''))}: Henry Hub ${live['henry_hub_usd_mmbtu']:.2f}, TTF €{live['ttf_eur_mwh']:.1f}/MWh (${live['ttf_usd_mmbtu']:.2f}),
Brent ${live['brent_usd_bbl']:.1f}, ₹{live['usdinr']:.2f}/$. Each of our US contract cargoes is worth {_money(e['us_cargo_value_each_inr_crore'])} vs spot. Keep all nominated to Dahej.</p>
<div id="market" class="chart"></div>

<h2>4. Options and risk (Monte Carlo, {s['paths']:,} paths)</h2>
<table><tr><th>Strategy</th><th>Expected cost</th><th>5–95% range</th><th>Bad-winter (1 in 20) overrun vs budget</th><th>Board risk limit</th></tr>{rows}</table>
<div id="fan" class="chart"></div><div id="strat" class="chart"></div>
<p class="meta">Method: TTF volatility {s['ttf_annual_vol_pct']:.0f}%/yr measured on {s['history_weeks']} weeks of history; paths centred on the 2027 analyst consensus
(${s['centred_on_consensus_ttf_usd_mmbtu']}/MMBtu); lock-in at live winter futures; budget ${s['budget_usd_mmbtu']}/MMBtu delivered ({_money(s['budget_inr_crore'])}); seed {s['seed']}.
{s['analyst_check']['inside']} of {s['analyst_check']['total']} analyst forecasts lie inside the simulated range.</p>

{checks}
<h2>6. Staged action (🏢 RISE with SAP)</h2>
<p>Purchase requisition <b>{pr['pr_number']}</b> · {html.escape(pr['document_type'])} · {pr['purchasing_org']} · plant {pr['plant']} · GL {pr['gl_account']} ·
status <b>{html.escape(pr['status'])}</b> · audit hash {pr['audit_hash']}</p>
<table><tr><th>Item</th><th>Description</th><th>Quantity</th><th>Indicative price</th><th>Indicative value</th></tr>{pr_rows}</table>

<h2>7. Sources</h2>
<ul><li>🏢 GAIL contract book, GMS winter nominations, Dahej inventory, SAP open orders and budget, procurement policy (sample data; your systems plug in here)</li>
<li>🌐 {html.escape(live.get('source_label', ''))}; winter futures settlements (TTF, NYMEX HH, Brent)</li>
<li>🌐 Analyst forecasts (collected {o.get('collected_on')}): <ul>{analysts}</ul></li>
<li>JKM is licensed (Platts); India spot estimated as TTF + ${pol['india_spot_premium_to_ttf_usd_mmbtu']:.2f}.</li></ul>
<div class="warn">Decision support only. Prices change daily; figures are at the time shown. Nothing is executed until approved.</div>
<div class="sig"><div>Recommended by: Head, LNG Portfolio</div><div>Approved by: {html.escape(approver)}</div><div>Date:</div></div>
<script>const S={json.dumps(charts)};for(const k in S){{vegaEmbed('#'+k,S[k],{{actions:false}});}}</script>
</body></html>"""


def build_and_publish_memo(c: Dict[str, Any], pr: Dict[str, Any]) -> Dict[str, Any]:
    OUT_DIR.mkdir(exist_ok=True)
    name = f"GAIL_Winter_LNG_Approval_{datetime.now().strftime('%Y-%m-%d_%H%M')}.html"
    doc = render_memo_html(c, pr)
    path = OUT_DIR / name
    path.write_text(doc, encoding="utf-8")
    url = publish_executive_report_to_gcs(doc, name)
    return {"url": url or str(path), "local_path": str(path), "published": bool(url), "filename": name}
