"""
Collection utilities for the multimodal ETL pipeline.

This module retrieves article metadata from HTML pages, RSS feeds, and JSON APIs,
then stores the collected dataset in MinIO for downstream extraction.
"""

import logging
import pandas as pd
import requests
import yaml
from pathlib import Path
from bs4 import BeautifulSoup
from io import BytesIO
from common.storage import get_minio_client, ensure_minio_bucket
from common.config import (
    FILE_COLLECT,
    MINIO_BUCKET_COLLECT
)
import feedparser

logger = logging.getLogger(__name__)

def load_config():
    """
    Load the YAML configuration file that defines data sources.

    Returns:
        dict: Parsed configuration containing source definitions.
    """
    config_path = Path(__file__).resolve().parents[2] / "common" / "config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def collect_articles(url: str, limit: int = 10) -> pd.DataFrame:
    """
    Scrape a web page and return a DataFrame of article metadata.

    Args:
        url (str): Source URL to scrape.
        limit (int): Maximum number of articles to return.

    Returns:
        pd.DataFrame: Article metadata with id, title, link, image_url, and source.
    """
    logger.info(f"Starting HTML article collection from {url}")
    articles_data = []

    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Try standard <article> parsing.
        articles = soup.find_all("article")[:limit]

        if not articles:
            logger.warning(f"No <article> tags found for {url} - trying fallback parser.")
            rows = soup.select("tr.athing")[:limit]
            for idx, row in enumerate(rows, 1):
                title_tag = row.select_one(".titleline a")
                link = title_tag["href"] if title_tag and title_tag.has_attr("href") else None
                articles_data.append({
                    "id": idx,
                    "title": title_tag.text.strip() if title_tag else "No title",
                    "link": link,
                    "image_url": None,
                    "source": url,
                })
        else:
            for idx, article in enumerate(articles, 1):
                title_tag = article.find("h1") or article.find("h2") or article.find("h3")
                link_tag = title_tag.find("a") if title_tag else None
                img_tag = article.find("img")
                articles_data.append({
                    "id": idx,
                    "title": title_tag.text.strip() if title_tag else "No title",
                    "link": link_tag["href"] if link_tag and link_tag.has_attr("href") else None,
                    "image_url": img_tag["src"] if img_tag and img_tag.has_attr("src") else None,
                    "source": url,
                })

    except Exception as e:
        logger.error(f"Error collecting from {url}: {e}")

    df = pd.DataFrame(articles_data)
    logger.info(f"Collected {len(df)} HTML articles from {url}")
    return df

def fetch_rss_articles(url: str, limit: int = 10) -> pd.DataFrame:
    """
    Fetch and parse articles from an RSS feed.

    Args:
        url (str): RSS feed URL.
        limit (int): Maximum number of entries to return.

    Returns:
        pd.DataFrame: Article metadata including title, link, image_url, and source.
    """
    logger.info(f"Starting RSS article collection from {url}")
    articles_data = []

    try:
        feed = feedparser.parse(url)
        entries = feed.entries[:limit]

        for idx, entry in enumerate(entries, 1):
            title = entry.get('title', 'No title')
            link = entry.get('link')
            image_url = None

            # Try to extract image from media_content or media_thumbnail.
            if 'media_content' in entry and entry.media_content:
                image_url = entry.media_content[0].get('url')
            elif 'media_thumbnail' in entry and entry.media_thumbnail:
                image_url = entry.media_thumbnail[0].get('url')

            # Fallback: extract image from HTML summary (e.g., PolitiFact, Reddit).
            if not image_url and 'summary' in entry:
                soup = BeautifulSoup(entry['summary'], 'html.parser')
                img_tag = soup.find('img')
                if img_tag and img_tag.has_attr('src'):
                    image_url = img_tag['src']

            articles_data.append({
                "id": idx,
                "title": title.strip(),
                "link": link,
                "image_url": image_url,
                "source": url,
                "source_name": feed.feed.get("title", "unknown source")
            })

    except Exception as e:
        logger.error(f"Error collecting RSS from {url}: {e}")

    df = pd.DataFrame(articles_data)
    logger.info(f"Collected {len(df)} RSS articles from {url}")
    return df

