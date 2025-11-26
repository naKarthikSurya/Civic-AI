from typing import Dict, List, Optional
import uuid
from pydantic import BaseModel

class SessionData(BaseModel):
    session_id: str
    history: List[Dict[str, str]] = []
    metadata: Dict[str, str] = {}

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
        """Adds a message to the session history."""
        if session_id not in self._sessions:
            # Auto-create if missing (or could raise error depending on policy)
            self._sessions[session_id] = SessionData(session_id=session_id)
        
        self._sessions[session_id].history.append({"role": role, "content": content})

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        """Returns the chat history for a session."""
        session = self.get_session(session_id)
        return session.history if session else []
