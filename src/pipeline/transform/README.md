

# Transformation Pipeline

## Overview

This module handles the **transformation phase** of the multimodal fake news detection ETL pipeline.  
It takes extracted data from MinIO, cleans and normalizes the text, validates associated images, and exports a standardized dataset ready for model training.

---

## Features

- **Automated transformation pipeline** with clear modular steps.
- **Logs each transformation step** for transparency and debugging.
- **Validates and filters** textual and image data.
- **Uploads transformed data** to MinIO for downstream processing.

---

## Files Description

| File | Description |
|------|-------------|
| `transform_data.py` | Main script that orchestrates the full transformation workflow. |
| `transform_pipeline.py` | Contains reusable functions for reading, cleaning, and writing data. |
| `transform_features.py` | Handles feature generation such as text normalization and length computation. |

---

## Transformation Steps

1. **Read Extracted Data**  
   Loads the dataset from the MinIO `extract` bucket using the MinIO client.

2. **Clean and Normalize Text**  
   - Converts text to lowercase  
   - Removes punctuation and stopwords  
   - Drops entries with missing or short text

3. **Validate Images**  
   Ensures that only valid, accessible image URLs are kept.

4. **Generate Features**  
   Adds engineered features such as:
   - `text_length`
   - `has_image`
   - `num_images`

5. **Save Transformed Data**  
   The cleaned dataset is saved to MinIO under:
   ```
   transform/transformed_articles.csv
   ```

---

## Logging

All operations are logged to the console and Airflow logs.  
Example log output:
```
[INFO] Starting transformation process...
[INFO] Loaded 200 raw articles from MinIO.
[INFO] Removed 15 duplicate entries.
[INFO] Normalized text fields successfully.
[INFO] Uploaded cleaned dataset to transform/transformed_articles.csv
```

---

## Execution

### 1. Run as a standalone script
```bash
python transform_data.py
```

### 2. Run inside the Airflow container
```bash
docker exec -it airflow-worker python /opt/airflow/src/pipeline/transform/transform_data.py
```

---

## Output

- Cleaned dataset: `transform/transformed_articles.csv` in MinIO  
- Logs: Printed in console and stored in Airflow logs  
- Ready for loading into the `load` stage of the pipeline

---

## Notes

- Ensure that `MINIO_ENDPOINT`, `MINIO_ACCESS_KEY`, and `MINIO_SECRET_KEY` are set in your `.env`.
- The pipeline assumes extracted data already exists in the `extract` bucket.