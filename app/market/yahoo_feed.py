"""
Live gas and oil market data from Yahoo Finance's public chart API.

Benchmarks (front-month futures):
    Henry Hub  NG=F      USD/MMBtu
    TTF        TTF=F     EUR/MWh   -> converted to USD/MMBtu with live EUR/USD
    Brent      BZ=F      USD/bbl   -> oil parity USD/MMBtu = Brent / 5.8
    USD/INR    INR=X
    EUR/USD    EURUSD=X
JKM (Asian LNG) is licensed Platts data and is not on free feeds; we say so on every card.

Stage safety net (the demo never breaks):
    1. live fetch (parallel, 8 s timeout), cached in-process for 15 min (history: 6 h)
    2. every good fetch is saved to GCS; if Yahoo fails we use the last saved copy
    3. if GCS is unreachable too, we use the bundled fixture
Every result carries `source_mode` ("live" | "last_saved" | "bundled") so cards can label it honestly.
"""

from __future__ import annotations

import json
import logging
import math
import os
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

FIXTURES_DIR = Path(__file__).resolve().parent.parent.parent / "fixtures"
BUCKET_NAME = os.getenv("GCS_DATALAKE_BUCKET", "gail-midstream-ge-demo-datalake")
GCS_PREFIX = "market"

TICKERS: Dict[str, str] = {
    "HENRY_HUB": "NG=F",
    "TTF": "TTF=F",
    "BRENT": "BZ=F",
    "USDINR": "INR=X",
    "EURUSD": "EURUSD=X",
}
MMBTU_PER_MWH = 3.412
MMBTU_PER_BBL = 5.8
IST = timezone(timedelta(hours=5, minutes=30))

LIVE_TTL_S = 15 * 60
HISTORY_TTL_S = 6 * 3600
HTTP_TIMEOUT_S = 8

_lock = threading.Lock()
_cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}


# --------------------------------------------------------------------------- helpers

def ttf_eur_mwh_to_usd_mmbtu(eur_mwh: float, eurusd: float) -> float:
    return eur_mwh * eurusd / MMBTU_PER_MWH


def brent_to_usd_mmbtu(usd_bbl: float) -> float:
    return usd_bbl / MMBTU_PER_BBL


def _now_ist() -> str:
    return datetime.now(IST).strftime("%d %b %Y %H:%M IST")


def _fetch_chart(ticker: str, rng: str, interval: str) -> Dict[str, Any]:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range={rng}&interval={interval}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_S) as r:
        payload = json.load(r)
    return payload["chart"]["result"][0]


def _fetch_many(rng: str, interval: str) -> Dict[str, Dict[str, Any]]:
    with ThreadPoolExecutor(max_workers=len(TICKERS)) as ex:
        futures = {k: ex.submit(_fetch_chart, t, rng, interval) for k, t in TICKERS.items()}
        return {k: f.result() for k, f in futures.items()}


def _gcs_save(name: str, data: Dict[str, Any]) -> None:
    try:
        from google.cloud import storage
        storage.Client().bucket(BUCKET_NAME).blob(f"{GCS_PREFIX}/{name}").upload_from_string(
            json.dumps(data), content_type="application/json")
    except Exception as e:  # never let the safety net break the demo
        logger.info("market cache not saved to GCS (%s): %s", name, e)


def _gcs_load(name: str) -> Optional[Dict[str, Any]]:
    try:
        from google.cloud import storage
        blob = storage.Client().bucket(BUCKET_NAME).blob(f"{GCS_PREFIX}/{name}")
        if blob.exists():
            return json.loads(blob.download_as_text())
    except Exception as e:
        logger.info("market cache not loaded from GCS (%s): %s", name, e)
    return None


