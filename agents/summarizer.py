import google.generativeai as genai
import os
import json
from dtos import AnalysisResult
import logging
from utils.tracing import trace_span

logger = logging.getLogger(__name__)

class SummarizerAgent:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')

    @trace_span("SummarizerAgent", "summarize")
    def summarize(self, query: str, analysis: AnalysisResult, history: list[dict] = []) -> str:
        history_text = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in history[-5:]])
        
        prompt = f"""<persona>
You are a friendly, knowledgeable RTI Assistant helping Indian citizens. You are like a smart, helpful friend who knows the law.
</persona>

<chat_history>
{history_text}
</chat_history>

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
- **Goal**: Gather missing details to provide better legal advice.
- **Action**: Ask specific questions about the incident/problem.
- **Example**: "To find the right judgment, could you tell me if you have already filed a First Appeal?"

**2. IF INTENT IS "legal_advice":**
- **Goal**: Provide a Legal Opinion based on Laws and Judgments.
- **Structure**:
  - **Legal Analysis**: Explain the relevant section of the RTI Act (e.g., Section 8(1)(j), Section 4).
  - **Relevant Judgments**: Cite specific case laws found in the context (e.g., *Girish Ramchandra Deshpande vs. CIC*). Explain *why* it applies.
  - **Suggested Solution**: Step-by-step legal remedy (e.g., "File a First Appeal under Section 19(1)...").

**3. IF INTENT IS "info":**
- **Goal**: Provide clear, factual information.
</guidelines>
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
