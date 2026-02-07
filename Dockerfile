# --------------------------------------------
# Dockerfile for Project 12 - Multimodal ETL
# Based on official Apache Airflow image
# --------------------------------------------

FROM apache/airflow:2.9.0

# Switch to root if system dependencies are needed (optional)
USER root
# Example: install OS packages (optional)
# RUN apt-get update && apt-get install -y libmagic1 ffmpeg && rm -rf /var/lib/apt/lists/*

# Switch to airflow user (required for pip installs)
USER airflow

# Copy dependency file to image
COPY pyproject.toml /opt/airflow/pyproject.toml

# Install dependencies defined in pyproject.toml
# Using uv (fast dependency resolver) if available, else fallback to pip
RUN pip install --no-cache-dir uv || true \
    && uv pip install -r /opt/airflow/pyproject.toml || pip install --no-cache-dir -e /opt/airflow

# Copy your source code
COPY src /opt/airflow/src
COPY data /opt/airflow/data
COPY docs /opt/airflow/docs

# Expose Airflow default port
EXPOSE 8080

# Default command
CMD ["webserver"]