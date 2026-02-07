"""
storage.py
----------
Provides base storage utilities for PostgreSQL and MinIO.
"""

import logging
from sqlalchemy import create_engine
from minio import Minio
from .config import (
    SQLALCHEMY_URL,
    MINIO_ENDPOINT,
    MINIO_ROOT_USER,
    MINIO_ROOT_PASSWORD
)

logger = logging.getLogger(__name__)
logger.propagate = False

def get_postgres_engine():
    """
    Create and return a SQLAlchemy engine connected to PostgreSQL.

    Returns:
        sqlalchemy.Engine: Configured SQLAlchemy engine.
    """
    engine = create_engine(SQLALCHEMY_URL, echo=False, future=True)
    logger.info("PostgreSQL engine created.")
    return engine

def get_minio_client():
    """
    Create and return a configured MinIO client.

    Returns:
        minio.Minio: MinIO client instance.
    """
    client = Minio(
        MINIO_ENDPOINT.replace("http://", "").replace("https://", ""),
        access_key=MINIO_ROOT_USER,
        secret_key=MINIO_ROOT_PASSWORD,
        secure=MINIO_ENDPOINT.startswith("https"),
    )
    logger.info("MinIO client initialized.")
    return client

def ensure_minio_bucket(bucket_name, client=None):
    """
    Ensure that a given MinIO bucket exists.

    Args:
        bucket_name (str): Bucket to verify or create.
        client (minio.Minio | None): Optional MinIO client instance.
    """
    if client is None:
        client = get_minio_client()
    try:
        found = client.bucket_exists(bucket_name)
        if not found:
            client.make_bucket(bucket_name)
            logger.info(f"Created new bucket: {bucket_name}")
        else:
            logger.info(f"Bucket '{bucket_name}' already exists.")
    except Exception as e:
        logger.error(f"Error ensuring bucket '{bucket_name}': {e}")
        raise
