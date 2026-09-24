"""V4 tests: feed conversions, analyst consensus, gap, pricing, Monte Carlo, cards, memo.

Run offline against the bundled market snapshot (GAIL_MARKET_OFFLINE=1), so results are stable.
"""

import json
import os

os.environ["GAIL_MARKET_OFFLINE"] = "1"

import pytest  # noqa: E402

from app.analytics import winter_decision as wd  # noqa: E402
from app.integration import gail_data, v4_tools  # noqa: E402
from app.market import yahoo_feed  # noqa: E402
from app.market.analyst_outlook import outlook, to_usd_mmbtu  # noqa: E402
from app.render.v4_surfaces import V4_BUILDERS  # noqa: E402


class _Ctx:
    def __init__(self):
        self.state = {}


@pytest.fixture(scope="module")
def ctx():
    return v4_tools.context()


def test_unit_conversions():
    assert yahoo_feed.ttf_eur_mwh_to_usd_mmbtu(34.12, 1.0) == pytest.approx(10.0)
    assert yahoo_feed.brent_to_usd_mmbtu(58.0) == pytest.approx(10.0)
    assert to_usd_mmbtu(11, "USD/mcf", 1.1) == pytest.approx(10.61, abs=0.01)


def test_offline_snapshot_is_labelled():
    live = yahoo_feed.live_snapshot()
    assert live["source_mode"] == "bundled"
    assert "Yahoo Finance" in live["source_label"]
    assert len(live["winter_futures"]) == 3


def test_analyst_consensus_uses_only_2027_verified_rows():
    o = outlook(eurusd=1.1374)
    assert o["count_by_benchmark"] == {"TTF": 4, "HENRY_HUB": 2, "BRENT": 2}
    # median of BofA 55, GS 31 (EUR/MWh) and Fitch 11 USD/mcf -> Fitch/GS region, not the BofA Q4 EUR 100
    assert 9 < o["consensus_usd_mmbtu"]["TTF"] < 12


def test_gap_from_gail_data(ctx):
    g = ctx["gap"]
    assert g["total_cargoes_needed"] == 6
    assert all(m["cargoes_needed"] == 2 for m in g["months"])
    assert g["priority_customers_protected"] is True
    assert g["force_majeure_contracts"][0]["id"] == "LT-QATAR-01"
    assert g["exposure_inr_crore_per_usd1"] == pytest.approx(6 * 3.2e6 * ctx["live"]["usdinr"] / 1e7, abs=1)


def test_contract_economics(ctx):
    e = ctx["econ"]
    assert e["avg_us_contract_landed_usd_mmbtu"] < e["avg_qatar_contract_landed_usd_mmbtu"] < e["avg_spot_replacement_usd_mmbtu"]
    assert e["qatar_outage_extra_cost_inr_crore"] > 0 and e["us_cargo_value_each_inr_crore"] > 0


def test_monte_carlo_is_reproducible_and_consistent(ctx):
    s1 = ctx["strategy"]
    s2 = wd.evaluate_strategies(ctx["live"], ctx["hist"]["rows"], ctx["outlook"]["consensus_usd_mmbtu"]["TTF"],
                                ctx["gap"], ctx["book"], ctx["policy"])
    assert [x["expected_inr_crore"] for x in s1["strategies"]] == [x["expected_inr_crore"] for x in s2["strategies"]]
    lock = next(x for x in s1["strategies"] if x["id"] == "LOCK_ALL")
    wait = next(x for x in s1["strategies"] if x["id"] == "WAIT")
    assert lock["p5_inr_crore"] == lock["p95_inr_crore"]          # locking removes price risk
    assert wait["p95_inr_crore"] > lock["p95_inr_crore"]            # waiting carries tail risk
    assert 0 <= s1["prob_wait_cheaper_than_lock_pct"] <= 100
    rec = next(x for x in s1["strategies"] if x["id"] == s1["recommended_id"])
    assert rec["within_risk_limit"] or not any(x["within_risk_limit"] for x in s1["strategies"])


