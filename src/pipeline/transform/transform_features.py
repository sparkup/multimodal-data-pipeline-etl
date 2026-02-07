"""
Feature engineering helpers for article datasets.

This module provides simple transformations used by the ETL pipeline, such as
text cleanup and derived feature creation.
"""

import pandas as pd
import logging

logger = logging.getLogger(__name__)

def clean_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Strip whitespace and normalize key text columns.

    Args:
        df (pd.DataFrame): Input dataset.

    Returns:
        pd.DataFrame: Dataset with cleaned text columns.
    """
    text_cols = ["title", "link", "image_url"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    logger.info("Text columns cleaned.")
    return df

def add_title_length(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a feature with the character length of each title.

    Args:
        df (pd.DataFrame): Input dataset.

    Returns:
        pd.DataFrame: Dataset with a new `title_length` column.
    """
    if "title" in df.columns:
        df["title_length"] = df["title"].apply(len)
        logger.info("Feature 'title_length' added.")
    return df

def build_feature_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """
    Combine feature transformations in sequence.

    Args:
        df (pd.DataFrame): Input dataset.

    Returns:
        pd.DataFrame: Transformed dataset.
    """
    df = clean_text_columns(df)
    df = add_title_length(df)
    return df