def fetch_api_articles(api_url: str, params=None, headers=None, limit: int = 10) -> pd.DataFrame:
    """
    Fetch articles from a JSON API endpoint and convert to a DataFrame.

    Args:
        api_url (str): API endpoint URL.
        params (dict | None): Optional query parameters.
        headers (dict | None): Optional HTTP headers.
        limit (int): Maximum number of items to return.

    Returns:
        pd.DataFrame: Article metadata with id, title, link, image_url, and source.
    """
    logger.info(f"Starting API article collection from {api_url}")
    articles_data = []

    try:
        response = requests.get(api_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Handle common JSON structures like {"articles": [...]} or {"data": [...]}.
        articles_list = []
        if isinstance(data, dict):
            # Try common keys.
            if 'articles' in data and isinstance(data['articles'], list):
                articles_list = data['articles'][:limit]
            elif 'data' in data and isinstance(data['data'], list):
                articles_list = data['data'][:limit]
            else:
                # Fallback: treat the dict as a single-item list.
                articles_list = [data] if limit > 0 else []
        elif isinstance(data, list):
            articles_list = data[:limit]
        else:
            logger.warning(f"Unexpected JSON structure from API: {api_url}")

        for idx, item in enumerate(articles_list, 1):
            title = item.get('title') or item.get('headline') or "No title"
            link = item.get('url') or item.get('link')
            image_url = item.get('image_url') or item.get('image') or None
            articles_data.append({
                "id": idx,
                "title": title,
                "link": link,
                "image_url": image_url,
                "source": api_url,
            })

    except Exception as e:
        logger.error(f"Error collecting API articles from {api_url}: {e}")

    df = pd.DataFrame(articles_data)
    logger.info(f"Collected {len(df)} API articles from {api_url}")
    return df

def upload_to_minio(df: pd.DataFrame, filename: str = FILE_COLLECT):
    """
    Upload a DataFrame to MinIO as a CSV file.

    Args:
        df (pd.DataFrame): Dataset to upload.
        filename (str): Object name in the MinIO bucket.
    """
    if df.empty:
        logger.warning("No articles to upload - DataFrame is empty.")
        return

    client = get_minio_client()
    ensure_minio_bucket(MINIO_BUCKET_COLLECT)

    csv_bytes = df.to_csv(index=False).encode("utf-8")

    client.put_object(
        bucket_name=MINIO_BUCKET_COLLECT,
        object_name=filename,
        data=BytesIO(csv_bytes),
        length=len(csv_bytes),
        content_type="text/csv",
    )

    logger.info(f"Uploaded {filename} to MinIO bucket 'collect'.")


def run_collection():
    """
    Run the collection workflow for all enabled sources.

    This is the main entrypoint for the Airflow `collect_task`.
    """
    config = load_config()
    sources = [src for src in config.get("sources", []) if src.get("enabled", False)]

    if not sources:
        logger.warning("No sources enabled in config.yaml.")
        return

    all_dataframes = []

    for src in sources:
        url = src.get("url")
        name = src.get("name", "unknown source")
        src_type = src.get("type", "html").lower()
        if src_type == "rss":
            logger.info(f"Collecting RSS articles from {name} ({url})")
            df = fetch_rss_articles(url)
        elif src_type == "api":
            logger.info(f"Collecting API articles from {name} ({url})")
            params = src.get("params")
            headers = src.get("headers")
            df = fetch_api_articles(url, params=params, headers=headers)
        else:
            logger.info(f"Collecting HTML articles from {name} ({url})")
            df = collect_articles(url)
        if not df.empty:
            all_dataframes.append(df)
        else:
            logger.warning(f"No articles found for {name}")

    if all_dataframes:
        final_df = pd.concat(all_dataframes, ignore_index=True)
        upload_to_minio(final_df)
        logger.info(f"Total {len(final_df)} articles uploaded to MinIO.")
    else:
        logger.warning("No data collected from any source.")


if __name__ == "__main__":
    run_collection()
