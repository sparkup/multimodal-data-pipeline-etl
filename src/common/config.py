"""
config.py
---------
Central configuration management for the ETL pipeline.
Loads environment variables from .env and provides helper functions.
"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables globally
load_dotenv()

logger = logging.getLogger(__name__)

# PostgreSQL configuration
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))

SQLALCHEMY_URL = (
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    if POSTGRES_USER and POSTGRES_PASSWORD and POSTGRES_DB
    else None
)

# MinIO configuration
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
MINIO_ROOT_USER = os.getenv("MINIO_ROOT_USER")
MINIO_ROOT_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"

# Default buckets for pipeline stages
MINIO_BUCKET_COLLECT = os.getenv("MINIO_BUCKET_COLLECT", "collect")
MINIO_BUCKET_EXTRACT = os.getenv("MINIO_BUCKET_EXTRACT", "extract")
MINIO_BUCKET_TRANSFORM = os.getenv("MINIO_BUCKET_TRANSFORM", "transform")
MINIO_BUCKET_LOAD = os.getenv("MINIO_BUCKET_LOAD", "load")
MINIO_BUCKET_IMAGE = os.getenv("MINIO_BUCKET_IMAGE", "image")

FILE_COLLECT = "collected_articles.csv"
FILE_EXTRACT = "extracted_articles.csv"
FILE_TRANSFORM = "transformed_articles.csv"
FILE_LOAD = "loaded_articles.csv"

# Airflow / ETL paths
AIRFLOW_HOME = os.getenv("AIRFLOW_HOME", "/opt/airflow")

def summary() -> None:
    """Log a summary of the configuration."""
    logger.info("---- Configuration Summary ----")
    logger.info(f"PostgreSQL URL: {SQLALCHEMY_URL or 'Not configured'}")
    logger.info(f"MinIO Endpoint: {MINIO_ENDPOINT}")
    logger.info(f"Buckets: collect={MINIO_BUCKET_COLLECT}, extract={MINIO_BUCKET_EXTRACT}, transform={MINIO_BUCKET_TRANSFORM}, load={MINIO_BUCKET_LOAD}")
    logger.info(f"Data Path: {DATA_PATH}")