def test_recommendation_follows_policy(ctx):
    # A very loose risk limit should let the cheapest-expected strategy (wait) win.
    loose = dict(ctx["policy"], risk_limit_p95_overrun_inr_crore=1e9)
    s = wd.evaluate_strategies(ctx["live"], ctx["hist"]["rows"], ctx["outlook"]["consensus_usd_mmbtu"]["TTF"],
                               ctx["gap"], ctx["book"], loose)
    cheapest = min(s["strategies"], key=lambda x: x["expected_inr_crore"])
    assert s["recommended_id"] == cheapest["id"]
    assert s["min_cargoes_to_lock"] == 0


def test_every_tool_names_its_sources_and_builds_a_card():
    tc = _Ctx()
    tools = [v4_tools.assess_winter_supply_gap, v4_tools.get_live_gas_market, v4_tools.get_gas_price_history,
             v4_tools.get_analyst_price_outlook, v4_tools.check_gail_position, v4_tools.evaluate_winter_procurement]
    for tool in tools:
        out = tool(tool_context=tc)
        json.dumps(out)  # model-facing summary must be JSON-serialisable
        assert out["sources"], tool.__name__
    # the combination claim: GAIL data and market data both appear across the decision
    dec = v4_tools.evaluate_winter_procurement(tool_context=tc)
    assert any(s.startswith("🏢") for s in dec["sources"]) and any(s.startswith("🌐") for s in dec["sources"])
    for key, builder in V4_BUILDERS.items():
        if key == "pending_v4_approval":
            continue
        parts = builder(tc.state[key], "s-test")
        assert len(parts) == 2


def test_approval_memo_and_sap_request(tmp_path, monkeypatch):
    monkeypatch.setattr("app.synthesis.approval_memo.OUT_DIR", tmp_path)
    monkeypatch.setattr("app.synthesis.approval_memo.publish_executive_report_to_gcs", lambda doc, name: None)
    tc = _Ctx()
    out = v4_tools.prepare_procurement_approval(tool_context=tc)
    assert out["sap_purchase_requisition"].startswith("PR-")
    assert "AWAITING APPROVAL" in out["sap_status"]
    assert out["memo_url"].endswith(".html")
    html_doc = open(out["memo_url"], encoding="utf-8").read()
    assert "Decision requested" in html_doc and "vegaEmbed" in html_doc
    assert len(V4_BUILDERS["pending_v4_approval"](tc.state["pending_v4_approval"], "s")) == 2


def test_gail_position_uses_internal_systems(ctx):
    p = ctx["position"]
    assert p["inventory"]["usable_tbtu"] == pytest.approx(3.6)
    assert p["inventory"]["can_absorb_a_missed_month"] is False        # 3.6 TBtu usable < ~7 TBtu monthly gap
    assert p["sap"]["gap_still_open_cargoes"] == 6                     # no SAP order covers the gap
    assert any("force majeure" in o["status"].lower() for o in p["sap"]["blocked_pos"])
    assert [d["month"] for d in p["deadlines"]] == ["Dec-26", "Jan-27", "Feb-27"]
    out = v4_tools.check_gail_position(tool_context=_Ctx())
    assert all(src.startswith("🏢") for src in out["sources"])         # this step is GAIL data only


def test_decision_deadline_is_a_hard_rule(ctx):
    from datetime import date
    args = (ctx["live"], ctx["hist"]["rows"], ctx["outlook"]["consensus_usd_mmbtu"]["TTF"], ctx["gap"], ctx["book"], ctx["policy"])
    s = wd.evaluate_strategies(*args, today=date(2026, 9, 24))
    assert s["months"][0]["decide_by"] == "2026-10-17" and s["months"][0]["days_to_decide"] == 23
    # After the Dec deadline, Dec cargoes can no longer wait: every strategy locks them.
    late = wd.evaluate_strategies(*args, today=date(2026, 10, 20))
    assert late["months"][0]["forced_lock"] is True and late["cargoes_forced_lock"] == 2
    assert late["min_cargoes_to_lock"] >= 2
    wait = next(x for x in late["strategies"] if x["id"] == "WAIT")
    lock = next(x for x in late["strategies"] if x["id"] == "LOCK_ALL")
    assert wait["p5_inr_crore"] < lock["expected_inr_crore"] < wait["p95_inr_crore"]


def test_approver_follows_delegation_of_authority(ctx):
    pol = ctx["policy"]
    assert wd.approver_for(300, pol) == "Executive Director (LNG)"
    assert wd.approver_for(4500, pol) == "Director (Marketing)"
    assert wd.approver_for(9000, pol) == "Board of Directors"
