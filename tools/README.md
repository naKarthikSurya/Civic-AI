# 🛠️ Tools Documentation

[![Tools](https://img.shields.io/badge/Tools-1%20Module-orange)](../README.md)

The `tools` package defines the framework for **custom tool extensions** that agents can invoke. It currently provides a base implementation and guidelines for adding new tools.

---

## 📂 Structure

- `base.py` – Core abstract classes (`ToolResult`, `AgentTool`) and common utilities.
- `README.md` – This documentation file.

---

## ⚙️ Core Classes (`base.py`)

### `ToolResult`
A Pydantic model representing the outcome of a tool execution.
```python
class ToolResult(BaseModel):
    content: Any = None          # Successful result data
    error: Optional[str] = None   # Error message if execution failed
    metadata: Optional[Dict] = None  # Additional context (e.g., source, timestamps)
```

### `AgentTool` (Abstract Base Class)
All custom tools must inherit from `AgentTool` and implement the following:
- **Properties**:
  - `name: str` – unique identifier used by the orchestrator.
  - `description: str` – human‑readable description.
- **Method**:
  - `execute(**kwargs) -> ToolResult` – performs the tool's action.

#### Example Implementation
```python
from tools.base import AgentTool, ToolResult

class LegalDatabaseTool(AgentTool):
    @property
    def name(self) -> str:
        return "legal_database"

    @property
    def description(self) -> str:
        return "Queries Indian legal database for statutes and case law"

    def execute(self, section: str, act: str = "IPC") -> ToolResult:
        try:
            result = database.query(act=act, section=section)
            return ToolResult(content=result, metadata={"source": "local_db", "act": act})
        except Exception as e:
            return ToolResult(error=str(e))
```

---

## 🚀 Adding a New Tool

1. **Create a file** in `tools/` (e.g., `my_tool.py`).
2. **Subclass `AgentTool`** and implement `name`, `description`, and `execute`.
3. **Register the tool** with the agent that will use it (see agent documentation).
4. **Document** the tool here, following the pattern above.

---

## 📚 Testing Tools

A simple pytest template:
```python
import pytest
from tools.my_tool import LegalDatabaseTool

def test_successful_query():
    tool = LegalDatabaseTool()
    result = tool.execute(section="302", act="IPC")
    assert result.error is None
    assert result.content is not None
    assert result.metadata["act"] == "IPC"

def test_error_handling():
    tool = LegalDatabaseTool()
    result = tool.execute(section="invalid")
    assert result.error is not None
    assert result.content is None
```
Run with `pytest tests/test_tools.py`.

---

## 📖 Further Reading

- [Main Project README](../README.md)
- [Google ADK Documentation](https://github.com/google/project-idx-ai-agents)
- [Gemini API Guide](https://ai.google.dev/docs)
