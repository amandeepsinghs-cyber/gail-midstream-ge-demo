"""Vega-Lite v5 spec for the SARIMAX line-pack forecast (Beat 3: Proof).

PPAC-style layout on one time axis:
  * last 48h of historian actuals (navy, solid) — the audience sees the daily pack/draft cycle
  * "Now" marker
  * two fitted-model forecasts from the same SARIMAX (dashed): without action (red) and with
    the LNG swap (green), each with 80% and 95% confidence cones that widen with horizon
  * the 76.0 kg/cm² contract floor and the breach point
"""

import math
from typing import Any, Dict, List

FORECAST_SPEC_KEY: str = "sarimax_forecast_spec"
FORECAST_SPEC_POINTER: str = f"/{FORECAST_SPEC_KEY}"

SERIES_ACTUAL = "Actual (historian)"
SERIES_BASE = "Forecast · without action"
SERIES_SWAP = "Forecast · with LNG swap"
C_ACTUAL, C_BASE, C_SWAP = "#1B365D", "#DC2626", "#008751"


def _iso(ts: str) -> str:
    # "2026-09-23 05:00:00" -> "2026-09-23T05:00:00" (ISO local time; parsed reliably by all browsers)
    return str(ts).replace(" ", "T")[:19]


def build_sarimax_vega_spec(summary: Any) -> Dict[str, Any]:
    data = summary if isinstance(summary, dict) else summary.model_dump()
    points: List[Dict[str, Any]] = data.get("hourly_forecast") or data.get("forecast_records") or []
    history: List[Dict[str, Any]] = data.get("history") or []
    floor = float(data.get("critical_pressure_threshold_kg_cm2", 76.0))
    station = str(data.get("target_station", "Chhainsa_CS")).replace("_CS", "")
    breach_ts = data.get("pressure_deficit_timestamp")

    lines: List[Dict[str, Any]] = []
    bands: List[Dict[str, Any]] = []
    for h in history:
        lines.append({"t": _iso(h["timestamp"]), "p": h["linepack_pressure_kg_cm2"], "series": SERIES_ACTUAL})

    # Anchor both forecasts (and their cones) on the last observed point so the lines connect
    if history:
        t0, p0 = _iso(history[-1]["timestamp"]), history[-1]["linepack_pressure_kg_cm2"]
        for s in (SERIES_BASE, SERIES_SWAP):
            lines.append({"t": t0, "p": p0, "series": s})
            bands.append({"t": t0, "series": s, "lo95": p0, "hi95": p0, "lo80": p0, "hi80": p0})

    for pt in points:
        t = _iso(pt["timestamp"])
        lines.append({"t": t, "p": pt["predicted_linepack_kg_cm2"], "series": SERIES_BASE})
        lines.append({"t": t, "p": pt["with_swap_linepack_kg_cm2"], "series": SERIES_SWAP})
        bands.append({"t": t, "series": SERIES_BASE,
                      "lo95": pt["conf_interval_95_lower"], "hi95": pt["conf_interval_95_upper"],
                      "lo80": pt.get("conf_interval_80_lower", pt["conf_interval_95_lower"]),
                      "hi80": pt.get("conf_interval_80_upper", pt["conf_interval_95_upper"])})
        bands.append({"t": t, "series": SERIES_SWAP,
                      "lo95": pt["with_swap_ci_lower"], "hi95": pt["with_swap_ci_upper"],
                      "lo80": pt.get("with_swap_ci80_lower", pt["with_swap_ci_lower"]),
                      "hi80": pt.get("with_swap_ci80_upper", pt["with_swap_ci_upper"])})

    vals = [r["p"] for r in lines] + [b["lo95"] for b in bands] + [b["hi95"] for b in bands] + [floor]
    y_scale = {"zero": False, "domain": [math.floor(min(vals) - 0.5), math.ceil(max(vals) + 0.5)]}
    x_enc = {"field": "t", "type": "temporal", "title": None,
             "axis": {"format": "%d %b %H:%M", "labelAngle": 0, "tickCount": 8, "grid": False}}
    series_domain = [SERIES_ACTUAL, SERIES_BASE, SERIES_SWAP]
    color_scale = {"domain": series_domain, "range": [C_ACTUAL, C_BASE, C_SWAP]}
    band_color = {"field": "series", "type": "nominal", "scale": color_scale}

    layers: List[Dict[str, Any]] = [
        # 95% cones (lighter) then 80% cones (darker)
        {"data": {"values": bands}, "mark": {"type": "area", "opacity": 0.12},
         "encoding": {"x": x_enc, "y": {"field": "lo95", "type": "quantitative", "scale": y_scale},
                      "y2": {"field": "hi95"}, "color": band_color}},
        {"data": {"values": bands}, "mark": {"type": "area", "opacity": 0.22},
         "encoding": {"x": x_enc, "y": {"field": "lo80", "type": "quantitative", "scale": y_scale},
                      "y2": {"field": "hi80"}, "color": band_color}},
        # contract floor
        {"data": {"values": [{"floor": floor}]},
         "mark": {"type": "rule", "strokeDash": [6, 4], "color": "#0F172A", "strokeWidth": 1.5},
         "encoding": {"y": {"field": "floor", "type": "quantitative", "scale": y_scale}}},
        # lines: history solid, forecasts dashed
        {"data": {"values": lines},
         "mark": {"type": "line", "strokeWidth": 2.6, "interpolate": "monotone"},
         "encoding": {
             "x": x_enc,
             "y": {"field": "p", "type": "quantitative", "scale": y_scale, "title": "Line-pack pressure (kg/cm²)"},
             "color": {"field": "series", "type": "nominal", "title": None, "scale": color_scale,
                       "legend": {"orient": "bottom", "symbolType": "stroke"}},
             "strokeDash": {"field": "series", "type": "nominal", "legend": None,
                            "scale": {"domain": series_domain, "range": [[1, 0], [6, 3], [6, 3]]}},
             "tooltip": [
                 {"field": "t", "type": "temporal", "title": "Time", "format": "%d %b %H:%M"},
                 {"field": "series", "title": "Series"},
                 {"field": "p", "type": "quantitative", "title": "kg/cm²", "format": ".2f"},
             ],
         }},
        {"data": {"values": [{"floor": floor, "label": f"{floor:.0f} kg/cm² contract floor"}]},
         "mark": {"type": "text", "align": "left", "dx": 4, "dy": -7, "fontSize": 11, "color": "#0F172A"},
         "encoding": {"y": {"field": "floor", "type": "quantitative", "scale": y_scale},
                      "x": {"value": 0}, "text": {"field": "label"}}},
    ]

    if history:
        now = [{"t": _iso(history[-1]["timestamp"]), "label": "Now"}]
        layers.append({"data": {"values": now},
                       "mark": {"type": "rule", "color": "#64748B", "strokeWidth": 1},
                       "encoding": {"x": x_enc}})
        layers.append({"data": {"values": now},
                       "mark": {"type": "text", "align": "left", "baseline": "top", "dx": 4, "y": 4,
                                "fontSize": 11, "fontWeight": "bold", "color": "#64748B"},
                       "encoding": {"x": x_enc, "text": {"field": "label"}}})

    if breach_ts:
        bp = next((pt for pt in points if pt["timestamp"] == breach_ts), None)
        if bp:
            mark_pt = [{"t": _iso(breach_ts), "p": bp["predicted_linepack_kg_cm2"],
                        "label": f"Breach {str(breach_ts)[11:16]}"}]
            layers.append({"data": {"values": mark_pt},
                           "mark": {"type": "point", "filled": True, "size": 90, "color": C_BASE},
                           "encoding": {"x": x_enc, "y": {"field": "p", "type": "quantitative", "scale": y_scale}}})
            layers.append({"data": {"values": mark_pt},
                           "mark": {"type": "text", "align": "right", "dx": -10, "dy": 16, "fontSize": 12,
                                    "fontWeight": "bold", "color": C_BASE},
                           "encoding": {"x": x_enc, "y": {"field": "p", "type": "quantitative", "scale": y_scale},
                                        "text": {"field": "label"}}})

    subtitle = (f"SARIMAX fitted on {data.get('fitted_on_hours', 72)}h historian data · "
                f"shaded cones = 80% / 95% confidence · hold-out back-test error {data.get('backtest_mape_pct', '—')}%")
    return {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": {"text": f"Can the grid carry it? · {station} line-pack: last 48h and next 24h",
                  "subtitle": subtitle, "anchor": "start", "fontSize": 15, "subtitleFontSize": 12},
        "width": "container",
        "height": 300,
        "autosize": {"type": "fit", "contains": "padding"},
        "layer": layers,
        "config": {"legend": {"symbolOpacity": 1, "symbolStrokeWidth": 3, "symbolSize": 300, "labelFontSize": 12}},
    }
