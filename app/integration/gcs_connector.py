"""
GAIL Midstream Demo - GCS Data Lake Connector
Seamlessly interacts with gs://gail-midstream-ge-demo-datalake/
with transparent fallback to local fixtures for offline/hybrid testing.
"""
import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import pandas as pd

logger = logging.getLogger("gail_gcs_connector")

BUCKET_NAME = os.getenv("GCS_DATALAKE_BUCKET", "gail-midstream-ge-demo-datalake")
LOCAL_FIXTURES_DIR = Path(__file__).resolve().parent.parent.parent / "fixtures"
LOCAL_ARTIFACTS_DIR = Path(__file__).resolve().parent.parent.parent / "output_artifacts"


def load_scada_telemetry(filename: str = "gail_hvj_scada_telemetry_72h.csv") -> pd.DataFrame:
    """
    Attempts to read SCADA telemetry from GCS raw/scada/ or falls back to local fixtures.
    """
    gcs_uri = f"gs://{BUCKET_NAME}/raw/scada/{filename}"
    try:
        from google.cloud import storage
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"raw/scada/{filename}")
        if blob.exists():
            import io
            content = blob.download_as_bytes()
            logger.info("Loaded telemetry from GCS: %s", gcs_uri)
            return pd.read_csv(io.BytesIO(content))
    except Exception as e:
        logger.debug("Falling back to local SCADA fixture (%s): %s", filename, e)

    local_path = LOCAL_FIXTURES_DIR / filename
    return pd.read_csv(local_path)


def load_geojson(filename: str = "river_crossings_gis.geojson") -> Dict[str, Any]:
    """
    Attempts to read GIS GeoJSON from GCS raw/gis/ or falls back to local fixtures.
    """
    try:
        from google.cloud import storage
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"raw/gis/{filename}")
        if blob.exists():
            return json.loads(blob.download_as_text())
    except Exception as e:
        logger.debug("Falling back to local GIS fixture (%s): %s", filename, e)

    local_path = LOCAL_FIXTURES_DIR / filename
    with open(local_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_nominations(filename: str = "customer_nominations_24h.json") -> Dict[str, Any]:
    """
    Attempts to read Customer Nominations from GCS raw/customer_nominations/ or falls back to local fixtures.
    """
    try:
        from google.cloud import storage
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"raw/customer_nominations/{filename}")
        if blob.exists():
            return json.loads(blob.download_as_text())
    except Exception as e:
        logger.debug("Falling back to local customer nominations fixture (%s): %s", filename, e)

    local_path = LOCAL_FIXTURES_DIR / filename
    with open(local_path, "r", encoding="utf-8") as f:
        return json.load(f)


def publish_executive_report_to_gcs(html_content: str, filename: str) -> Optional[str]:
    """
    Publishes compiled executive report to gs://<BUCKET_NAME>/curated/executive_reports/<filename>
    Returns browser-accessible Cloud Storage web URL if successful, or None if offline.
    """
    gcs_uri = f"gs://{BUCKET_NAME}/curated/executive_reports/{filename}"
    web_url = f"https://storage.cloud.google.com/{BUCKET_NAME}/curated/executive_reports/{filename}"
    try:
        from google.cloud import storage
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"curated/executive_reports/{filename}")
        blob.upload_from_string(html_content, content_type="text/html")
        logger.info("Published executive report to GCS: %s (%s)", gcs_uri, web_url)
        return web_url
    except Exception as e:
        logger.warning("Could not publish report to GCS (%s): %s", gcs_uri, e)
        return None
