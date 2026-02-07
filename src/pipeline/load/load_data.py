"""
Load step for the multimodal ETL pipeline.

This module copies transformed data from the MinIO `transform` bucket to the
`load` bucket to prepare for downstream consumption.
"""

import logging
from io import BytesIO
from common.logging_conf import setup_logging
from common.storage import get_minio_client, ensure_minio_bucket
from common.config import (
    FILE_TRANSFORM,
    FILE_LOAD,
    MINIO_BUCKET_TRANSFORM,
    MINIO_BUCKET_LOAD
)
from minio.error import S3Error

setup_logging()
logger = logging.getLogger(__name__)

def run_load():
    """
    Run the load step by transferring the transformed file into the load bucket.

    Returns:
        str: "success" if the transfer completes without error.
    """
    try:
        logger.info("Starting load_data script...")
        logger.info("Starting data load process...")

        # Initialize MinIO client
        client = get_minio_client()
        logger.info("Connected to MinIO successfully.")

        # Ensure target bucket exists
        ensure_minio_bucket(MINIO_BUCKET_LOAD)
        logger.info(f"Bucket '{MINIO_BUCKET_LOAD}' verified or created.")

        # Download transformed file from MinIO
        logger.info(f"Downloading '{FILE_TRANSFORM}' from bucket '{MINIO_BUCKET_TRANSFORM}'...")
        response = client.get_object(MINIO_BUCKET_TRANSFORM, FILE_TRANSFORM)
        data = response.read()
        response.close()
        response.release_conn()
        logger.info(f"Download complete: '{FILE_TRANSFORM}' ({len(data)} bytes).")

        # Upload file to the load bucket
        logger.info(f"Uploading to '{MINIO_BUCKET_LOAD}/{FILE_LOAD}'...")
        data_stream = BytesIO(data)
        client.put_object(
            MINIO_BUCKET_LOAD,
            FILE_LOAD,
            data_stream,
            length=len(data)
        )
        logger.info(f"Upload complete: '{FILE_LOAD}' successfully stored in '{MINIO_BUCKET_LOAD}'.")

        logger.info("Data load process finished successfully.")
        return "success"

    except S3Error as e:
        logger.error(f"MinIO S3Error: {e}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error during load: {e}")
        raise

if __name__ == "__main__":
    result = run_load()
    print(result)
