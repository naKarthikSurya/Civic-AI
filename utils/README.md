# Utils Module

Utility functions and classes for the LegalAdviser-AI application.

## Overview

This module contains reusable components for session management, logging, and observability.

---

## Modules

### 1. Session Manager (`session.py`)

**Purpose**: Manages user chat sessions with disk-based persistence.

#### Features
- ✅ Create and manage chat sessions
- ✅ Store conversation history
- ✅ Persist sessions to disk (`sessions.json`)
- ✅ Auto-load sessions on server restart
- ✅ Auto-cleanup of old sessions (24hr TTL)

#### Class: `SessionData`

Pydantic model representing a chat session.

**Fields**:
```python
session_id: str              # Unique session identifier (UUID)
title: str                   # Session title (first6 words of query)
history: List[Dict[str, str]]  # Message history
metadata: Dict[str, str]     # Additional metadata
created_at: datetime         # Creation timestamp
last_active: datetime        # Last activity timestamp
```

#### Class: `SessionManager`

Manages all session operations.

**Methods**:

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `create_session()` | - | `str` | Creates new session, returns session_id |
| `get_session(session_id)` | `session_id: str` | `Optional[SessionData]` | Retrieves session by ID |
| `add_message(session_id, role, content)` | `session_id: str`<br>`role: str`<br>`content: str` | `None` | Adds message to history |
| `get_history(session_id)` | `session_id: str` | `List[Dict]` | Gets conversation history |
| `update_title(session_id, title)` | `session_id: str`<br>`title: str` | `None` | Updates session title |
| `cleanup_sessions(max_age_hours)` | `max_age_hours: int = 24` | `None` | Removes old sessions |

**Private Methods**:
- `_load_sessions()` - Loads sessions from `sessions.json` on startup
- `_save_sessions()` - Saves sessions to disk after every change

#### Usage Example

```python
from utils.session import SessionManager

# Initialize
manager = SessionManager()

# Create session
session_id = manager.create_session()

# Add messages
manager.add_message(session_id, "user", "What is Section 302 IPC?")
manager.add_message(session_id, "model", "Section 302 deals with...")

# Update title
manager.update_title(session_id, "Section 302 IPC Query")

# Retrieve history
history = manager.get_history(session_id)
print(history)  # [{"role": "user", "content": "..."}, ...]

# Get session
session = manager.get_session(session_id)
print(session.title)  # "Section 302 IPC Query"
```

#### Persistence Details

**File**: `sessions.json` (root directory)

**Format**:
```json
{
  "abc-123": {
    "session_id": "abc-123",
    "title": "RTI Application Help",
    "history": [
      {"role": "user", "content": "How to file RTI?"},
      {"role": "model", "content": "Follow these steps..."}
    ],
    "metadata": {},
    "created_at": "2025-11-29T10:00:00",
    "last_active": "2025-11-29T10:05:00"
  }
}
```

**Auto-Load**: Sessions automatically load on server startup
**Auto-Save**: Every change is immediately persisted to disk

#### Session Cleanup

Background task in `main.py` automatically cleans up old sessions:

```python
async def run_cleanup_task():
    while True:
        await asyncio.sleep(3600)  # Run every hour
        session_manager.cleanup_sessions(max_age_hours=24)
```

Sessions inactive for 24+ hours are deleted.

---

### 2. Tracing Utility (`tracing.py`)

**Purpose**: Provides observability through structured logging and tracing.

#### Features
- ✅ Structured JSON logging
- ✅ Function execution timing
- ✅ Error tracking
- ✅ Decorator-based tracing

#### Class: `Tracer`

Static utility for logging agent activities.

**Methods**:

| Method | Parameters | Description |
|--------|------------|-------------|
| `trace_agent()` | `agent_name: str`<br>`action: str`<br>`inputs: Dict`<br>`outputs: Any`<br>`duration: float` | Logs a structured trace event |

#### Decorator: `@trace_span(agent_name, action_name)`

Wraps functions to automatically log execution.

**Usage Example**:

```python
from utils.tracing import trace_span

class MyAgent:
    @trace_span("MyAgent", "process_query")
    def process_query(self, query: str) -> str:
        # Your logic here
        return "response"
```

