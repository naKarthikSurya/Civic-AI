import os
import logging
import json
import re
from typing import List, Optional
import asyncio

from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search
from google.genai import types

from dtos import ResearchReport, SearchResult

logger = logging.getLogger(__name__)

class ResearchAgent:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found. Please set it in your .env file")
        
        # Initialize Gemini Model
        self.model = Gemini(model="gemini-2.5-flash")
        
        # System Prompt with Legal Adviser Persona and Acts
        self.system_prompt = """
        You are an expert Legal Adviser and Researcher for Indian Law (LegalAdviser-AI).
        Your goal is to provide accurate, actionable legal advice in a **natural, conversational, and empathetic manner**.
        
        **Target Audience:** General Public (Non-lawyers). Use simple, easy-to-understand English.
        
        You have access to Google Search to find the latest information, judgments, and legal texts.
        
        Your capabilities cover the following Acts and Laws:
        - Indian Penal Code, 1860 (IPC)
        - Bharatiya Nyaya Sanhita, 2023 (BNS)
        - Code of Criminal Procedure, 1973 (CrPC)
        - Negotiable Instruments Act, 1881
        - Hindu Marriage Act, 1955
        - Indian Divorce Act, 1869
        - Indian Evidence Act, 1872
        - Civil Procedure Code, 1908
        - Motor Vehicles Act, 1988
        - Right to Information Act, 2005 (RTI)
        
        When answering:
        1. **Be Direct & Concise:** Answer the question immediately. Keep the response **under 150 words**. Be brief and to-the-point.
        2. **Simple English:** Avoid complex legal jargon. If you must use a term, explain it simply.
        3. **Practical Steps:** Give 2-3 clear, actionable steps in bullet points.
        4. **Cite Laws Naturally:** Mention relevant Sections/Acts briefly within the text.
        5. **Include Case Examples:** When providing legal advice, include 2-3 relevant court judgments in the "relevant_judgments" array. Keep case descriptions VERY brief (1 line each in the summary).
        6. **Devgan.in Priority:** For IPC/CrPC/BNS, prioritize information from 'devgan.in' if available.
        
        **CRITICAL: Be BRIEF! Users want quick, actionable advice, not essays.**
        
        **CRITICAL: OUTPUT FORMAT**
        You MUST return a valid JSON object. Do not return plain text.
        {
            "key_facts": ["fact 1", "fact 2"],
            "summary": "Your BRIEF, actionable answer (under 150 words). Use bullet points. Mention 1-2 case examples by name inline.",
            "relevant_judgments": [
                {"title": "Case Title", "url": "URL", "snippet": "One-line relevance", "source": "Source Name"}
            ]
        }
        
        **IMPORTANT:** Keep the summary VERY brief. Include 2-3 cases in "relevant_judgments" array, not 4-5.
        """
        
        class LegalAdviserAgent(Agent):
            pass

        # Initialize Agent
        self.agent = LegalAdviserAgent(
            name="LegalAdviserAgent",
            model=self.model,
            tools=[google_search],
            instruction=self.system_prompt
        )
        
        # ADK infers app_name from the directory ('agents'), so we match it to avoid warnings
        self.runner = InMemoryRunner(agent=self.agent, app_name="agents")

    async def research(self, query: str, history: list[dict] = [], user_session_id: str = None) -> ResearchReport:
        logger.info(f"Starting research for: {query}")
        
        # Query Optimization for specific sources
        search_query = query
        lower_query = query.lower()
        
        # Append site:devgan.in for specific laws as requested
        if any(term in lower_query for term in ["ipc", "crpc", "penal code", "criminal procedure", "bns", "bharatiya nyaya sanhita"]):
             search_query = f"{query} (source: devgan.in OR indiankanoon.org)"
        
        try:
            # Use the user's session ID for ADK session continuity
            # This ensures conversation history is maintained across queries
            adk_session_id = f"adk_{user_session_id}" if user_session_id else "session_" + os.urandom(4).hex()
            
            # Always try to create the session - ADK will reuse if it already exists
            try:
                await self.runner.session_service.create_session(
                    app_name="agents", 
                    user_id="researcher", 
                    session_id=adk_session_id
                )
                logger.info(f"Created new ADK session: {adk_session_id}")
            except Exception as e:
                # Session might already exist, which is fine - we'll reuse it
                logger.info(f"Using existing ADK session: {adk_session_id}")
            
            # Format history for context
            history_context = ""
            if history:
                history_context = "<chat_history>\n" + "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in history[-5:]]) + "\n</chat_history>\n\n"

            # Run the agent
            event_generator = self.runner.run_async(
                user_id="researcher",
                session_id=adk_session_id,
                new_message=types.Content(role="user", parts=[types.Part(text=history_context + search_query)])
            )
            
            text_response = ""
            async for event in event_generator:
                # Extract text from event content
                if hasattr(event, 'content') and event.content:
                    # event.content is types.Content
                    for part in event.content.parts:
                        if part.text:
                            text_response += part.text
            
            # Robust JSON extraction
            json_match = re.search(r"```json\s*(.*?)\s*```", text_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Fallback: try to find the first '{' and last '}'
                start = text_response.find('{')
                end = text_response.rfind('}')
                if start != -1 and end != -1:
                    json_str = text_response[start:end+1]
                else:
                    json_str = text_response # Hope for the best
            
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse JSON. Falling back to raw text. Raw response: {text_response}")
                # Fallback: Treat the entire response as the summary
                data = {
                    "key_facts": [],
                    "summary": text_response, # Use the raw text as the summary
                    "relevant_judgments": []
                }
            
            # Map to ResearchReport
            relevant_judgments_data = data.get("relevant_judgments", [])
            relevant_judgments = [
                SearchResult(
                    title=j.get("title", "Unknown"),
                    url=j.get("url", ""),
                    snippet=j.get("snippet", ""),
                    source=j.get("source", "Google Search")
                ) for j in relevant_judgments_data
            ]
            
            return ResearchReport(
                query=query,
                key_facts=data.get("key_facts", []),
                relevant_judgments=relevant_judgments,
                summary=data.get("summary", "")
            )
            
        except Exception as e:
            logger.error(f"Research failed: {e}", exc_info=True)
            return ResearchReport(
                query=query,
                key_facts=["Error during research"],
                relevant_judgments=[],
                summary=f"Failed to conduct research due to error: {e}"
            )

