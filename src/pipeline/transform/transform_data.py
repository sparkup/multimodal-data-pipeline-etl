"""
transform_data.py
-----------------
Reads the raw dataset from MinIO, applies cleaning and normalization,
and writes the processed dataset back to MinIO.
"""

import io
import logging
import os
import time
import yaml
import pandas as pd
from common.logging_conf import setup_logging
from common.storage import get_minio_client, ensure_minio_bucket
from common.config import (
    FILE_EXTRACT,
    FILE_TRANSFORM,
    MINIO_BUCKET_EXTRACT,
    MINIO_BUCKET_TRANSFORM
)
from pipeline.transform.transform_pipeline import transform_articles

# Reduce logging level to WARNING for all modules
logging.getLogger().setLevel(logging.WARNING)

# Optional: silence noisy libraries (e.g., urllib3, MinIO)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("minio").setLevel(logging.ERROR)
logging.getLogger("pipeline").setLevel(logging.WARNING)

def initialize_logger():
    """
    Initialize a default logger configuration if no handlers exist.
    """
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )

initialize_logger()
logger = logging.getLogger(__name__)

def run_transformation(
    client=None,
):
    """
    Read raw CSV from MinIO, transform it, and write results back to MinIO.

    Args:
        client (Minio | None): Optional MinIO client instance.

    Returns:
        pd.DataFrame: Transformed dataset.
    """
    logger.info("Starting transformation process...")
    start_time = time.time()

    if client is None:
        try:
            client = get_minio_client()
        except Exception as e:
            logger.exception(f"Failed to get MinIO client: {e}")
            raise

    # Ensure processed bucket exists
    try:
        ensure_minio_bucket(MINIO_BUCKET_TRANSFORM, client)
    except Exception as e:
        logger.exception(f"Failed to ensure bucket '{MINIO_BUCKET_TRANSFORM}': {e}")
        raise

    # Read raw data with enhanced error handling
    try:
        logger.info(f"Attempting to download object '{FILE_EXTRACT}' from bucket '{MINIO_BUCKET_EXTRACT}' in MinIO...")
        response = client.get_object(MINIO_BUCKET_EXTRACT, FILE_EXTRACT)
        data_bytes = response.read()
        if not data_bytes:
            logger.error(f"Downloaded object '{FILE_EXTRACT}' from bucket '{MINIO_BUCKET_EXTRACT}' is empty.")
            raise ValueError(f"Downloaded object '{FILE_EXTRACT}' from bucket '{MINIO_BUCKET_EXTRACT}' is empty.")
        try:
            df_raw = pd.read_csv(io.BytesIO(data_bytes))
        except Exception as parse_exc:
            logger.exception(f"Failed to parse CSV data from '{FILE_EXTRACT}' in bucket '{MINIO_BUCKET_EXTRACT}'.")
            raise ValueError(f"Failed to parse CSV data from '{FILE_EXTRACT}' in bucket '{MINIO_BUCKET_EXTRACT}'.") from parse_exc
        if df_raw.empty:
            logger.error(f"Parsed DataFrame from '{FILE_EXTRACT}' in bucket '{MINIO_BUCKET_EXTRACT}' is empty.")
            raise ValueError(f"Parsed DataFrame from '{FILE_EXTRACT}' in bucket '{MINIO_BUCKET_EXTRACT}' is empty.")
        logger.info(f"Successfully loaded raw dataset '{FILE_EXTRACT}' from bucket '{MINIO_BUCKET_EXTRACT}' with {len(df_raw)} records.")
    except Exception as e:
        logger.exception(f"Error while downloading or reading raw data from MinIO object '{FILE_EXTRACT}' in bucket '{MINIO_BUCKET_EXTRACT}'.")
        raise

    # Clean the dataset using transform pipeline
    try:
        df_clean = transform_articles(df_raw)
        logger.info(f"Transformed dataset has {len(df_clean)} records.")
    except Exception as e:
        logger.exception(f"Data transformation failed: {e}")
        raise

    # Write cleaned data to processed zone
    try:
        logger.info(f"Uploading cleaned dataset to '{MINIO_BUCKET_TRANSFORM}/{FILE_TRANSFORM}'...")
        csv_bytes = df_clean.to_csv(index=False).encode("utf-8")

        # Create processed-data bucket if it doesn't exist
        try:
            client.make_bucket(MINIO_BUCKET_TRANSFORM)
            logger.info(f"Created bucket '{MINIO_BUCKET_TRANSFORM}'.")
        except Exception:
            logger.info(f"Bucket '{MINIO_BUCKET_TRANSFORM}' already exists or creation failed.")

        client.put_object(
            bucket_name=MINIO_BUCKET_TRANSFORM,
            object_name=FILE_TRANSFORM,
            data=io.BytesIO(csv_bytes),
            length=len(csv_bytes),
            content_type="text/csv",
        )
        logger.info(f"Transformation completed: '{FILE_TRANSFORM}' uploaded to '{MINIO_BUCKET_TRANSFORM}'.")
    except Exception as e:
        logger.exception(f"Failed to write transformed data to MinIO: {e}")
        raise

    elapsed_time = time.time() - start_time
    logger.info(f"Transformation process finished in {elapsed_time:.2f} seconds.")

    logger.info("Transformation task completed successfully.")
    return df_clean


if __name__ == "__main__":
    setup_logging()
    run_transformation()
