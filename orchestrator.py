from agents.analyzer import AnalyzerAgent
from agents.searcher import SearcherAgent
from agents.summarizer import SummarizerAgent
from agents.drafter import DraftingAgent
from dtos import ChatResponse
import logging

logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self):
        self.analyzer = AnalyzerAgent()
        self.searcher = SearcherAgent()
        self.summarizer = SummarizerAgent()
        self.drafter = DraftingAgent()

    def process_query(self, query: str) -> ChatResponse:
        print(f"\n{'='*50}\nUser: {query}\n{'='*50}")
        
        # 1. Analyze Query & Intent
        analysis = self.analyzer.analyze_query(query)
        print(f"\n[Analyzer Agent]: Intent detected -> '{analysis.intent}'")
        print(f"[Analyzer Agent]: Reasoning -> {analysis.reasoning}")
        
        if analysis.intent == "clarify":
            # Skip search and go straight to summarizer to ask questions
            reply = self.summarizer.summarize(query, analysis)
            print(f"\n[Summarizer Agent]: Asking clarification -> {reply}")
            print(f"\n{'='*50}\nFinal Response Sent\n{'='*50}")
            return ChatResponse(reply=reply, rti_draft=None, analysis=analysis)

        print(f"[Analyzer Agent]: Generated Search Queries -> {analysis.search_queries}")

        # 2. Search & Fetch
        search_results = self.searcher.search(analysis.search_queries)
        print(f"\n[Searcher Agent]: Found {len(search_results)} results.")
        for i, res in enumerate(search_results[:3]):
            print(f"  - {i+1}. {res.title} ({res.url})")
            
        search_context = self.searcher.fetch_content(search_results, priority_domains=analysis.priority_domains)
        
        # 3. Analyze Results (Fact Extraction)
        analysis = self.analyzer.analyze_results(analysis, search_context, search_results)
        print(f"\n[Analyzer Agent]: Extracted {len(analysis.key_facts)} key facts.")
        
        # 4. Summarize (Natural Response)
        reply = self.summarizer.summarize(query, analysis)
        print(f"\n[Summarizer Agent]: Generated Response -> {reply[:100]}...")
        
        # 5. Draft (On-Demand)
        rti_draft = None
        if analysis.intent == "draft_rti":
            print(f"\n[Drafting Agent]: Generating RTI Draft...")
            rti_draft = self.drafter.draft(query, analysis)
            print(f"[Drafting Agent]: Draft Generated.")
            
        print(f"\n{'='*50}\nFinal Response Sent\n{'='*50}")
        return ChatResponse(
            reply=reply,
            rti_draft=rti_draft,
            analysis=analysis
        )
