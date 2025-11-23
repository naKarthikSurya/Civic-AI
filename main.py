from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from orchestrator import Orchestrator
from dtos import ChatRequest, ChatResponse
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="RTI Agent API")

orchestrator = Orchestrator()

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not request.message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    try:
        response = orchestrator.process_query(request.message)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "RTI Agent API is running"}
