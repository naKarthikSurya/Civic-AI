from duckduckgo_search import DDGS
from typing import List, Dict, Any
import logging
from tools.base import AgentTool, ToolResult

logger = logging.getLogger(__name__)

class SearchTool(AgentTool):
    @property
    def name(self) -> str:
        return "duckduckgo_search"

    @property
    def description(self) -> str:
        return "Performs a web search using DuckDuckGo to find relevant information."

    def execute(self, query: str, max_results: int = 5) -> ToolResult:
        """
        Performs a search using DuckDuckGo.
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
            return ToolResult(content=results)
        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")
            return ToolResult(content=[], error=str(e))

# Backward compatibility wrapper (optional, but good for gradual migration)
def duckduckgo_search_tool(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    tool = SearchTool()
    result = tool.execute(query=query, max_results=max_results)
    return result.content
