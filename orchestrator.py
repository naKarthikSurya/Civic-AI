from agents.analyzer import AnalyzerAgent
from agents.searcher import SearcherAgent
from agents.summarizer import SummarizerAgent
from dtos import ChatResponse
import logging

logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self):
        self.analyzer = AnalyzerAgent()
        self.searcher = SearcherAgent()
        self.summarizer = SummarizerAgent()

    def process_query(self, query: str, history: list[dict] = []) -> ChatResponse:
        logger.info(f"User Query: {query}")
        
        try:
            # 1. ROUTER: Analyze Query & Intent
            analysis = self.analyzer.analyze_query(query, history)
            logger.info(f"Intent detected: {analysis.intent}")
            
            # 2. ROUTING LOGIC
            if analysis.intent == "clarify":
                return self._run_clarification_flow(query, analysis, history)
            elif analysis.intent == "legal_advice":
                # Treat legal advice as a specialized research flow
                return self._run_research_flow(query, analysis, history)
            else: # intent == "info" or fallback
                return self._run_research_flow(query, analysis, history)
        except Exception as e:
            logger.error(f"Orchestrator Error: {e}", exc_info=True)
            raise e

    def _run_clarification_flow(self, query: str, analysis: ChatResponse, history: list[dict]) -> ChatResponse:
        logger.info("Flow: Clarification")
        reply = self.summarizer.summarize(query, analysis, history)
        return ChatResponse(reply=reply, analysis=analysis)

    def _run_research_flow(self, query: str, analysis: ChatResponse, history: list[dict]) -> ChatResponse:
        logger.info("Flow: Research/Legal")
        logger.info(f"Search Queries: {analysis.search_queries}")

        # Search & Fetch
        search_results = self.searcher.search(analysis.search_queries)
        logger.info(f"Found {len(search_results)} results.")
        
        search_context = self.searcher.fetch_content(search_results, priority_domains=analysis.priority_domains)
        
        # Analyze Results (Fact Extraction)
        analysis = self.analyzer.analyze_results(analysis, search_context, search_results)
        logger.info(f"Extracted {len(analysis.key_facts)} key facts.")
        
        # Summarize
        reply = self.summarizer.summarize(query, analysis, history)
        
        return ChatResponse(reply=reply, analysis=analysis)
