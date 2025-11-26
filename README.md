# CivicAI ⚖️
**AI-Powered Legal Advisory for Indian Citizens**

CivicAI (formerly RTI Agent) is an intelligent legal assistant designed to empower Indian citizens by simplifying the Right to Information (RTI) Act and providing accessible legal guidance. It uses advanced AI to analyze user queries, search for relevant laws and judgments, and provide actionable solutions.

## 🚀 Features

*   **Legal Advisory**: Understands natural language queries about legal issues (e.g., "Police refused to file FIR", "RTI for road repair").
*   **Intelligent Analysis**: Identifies the core intent (Legal Advice, Information, or Clarification).
*   **Case Law Search**: Actively searches **Indian Kanoon** and other legal databases for relevant judgments and precedents.
*   **Actionable Solutions**: Provides step-by-step guidance, including which RTI sections to use and how to file appeals.
*   **Chat History**: Keeps track of your recent consultations for easy reference (stored locally).

## 🛠️ Tech Stack

*   **Backend**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
*   **AI Model**: [Google Gemini 2.0 Flash](https://ai.google.dev/) (via `google-generativeai`)
*   **Search**: [DuckDuckGo](https://pypi.org/project/duckduckgo-search/) (for legal research)
*   **Content Extraction**: [Trafilatura](https://trafilatura.readthedocs.io/) (for reading judgments)
*   **Frontend**: HTML5, TailwindCSS, Vanilla JS
*   **Observability**: Custom tracing for agent workflows.

## 📂 Project Structure

```
CivicAI/
├── agents/             # AI Agents (Analyzer, Searcher, Summarizer)
├── tools/              # Tools (Search, Content Fetcher)
├── templates/          # HTML Templates (Jinja2)
├── static/             # CSS/JS Assets
├── utils/              # Utilities (Session, Tracing)
├── main.py             # FastAPI Application Entrypoint
├── orchestrator.py     # Agent Orchestrator (Router Pattern)
└── dtos.py             # Data Transfer Objects
```

## ⚡ Setup & Usage

### Prerequisites
*   Python 3.10+
*   Google AI Studio API Key

### Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/CivicAI.git
    cd CivicAI
    ```

2.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Environment Variables**:
    Create a `.env` file in the root directory:
    ```env
    GOOGLE_API_KEY=your_gemini_api_key_here
    ```

### Running the Application

Start the server using Uvicorn:
```bash
uvicorn main:app --reload
```

Open your browser and navigate to:
**http://127.0.0.1:8000**

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

This project is open-source and available under the MIT License.

---
*Empowering Citizens with Information.*