def _fixture_load(name: str) -> Dict[str, Any]:
    with open(FIXTURES_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


def _cached(key: str, ttl: float, build, cache_name: str) -> Dict[str, Any]:
    with _lock:
        hit = _cache.get(key)
        if hit and time.time() - hit[0] < ttl:
            return hit[1]
    try:
        if os.getenv("GAIL_MARKET_OFFLINE") == "1":
            raise RuntimeError("offline mode")
        data = build()
        data["source_mode"] = "live"
        threading.Thread(target=_gcs_save, args=(cache_name, data), daemon=True).start()
    except Exception as e:
        logger.warning("Yahoo fetch failed for %s, using fallback: %s", key, e)
        data = None if os.getenv("GAIL_MARKET_OFFLINE") == "1" else _gcs_load(cache_name)
        if data:
            data["source_mode"] = "last_saved"
        else:
            data = _fixture_load(cache_name)
            data["source_mode"] = "bundled"
    data["source_label"] = source_label(data)
    with _lock:
        _cache[key] = (time.time(), data)
    return data


def source_label(data: Dict[str, Any]) -> str:
    mode = data.get("source_mode", "live")
    as_of = data.get("as_of_ist", "")
    if mode == "live":
        return f"Live · Yahoo Finance · {as_of}"
    if mode == "last_saved":
        return f"Last live prices (Yahoo Finance) as of {as_of}"
    return f"Saved market snapshot (Yahoo Finance) as of {as_of}"


# --------------------------------------------------------------------------- live snapshot

def _build_live() -> Dict[str, Any]:
    raw = _fetch_many("5d", "1d")
    meta = {k: v["meta"] for k, v in raw.items()}

    def px(k: str) -> float:
        p = meta[k].get("regularMarketPrice")
        if p is None:
            closes = [c for c in raw[k]["indicators"]["quote"][0]["close"] if c is not None]
            p = closes[-1]
        return float(p)

    def prev(k: str) -> Optional[float]:
        closes = [c for c in raw[k]["indicators"]["quote"][0]["close"] if c is not None]
        return float(closes[-2]) if len(closes) >= 2 else None

    hh, ttf_eur, brent, inr, eur = px("HENRY_HUB"), px("TTF"), px("BRENT"), px("USDINR"), px("EURUSD")
    ttf_usd = ttf_eur_mwh_to_usd_mmbtu(ttf_eur, eur)

    def chg(k: str, now: float) -> Optional[float]:
        p = prev(k)
        return round((now / p - 1) * 100, 2) if p else None

    return {
        "as_of_ist": _now_ist(),
        "henry_hub_usd_mmbtu": round(hh, 3),
        "ttf_eur_mwh": round(ttf_eur, 3),
        "ttf_usd_mmbtu": round(ttf_usd, 3),
        "brent_usd_bbl": round(brent, 2),
        "brent_usd_mmbtu": round(brent_to_usd_mmbtu(brent), 3),
        "usdinr": round(inr, 3),
        "eurusd": round(eur, 4),
        "day_change_pct": {
            "HENRY_HUB": chg("HENRY_HUB", hh), "TTF": chg("TTF", ttf_eur),
            "BRENT": chg("BRENT", brent), "USDINR": chg("USDINR", inr),
        },
        "contracts": {k: (meta[k].get("shortName") or meta[k].get("longName") or TICKERS[k]) for k in TICKERS},
        "tickers": dict(TICKERS),
        "winter_futures": _winter_futures(front={"TTF": ttf_eur, "HENRY_HUB": hh, "BRENT": brent}, eurusd=eur),
    }


# --------------------------------------------------------------------------- winter futures

MONTH_CODES = "FGHJKMNQUVXZ"
FUTURES_ROOTS = {"TTF": "TTF", "HENRY_HUB": "NG", "BRENT": "BZ"}


def winter_months(today: Optional[datetime] = None) -> List[datetime]:
    """Dec, Jan, Feb of the coming winter."""
    t = today or datetime.now(IST)
    year = t.year if t.month <= 11 else t.year + 1
    if t.month <= 2:
        year = t.year - 1
    return [datetime(year, 12, 1), datetime(year + 1, 1, 1), datetime(year + 1, 2, 1)]


def _last_settlement(ticker: str) -> Optional[Tuple[float, str]]:
    try:
        raw = _fetch_chart(ticker, "1mo", "1d")
        s = _series(raw)
        if not s:
            return None
        d = max(s)
        return s[d], d
    except Exception:
        return None


def _winter_futures(front: Dict[str, float], eurusd: float) -> List[Dict[str, Any]]:
    months = winter_months()
    jobs = {(b, m.strftime("%Y-%m")): f"{root}{MONTH_CODES[m.month - 1]}{m.strftime('%y')}.NYM"
            for b, root in FUTURES_ROOTS.items() for m in months}
    with ThreadPoolExecutor(max_workers=len(jobs)) as ex:
        got = dict(zip(jobs, ex.map(_last_settlement, jobs.values())))
    out: List[Dict[str, Any]] = []
    for m in months:
        key = m.strftime("%Y-%m")
        row: Dict[str, Any] = {"month": key, "label": m.strftime("%b-%y")}
        prev_ttf = None
        for b in FUTURES_ROOTS:
            hit = got.get((b, key))
            if hit:
                row[b] = round(hit[0], 3)
                row[f"{b}_source"] = f"{jobs[(b, key)]} settle {hit[1]}"
            else:
                # not listed on the free feed: carry the previous winter month, else the front month
                carry = out[-1].get(b) if out else None
                row[b] = round(carry if carry is not None else front[b], 3)
                row[f"{b}_source"] = "previous month carried (not on free feed)" if carry is not None else "front month"
        row["TTF_usd_mmbtu"] = round(ttf_eur_mwh_to_usd_mmbtu(row["TTF"], eurusd), 3)
        out.append(row)
    return out


def live_snapshot() -> Dict[str, Any]:
    return dict(_cached("live", LIVE_TTL_S, _build_live, "latest_snapshot.json"))


# --------------------------------------------------------------------------- history

def _series(raw: Dict[str, Any]) -> Dict[str, float]:
    ts = raw.get("timestamp") or []
    closes = raw["indicators"]["quote"][0]["close"]
    out: Dict[str, float] = {}
    for t, c in zip(ts, closes):
        if c is None or (isinstance(c, float) and math.isnan(c)):
            continue
        out[datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d")] = float(c)
    return out


def _build_history(years: int = 5) -> Dict[str, Any]:
    raw = _fetch_many(f"{years}y", "1wk")
    s = {k: _series(v) for k, v in raw.items()}
    # align on weeks where every benchmark has a close; carry EUR/USD forward if a week is missing
    eur_last = None
    rows: List[Dict[str, Any]] = []
    for d in sorted(set(s["HENRY_HUB"]) & set(s["TTF"]) & set(s["BRENT"])):
        eur_last = s["EURUSD"].get(d, eur_last)
        if eur_last is None:
            continue
        rows.append({
            "date": d,
            "henry_hub": round(s["HENRY_HUB"][d], 3),
            "ttf_eur_mwh": round(s["TTF"][d], 3),
            "ttf_usd_mmbtu": round(ttf_eur_mwh_to_usd_mmbtu(s["TTF"][d], eur_last), 3),
            "brent_usd_bbl": round(s["BRENT"][d], 2),
            "brent_usd_mmbtu": round(brent_to_usd_mmbtu(s["BRENT"][d]), 3),
        })
    if len(rows) < 52:
        raise ValueError(f"history too short: {len(rows)} weeks")
    return {"as_of_ist": _now_ist(), "years": years, "interval": "weekly", "rows": rows}


def price_history(years: int = 5) -> Dict[str, Any]:
    return dict(_cached(f"history_{years}", HISTORY_TTL_S, lambda: _build_history(years), "price_history_5y.json"))


def refresh_bundled_fixtures() -> None:
    """Dev helper: fetch live data now and write it as the bundled fallback fixtures."""
    live = _build_live()
    live["source_mode"] = "bundled"
    hist = _build_history(5)
    hist["source_mode"] = "bundled"
    for name, data in (("latest_snapshot.json", live), ("price_history_5y.json", hist)):
        with open(FIXTURES_DIR / name, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=1)
    print(f"HH {live['henry_hub_usd_mmbtu']} | TTF EUR{live['ttf_eur_mwh']}/MWh = ${live['ttf_usd_mmbtu']} | "
          f"Brent {live['brent_usd_bbl']} | USDINR {live['usdinr']} | {len(hist['rows'])} weeks history")


if __name__ == "__main__":
    refresh_bundled_fixtures()
