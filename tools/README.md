# Tools Module

Custom tools and utilities for extending agent capabilities.

## Overview

This module provides a framework for creating custom tools that agents can use. Currently implements a base class following the Model Context Protocol (MCP) pattern.

---

## Base Tool (`base.py`)

### Class: `ToolResult`

Pydantic model for tool execution results.

**Fields**:
```python
content: Any                    # Tool output/result
error: Optional[str]           # Error message if failed
metadata: Optional[Dict]       # Additional context
```

**Usage**:
```python
from tools.base import ToolResult

# Success
result = ToolResult(content="Data retrieved successfully")

# Error
result = ToolResult(
    content=None,
    error="Connection timeout",
    metadata={"retry_count": 3}
)
```

### Class: `AgentTool` (Abstract Base Class)

Base class for all custom tools.

**Abstract Properties**:
- `name` → `str`: Tool identifier
- `description` → `str`: Human-readable description

**Abstract Methods**:
- `execute(**kwargs) → ToolResult`: Execute the tool

**Example Implementation**:

```python
from tools.base import AgentTool, ToolResult

class WebScraperTool(AgentTool):
    @property
    def name(self) -> str:
        return "web_scraper"
    
    @property
    def description(self) -> str:
        return "Scrapes content from a given URL"
    
    def execute(self, url: str) -> ToolResult:
        try:
            # Your scraping logic
            content = scrape_website(url)
            return ToolResult(content=content)
        except Exception as e:
            return ToolResult(
                content=None,
                error=str(e)
            )
```

---

## Creating Custom Tools

### Step 1: Define Your Tool

Create a new file `tools/my_tool.py`:

```python
from tools.base import AgentTool, ToolResult
from typing import Dict, Any

class LegalDatabaseTool(AgentTool):
    """Queries a custom legal database"""
    
    @property
    def name(self) -> str:
        return "legal_database"
    
    @property
    def description(self) -> str:
        return "Queries Indian legal database for statutes and case law"
    
    def execute(self, section: str, act: str = "IPC") -> ToolResult:
        """
        Query legal database
        
        Args:
            section: Section number (e.g., "302")
            act: Act name (default: "IPC")
        
        Returns:
            ToolResult with statute details
        """
        try:
            # Query your database
            result = database.query(act=act, section=section)
            
            return ToolResult(
                content=result,
                metadata={"source": "local_db", "act": act}
            )
        except Exception as e:
            return ToolResult(
                content=None,
                error=f"Database query failed: {str(e)}"
            )
```

### Step 2: Register with Agent

Add to your agent class:

```python
from agents.researcher import ResearchAgent
from tools.my_tool import LegalDatabaseTool

class EnhancedResearchAgent(ResearchAgent):
    def __init__(self):
        super().__init__()
        self.legal_db = LegalDatabaseTool()
    
    async def research(self, query: str, history: list = []):
        # Use custom tool
        if "section" in query.lower():
            section = extract_section(query)
            db_result = self.legal_db.execute(section=section)
            
            if not db_result.error:
                # Use database result
                return process_result(db_result.content)
        
        # Fall back to web search
        return await super().research(query, history)
```

---

## Tool Patterns

### 1. Data Retrieval Tool

```python
class DataRetrievalTool(AgentTool):
    @property
    def name(self) -> str:
        return "data_retriever"
    
    @property
    def description(self) -> str:
        return "Retrieves data from external source"
    
    def execute(self, query: str) -> ToolResult:
        data = fetch_data(query)
        return ToolResult(content=data)
```

### 2. Validation Tool

```python
class ValidationTool(AgentTool):
    @property
    def name(self) -> str:
        return "validator"
    
    @property
    def description(self) -> str:
        return "Validates legal document format"
    
    def execute(self, document: Dict) -> ToolResult:
        is_valid = validate_document(document)
        return ToolResult(
            content={"valid": is_valid},
            metadata={"document_type": document.get("type")}
        )
```

### 3. Transformation Tool

