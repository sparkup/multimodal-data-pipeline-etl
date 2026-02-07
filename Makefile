# --------------------------------------------
# Project: Multimodal ETL
# Author: David Worsley-Tonks
# Description: Simple automation for local setup and ETL workflow
# --------------------------------------------

# Default environment file
ENV_FILE ?= .env

# Docker compose base command
DC = docker compose

# Colors
GREEN := \033[0;32m
NC := \033[0m

# --------------------------------------------
# Targets
# --------------------------------------------

## Start all services (Airflow, Postgres, MinIO)
up:
	@echo "$(GREEN)Starting environment...$(NC)"
	$(DC) up -d

## Stop and remove all containers + volumes
down:
	@echo "$(GREEN)Stopping and cleaning environment...$(NC)"
	$(DC) down -v

## Initialize Airflow database and create default admin user
airflow-init:
	@echo "$(GREEN)Initializing Airflow database...$(NC)"
	$(DC) run --rm airflow-webserver airflow db migrate
	@echo "$(GREEN)Creating Airflow admin user...$(NC)"
	$(DC) run --rm airflow-webserver airflow users create \
		--username admin \
		--firstname Admin \
		--lastname User \
		--role Admin \
		--email admin@example.com || true
	@echo "$(GREEN)Airflow initialized at http://localhost:8080$(NC)"

## View logs of the Airflow webserver
logs:
	$(DC) logs -f airflow-webserver

## Show running containers
ps:
	$(DC) ps

## Display help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[32m%-15s\033[0m %s\n", $$1, $$2}'
