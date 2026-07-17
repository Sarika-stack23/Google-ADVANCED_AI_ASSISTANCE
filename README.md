# Advanced Mathematics AI Agent Platform

![Hackathon Showcase](https://img.shields.io/badge/Status-Production--Ready-success?style=for-the-badge)
# Google Advanced AI Assistance

An intelligent, multi-agent AI mathematics tutor built for Indian school students. Designed with Google's ADK (Agent Development Kit), LangGraph, and Gemini, this platform provides interactive, deterministic, and safe educational support.

## 🚀 Live Demo (Hackathon Submission)

- **Frontend (Web App)**: [https://google-advanced-ai.web.app](https://google-advanced-ai.web.app) (Firebase Hosting)
- **Backend (API Base)**: [https://api.google-advanced-ai.run.app](https://api.google-advanced-ai.run.app) (Google Cloud Run)
- **Demo Video**: [Watch the 3-minute pitch](https://youtube.com/mock-link-for-hackathon)

## ✨ Key Features

1. **Multi-Agent Orchestration**: We broke down the monolithic "AI tutor" into 5 distinct agents using the **Google Agent Development Kit (ADK)**:
   - **Planner Agent**: Classifies queries and routes them logically.
   - **Memory Agent**: Recalls the student's weak topics to personalize teaching.
   - **Solver Agent**: The core math reasoning engine.
   - **Verifier Agent**: Automatically catches and prevents AI hallucinations by self-correcting the Solver up to 3 times.
   - **Formatter Agent**: Styles the final output pedagogically.

2. **Model Context Protocol (MCP)**:
   The LLM doesn't blindly guess complex calculus. Instead, it securely interfaces with 6 isolated MCP sandboxed environments:
   - **SymPy Engine**: For deterministic calculus and algebra.
   - **Python Sandbox**: Inline execution via `RestrictedPython` for arbitrary algorithms.
   - **Gemini Vision**: Solves handwritten equations uploaded as images.
   - **Matplotlib Renderer**: Generates SVG graphs dynamically.
   - **PDF Reader**: Parses study materials and exam papers.

3. **LangGraph State Machine**: 
   The backend uses LangGraph to manage cyclical graphs and retry logic, ensuring robust mathematical proofs.

4. **Premium React Frontend**:
   A blazing fast Vite + React SPA featuring SSE (Server-Sent Events) for token-by-token streaming, complete with rigorous KaTeX LaTeX rendering and a dark/light mode glassmorphic UI.

5. **Progress & Safety**:
   - **Qdrant Vector DB** for real-time RAG context retrieval.
   - **Firestore** for chat history and topic mastery heatmap tracking.
   - **Safety First**: Integrated strict Gemini safety settings and explicit prompt injection guards.

## 🚀 Live Demo
*Link to be added during final submission.*

## 🏗 Architecture
Please see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed Mermaid diagrams of the LangGraph state machine and the ADK Agent interactions.

## 💻 Tech Stack
- **Frontend**: React 19, Vite, TypeScript, KaTeX, Lucide-React
- **Backend**: FastAPI, Python 3.11+, LangGraph, Google ADK
- **AI Models**: Gemini 2.5 Flash, Gemini Vision
- **Database**: Firebase Firestore, Qdrant
- **Deployment**: Google Cloud Run, Firebase Hosting

## 🛠 Running Locally

1. Clone the repository and install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure `.env`:
   ```bash
   GEMINI_API_KEY=your_key
   USE_MCP=true
   ```
3. Start the FastAPI backend:
   ```bash
   uvicorn backend.src.main:app --reload --port 8080
   ```
4. Start the React Frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

---
*Built with ❤️ for students learning mathematics.*