from agents.analyzer import AnalyzerAgent
from agents.researcher import ResearchAgent
from agents.summarizer import SummarizerAgent
from dtos import ChatResponse
import logging

logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self):
        self.analyzer = AnalyzerAgent()
        self.researcher = ResearchAgent()
        self.summarizer = SummarizerAgent()

    async def process_query(self, query: str, history: list[dict] = [], session_id: str = None) -> ChatResponse:
        logger.info(f"User Query: {query}")
        
        try:
            # 1. ROUTER: Analyze Query & Intent
            analysis = self.analyzer.analyze_query(query, history)
            logger.info(f"Intent detected: {analysis.intent}")
            
            # 2. ROUTING LOGIC
            if analysis.intent == "clarify":
                return await self._run_clarification_flow(query, analysis, history)
            elif analysis.intent == "legal_advice":
                # Treat legal advice as a specialized research flow
                return await self._run_research_flow(query, analysis, history, session_id)
            else: # intent == "info" or fallback
                return await self._run_research_flow(query, analysis, history, session_id)
        except Exception as e:
            logger.error(f"Orchestrator Error: {e}", exc_info=True)
            raise e

    async def _run_clarification_flow(self, query: str, analysis: ChatResponse, history: list[dict]) -> ChatResponse:
        logger.info("Flow: Clarification")
        # Summarizer is sync for now, but we can wrap it or just call it
        reply = self.summarizer.summarize(query, analysis, history)
        return ChatResponse(reply=reply, analysis=analysis)

    async def _run_research_flow(self, query: str, analysis: ChatResponse, history: list[dict], session_id: str = None) -> ChatResponse:
        logger.info("Flow: Research/Legal")
        
        # Use ResearchAgent (ADK) with session_id for conversation continuity
        report = await self.researcher.research(query, history, user_session_id=session_id)
        
        # Update analysis with facts from report
        analysis.key_facts = report.key_facts
        analysis.relevant_judgments = report.relevant_judgments
        
        # The report summary is already a good reply, but we can optionally pass it through summarizer if needed.
        # For now, let's use the report summary directly as it comes from the Legal Adviser persona.
        reply = report.summary
        
        return ChatResponse(reply=reply, analysis=analysis)
