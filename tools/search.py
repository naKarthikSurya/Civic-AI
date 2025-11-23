from ddgs import DDGS
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

def duckduckgo_search_tool(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Performs a search using DuckDuckGo (via ddgs).
    """
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", ""),
                    "source": "duckduckgo"
                })
    except Exception as e:
        logger.error(f"DuckDuckGo search failed: {e}")
    return results