**Log Output**:
```json
{
  "type": "agent_trace",
  "agent": "MyAgent",
  "action": "process_query",
  "inputs": {
    "args": ["What is RTI?"],
    "kwargs": {}
  },
  "outputs": "response",
  "duration_ms": 1234.56
}
```

#### Benefits
- Track performance bottlenecks
- Debug agent behavior
- Monitor production systems
- Analyze request patterns

#### Logging Configuration

Default configuration in `tracing.py`:

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
```

To change log level:
```python
import logging
logging.getLogger("LegalAdviser-Trace").setLevel(logging.DEBUG)
```

---

## Best Practices

### Session Management
1. Always check session exists before accessing
2. Update `last_active` on every interaction (auto-handled)
3. Set descriptive titles for UX
4. Keep history size manageable (current: unlimited, consider adding limit)

### Tracing
1. Use `@trace_span` for all agent methods
2. Log at INFO level for normal operations
3. Log at ERROR level for exceptions
4. Include relevant context in logs

---

## Error Handling

### SessionManager Errors

**File Permission Issues**:
```python
try:
    manager = SessionManager()
except IOError as e:
    print(f"Cannot access sessions.json: {e}")
```

**Corrupted sessions.json**:
- File is automatically reinitialized on error
- Error logged: `"Error loading sessions: {e}"`
- System continues with empty session dict

### Tracing Errors

Errors are caught and logged, exceptions are re-raised:

```python
@trace_span("Agent", "method")
def method(self):
    try:
        # ...
    except Exception as e:
        # Logged automatically by decorator
        raise  # Re-raised for upstream handling
```

---

## Testing

### Session Manager Tests

```python
import pytest
from utils.session import SessionManager

def test_create_session():
    manager = SessionManager()
    sid = manager.create_session()
    assert sid is not None
    assert manager.get_session(sid) is not None

def test_session_persistence():
    manager1 = SessionManager()
    sid = manager1.create_session()
    manager1.add_message(sid, "user", "test")
    
    # Simulate server restart
    manager2 = SessionManager()
    assert manager2.get_session(sid) is not None
    assert len(manager2.get_history(sid)) == 1
```

### Tracing Tests

```python
from utils.tracing import trace_span

@trace_span("TestAgent", "test_method")
def test_method():
    return "result"

# Check logs for trace output
test_method()
```

---

## Configuration

### Session Manager

```python
# Default storage file
manager = SessionManager(storage_file="sessions.json")

# Custom location
manager = SessionManager(storage_file="data/my_sessions.json")

# Cleanup interval
cleanup_sessions(max_age_hours=48)  # 48 hour TTL
```

### Tracing

```python
# Enable DEBUG logging
import logging
logging.getLogger("LegalAdviser-Trace").setLevel(logging.DEBUG)

# Custom logger
logger = logging.getLogger("MyCustomLogger")
```

---

## Performance Considerations

### Session Manager
- **Disk I/O**: Every session change writes to disk (consider batching for high-traffic scenarios)
- **Memory**: All sessions loaded in memory (fine for small-medium scale, consider DB for large scale)
- **Cleanup**: Runs hourly (adjust frequency in `main.py` if needed)

### Tracing
- **Overhead**: Minimal (~1-2ms per traced function call)
- **Log Volume**: Can grow quickly with INFO level - rotate logs in production

---

## Migration Guide

### From In-Memory to Database

To migrate  sessions to a database (e.g., PostgreSQL):

1. **Define database schema**:
```sql
CREATE TABLE sessions (
    session_id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(255),
    history JSONB,
    metadata JSONB,
    created_at TIMESTAMP,
    last_active TIMESTAMP
);
```

2. **Update SessionManager**:
```python
class DatabaseSessionManager(SessionManager):
    def __init__(self, db_connection):
        self.db = db_connection
    
    def _load_sessions(self):
        # Load from database
        pass
    
    def _save_sessions(self):
        # Save to database
        pass
```

3. **Swap implementation** in `main.py`:
```python
session_manager = DatabaseSessionManager(db)
```

---

## Dependencies

- `pydantic` - Data validation for SessionData
- `json` - Session serialization
- `logging` - Tracing and observability
- `datetime` - Timestamp management

---

## Learn More

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Python Logging Cookbook](https://docs.python.org/3/howto/logging-cookbook.html)
- [Main Project README](../README.md)
