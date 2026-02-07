# Multimodal Data Pipeline (ETL)

> A production-oriented multimodal ETL system for collecting, enriching, and structuring web content with Airflow, PostgreSQL, and MinIO.

## Project Overview

This repository contains a production-oriented multimodal ETL pipeline that collects, enriches, transforms, and loads heterogeneous web content into structured storage for downstream analytics and ML workloads.

The pipeline ingests text and images (and can be extended to audio/video metadata), normalizes records into a consistent schema, and tracks execution performance through Airflow metadata and KPI dashboards.

It is orchestrated with Apache Airflow, stores structured data in PostgreSQL, and uses MinIO for object storage. Everything runs locally via Docker Compose.

## Key Features

- Automated extraction of multimodal web content (articles, images, podcasts, videos)
- Data transformation and normalization into a unified schema
- Structured storage using PostgreSQL and object storage via MinIO
- Workflow orchestration with Apache Airflow (DAG scheduling, retries, backfills)
- ETL monitoring through reports and KPI-oriented notebooks
- Designed for local execution and downstream ML integration

## What This Project Is / Is Not

**This project is:**

- A practical, production-oriented multimodal ETL pipeline
- A reproducible local stack for ingestion, transformation, and monitoring
- A solid foundation for downstream ML or analytics workflows

**This project is not:**

- A hosted or managed production deployment
- A full data labeling or model training system
- A real-time streaming pipeline (batch-oriented by design)

## Architecture & Tech Stack

| Component        | Technology                                                      |
| ---------------- | --------------------------------------------------------------- |
| Orchestration    | Apache Airflow 2.x                                              |
| Data Storage     | PostgreSQL                                                      |
| Object Storage   | MinIO                                                           |
| ETL Processing   | Python 3 (pandas, requests, BeautifulSoup, newspaper3k, polars) |
| Containerization | Docker, Docker Compose                                          |

## Getting Started

### Prerequisites

- Docker
- Docker Compose
- Make (optional, recommended)

### Installation

Clone the repository:

```bash
git clone https://github.com/sparkup/multimodal-data-pipeline-etl.git
cd multimodal-data-pipeline-etl
```

Create the environment file:

```bash
cp .env.example .env
```

Start the stack:

```bash
make up
```

This launches:

- Apache Airflow web UI: http://localhost:8080
- PostgreSQL database
- MinIO console

Initialize Airflow:

```bash
make airflow-init
```

## Usage

1. Access the Airflow UI at http://localhost:8080
2. Enable and trigger the DAG responsible for the multimodal ETL workflow
3. Monitor task execution, logs, retries, and scheduling directly from the UI

To stop all services:

```bash
make down
```

## Repository Structure

```
docs/               # Documentation, schema, and monitoring plan
notebooks/          # Exploration and monitoring notebooks
src/                # ETL pipeline code and Airflow DAGs
docker-compose.yml  # Local orchestration
Dockerfile          # Airflow image
Dockerfile.jupyter  # Jupyter image
```

## Documentation

Primary docs and references:

- [Data exploration report](docs/data_exploration_report.md)
- [Data dictionary](docs/data_dictionary.md)
- [Monitoring plan](docs/dashboard_monitoring.md)
- [Schema diagram (PNG)](docs/schema.png)
- [Schema source (Mermaid)](docs/schema.mmd)
- [Transformation pipeline README](src/pipeline/transform/README.md)

## Local Development

```bash
cp .env.example .env
make up
```

## Development Notes

- Dependencies are managed via `pyproject.toml`
- Source code and DAGs are mounted into the Airflow container for iterative development
- The pipeline is designed to be extended with additional data sources or downstream consumers

## License

MIT License

This project is licensed under the MIT License. You are free to use, modify, and distribute this software, provided that the original copyright notice and license terms are included.
