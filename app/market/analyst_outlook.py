"""
Analyst price outlook: published, dated forecasts collected from named sources.

Not fetched live on stage (safer): the table lives in fixtures/analyst_outlook.json, and each row
carries its institution, report, publication date, period, original unit and URL. Only rows
flagged "verified" are used. Values are converted to USD/MMBtu so all benchmarks compare directly.
The consensus is the median of the verified forecasts per benchmark.
"""

from __future__ import annotations

import json
import statistics
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.market.yahoo_feed import MMBTU_PER_BBL, MMBTU_PER_MWH

FIXTURES_DIR = Path(__file__).resolve().parent.parent.parent / "fixtures"
BENCHMARKS = ("TTF", "HENRY_HUB", "BRENT")
MMBTU_PER_MCF = 1.037


def load_outlook(path: Optional[Path] = None) -> Dict[str, Any]:
    with open(path or FIXTURES_DIR / "analyst_outlook.json", "r", encoding="utf-8") as f:
        return json.load(f)


def to_usd_mmbtu(value: float, unit: str, eurusd: float) -> float:
    u = unit.replace(" ", "").lower()
    if u in ("eur/mwh", "€/mwh"):
        return value * eurusd / MMBTU_PER_MWH
    if u in ("usd/mwh", "$/mwh"):
        return value / MMBTU_PER_MWH
    if u in ("usd/bbl", "$/bbl"):
        return value / MMBTU_PER_BBL
    if u in ("usd/mcf", "$/mcf"):
        return value / MMBTU_PER_MCF
    return value  # USD/MMBtu


def outlook(eurusd: float) -> Dict[str, Any]:
    raw = load_outlook()
    rows: List[Dict[str, Any]] = []
    for f in raw.get("forecasts", []):
        if f.get("confidence") != "verified" or f.get("benchmark") not in BENCHMARKS:
            continue
        r = dict(f)
        r["value_usd_mmbtu"] = round(to_usd_mmbtu(float(f["value"]), f["unit"], eurusd), 2)
        if f["benchmark"] == "BRENT":
            r["value_usd_bbl"] = float(f["value"])
        rows.append(r)

    consensus: Dict[str, Optional[float]] = {}
    counts: Dict[str, int] = {}
    ranges: Dict[str, Optional[List[float]]] = {}
    for b in BENCHMARKS:
        all_vals = [r["value_usd_mmbtu"] for r in rows if r["benchmark"] == b]
        vals = [r["value_usd_mmbtu"] for r in rows if r["benchmark"] == b and r.get("use_for_consensus", True)]
        counts[b] = len(all_vals)
        consensus[b] = round(statistics.median(vals), 2) if vals else None
        ranges[b] = [round(min(all_vals), 2), round(max(all_vals), 2)] if all_vals else None

    brent_bbl = [r["value_usd_bbl"] for r in rows if r["benchmark"] == "BRENT" and r.get("use_for_consensus", True)]
    return {
        "collected_on": raw.get("collected_on"),
        "note": raw.get("note", ""),
        "forecasts": rows,
        "consensus_usd_mmbtu": consensus,
        "consensus_brent_usd_bbl": round(statistics.median(brent_bbl), 1) if brent_bbl else None,
        "consensus_ttf_eur_mwh": (round(consensus["TTF"] * MMBTU_PER_MWH / eurusd, 1)
                                  if consensus.get("TTF") else None),
        "count_by_benchmark": counts,
        "range_usd_mmbtu": ranges,
        "institutions": sorted({r["institution"] for r in rows}),
    }


def period_mid(row: Dict[str, Any]) -> date:
    return date.fromisoformat(row["period_mid"])
