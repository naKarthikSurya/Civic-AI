# 🛠️ Utils Documentation

[![Utils](https://img.shields.io/badge/Utils-2%20Modules-green)](../README.md)

The `utils` package provides reusable building blocks for session management, tracing, and other cross‑cutting concerns.

---

## 📂 Structure

- `session.py` – Handles user session lifecycle, persistence to `sessions.json`, and automatic cleanup.
- `tracing.py` – Structured logging and performance tracing utilities used by all agents.

---

## 📋 Session Manager (`session.py`)

**Purpose**: Keep conversation history across requests and ensure stale sessions are removed.

### Core Classes
- `SessionData` – Pydantic model representing a single session.
- `SessionManager` – Singleton‑style manager exposing CRUD operations.

### Public API
| Method | Parameters | Returns | Description |
|---|---|---|---|
| `create_session()` | – | `str` | Creates a new session and returns its UUID. |
| `get_session(session_id)` | `session_id: str` | `Optional[SessionData]` | Retrieves a session object or `None` if missing. |
| `add_message(session_id, role, content)` | `session_id: str`, `role: str`, `content: str` | `None` | Appends a message to the session history. |
| `get_history(session_id)` | `session_id: str` | `List[Dict]` | Returns the ordered list of messages. |
| `update_title(session_id, title)` | `session_id: str`, `title: str` | `None` | Sets a human‑readable title for the session (used in UI). |
| `cleanup_sessions(max_age_hours=24)` | `max_age_hours: int` | `None` | Deletes sessions older than the TTL.

### Persistence Details
- Sessions are stored in **`sessions.json`** at the repository root.
- The file is loaded on server start and saved after every mutation.
- Errors loading the file fall back to an empty store and are logged.

### Usage Example
```python
from utils.session import SessionManager

manager = SessionManager()
session_id = manager.create_session()
manager.add_message(session_id, "user", "What is Section 302 IPC?")
manager.add_message(session_id, "assistant", "Section 302 deals with murder...")
print(manager.get_history(session_id))
```

---

## 📈 Tracing Utility (`tracing.py`)

**Purpose**: Provide observability for debugging and performance monitoring.

### Features
- **Structured JSON logs** – easy to ship to log aggregation services.
- **Execution timing** – `@trace_span` decorator records start/end timestamps.
- **Error capture** – automatically logs exceptions with stack traces.

### Core API
- `Tracer.trace_agent(agent_name, action, inputs, outputs, duration)` – low‑level logging function.
- `@trace_span(agent_name, action_name)` – decorator to wrap any function.

### Example
```python
from utils.tracing import trace_span

@trace_span("Analyzer", "analyze_query")
def analyze_query(query):
    # ... implementation ...
    return result
```

Logs will look like:
```json
{ "type": "agent_trace", "agent": "Analyzer", "action": "analyze_query", "inputs": {"args": ["Police refused FIR?"]}, "outputs": {"intent": "legal_advice"}, "duration_ms": 124.5 }
```

---

## ⚙️ Configuration

Both utilities read configuration from environment variables when needed (e.g., `SESSION_TTL_HOURS`). Defaults are defined in the module.

---

## 🧪 Testing

```bash
pytest tests/test_utils.py
```

Typical tests verify session creation, persistence, cleanup, and that tracing logs are emitted.

---

## 📚 Further Reading

- [Main Project README](../README.md)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Docs](https://docs.pydantic.dev/)
