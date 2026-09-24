"""Vega-Lite v5 specs for the V4 cards and the approval memo (one function per business question)."""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List

SCHEMA = "https://vega.github.io/schema/vega-lite/v5.json"
NAVY, RED, GREEN, ORANGE, GREY, BLUE = "#1B365D", "#DC2626", "#008751", "#E65100", "#94A3B8", "#1A73E8"


def _base(title: str, subtitle: str, height: int) -> Dict[str, Any]:
    return {"$schema": SCHEMA, "width": "container", "height": height,
            "autosize": {"type": "fit", "contains": "padding"},
            "title": {"text": title, "subtitle": subtitle, "anchor": "start", "fontSize": 14, "subtitleFontSize": 11},
            "config": {"legend": {"orient": "bottom", "labelFontSize": 11}, "axis": {"labelFontSize": 11}}}


# Q1 ------------------------------------------------------------------------------------------
def gap_chart(gap: Dict[str, Any]) -> Dict[str, Any]:
    order = ["Domestic gas", "Contract LNG (delivering)", "Dahej inventory draw", "GAP (Qatar force majeure)"]
    rows: List[Dict[str, Any]] = []
    for m in gap["months"]:
        for i, (k, v) in enumerate([(order[0], m["domestic_mmscmd"]), (order[1], m["contract_lng_mmscmd"]),
                                     (order[2], m["inventory_draw_mmscmd"]), (order[3], m["gap_mmscmd"])]):
            rows.append({"month": m["label"], "source": k, "mmscmd": v, "o": i})
    labels = [{"month": m["label"], "y": m["demand_mmscmd"], "t": f"short {m['cargoes_needed']} cargoes"} for m in gap["months"]]
    spec = _base("Winter supply vs customer demand (MMSCMD)", "Axis starts at 60 so the gap is visible · 🏢 sample GAIL data", 230)
    spec["layer"] = [
        {"data": {"values": rows}, "mark": {"type": "bar", "clip": True},
         "encoding": {"x": {"field": "month", "type": "ordinal", "title": None, "sort": None, "axis": {"labelAngle": 0}},
                      "y": {"field": "mmscmd", "type": "quantitative", "stack": "zero", "title": "MMSCMD",
                            "scale": {"domain": [60, 100]}},
                      "color": {"field": "source", "type": "nominal", "title": None,
                                "scale": {"domain": order, "range": [NAVY, BLUE, GREY, RED]}},
                      "order": {"field": "o"},
                      "tooltip": [{"field": "month"}, {"field": "source"}, {"field": "mmscmd", "format": ".2f"}]}},
        {"data": {"values": labels}, "mark": {"type": "text", "dy": -8, "fontWeight": "bold", "color": RED},
         "encoding": {"x": {"field": "month", "type": "ordinal", "sort": None}, "y": {"field": "y", "type": "quantitative"},
                      "text": {"field": "t"}}},
    ]
    return spec


# Q2 ------------------------------------------------------------------------------------------
def market_chart(live: Dict[str, Any], econ: Dict[str, Any]) -> Dict[str, Any]:
    rows = [
        {"k": "Henry Hub (US)", "v": live["henry_hub_usd_mmbtu"], "g": "🌐 Market today"},
        {"k": "Brent (oil parity)", "v": live["brent_usd_mmbtu"], "g": "🌐 Market today"},
        {"k": "TTF (Europe)", "v": live["ttf_usd_mmbtu"], "g": "🌐 Market today"},
        {"k": "Our US contract, landed Dahej", "v": econ["avg_us_contract_landed_usd_mmbtu"], "g": "🏢 GAIL cost (winter)"},
        {"k": "Our Qatar contract (lost), landed", "v": econ["avg_qatar_contract_landed_usd_mmbtu"], "g": "🏢 GAIL cost (winter)"},
        {"k": "Spot replacement, landed Dahej", "v": econ["avg_spot_replacement_usd_mmbtu"], "g": "Replacement (winter)"},
    ]
    for r in rows:
        r["t"] = f"${r['v']:.2f}"
    spec = _base("Market prices vs what gas costs GAIL (USD/MMBtu)", f"{live.get('source_label', '')} · winter = Dec–Feb futures", 230)
    y = {"field": "k", "type": "nominal", "title": None, "sort": None}
    spec["layer"] = [
        {"data": {"values": rows}, "mark": {"type": "bar", "cornerRadiusEnd": 3, "height": 22},
         "encoding": {"y": y, "x": {"field": "v", "type": "quantitative", "title": "USD/MMBtu"},
                      "color": {"field": "g", "type": "nominal", "title": None,
                                "scale": {"domain": ["🌐 Market today", "🏢 GAIL cost (winter)", "Replacement (winter)"],
                                          "range": [GREY, NAVY, RED]}},
                      "tooltip": [{"field": "k"}, {"field": "v", "format": ".2f"}]}},
        {"data": {"values": rows}, "mark": {"type": "text", "align": "left", "dx": 4, "fontWeight": "bold"},
         "encoding": {"y": y, "x": {"field": "v", "type": "quantitative"}, "text": {"field": "t"}}},
    ]
    return spec


