# Data Dictionary – Multimodal Fake News Detection

This document provides a detailed description of all data fields produced and processed by the ETL pipeline. It defines the data schema used for AI model training and describes the role of each field in the classification task.

---

## 1. Source Table

| Field Name | Type | Description | Role in Model |
|-------------|------|--------------|----------------|
| id | Integer | Unique identifier for each news source | Identifier only |
| name | String | Name of the source (e.g., Reddit, Snopes, PolitiFact) | Contextual feature |
| url | String | URL of the data source | Metadata, not used directly in model |

---

## 2. Article Table

| Field Name | Type | Description | Role in Model |
|-------------|------|--------------|----------------|
| id | Integer | Unique identifier for each article | Identifier only |
| source_id | Integer | Foreign key linking to the Source table | Relationship reference |
| title | String | Title of the article | Text input for NLP |
| text | String | Main body or description of the article | Text input for NLP |
| published_at | Datetime | Publication date of the article | Temporal feature |
| label | String | Label indicating whether the article is Fake or Real | Target variable (y) |

---

## 3. Image Table

| Field Name | Type | Description | Role in Model |
|-------------|------|--------------|----------------|
| id | Integer | Unique identifier for each image | Identifier only |
| article_id | Integer | Foreign key linking to the related article | Relationship reference |
| image_url | String | URL of the associated image | Visual input reference |
| image_object | String | Description or object detected in the image (optional) | Visual-derived feature |

---

## 4. Metadata Table

| Field Name | Type | Description | Role in Model |
|-------------|------|--------------|----------------|
| id | Integer | Unique identifier for the metadata entry | Identifier only |
| article_id | Integer | Foreign key linking to the Article table | Relationship reference |
| key | String | Name of the metadata field (e.g., author, category) | Auxiliary feature |
| value | String | Value of the metadata field | Auxiliary feature |

---

## 5. Derived / Transformed Fields

| Field Name | Type | Description | Role in Model |
|-------------|------|--------------|----------------|
| title_length | Integer | Length of the article title in characters | Numerical feature |
| text_length | Integer | Length of the article text in characters | Numerical feature |
| num_images | Integer | Number of images detected per article | Numerical feature |
| has_image | Boolean | Indicates whether the article includes an image | Binary feature |

---

## Notes

- All textual fields (`title`, `text`) are normalized during transformation (lowercased, punctuation removed, etc.).
- Image metadata and content are stored in MinIO, while tabular data are stored as CSV in MinIO and optionally in PostgreSQL.
- The data schema is aligned with the conceptual model defined in `docs/schema.mmd` and `docs/schema.png`.

