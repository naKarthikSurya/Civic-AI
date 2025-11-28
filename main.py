from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from orchestrator import Orchestrator
from dtos import ChatRequest, ChatResponse
from utils.session import SessionManager
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="LegalAdviser-AI API")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize Services
orchestrator = Orchestrator()
session_manager = SessionManager()

import asyncio

# ... (existing imports)

# Background Task for Session Cleanup
async def run_cleanup_task():
    while True:
        await asyncio.sleep(3600) # Run every hour
        session_manager.cleanup_sessions(max_age_hours=24)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_cleanup_task())

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not request.message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    if len(request.message) > 5000:
        raise HTTPException(status_code=400, detail="Message too long")
    
    session_id = request.session_id
    is_new_session = False
    
    # Validate or create session
    if not session_id or not session_manager.get_session(session_id):
        session_id = session_manager.create_session()
        is_new_session = True
        
    try:
        # Get history
        history = session_manager.get_history(session_id)
        
        # Generate Title if new session (simple heuristic: first 50 chars)
        if is_new_session or len(history) == 0:
            # Generate a short title from the query
            title = " ".join(request.message.split()[:6])  # First 6 words
            if len(title) > 40:
                title = title[:37] + "..."
            session_manager.update_title(session_id, title)
        
        # Process query
        response = await orchestrator.process_query(request.message, history)
        
        # Update history
        session_manager.add_message(session_id, "user", request.message)
        session_manager.add_message(session_id, "model", response.reply)
        
        response.session_id = session_id
        response.session_title = session_manager.get_session(session_id).title
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat/{session_id}/history")
async def get_chat_history(session_id: str):
    """Returns the chat history for a specific session."""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.history

@app.get("/sessions/{session_id}")
async def get_session_info(session_id: str):
    """Returns session metadata (title)."""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": session.session_id, "title": session.title}

# Page Routes

# Page Routes
# Page Routes
@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/chat")
async def read_chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/about")
async def read_about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

