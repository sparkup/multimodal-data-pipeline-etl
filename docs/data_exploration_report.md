# Multimodal Source Exploration Report
**Fake News Detection - Multimodal Data Extraction**

---

## 1. Objective

This report identifies the main **text + image** data sources that can be used to train a multimodal fake news detection model. It summarizes available datasets, their modalities (text, image, video), label quality, and practical extraction approaches.

---

## 2. Methodology

Research sources included:
- **Google Dataset Search**, **Kaggle**, **Hugging Face Datasets**
- **Public APIs** catalogs
- Research papers and documentation on multimodal fake news detection

Each source is evaluated by:
- **Data type** (text, image, video, etc.)
- **Format** (CSV, JSON, API)
- **Language**
- **Label quality**
- **Extraction method**

---

## 3. Summary of Selected Sources

| Source | Modalities | Format / Access | Language | Labels (quality) | Proposed extraction |
|:-------|:-----------|:----------------|:--------|:-----------------|:--------------------|
| **FakeNewsNet** (PolitiFact + GossipCop) | Text, images, social metadata | JSON/CSV, GitHub | EN | High (fact-checkers) | Git clone + JSON/CSV parsing, image download |
| **Fakeddit** (Kaggle/Hugging Face) | Text (title), image | CSV + image links | EN | High (multi-class annotations) | Kaggle or HF download, label normalization |
| **Snopes** | Text + images | Website + RSS | EN | Very high (fact-checkers) | RSS scraping + image retrieval |
| **PolitiFact** | Text + images | Website + RSS | EN | Very high ("True" -> "Pants on Fire") | RSS-driven scraping |
| **NewsData.io** | Text + image_url | REST API (JSON) | Multi (EN, FR, ES) | Medium (unlabeled) | API extraction for neutral corpus |
| **GDELT 2.0** | Text, images (links), TV captions | CSV/API | Multi | Unlabeled | Batch download of daily files |
| **Reddit** (r/conspiracy, r/worldnews) | Text + images | Reddit API | Multi | Low (unlabeled) | API extraction + keyword filtering |

---

## 4. Detailed Source Notes

### 4.1 FakeNewsNet
- **Modalities**: text + image + social signals (Twitter)
- **Language**: English
- **Format**: JSON and CSV
- **Labels**: `real` / `fake` - high quality (fact-checkers)
- **Extraction**:
  - Clone the GitHub repository
  - Parse JSON files and download images from `image_url`
  - Store in MinIO for harmonization

### 4.2 Fakeddit
- **Modalities**: text (Reddit title) + image
- **Language**: English
- **Format**: CSV with image links
- **Labels**: multi-class (`true`, `satire`, `manipulated`, etc.)
- **Extraction**:
  - Download via Kaggle API
  - Normalize labels to `real` / `fake`

### 4.3 Snopes / PolitiFact
- **Modalities**: text + image
- **Language**: English
- **Format**: HTML / RSS
- **Labels**: very reliable (`True`, `False`, `Mixed`, `Unproven`, etc.)
- **Extraction**:
  - Use RSS feeds to limit network load
  - Scrape text and images with Scrapy/Selenium
  - Map `claim`, `verdict`, and cover image

### 4.4 NewsData.io
- **Modalities**: text + image_url
- **Language**: multilingual (including French)
- **Format**: JSON via REST API
- **Labels**: none (unlabeled)
- **Extraction**:
  - Use API key to collect recent articles
  - Store text + image_url in MinIO
  - Useful for pre-training embeddings

### 4.5 GDELT 2.0
- **Modalities**: text, images, video (TV)
- **Language**: multilingual
- **Format**: TSV/CSV + API
- **Labels**: none (unlabeled)
- **Extraction**:
  - Download daily batches
  - Filter by language and domain
  - Useful for unsupervised tasks

### 4.6 Reddit
- **Modalities**: text + image
- **Language**: multilingual
- **Format**: JSON via API
- **Labels**: none (unsupervised)
- **Extraction**:
  - Use the Reddit API
  - Filter subreddits `r/conspiracy`, `r/worldnews`
  - Optionally weak-label with Snopes/PolitiFact

---

## 5. Target Data Schema

```text
id (str)
source (str)
url (str)
title (str)
text (str)
image_url (str)
image_object (str)
published_at (datetime)
lang (str)
label (str)
label_source (str)
license (str)
ingested_at (datetime)
```

---

## 6. Recommended Extraction Methods

| Type | Python Tooling | Example Sources | Description |
|------|----------------|-----------------|-------------|
| **REST API** | `requests`, `httpx` | NewsData.io, Reddit | Authenticated API calls with pagination to collect articles and metadata. |
| **HTML / RSS Scraping** | `feedparser`, `Scrapy`, `BeautifulSoup` | Snopes, PolitiFact | Read RSS feeds and parse HTML content (text + images). |
| **Public Datasets** | `datasets` (Hugging Face), `kaggle` | Fakeddit, FakeNewsNet | Direct downloads of labeled multimodal datasets. |
| **Batch / Remote Files** | `pandas`, `urllib`, `os`, `requests` | GDELT, Kaggle archives | Download large CSV/TSV batches. |
| **Airflow Automation** | `PythonOperator` + MinIO client | All | Orchestrate extraction -> transformation -> loading (MinIO / PostgreSQL). |

---

## 7. Processing Pipeline (Overview)

### Main steps:
1. **Collection** - via APIs, RSS, or static dataset downloads.
2. **Extraction** - parse articles to capture text + image_url.
3. **Enrichment** - add metadata: source, language, date, label.
4. **Cleaning / Transformation** - normalize formats (UTF-8, ISO dates, etc.).
5. **Storage** - save:
   - **CSV / Parquet** for text data,
   - **MinIO** for images.
6. **Monitoring** - Airflow logs + data completeness checks.

The current Airflow pipeline runs two core tasks:
- `collect_task` -> collects and stores `sample_articles.csv` in MinIO.
- `extract_task` -> enriches with text and images, stores `articles_enriched.csv`.

These scripts are designed to scale to additional sources (FakeNewsNet, Fakeddit, etc.).

---

## 8. Monitoring Plan

A monitoring plan ensures ETL reliability:
- **Track Airflow runs** (DAG status and average task duration)
- **Automated checks**:
  - CSV file is not empty
  - Minimum article count per run
  - Valid image URLs present
- **KPI dashboard**:
  - extraction error rate
  - valid vs. invalid articles
  - average latency per source
- **Alerts**:
  - empty CSVs, critical exceptions, parsing failures

Airflow logs and MinIO buckets provide a complete audit trail.

---

## 9. Conclusion

This exploration identified several strong sources for multimodal fake news detection. **FakeNewsNet**, **Fakeddit**, and **Snopes/PolitiFact** provide high-quality labeled data, while **Reddit**, **GDELT**, and **NewsData.io** add unlabeled examples useful for pre-training.

The current architecture (Airflow + MinIO + modular Python scripts) enables:
- automated extraction,
- easy extension to new sources,
- and end-to-end reproducibility.
