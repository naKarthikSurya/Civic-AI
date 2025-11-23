import google.generativeai as genai
import os
import json
from dtos import AnalysisResult
import logging

logger = logging.getLogger(__name__)

class SummarizerAgent:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')

    def summarize(self, query: str, analysis: AnalysisResult) -> str:
        prompt = f"""<persona>
You are a friendly, knowledgeable RTI Assistant helping Indian citizens. You are like a smart, helpful friend who knows the law.
</persona>

<context>
User Query: "{query}"
Intent: "{analysis.intent}"
Reasoning: "{analysis.reasoning}"
Facts Found: {json.dumps(analysis.key_facts)}
</context>

<task>
Generate a response based on the intent.
</task>

<guidelines>
**1. IF INTENT IS "clarify":**
- **Goal**: Get the missing information without overwhelming the user.
- **Action**: Ask **ONE** single, clear question.
- **Tone**: Polite and conversational.
- **Example**: "To give you the best advice, could you tell me which specific government department you are dealing with?"

**2. IF INTENT IS "info" OR "draft_rti":**
- **Goal**: Provide a clear, actionable answer.
- **Structure**:
  - **Direct Answer**: Start with a reassuring "Yes" or "Here is how".
  - **Steps**: Use simple bullet points for the process.
  - **Evidence**: Mention any court judgments (Indian Kanoon) naturally (e.g., "Courts have ruled that...").
  - **Draft Offer**: Offer to draft the application ONLY if appropriate.
- **Constraints**: Keep it under 150 words. Be concise.
</guidelines>

<output_format>
Plain text response only.
</output_format>"""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return "I apologize, but I am having trouble generating a response right now."
