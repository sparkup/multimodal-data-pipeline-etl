# ETL Monitoring Plan

## Objective
Define how the multimodal ETL pipeline will be monitored to ensure data reliability, performance, and timely alerts in case of failures.

---

## 1. Scope

This monitoring plan applies to the ETL pipeline managed through Apache Airflow and deployed via Docker Compose.  
It covers the ingestion, transformation, and loading of text, image, audio, and video data.

---

## 2. Key Performance Indicators (KPIs)

| Category | KPI | Description |
|-----------|-----|-------------|
| **Data Availability** | Record count per source | Ensure expected number of items per ingestion run |
| **Data Quality** | % of failed or missing records | Monitor extraction success rate |
| **Pipeline Health** | Task success/failure rate | Track Airflow DAG runs by status |
| **Performance** | Task duration | Measure average runtime for ETL stages |
| **Storage** | MinIO usage | Monitor total storage size and bucket growth |

---

## 3. Monitoring Tools

- **Airflow UI** → Primary view of DAG success/failure and task duration.  
- **PostgreSQL (`etl_metrics` table)** → Centralized store for ETL run stats.  
- **Jupyter Dashboard (`etl_kpis.ipynb`)** → Visual analytics of ETL metrics.  
- **Logs** → Airflow and ETL component logs, consolidated via Docker.

---

## 4. Alerting & Response

| Event | Detection | Action |
|--------|------------|--------|
| Task failure | Airflow DAG alerts | Investigate logs, retry task |
| Low data volume | KPI threshold | Re-run extraction or investigate source |
| Storage full | MinIO bucket alert | Archive or purge data |
| Performance degradation | KPI trend analysis | Optimize scripts or adjust schedule |

---

## 5. Maintenance

- Review dashboards weekly.  
- Export reports monthly.  
- Rotate Airflow logs every 30 days.  
- Validate schema consistency quarterly.

---

## 6. Future Enhancements

- Integrate **Prometheus + Grafana** for real-time monitoring.  
- Implement **email or Slack alerts** via Airflow callbacks.  
- Automate KPI report exports to PDF or HTML for business review.