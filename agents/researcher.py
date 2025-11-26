import google.generativeai as genai
import os
from typing import List
from tools.search import hybrid_search
from tools.content import fetch_page_content
from dtos import ResearchReport, SearchResult
import logging

logger = logging.getLogger(__name__)

class ResearchAgent:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            logger.warning("GOOGLE_API_KEY not found in environment variables.")
        else:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')

    def research(self, query: str) -> ResearchReport:
        logger.info(f"Starting research for: {query}")
        
        # 1. Search
        search_results = hybrid_search(query, max_results=3)
        relevant_judgments = []
        
        # 2. Fetch & Analyze
        context_text = ""
        for result in search_results:
            content = fetch_page_content(result['url'])
            if content:
                # Truncate content to avoid token limits if necessary, though 1.5 flash has large context
                snippet = content[:2000] 
                context_text += f"\nSource: {result['url']}\nTitle: {result['title']}\nContent: {snippet}\n---\n"
                
                relevant_judgments.append(SearchResult(
                    title=result['title'],
                    url=result['url'],
                    snippet=result['snippet'],
                    source=result['source']
                ))

        # 3. Summarize with LLM
        if not self.api_key:
             return ResearchReport(
                query=query,
                key_facts=["API Key missing, cannot summarize."],
                relevant_judgments=relevant_judgments,
                summary="Please provide GOOGLE_API_KEY to enable AI summarization."
            )

        prompt = f"""
        You are an expert Legal Researcher for RTI (Right to Information) in India.
        Analyze the following search results and extracted content to answer the user's query: "{query}"
        
        Focus on:
        1. Relevant RTI Act sections.
        2. Key judgments (CIC/High Court/Supreme Court) if mentioned.
        3. Whether the information is generally disclosable or exempt.
        
        Search Data:
        {context_text}
        
        Output a JSON object with the following structure (do not use markdown code blocks, just raw JSON):
        {{
            "key_facts": ["fact 1", "fact 2"],
            "summary": "Detailed summary of the findings..."
        }}
        """
        
        try:
            response = self.model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            import json
            data = json.loads(response.text)
            
            return ResearchReport(
                query=query,
                key_facts=data.get("key_facts", []),
                relevant_judgments=relevant_judgments,
                summary=data.get("summary", "")
            )
        except Exception as e:
            logger.error(f"LLM Summarization failed: {e}")
            return ResearchReport(
                query=query,
                key_facts=["Error in summarization"],
                relevant_judgments=relevant_judgments,
                summary=f"Failed to summarize findings due to error: {e}"
            )
