from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel

class ToolResult(BaseModel):
    content: Any
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}

class AgentTool(ABC):
    """
    Abstract base class for Agent Tools, inspired by the Model Context Protocol (MCP).
    Enforces a standard interface for all tools.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the tool."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """A description of what the tool does."""
        pass

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """
        Execute the tool with the given arguments.
        Returns a ToolResult object.
        """
        pass
