from tools.search import SearchTool
from tools.content import ContentTool
from dtos import SearchResult
from typing import List
import logging
from utils.tracing import trace_span

logger = logging.getLogger(__name__)

class SearcherAgent:
    def __init__(self):
        self.search_tool = SearchTool()
        self.content_tool = ContentTool()

    @trace_span("SearcherAgent", "search")
    def search(self, queries: List[str]) -> List[SearchResult]:
        logger.info(f"Searcher executing queries: {queries}")
        all_results = []
        seen_urls = set()

        for query in queries:
            # Increase max_results to 10 to get more Indian Kanoon judgments
            tool_result = self.search_tool.execute(query=query, max_results=10)
            if tool_result.error:
                logger.error(f"Search error for query '{query}': {tool_result.error}")
                continue
                
            results = tool_result.content
            for r in results:
                if r['url'] not in seen_urls:
                    all_results.append(SearchResult(
                        title=r['title'],
                        url=r['url'],
                        snippet=r['snippet'],
                        source=r['source']
                    ))
                    seen_urls.add(r['url'])
        
        return all_results

    @trace_span("SearcherAgent", "fetch_content")
    def fetch_content(self, results: List[SearchResult], priority_domains: List[str] = None) -> str:
        context_text = ""
        
        # Generic prioritization based on domains provided by Analyzer
        if priority_domains:
            prioritized = [r for r in results if any(d in r.url for d in priority_domains)]
            others = [r for r in results if not any(d in r.url for d in priority_domains)]
            # Put prioritized results at the top
            final_results = prioritized[:4] + others[:4]
        else:
            final_results = results[:8]
        
        # Fetch content for top 8 results
        for result in final_results: 
             tool_result = self.content_tool.execute(url=result.url)
             content = tool_result.content
             if content:
                snippet = content[:2000]
                context_text += f"\nSource: {result.url}\nTitle: {result.title}\nContent: {snippet}\n---\n"
        return context_text
