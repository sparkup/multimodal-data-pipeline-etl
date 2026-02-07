"""
Extraction and enrichment logic for the multimodal ETL pipeline.

This module reads collected article metadata from MinIO, extracts article text
and image URLs, and writes the enriched dataset back to MinIO.
"""

import yaml
import logging
import pandas as pd
from io import BytesIO
from pathlib import Path
from common.storage import get_minio_client, ensure_minio_bucket
from common.config import (
    FILE_COLLECT,
    FILE_EXTRACT,
    MINIO_BUCKET_COLLECT,
    MINIO_BUCKET_EXTRACT
)
from .scrapers.text import extract_text_from_url
from .scrapers.image import extract_images_from_url

logger = logging.getLogger(__name__)

def load_config():
    """
    Load the YAML configuration file that defines data sources.

    Returns:
        dict: Parsed configuration containing source definitions.
    """
    config_path = Path(__file__).resolve().parents[2] / "common" / "config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

# --------------------------------------------------------------------
# Helper functions
# --------------------------------------------------------------------
def download_from_minio(filename: str) -> pd.DataFrame:
    """
    Download a CSV file from MinIO and return it as a DataFrame.

    Args:
        filename (str): Object name in the MinIO bucket.

    Returns:
        pd.DataFrame: Loaded dataset.
    """
    client = get_minio_client()
    response = client.get_object(MINIO_BUCKET_COLLECT, filename)
    df = pd.read_csv(response)
    logger.info(f"Downloaded {filename} from MinIO with {len(df)} rows.")
    return df


def upload_to_minio(df: pd.DataFrame, filename: str):
    """
    Upload a DataFrame to MinIO as a CSV file.

    Args:
        df (pd.DataFrame): Dataset to upload.
        filename (str): Object name in the MinIO bucket.
    """
    client = get_minio_client()
    ensure_minio_bucket(MINIO_BUCKET_EXTRACT, client)
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    client.put_object(
        bucket_name=MINIO_BUCKET_EXTRACT,
        object_name=filename,
        data=BytesIO(csv_bytes),
        length=len(csv_bytes),
        content_type="text/csv",
    )
    logger.info(f"Uploaded {filename} to MinIO bucket '{MINIO_BUCKET_EXTRACT}'.")


# --------------------------------------------------------------------
# Main extraction logic
# --------------------------------------------------------------------
def extract_and_enrich_articles():
    """
    Extract article content and enrich metadata for each collected record.

    Returns:
        pd.DataFrame | None: The enriched dataset, or None if extraction fails.
    """
    try:
        df = download_from_minio(FILE_COLLECT)
    except Exception as e:
        logger.error(f"Failed to download input file from MinIO: {e}")
        return

    if df.empty:
        logger.warning("Input CSV from MinIO is empty. Nothing to extract.")
        return

    enriched_rows = []
    for _, row in df.iterrows():
        link = row.get("link")
        if not link:
            continue

        logger.info(f"Extracting content from: {link}")
        text_content = extract_text_from_url(link)
        image_urls = extract_images_from_url(link)

        enriched_rows.append({
            "id": row.get("id"),
            "title": row.get("title"),
            "link": link,
            "image_url": row.get("image_url"),
            "extracted_text": text_content,
            "found_images": ";".join(image_urls) if image_urls else None,
        })

    enriched_df = pd.DataFrame(enriched_rows)

    if not enriched_df.empty:
        upload_to_minio(enriched_df, FILE_EXTRACT)
        logger.info(f"Extraction complete - saved {len(enriched_df)} enriched articles.")
    else:
        logger.warning("No enriched articles were created. Output file not uploaded.")


def run_extraction():
    """
    Entrypoint for the Airflow extraction task.
    """
    extract_and_enrich_articles()


if __name__ == "__main__":
    run_extraction()
