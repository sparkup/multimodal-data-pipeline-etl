"""
Image extraction and upload utilities.

This module collects image URLs from a web page and uploads the images to MinIO,
optionally tagging them with an article identifier.
"""

import re
import logging
import requests
from bs4 import BeautifulSoup
import io
from urllib.parse import urlparse
import hashlib
from common.storage import get_minio_client, ensure_minio_bucket
from common.config import (
    MINIO_BUCKET_IMAGE
)

logger = logging.getLogger(__name__)

def extract_images_from_url(url: str, article_id: str = None):
    """
    Extract image URLs from a web page and upload them to MinIO.

    Args:
        url (str): Page URL to parse.
        article_id (str | None): Optional identifier to include in object names.

    Returns:
        list[str]: MinIO object paths for uploaded images.
    """
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        image_urls = [img["src"] for img in soup.find_all("img") if img.get("src") and img["src"].startswith("http")]
        # Limit to a small sample to avoid excessive downloads.
        image_urls = image_urls[:5]

        client = get_minio_client()
        ensure_minio_bucket(MINIO_BUCKET_IMAGE)

        uploaded_paths = []

        # Sanitize and truncate article_id if provided.
        sanitized_article_id = None
        if article_id:
            sanitized_article_id = re.sub(r'[^a-zA-Z0-9_-]', '_', article_id)[:50]

        for img_url in image_urls:
            try:
                img_response = requests.get(img_url, stream=True, timeout=10)
                img_response.raise_for_status()

                sha1 = hashlib.sha1(img_url.encode('utf-8')).hexdigest()
                path = urlparse(img_url).path
                ext = ".jpg"
                if '.' in path and len(path.split('.')[-1]) <= 5:
                    ext = '.' + path.split('.')[-1].split('?')[0].split('#')[0]

                if sanitized_article_id:
                    object_name = f"{sanitized_article_id}_{sha1}{ext}"
                else:
                    object_name = f"{sha1}{ext}"

                metadata = {}
                if sanitized_article_id:
                    metadata['article_id'] = sanitized_article_id
                metadata['source_url'] = img_url
                metadata['original_filename'] = path.split('/')[-1] if '/' in path else path

                client.put_object(
                    bucket_name=MINIO_BUCKET_IMAGE,
                    object_name=object_name,
                    data=io.BytesIO(img_response.content),
                    length=len(img_response.content),
                    content_type=img_response.headers.get("Content-Type", "image/jpeg"),
                    metadata=metadata
                )
                uploaded_paths.append(f"image/{object_name}")
                logger.info(f"Uploaded image {img_url} as {object_name} to MinIO bucket 'image'.")
            except Exception as e:
                logger.warning(f"Failed to download or upload image {img_url}: {e}")

        return uploaded_paths
    except Exception as e:
        logger.warning(f"Failed to extract images from {url}: {e}")
        return []
