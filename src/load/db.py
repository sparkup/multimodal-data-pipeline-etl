"""
db.py
-----
Database connection and loading utilities for PostgreSQL.
"""

import logging
import pandas as pd
from sqlalchemy import create_engine, text
from common.config import SQLALCHEMY_URL

logger = logging.getLogger(__name__)

def get_engine():
    """
    Create and return a SQLAlchemy engine.

    Returns:
        sqlalchemy.Engine: Configured SQLAlchemy engine.
    """
    engine = create_engine(SQLALCHEMY_URL, echo=False, future=True)
    logger.info("PostgreSQL engine initialized.")
    return engine

def execute_sql_file(path: str):
    """
    Execute an entire SQL file (schema creation, seeds, etc.).

    Args:
        path (str): Path to the SQL file to execute.
    """
    engine = get_engine()
    with engine.begin() as conn:
        with open(path, "r") as f:
            sql = f.read()
        conn.execute(text(sql))
        logger.info(f"Executed SQL file: {path}")

def insert_dataframe(df: pd.DataFrame, table_name: str, if_exists="append"):
    """
    Insert a DataFrame into a target table.

    Args:
        df (pd.DataFrame): Data to insert.
        table_name (str): Target table name.
        if_exists (str): Behavior if table exists ("append", "replace", "fail").
    """
    engine = get_engine()
    df.to_sql(table_name, con=engine, if_exists=if_exists, index=False)
    logger.info(f"Inserted {len(df)} records into {table_name}.")
