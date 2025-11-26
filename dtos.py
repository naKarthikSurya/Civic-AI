from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    source: str = "web"

class AnalysisResult(BaseModel):
    intent: Literal["info", "legal_advice", "clarify"] = Field(description="User intent: 'info', 'legal_advice', or 'clarify' if more details are needed.")
    search_queries: List[str] = Field(description="List of optimized search queries.")
    key_facts: List[str] = Field(description="Extracted key facts from search results.")
    relevant_judgments: List[SearchResult] = Field(description="List of relevant judgments found.")
    reasoning: str = Field(description="Internal reasoning about the problem.")
    priority_domains: List[str] = Field(default_factory=list, description="List of domains to prioritize in search results (e.g., 'indiankanoon.org').")

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    analysis: Optional[AnalysisResult] = None
    session_id: Optional[str] = None