# Q3 ------------------------------------------------------------------------------------------
def history_chart(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    vals = []
    for r in rows:
        vals += [{"d": r["date"], "s": "TTF (Europe)", "v": r["ttf_usd_mmbtu"]},
                 {"d": r["date"], "s": "Henry Hub (US)", "v": r["henry_hub"]},
                 {"d": r["date"], "s": "Brent (oil parity)", "v": r["brent_usd_mmbtu"]}]
    peak = max(rows, key=lambda r: r["ttf_usd_mmbtu"])
    ann = [{"d": peak["date"], "v": peak["ttf_usd_mmbtu"], "t": f"2022 crisis: ${peak['ttf_usd_mmbtu']:.0f}"},
           {"d": rows[-1]["date"], "v": rows[-1]["ttf_usd_mmbtu"], "t": f"Today ${rows[-1]['ttf_usd_mmbtu']:.1f}"}]
    x = {"field": "d", "type": "temporal", "title": None, "axis": {"format": "%b %y", "grid": False}}
    dom = ["TTF (Europe)", "Henry Hub (US)", "Brent (oil parity)"]
    spec = _base("5 years of gas prices: Europe vs US (USD/MMBtu, weekly)", "🌐 Yahoo Finance front-month futures", 260)
    spec["layer"] = [
        {"data": {"values": vals}, "mark": {"type": "line", "strokeWidth": 2},
         "encoding": {"x": x, "y": {"field": "v", "type": "quantitative", "title": "USD/MMBtu"},
                      "color": {"field": "s", "type": "nominal", "title": None, "scale": {"domain": dom, "range": [RED, NAVY, GREY]}},
                      "tooltip": [{"field": "d", "type": "temporal"}, {"field": "s"}, {"field": "v", "format": ".2f"}]}},
        {"data": {"values": ann}, "mark": {"type": "point", "filled": True, "size": 70, "color": RED},
         "encoding": {"x": x, "y": {"field": "v", "type": "quantitative"}}},
        {"data": {"values": ann}, "mark": {"type": "text", "align": "right", "dx": -6, "dy": -8, "fontWeight": "bold", "color": RED},
         "encoding": {"x": x, "y": {"field": "v", "type": "quantitative"}, "text": {"field": "t"}}},
    ]
    return spec


# Q4 ------------------------------------------------------------------------------------------
def outlook_chart(outl: Dict[str, Any], live: Dict[str, Any]) -> Dict[str, Any]:
    pts = [{"d": r["period_mid"], "v": r["value_usd_mmbtu"], "who": r["institution"],
            "t": f"{r['institution'].split()[0]} {r['period']}", "orig": f"{r['value']} {r['unit']}", "pub": r["published"]}
           for r in outl["forecasts"] if r["benchmark"] == "TTF"]
    fut = [{"d": f["month"] + "-15", "v": f["TTF_usd_mmbtu"], "t": f"Futures {f['label']}"} for f in live["winter_futures"]]
    today = [{"d": date.today().isoformat(), "v": live["ttf_usd_mmbtu"], "t": "Today"}]
    cons = outl["consensus_usd_mmbtu"]["TTF"]
    last_d = max(p["d"] for p in pts) if pts else fut[-1]["d"]
    x = {"field": "d", "type": "temporal", "title": None, "axis": {"format": "%b %y", "grid": False}}
    y = {"field": "v", "type": "quantitative", "title": "TTF, USD/MMBtu"}
    spec = _base("What the experts expect for European gas (TTF)", f"🌐 Published forecasts, collected {outl.get('collected_on')} · dashed = 2027 consensus", 250)
    spec["layer"] = [
        {"data": {"values": [{"c": cons}]}, "mark": {"type": "rule", "strokeDash": [6, 4], "color": GREEN},
         "encoding": {"y": {"field": "c", "type": "quantitative"}}},
        {"data": {"values": today + fut}, "mark": {"type": "point", "shape": "diamond", "filled": True, "size": 110, "color": NAVY},
         "encoding": {"x": x, "y": y, "tooltip": [{"field": "t"}, {"field": "v", "format": ".2f"}]}},
        {"data": {"values": pts}, "mark": {"type": "point", "filled": True, "size": 140},
         "encoding": {"x": x, "y": y, "color": {"field": "who", "type": "nominal", "title": None},
                      "tooltip": [{"field": "who", "title": "Institution"}, {"field": "t"}, {"field": "orig", "title": "Original"},
                                  {"field": "pub", "title": "Published"}, {"field": "v", "format": ".2f", "title": "USD/MMBtu"}]}},
        {"data": {"values": pts}, "mark": {"type": "text", "align": "left", "dx": 8, "fontSize": 10},
         "encoding": {"x": x, "y": y, "text": {"field": "t"}}},
        {"data": {"values": [{"d": last_d, "v": cons, "t": f"2027 consensus ${cons:.1f}"}]},
         "mark": {"type": "text", "align": "right", "dy": -6, "color": GREEN, "fontWeight": "bold"},
         "encoding": {"x": x, "y": y, "text": {"field": "t"}}},
    ]
    return spec


# Q5 ------------------------------------------------------------------------------------------
def fan_chart(strategy: Dict[str, Any], hist_rows: List[Dict[str, Any]], outl: Dict[str, Any],
              live: Dict[str, Any], budget_ttf: float) -> Dict[str, Any]:
    hist = [{"d": r["date"], "v": r["ttf_usd_mmbtu"]} for r in hist_rows]
    fan = strategy["ttf_fan_12m"]
    fut = [{"d": f["month"] + "-15", "v": f["TTF_usd_mmbtu"], "t": f"Lock-in {f['label']}"} for f in live["winter_futures"]]
    an = [{"d": r["period_mid"], "v": r["value_usd_mmbtu"], "t": r["institution"]}
          for r in outl["forecasts"] if r["benchmark"] == "TTF"]
    x = {"field": "d", "type": "temporal", "title": None, "axis": {"format": "%b %y", "grid": False}}
    yv = {"field": "v", "type": "quantitative", "title": "TTF, USD/MMBtu", "scale": {"domain": [0, 60], "clamp": True}}
    spec = _base(f"{strategy['paths']:,} simulated futures for TTF (next 12 months)",
                 "Shaded = 50% and 90% of simulated paths · ◆ lock-in prices today · ● analysts · dashed = budget", 290)
    spec["layer"] = [
        {"data": {"values": fan}, "mark": {"type": "area", "opacity": 0.15, "color": RED},
         "encoding": {"x": {**x, "field": "date"}, "y": {"field": "p5", "type": "quantitative", "scale": {"domain": [0, 60], "clamp": True}},
                      "y2": {"field": "p95"}}},
        {"data": {"values": fan}, "mark": {"type": "area", "opacity": 0.25, "color": RED},
         "encoding": {"x": {**x, "field": "date"}, "y": {"field": "p25", "type": "quantitative"}, "y2": {"field": "p75"}}},
        {"data": {"values": fan}, "mark": {"type": "line", "color": RED, "strokeDash": [4, 3]},
         "encoding": {"x": {**x, "field": "date"}, "y": {"field": "p50", "type": "quantitative"}}},
        {"data": {"values": hist}, "mark": {"type": "line", "color": NAVY, "strokeWidth": 2.2},
         "encoding": {"x": x, "y": yv, "tooltip": [{"field": "d", "type": "temporal"}, {"field": "v", "format": ".2f"}]}},
        {"data": {"values": [{"b": budget_ttf}]}, "mark": {"type": "rule", "strokeDash": [6, 4], "color": GREEN, "strokeWidth": 1.5},
         "encoding": {"y": {"field": "b", "type": "quantitative"}}},
        {"data": {"values": fut}, "mark": {"type": "point", "shape": "diamond", "filled": True, "size": 110, "color": NAVY},
         "encoding": {"x": x, "y": yv, "tooltip": [{"field": "t"}, {"field": "v", "format": ".2f"}]}},
        {"data": {"values": an}, "mark": {"type": "point", "filled": True, "size": 90, "color": ORANGE},
         "encoding": {"x": x, "y": yv, "tooltip": [{"field": "t"}, {"field": "v", "format": ".2f"}]}},
    ]
    return spec


def strategy_chart(strategy: Dict[str, Any]) -> Dict[str, Any]:
    rows = []
    for s in strategy["strategies"]:
        rows.append({"k": s["label"], "exp": s["expected_inr_crore"], "p5": s["p5_inr_crore"], "p95": s["p95_inr_crore"],
                     "ok": "Within board risk limit" if s["within_risk_limit"] else "Breaches risk limit",
                     "t": f"₹{s['expected_inr_crore']:,.0f} Cr (worst ₹{s['p95_inr_crore']:,.0f})"})
    b, lim = strategy["budget_inr_crore"], strategy["budget_inr_crore"] + strategy["risk_limit_inr_crore"]
    y = {"field": "k", "type": "nominal", "title": None, "sort": None}
    spec = _base("Winter cost by strategy (₹ Cr): expected, with 5–95% range",
                 f"Green line = budget ₹{b:,.0f} Cr · red line = budget + board risk limit ₹{lim:,.0f} Cr", 190)
    spec["layer"] = [
        {"data": {"values": rows}, "mark": {"type": "rule", "strokeWidth": 2, "color": GREY},
         "encoding": {"y": y, "x": {"field": "p5", "type": "quantitative", "title": "₹ Crore"}, "x2": {"field": "p95"}}},
        {"data": {"values": rows}, "mark": {"type": "point", "filled": True, "size": 220},
         "encoding": {"y": y, "x": {"field": "exp", "type": "quantitative"},
                      "color": {"field": "ok", "type": "nominal", "title": None,
                                "scale": {"domain": ["Within board risk limit", "Breaches risk limit"], "range": [GREEN, RED]}},
                      "tooltip": [{"field": "k"}, {"field": "exp", "format": ",.0f"}, {"field": "p5", "format": ",.0f"},
                                  {"field": "p95", "format": ",.0f"}]}},
        {"data": {"values": rows}, "mark": {"type": "text", "dy": -14, "fontSize": 11, "fontWeight": "bold"},
         "encoding": {"y": y, "x": {"field": "exp", "type": "quantitative"}, "text": {"field": "t"}}},
        {"data": {"values": [{"v": b}]}, "mark": {"type": "rule", "color": GREEN, "strokeDash": [6, 4]},
         "encoding": {"x": {"field": "v", "type": "quantitative"}}},
        {"data": {"values": [{"v": lim}]}, "mark": {"type": "rule", "color": RED, "strokeDash": [6, 4]},
         "encoding": {"x": {"field": "v", "type": "quantitative"}}},
    ]
    return spec


# Q5 (our position) ---------------------------------------------------------------------------
def deadline_chart(pos: Dict[str, Any]) -> Dict[str, Any]:
    rows = [{"k": f"{d['month']} cargoes ({d['cargoes']})", "days": max(d["days_left"], 0),
             "t": f"contract by {d['decide_by']} · {max(d['days_left'], 0)} days",
             "urgency": "Under 30 days" if d["days_left"] < 30 else "30+ days"} for d in pos["deadlines"]]
    spec = _base("How long can we wait? Days left to contract each month's cargoes",
                 f"{pos['lead_time_days']}-day procurement lead time · 🏢 sample GAIL policy", 150)
    y = {"field": "k", "type": "nominal", "title": None, "sort": None}
    spec["layer"] = [
        {"data": {"values": rows}, "mark": {"type": "bar", "cornerRadiusEnd": 3, "height": 22},
         "encoding": {"y": y, "x": {"field": "days", "type": "quantitative", "title": "days from today",
                                    "scale": {"domain": [0, max(r["days"] for r in rows) * 1.6 + 1]}},
                      "color": {"field": "urgency", "type": "nominal", "title": None,
                                "scale": {"domain": ["Under 30 days", "30+ days"], "range": [RED, NAVY]}},
                      "tooltip": [{"field": "k"}, {"field": "t"}]}},
        {"data": {"values": rows}, "mark": {"type": "text", "align": "left", "dx": 6, "fontSize": 11},
         "encoding": {"y": y, "x": {"field": "days", "type": "quantitative"}, "text": {"field": "t"}}},
    ]
    return spec