```python
class PDFConverterTool(AgentTool):
    @property
    def name(self) -> str:
        return "pdf_converter"
    
    @property
    def description(self) -> str:
        return "Converts RTI application to PDF"
    
    def execute(self, text: str, metadata: Dict) -> ToolResult:
        try:
            pdf_bytes = generate_pdf(text, metadata)
            return ToolResult(
                content=pdf_bytes,
                metadata={"format": "pdf", "size": len(pdf_bytes)}
            )
        except Exception as e:
            return ToolResult(content=None, error=str(e))
```

---

## Tool Best Practices

### Error Handling
```python
def execute(self, **kwargs) -> ToolResult:
    try:
        # Validate inputs
        if not kwargs.get("required_param"):
            return ToolResult(
                content=None,
                error="Missing required parameter: required_param"
            )
        
        # Execute
        result = your_logic()
        
        # Return success
        return ToolResult(content=result)
        
    except ValueError as e:
        # Handle specific errors
        return ToolResult(content=None, error=f"Validation error: {e}")
    
    except Exception as e:
        # Handle unexpected errors
        return ToolResult(content=None, error=f"Unexpected error: {e}")
```

### Logging
```python
import logging

logger = logging.getLogger(__name__)

class MyTool(AgentTool):
    def execute(self, **kwargs) -> ToolResult:
        logger.info(f"Executing {self.name} with params: {kwargs}")
        
        result = process()
        
        logger.info(f"Tool completed successfully")
        return ToolResult(content=result)
```

### Caching
```python
from functools import lru_cache

class CachedTool(AgentTool):
    @lru_cache(maxsize=100)
    def _fetch_data(self, key: str):
        # Expensive operation
        return database.query(key)
    
    def execute(self, key: str) -> ToolResult:
        data = self._fetch_data(key)
        return ToolResult(content=data)
```

---

## Testing Tools

```python
import pytest
from tools.my_tool import LegalDatabaseTool

def test_tool_success():
    tool = LegalDatabaseTool()
    result = tool.execute(section="302", act="IPC")
    
    assert result.error is None
    assert result.content is not None
    assert result.metadata["act"] == "IPC"

def test_tool_error_handling():
    tool = LegalDatabaseTool()
    result = tool.execute(section="invalid")
    
    assert result.error is not None
    assert result.content is None
```

Run tests:
```bash
pytest tests/test_tools.py
```

---

## Future Tool Ideas

### Legal Document Parser
```python
class LegalDocumentParser(AgentTool):
    """Extracts structured data from legal documents"""
    # Parse PDFs, extract sections, identify parties, etc.
```

### RTI Draft Generator
```python
class RTIDraftTool(AgentTool):
    """Generates RTI application drafts"""
    # Takes user input, generates formatted RTI letter
```

### Case Law Analyzer
```python
class CaseLawAnalyzer(AgentTool):
    """Analyzes similarities between cases"""
    # Compares facts, identifies precedents
```

### Legal Form Builder
```python
class LegalFormBuilder(AgentTool):
    """Builds legal forms (complaints, affidavits, etc.)"""
    # Template-based form generation
```

---

## Integration with ADK

While the current Researcher Agent uses Google ADK's built-in `google_search` tool, you can create custom tools:

```python
from google.adk.tools import tool

@tool(
    name="legal_database",
    description="Queries Indian legal database"
)
def query_legal_db(section: str, act: str = "IPC") -> str:
    """Query legal database for statutes"""
    # Implementation
    return result
```

Then register in Agent:

```python
from my_tools import query_legal_db

agent = Agent(
    name="LegalAgent",
    model=model,
    tools=[google_search, query_legal_db]  # Add custom tool
)
```

---

## Dependencies

- `pydantic` - Data validation for ToolResult
- `abc` - Abstract base class support
- `typing` - Type hints

---

## Learn More

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Google ADK Tools](https://github.com/google/project-idx-ai-agents)
- [Main Project README](../README.md)
