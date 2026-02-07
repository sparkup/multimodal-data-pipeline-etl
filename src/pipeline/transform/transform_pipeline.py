"""
Transformation pipeline entrypoints.

Defines the main transformation flow that applies feature engineering and
data cleanup steps to collected articles.
"""

import pandas as pd
import logging
from pipeline.transform.transform_features import build_feature_pipeline

logger = logging.getLogger(__name__)

def transform_articles(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply the transformation pipeline to a DataFrame of articles.

    Args:
        df (pd.DataFrame): Raw article dataset.

    Returns:
        pd.DataFrame: Transformed dataset with engineered features.
    """
    logger.info("Starting transformation pipeline...")
    df_transformed = build_feature_pipeline(df)
    logger.info("Transformation pipeline complete.")
    return df_transformed
