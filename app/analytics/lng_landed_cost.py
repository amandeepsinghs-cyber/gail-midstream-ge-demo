"""
Deterministic LNG landed-cost engine (delivered Dahej, USD/MMBtu).

All arithmetic happens here, in code; the LLM only narrates the result.
Inputs come from fixtures/lng_market_snapshot.json and are ILLUSTRATIVE demo values,
not GAIL contract terms or live market quotes.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

FIXTURES_DIR = Path(__file__).resolve().parent.parent.parent / "fixtures"


def load_market_snapshot(path: Optional[Path] = None) -> Dict[str, Any]:
    with open(path or FIXTURES_DIR / "lng_market_snapshot.json", "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_options(snapshot: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Price every sourcing option, screen for timing feasibility, recommend the cheapest feasible."""
    snap = snapshot or load_market_snapshot()
    regas = float(snap["regas_tariff_usd_mmbtu"])
    cover_days = int(snap["terminal_inventory_cover_days"])
    cargo = float(snap["cargo_size_mmbtu"])
    fx = float(snap["fx_inr_per_usd"])

    options: List[Dict[str, Any]] = []
    for opt in snap["options"]:
        components = {k: float(v) for k, v in opt["components"].items()}
        components["regas"] = regas
        delivered = round(sum(components.values()), 3)
        feasible = int(opt["arrival_days"]) <= cover_days
        options.append({
            "id": opt["id"],
            "label": opt["label"],
            "formula": opt["formula"],
            "components_usd_mmbtu": components,
            "delivered_cost_usd_mmbtu": delivered,
            "arrival_days": int(opt["arrival_days"]),
            "feasible": feasible,
            "screen_reason": "Arrives before terminal inventory runs down" if feasible
            else f"Arrives in {opt['arrival_days']} days - after {cover_days}-day terminal inventory cover",
        })

    feasible_opts = [o for o in options if o["feasible"]]
    chosen = min(feasible_opts, key=lambda o: o["delivered_cost_usd_mmbtu"])
    # Benchmark = the default desk action today: buy spot
    spot = next(o for o in options if o["id"] == "SPOT_JKM")
    saving_usd_mmbtu = round(spot["delivered_cost_usd_mmbtu"] - chosen["delivered_cost_usd_mmbtu"], 3)
    saving_usd = saving_usd_mmbtu * cargo
    saving_inr_cr = round(saving_usd * fx / 1e7, 1)

    for o in options:
        o["recommended"] = o["id"] == chosen["id"]

    return {
        "as_of": snap["as_of"],
        "disclaimer": snap["disclaimer"],
        "delivery_terminal": snap["delivery_terminal"],
        "benchmarks_usd_mmbtu": snap["benchmarks_usd_mmbtu"],
        "fx_inr_per_usd": fx,
        "cargo_size_mmbtu": cargo,
        "terminal_inventory_cover_days": cover_days,
        "options": options,
        "recommended_option_id": chosen["id"],
        "recommended_option_label": chosen["label"],
        "recommended_delivered_cost_usd_mmbtu": chosen["delivered_cost_usd_mmbtu"],
        "benchmark_option_label": spot["label"],
        "saving_vs_spot_usd_mmbtu": saving_usd_mmbtu,
        "saving_vs_spot_usd_mn": round(saving_usd / 1e6, 2),
        "saving_vs_spot_inr_crore": saving_inr_cr,
    }
