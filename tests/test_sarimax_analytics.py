"""Test SARIMAX linepack predictive forecasting engine."""

from app.analytics.sarimax_linepack import SarimaxLinepackEngine

def test_load_historical_scada():
    engine = SarimaxLinepackEngine()
    df = engine.load_historical_data()
    assert len(df) == 72
    assert "linepack_pressure_kg_cm2" in df.columns
    assert "gas_flow_mmscmd" in df.columns
    assert "siemens_gt_exhaust_temp_c" in df.columns
    assert df["linepack_pressure_kg_cm2"].min() >= 70.0

def test_load_exogenous_forecast():
    engine = SarimaxLinepackEngine()
    df_exog, meta = engine.load_exogenous_forecast()
    assert len(df_exog) == 24
    assert "scheduled_offtake_mmscmd" in df_exog.columns
    assert "predicted_ambient_temp_c" in df_exog.columns

def test_sarimax_forecast_execution():
    engine = SarimaxLinepackEngine()
    results = engine.run_forecast(horizon_hours=24)
    
    assert results["target_station"] == "Chhainsa_CS"
    assert results["horizon_hours"] == 24
    assert len(results["hourly_forecast"]) == 24
    assert results["model_aic"] > 0
    assert results["pressure_deficit_hour_ahead"] is not None
    
    setpoint = results["setpoint_recommendation"]
    assert setpoint["target_station"] == "Vijaipur Compressor Hub"
    assert setpoint["throughput_adjustment_pct"] == 3.8
    assert setpoint["fuel_gas_savings_scm_day"] == 18500.0
    assert setpoint["project_sanchay_daily_savings_inr"] > 400000.0
