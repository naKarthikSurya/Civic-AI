import trafilatura
import logging

logger = logging.getLogger(__name__)

def fetch_page_content(url: str) -> str:
    """
    Fetches and extracts the main text content from a URL using Trafilatura.
    """
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded)
            if text:
                return text
    except Exception as e:
        logger.error(f"Failed to fetch content from {url}: {e}")
    
    return ""
