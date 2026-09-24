"""Tests for the V3 storyline: shortfall -> LNG decision -> fitted SARIMAX proof -> brief + SAP."""

import numpy as np

from app import scenario
from app.analytics.lng_landed_cost import evaluate_options
from app.analytics.sarimax_linepack import CONTRACT_FLOOR_KG_CM2, SarimaxLinepackEngine
from app.integration.tools import (
    audit_grid_and_weather_risk,
    evaluate_lng_supply_options,
    publish_decision_brief,
    run_sarimax_linepack_forecast,
)
from app.render.a2ui_emit import build_decision_surface, build_lng_surface, build_sarimax_surface
from app.render.forecast_vega import build_sarimax_vega_spec


def test_shortfall_is_four_mmscmd():
    sf = scenario.shortfall()
    assert sf["shortfall_mmscmd"] == 4.0
    assert round(sf["fertilizer_delta_mmscmd"], 1) == 3.0
    assert round(sf["cgd_delta_mmscmd"], 1) == 1.0


def test_landed_cost_formulas_and_screen():
    res = evaluate_options()
    by_id = {o["id"]: o for o in res["options"]}
    assert by_id["SPOT_JKM"]["delivered_cost_usd_mmbtu"] == round(13.60 + 0.25 + 0.60, 3)
    assert by_id["US_HH_REROUTE"]["feasible"] is False          # arrives after inventory cover
    assert res["recommended_option_id"] == "QATAR_TIME_SWAP"
    expected_cr = round((by_id["SPOT_JKM"]["delivered_cost_usd_mmbtu"]
                         - by_id["QATAR_TIME_SWAP"]["delivered_cost_usd_mmbtu"]) * 3.2e6 * 84.0 / 1e7, 1)
    assert res["saving_vs_spot_inr_crore"] == expected_cr


def test_sarimax_is_really_fitted():
    res, df = SarimaxLinepackEngine().fit()
    beta = dict(zip(res.model.param_names, res.params))["x1"]
    # the generator uses 0.125 kg/cm2 per MMSCMD-h; the fitted model must recover it
    assert 0.10 < beta < 0.15
    assert np.isfinite(res.aic)


def test_two_scenarios_tell_the_story():
    f = scenario.forecast()
    assert len(f["forecast_records"]) == 24
    assert f["pressure_deficit_hour_ahead"] == 14
    assert f["minimum_predicted_pressure_kg_cm2"] < CONTRACT_FLOOR_KG_CM2
    assert f["with_swap_breach"] is False
    assert f["with_swap_minimum_kg_cm2"] > CONTRACT_FLOOR_KG_CM2
    assert f["setpoint_recommendation"]["throughput_adjustment_pct"] == 3.8
    hours = [r["hour_ahead"] for r in f["forecast_records"]]
    assert hours == list(range(1, 25))


def test_numbers_consistent_across_beats():
    a = audit_grid_and_weather_risk()
    l = evaluate_lng_supply_options()
    f = run_sarimax_linepack_forecast()
    d = publish_decision_brief()
    assert a.demand_shortfall["shortfall_mmscmd"] == l.shortfall_mmscmd == d.shortfall_mmscmd
    assert l.saving_vs_spot_inr_crore == d.saving_vs_spot_inr_crore
    assert f.pressure_deficit_hour_ahead == d.breach_hour_without_action
    assert f.with_swap_minimum_kg_cm2 == d.min_pressure_with_action_kg_cm2
    assert d.report_url.endswith(".html")
    assert d.sap_work_order_id.startswith("WO-")


def test_forecast_shows_its_work():
    f = scenario.forecast()
    assert len(f["history"]) == 48
    assert f["band_halfwidth_95_t24"] > 2 * f["band_halfwidth_95_t1"]   # cone widens with horizon
    assert f["backtest_mape_pct"] < 1.0                                  # hold-out validation
    assert f["daily_cycle_amplitude_kg_cm2"] > 1.0                       # visible daily cycle
    assert f["with_swap_min_lower95_kg_cm2"] > CONTRACT_FLOOR_KG_CM2      # safe even at 95% edge


def test_surfaces_build():
    spec = build_sarimax_vega_spec(scenario.forecast())
    line_layer = next(l for l in spec["layer"] if isinstance(l.get("mark"), dict) and l["mark"].get("type") == "line")
    series = {v["series"] for v in line_layer["data"]["values"]}
    assert len(series) == 3   # actual history + two forecast scenarios
    assert len(build_sarimax_surface(run_sarimax_linepack_forecast().model_dump(), "s")) == 3
    assert len(build_lng_surface(evaluate_lng_supply_options().model_dump(), "s")) == 2
    assert len(build_decision_surface(publish_decision_brief().model_dump(), "s")) == 2
