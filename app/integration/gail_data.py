"""
GAIL internal data loader (contract book, winter supply plan, procurement policy).

Reads from the data lake (gs://<bucket>/raw/gail_internal/) and falls back to the bundled sample
files. Every file is labelled SAMPLE DATA: the structure mirrors GAIL's systems; real data plugs in.
"""

from __future__ import annotations

import json
import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)

BUCKET_NAME = os.getenv("GCS_DATALAKE_BUCKET", "gail-midstream-ge-demo-datalake")
LOCAL_DIR = Path(__file__).resolve().parent.parent.parent / "fixtures" / "gail_internal"
GCS_PREFIX = "raw/gail_internal"


@lru_cache(maxsize=8)
def load_internal(name: str) -> Dict[str, Any]:
    try:
        if os.getenv("GAIL_MARKET_OFFLINE") == "1":
            raise RuntimeError("offline mode")
        from google.cloud import storage
        blob = storage.Client().bucket(BUCKET_NAME).blob(f"{GCS_PREFIX}/{name}")
        if blob.exists():
            data = json.loads(blob.download_as_text())
            data["_loaded_from"] = f"gs://{BUCKET_NAME}/{GCS_PREFIX}/{name}"
            return data
    except Exception as e:
        logger.debug("internal data %s from local sample: %s", name, e)
    with open(LOCAL_DIR / name, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["_loaded_from"] = f"sample data ({name})"
    return data


def contract_book() -> Dict[str, Any]:
    return load_internal("contract_book.json")


def supply_plan() -> Dict[str, Any]:
    return load_internal("winter_supply_plan.json")


def policy() -> Dict[str, Any]:
    return load_internal("procurement_policy.json")


def sap_position() -> Dict[str, Any]:
    return load_internal("sap_open_position.json")
