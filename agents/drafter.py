import google.generativeai as genai
import os
from dtos import AnalysisResult
import logging
import json

logger = logging.getLogger(__name__)

class DraftingAgent:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')

    def draft(self, query: str, analysis: AnalysisResult) -> str:
        if not self.api_key:
            return "API Key missing."

        prompt = f"""<role>
You are an expert RTI (Right to Information Act 2005) application drafter.
</role>

<user_request>
{query}
</user_request>

<facts>
{json.dumps(analysis.key_facts, indent=2)}
</facts>

<task>
Draft a formal RTI application based on the user's request and the context facts provided.
</task>

<rules>
1. Use ONLY the facts explicitly provided above
2. Do NOT invent or assume any information
3. Use placeholders for missing information:
   - [Your Full Name]
   - [Your Address]
   - [Date]
   - [Public Authority Name]
   - etc.

4. Follow RTI Act 2005 format:
   - Address to: Public Information Officer
   - Clear subject line
   - Specific information requested
   - Reference to RTI Act 2005, Section 6(1)
   - Applicant details section with placeholders
   - Fee mention (if applicable)

5. Be specific about the information sought
6. Keep language formal but clear
7. Ensure legal compliance
</rules>

<output_format>
Output ONLY the RTI application text. No explanations, no comments, just the draft.
</output_format>"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Drafting failed: {e}")
            return "Failed to generate draft."
