import google.generativeai as genai
import os
import json
from dtos import AnalysisResult, SearchResult
from typing import List
import logging
from utils.tracing import trace_span

logger = logging.getLogger(__name__)

class AnalyzerAgent:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found. Please set it in your .env file")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    @trace_span("AnalyzerAgent", "analyze_query")
    def analyze_query(self, query: str, history: list[dict] = []) -> AnalysisResult:
        """
        Step 1: Analyze user query to determine intent and generate search queries.
        """
        history_text = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in history[-5:]]) # Last 5 messages
        
        prompt = f"""<system_role>
You are an expert Legal Analyst for India (LegalAdviser-AI). Your goal is to understand the user's need and generate precise search queries to find the right information across various Indian Laws (IPC, CrPC, BNS, RTI, etc.).
</system_role>

<chat_history>
{history_text}
</chat_history>

<user_query>
{query}
</user_query>

<task>
1. **Analyze Intent**: Determine if the user wants "info" (general queries), "legal_advice" (seeking solutions/judgments for a problem), or needs to "clarify" (vague query).
   - **"legal_advice"**: If the user describes a specific problem (e.g., "Police refused FIR", "Marks not given", "Cheque bounced") and seeks a solution or remedy.
   - **"clarify"**: If the query is too vague to give specific advice.
   - **"info"**: General questions about laws/rules.

2. **Generate Search Queries**:
   - If intent is "legal_advice", you MUST generate queries for **Case Law** and **Judgments**.
   - Use `site:indiankanoon.org` and `site:devgan.in` aggressively.
   - For IPC/CrPC/BNS queries, prioritize `devgan.in`.
</task>

<rules_for_search_queries>
- **Keywords Only**: Do NOT use natural language questions.
- **Operators**: Use `site:`, `""`, `OR`.
- **Mandatory**: If intent is "legal_advice", at least 2 queries MUST be `site:indiankanoon.org [keywords]` or `site:devgan.in [keywords]`.
</rules_for_search_queries>

<output_format>
Respond with valid JSON only:
{{
    "intent": "info|legal_advice|clarify",
    "search_queries": [
        "site:indiankanoon.org [keywords] (Judgment 1)",
        "site:devgan.in [keywords] (Section info)",
        "[keywords] legal rules"
    ],
    "priority_domains": ["indiankanoon.org", "devgan.in"],
    "reasoning": "..."
}}
</output_format>"""
        
        try:
            response = self.model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            data = json.loads(response.text)
            
            # Print what the analyzer understood
            print("\nANALYZER AGENT - analyze_query()")
            print(f"User Query: {query}")
            print(f"Intent Detected: {data.get('intent', 'info')}")
            print(f"Search Queries Generated:")
            for sq in data.get("search_queries", []):
                print(f"  - {sq}")
            print(f"Reasoning: {data.get('reasoning', '')}")
            
            return AnalysisResult(
                intent=data.get("intent", "info"),
                search_queries=data.get("search_queries", [query]),
                priority_domains=data.get("priority_domains", ["indiankanoon.org", "devgan.in"]),
                key_facts=[],
                relevant_judgments=[],
                reasoning=data.get("reasoning", "")
            )
        except Exception as e:
            logger.error(f"Query analysis failed: {e}")
            return AnalysisResult(intent="info", search_queries=[query], key_facts=[], relevant_judgments=[], reasoning="Error in analysis")

    @trace_span("AnalyzerAgent", "analyze_results")
    def analyze_results(self, current_analysis: AnalysisResult, search_context: str, search_results: List[SearchResult]) -> AnalysisResult:
        """
        Step 2: Analyze search results to extract key facts and relevant judgments.
        STRICT RULE: Do not assume or predict. Use ONLY the provided search_context.
        """
        prompt = f"""You are an expert Legal Analyst extracting information from search results.

<search_context>
{search_context}
</search_context>

<task>
Carefully analyze the search context above and extract:

1. KEY FACTS
   - Extract factual information relevant to the legal query
   - Include specific Acts, Sections, rules, or procedures mentioned
   - Include relevant case law or court decisions if present
   - CRITICAL: Only extract facts explicitly stated in the search context
   - Do NOT invent, assume, or hallucinate information

2. RELEVANT JUDGMENTS
   - Note any court cases (Supreme Court/High Court) or CIC decisions mentioned
   - Include case names and key rulings if available
   
STRICT RULES:
- Base your analysis ONLY on the provided search context
- If information is not in the context, do not include it
- Be specific and cite sources when possible
</task>

<output_format>
Respond with ONLY valid JSON:
{{
    "key_facts": ["fact 1", "fact 2", "fact 3"],
    "relevant_judgments_indices": [0, 2]
}}
</output_format>"""
        
        try:
            response = self.model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            data = json.loads(response.text)
            
            # Update the analysis object
            current_analysis.key_facts = data.get("key_facts", [])
            # For simplicity, we just pass all search results as relevant for now, 
            # or we could filter based on the indices if the LLM was perfect.
            # Let's just pass the top results that were actually fetched.
            current_analysis.relevant_judgments = search_results 
            
            return current_analysis
        except Exception as e:
            logger.error(f"Result analysis failed: {e}")
            return current_analysis
