from ddgs import DDGS
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

print("Testing DuckDuckGo Search...")
try:
    results = DDGS().text("site:indiankanoon.org RTI internal marks engineering college", max_results=3)
    print(f"Results found: {len(results)}")
    for r in results:
        print(r)
except Exception as e:
    print(f"Error: {e}")
