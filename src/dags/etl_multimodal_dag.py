"""
etl_multimodal_dag.py
---------------------
Defines the Airflow DAG for the multimodal ETL pipeline.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import logging

from common.logging_conf import setup_logging
from pipeline.collect.collection import run_collection
from pipeline.extract.extraction import run_extraction
from pipeline.transform.transform_data import run_transformation
from pipeline.load.load_data import run_load
from load.seed_reference import seed_reference_data

setup_logging()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

logging.getLogger("airflow.task").propagate = False
logging.getLogger("airflow.utils.log").propagate = False
logger = logging.getLogger(__name__)
logger.propagate = False

# Default Airflow arguments
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


def collect_task(**context):
    """
    Airflow task wrapper for collection.

    Args:
        **context: Airflow task context (unused).
    """
    try:
        logger.info("Running collection step...")
        run_collection()
        logger.info("Collection step complete.")
    except Exception as e:
        logger.exception(f"Error in collection step: {e}")
        raise


def extract_task(**context):
    """
    Airflow task wrapper for extraction and enrichment.

    Args:
        **context: Airflow task context (unused).
    """
    try:
        logger.info("Running extraction step...")
        run_extraction()
        logger.info("Extraction step complete.")
    except Exception as e:
        logger.exception(f"Error in extraction step: {e}")
        raise


def transform_task(**context):
    """
    Airflow task wrapper for transformation.

    Args:
        **context: Airflow task context (unused).
    """
    try:
        logger.info("Starting transformation step...")
        run_transformation()
        logger.info("Transformation step complete.")
    except Exception as e:
        logger.exception(f"Error in transformation step: {e}")
        raise


def load_task(**context):
    """
    Airflow task wrapper for loading transformed data.

    Args:
        **context: Airflow task context (unused).
    """
    try:
        logger.info("Starting load step...")
        run_load()
        logger.info("Load step complete.")
    except Exception as e:
        logger.exception(f"Error in load step: {e}")
        raise


def seed_reference_task(**context):
    """
    Airflow task wrapper for seeding reference data.

    Args:
        **context: Airflow task context (unused).
    """
    try:
        logger.info("Starting reference data seeding...")
        seed_reference_data()
        logger.info("Reference data seeding complete.")
    except Exception as e:
        logger.exception(f"Error in reference data seeding step: {e}")
        raise


# DAG definition
with DAG(
    dag_id="etl_multimodal_dag",
    default_args=default_args,
    description="ETL pipeline for multimodal data (text, images, audio, video)",
    schedule_interval="@daily",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["etl", "multimodal"],
) as dag:

    collect = PythonOperator(
        task_id="collect",
        python_callable=collect_task,
        provide_context=True,
    )

    extract = PythonOperator(
        task_id="extract",
        python_callable=extract_task,
        provide_context=True,
    )

    transform = PythonOperator(
        task_id="transform",
        python_callable=transform_task,
        provide_context=True,
    )

    load = PythonOperator(
        task_id="load",
        python_callable=load_task,
        provide_context=True,
    )

    seed_reference = PythonOperator(
        task_id="seed_reference_data",
        python_callable=seed_reference_task,
        provide_context=True,
    )

    collect >> extract >> transform >> load >> seed_reference


if __name__ == "__main__":
    try:
        logger.info("Starting ETL pipeline for debugging...")
        logger.info("Running collection step...")
        run_collection()
        logger.info("Collection step completed successfully.")

        logger.info("Running extraction step...")
        run_extraction()
        logger.info("Extraction step completed successfully.")

        logger.info("Running transformation step...")
        run_transformation()
        logger.info("Transformation step completed successfully.")

        logger.info("Running load step...")
        run_load()
        logger.info("Load step completed successfully.")

        logger.info("Running reference data seeding step...")
        seed_reference_data()
        logger.info("Reference data seeding step completed successfully.")

        logger.info("ETL pipeline completed successfully.")

    except Exception as e:
        logger.exception(f"ETL pipeline failed: {e}")
        raise
