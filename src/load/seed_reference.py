"""
seed_reference.py
-----------------
Seeds reference or lookup data into the database (languages, media types, etc.).
"""

import logging
import pandas as pd
from load.db import insert_dataframe

logger = logging.getLogger(__name__)

def seed_reference_data():
    """
    Seed static reference tables with predefined data.
    """
    # Example static data
    media_types = pd.DataFrame({
        "code": ["text", "image", "audio", "video"],
        "description": [
            "Text content (articles, transcripts)",
            "Image content (photos, logos)",
            "Audio content (podcasts, sound bites)",
            "Video content (clips, interviews)"
        ]
    })

    try:
        insert_dataframe(media_types, "ref_media_types", if_exists="replace")
        logger.info("Reference data successfully seeded.")
    except Exception as e:
        logger.error(f"Error seeding reference data: {e}")
        raise

if __name__ == "__main__":
    seed_reference_data()
