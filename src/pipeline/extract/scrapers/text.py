"""
Text extraction utilities.

This module extracts readable text content from a web page while removing
scripts and style elements.
"""

import logging
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def extract_text_from_url(url: str) -> str:
    """
    Extract and clean textual content from an article URL.

    Args:
        url (str): URL of the article to scrape.

    Returns:
        str | None: Cleaned text content, or None if extraction fails.
    """
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove non-content elements.
        for element in soup(["script", "style", "noscript"]):
            element.extract()

        paragraphs = [p.get_text().strip() for p in soup.find_all("p") if len(p.get_text().strip()) > 40]
        # Limit to the first 10 substantial paragraphs.
        return "\n".join(paragraphs[:10])
    except Exception as e:
        logger.warning(f"Failed to extract text from {url}: {e}")
        return None
