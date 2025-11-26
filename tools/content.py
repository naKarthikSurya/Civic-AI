import trafilatura
import logging
from tools.base import AgentTool, ToolResult

logger = logging.getLogger(__name__)

class ContentTool(AgentTool):
    @property
    def name(self) -> str:
        return "fetch_content"

    @property
    def description(self) -> str:
        return "Fetches and extracts the main text content from a URL."

    def execute(self, input: str) -> ToolResult:
        """
        Fetches and extracts the main text content from a URL using Trafilatura.
        """
        try:
            downloaded = trafilatura.fetch_url(input)
            if downloaded:
                text = trafilatura.extract(downloaded)
                if text:
                    return ToolResult(content=text)
            return ToolResult(content="")
        except Exception as e:
            logger.error(f"Failed to fetch content from {input}: {e}")
            return ToolResult(content="", error=str(e))

# Backward compatibility wrapper
def fetch_page_content(url: str) -> str:
    tool = ContentTool()
    result = tool.execute(url=url)
    return result.content
