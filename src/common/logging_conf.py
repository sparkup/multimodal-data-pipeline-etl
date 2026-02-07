"""
logging_conf.py
---------------
Provides a standardized logging configuration for all ETL components.
"""

import logging

def setup_logging():
    """
    Configure a shared logging format for the ETL components.

    Returns:
        logging.Logger: The root logger configured with handlers.
    """
    logger = logging.getLogger()
    if logger.handlers:
        return logger  # Prevent duplicate handlers

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
    )

    return logger

# Initialize logging when module is imported
setup_logging()
