# RTI Agent

An AI-powered assistant for drafting Right to Information (RTI) applications in India.

## Setup

1.  **Clone the repository** and switch to the `agent-impl` branch.
2.  **Install dependencies**:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    pip install -r requirements.txt
    ```
3.  **Set up Environment Variables**:
    - Create a `.env` file in the root directory.
    - Add your Google API Key: `GOOGLE_API_KEY=your_api_key_here`
    - Alternatively, you can enter the key in the Streamlit sidebar.

## Running the Application

### Streamlit UI (Recommended for Testing)
Run the interactive UI to chat with the agent:
```bash
streamlit run ui.py
```

### FastAPI Backend
Run the API server:
```bash
uvicorn main:app --reload
```
The API will be available at `http://localhost:8000/chat`.

## Architecture
- **Agents**: `ResearchAgent` (Hybrid Search) and `DraftingAgent` (Drafting).
- **Orchestrator**: Manages the flow.
- **Tools**: DuckDuckGo Search, Google Search, Trafilatura (Content Extraction).