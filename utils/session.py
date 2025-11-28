from typing import Dict, List, Optional
import uuid
from pydantic import BaseModel, Field
from datetime import datetime

class SessionData(BaseModel):
    session_id: str
    title: str = "New Chat"
    history: List[Dict[str, str]] = []
    metadata: Dict[str, str] = {}
    created_at: datetime = Field(default_factory=datetime.now)
    last_active: datetime = Field(default_factory=datetime.now)

class SessionManager:
    """
    Manages user sessions and chat history.
    Currently uses in-memory storage, but designed to be extensible for DB.
    """
    def __init__(self):
        self._sessions: Dict[str, SessionData] = {}

    def create_session(self) -> str:
        """Creates a new session and returns the session_id."""
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = SessionData(session_id=session_id)
        return session_id

    def get_session(self, session_id: str) -> Optional[SessionData]:
        """Retrieves a session by ID."""
        return self._sessions.get(session_id)

    def add_message(self, session_id: str, role: str, content: str):
        """Adds a message to the session history and updates last_active."""
        if session_id not in self._sessions:
            # Auto-create if missing (or could raise error depending on policy)
            self._sessions[session_id] = SessionData(session_id=session_id)
        
        session = self._sessions[session_id]
        session.history.append({"role": role, "content": content})
        session.last_active = datetime.now()

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        """Returns the chat history for a session."""
        session = self.get_session(session_id)
        return session.history if session else []

    def update_title(self, session_id: str, title: str):
        """Updates the title of a session."""
        if session_id in self._sessions:
            self._sessions[session_id].title = title

    def cleanup_sessions(self, max_age_hours: int = 24):
        """Removes sessions inactive for more than max_age_hours."""
        now = datetime.now()
        expired_sessions = []
        for sid, session in self._sessions.items():
            age = now - session.last_active
            if age.total_seconds() > (max_age_hours * 3600):
                expired_sessions.append(sid)
        
        for sid in expired_sessions:
            del self._sessions[sid]
        
        if expired_sessions:
            print(f"Cleaned up {len(expired_sessions)} expired sessions.")
