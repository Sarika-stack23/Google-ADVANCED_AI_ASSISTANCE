<div align="center">

  <img src="https://img.icons8.com/3d-fluency/94/calculator.png" width="80" alt="Agentic Math Solver Logo" />

  # 🧮 Agentic Math Solver

  **A multi-agent AI mathematics tutor with LangGraph orchestration, MCP tooling, and a premium React UI — built for students, powered by Gemini & Groq.**

  [![Live Demo](https://img.shields.io/badge/🌐_Live_Demo-Vercel-000?style=for-the-badge&logo=vercel)](https://advanced-math-ai.vercel.app)
  [![API Docs](https://img.shields.io/badge/📡_API-Hugging_Face-yellow?style=for-the-badge&logo=huggingface)](https://false45-math-api.hf.space/docs)
  [![License: MIT](https://img.shields.io/badge/License-MIT-A855F7?style=for-the-badge)](LICENSE)
  [![Python 3.9+](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
  [![React 19](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=white)](https://react.dev)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
  [![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](Dockerfile)
  [![Tests](https://img.shields.io/badge/Tests-19_Suites-22C55E?style=for-the-badge&logo=pytest&logoColor=white)](tests/)

</div>

<br />

<div align="center">
  <strong>
    <a href="#-features">Features</a> · 
    <a href="#-architecture">Architecture</a> · 
    <a href="#-tech-stack">Tech Stack</a> · 
    <a href="#-screenshots">Screenshots</a> · 
    <a href="#-getting-started">Getting Started</a> · 
    <a href="#-roadmap">Roadmap</a> · 
    <a href="#-contributing">Contributing</a>
  </strong>
</div>

<br />

---

## ✨ Features

| | Feature | Description |
| :---: | :--- | :--- |
| 🧠 | **Intelligent Math Chat** | Real-time AI tutor with step-by-step reasoning. Renders complex equations perfectly via LaTeX (KaTeX). Powered by a LangGraph multi-agent pipeline with plan → solve → verify → format stages. |
| 📸 | **Multimodal Input** | Upload PDFs or use your camera to scan handwritten math problems. Google Gemini Vision extracts and solves them instantly. |
| 📚 | **NCERT Quiz Engine** | Interactive MCQs for Class 9–10 students powered by **Qdrant Vector DB** and **RAG** (Retrieval-Augmented Generation). |
| 📐 | **Symbolic Math Engine** | Dedicated SymPy computation engine — differentiate, integrate, find roots, and plot 2D function graphs dynamically. |
| 📈 | **Progress Dashboard** | Tracks streaks, accuracy, and weak topics with **Firebase Auth** + a live **Recharts** line graph. |
| 🔗 | **MCP Tool Servers** | 6 sandboxed Model Context Protocol servers (SymPy, Calculator, Graph Plotter, Python Executor, Image Solver, PDF Reader) give the AI real computation power instead of hallucinating math. |
| 🎨 | **Premium UI/UX** | Dark-mode-first React SPA with glassmorphism, micro-animations, and mobile-responsive design via Vite. |

---

## 🏗 Architecture

The system uses **LangGraph** for stateful multi-agent orchestration, with **Google ADK agents** as specialized reasoning nodes and **MCP servers** as sandboxed tool backends.

```mermaid
graph TD
    %% ─── Frontend ───────────────────────────────────────────────
    Client["🖥️ React SPA<br/>(Vite + TypeScript)"]

    %% ─── API Gateway ────────────────────────────────────────────
    subgraph API["⚡ API Layer"]
        FastAPI["FastAPI Gateway"]
        Auth["Firebase Auth<br/>Middleware"]
    end

    %% ─── LangGraph Orchestrator ─────────────────────────────────
    subgraph Orchestration["🔄 LangGraph State Machine"]
        Planner["📋 Planner Node"]
        RAG["📖 RAG Node"]
        Memory["🧠 Memory Node"]
        Solver["🔧 Solver Node"]
        Verifier["✅ Verifier Node"]
        Formatter["🎨 Format Node"]
    end

    %% ─── Data Stores ────────────────────────────────────────────
    subgraph Storage["💾 Storage"]
        Firestore[("Firestore")]
        Qdrant[("Qdrant<br/>Vector DB")]
    end

    %% ─── MCP Tool Servers ───────────────────────────────────────
    subgraph MCP["🔌 MCP Tool Servers"]
        SymPy["SymPy MCP"]
        Calc["Calculator MCP"]
        GraphPlot["Graph Plotter MCP"]
        PyExec["Python Sandbox MCP"]
        ImgSolver["Image Solver MCP"]
        PDFReader["PDF Reader MCP"]
    end

    %% ─── Connections ────────────────────────────────────────────
    Client -- "SSE Stream" --> FastAPI
    FastAPI --> Auth
    FastAPI --> Planner

    Planner --> RAG
    Planner --> Memory
    RAG --> Solver
    Memory --> Solver
    Solver --> Verifier
    Verifier -- "❌ Retry" --> Solver
    Verifier -- "✅ Pass" --> Formatter
    Formatter --> Client

    Memory -.-> Firestore
    RAG -.-> Qdrant

    Solver --> SymPy
    Solver --> Calc
    Solver --> GraphPlot
    Solver --> PyExec
    Solver --> ImgSolver
    Solver --> PDFReader
```

> **How it works:** The user's question enters the LangGraph state machine. The **Planner** classifies it, the **RAG** and **Memory** nodes fetch relevant context in parallel, the **Solver** generates a solution using MCP tools for real computation, the **Verifier** checks correctness (retrying up to 3× if wrong), and the **Formatter** adds LaTeX styling before streaming back to the client.

---

## 💻 Tech Stack

### Frontend
![React](https://img.shields.io/badge/React_19-20232A?style=flat-square&logo=react&logoColor=61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=flat-square&logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-B73BFE?style=flat-square&logo=vite&logoColor=FFD62E)
![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=flat-square&logo=firebase&logoColor=white)
![Vercel](https://img.shields.io/badge/Vercel-000?style=flat-square&logo=vercel&logoColor=white)

- **KaTeX** — LaTeX math rendering
- **Recharts** — interactive data visualization
- **Lucide React** — modern icon library
- **React Markdown** — rich text formatting

### Backend
![Python](https://img.shields.io/badge/Python_3.9+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=flat-square&logo=docker&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat-square&logo=langchain&logoColor=white)

- **LangGraph** — multi-agent state machine orchestration
- **Google ADK** — agent development kit for specialized reasoning
- **Gemini 2.5 Flash** — primary LLM (multimodal)
- **Groq (Llama 3.3 70B)** — fast inference fallback
- **SymPy** — symbolic mathematics engine
- **Qdrant** — vector database for NCERT RAG
- **Firebase Admin** — Firestore + Auth

### DevOps
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white)
![Hugging Face](https://img.shields.io/badge/Hugging_Face-FFD21E?style=flat-square&logo=huggingface&logoColor=000)

- **CI/CD** — GitHub Actions with automated testing
- **Backend Hosting** — Hugging Face Spaces (Docker)
- **Frontend Hosting** — Vercel
- **Containerization** — Docker + Docker Compose

---

## 📸 Screenshots

<div align="center">

| Dark Mode | Light Mode |
| :---: | :---: |
| <img src="screenshots/dark_mode.png" width="400" alt="Dark Mode UI" /> | <img src="screenshots/light_mode.png" width="400" alt="Light Mode UI" /> |

</div>

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.9+** and pip
- **Node.js 18+** and npm
- **Docker** (optional)

### Option 1 — Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/Sarika-stack23/agentic-math-solver.git
cd agentic-math-solver

# Configure environment
cp .env.example .env
# Edit .env with your API keys (GEMINI_API_KEY, GROQ_API_KEY, etc.)

# Start all services
docker compose up --build
```

| Service | URL |
| :--- | :--- |
| Backend API | `http://localhost:8080` |
| API Docs (Swagger) | `http://localhost:8080/docs` |
| Frontend | `http://localhost:5173` |

### Option 2 — Local Development

#### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

pip install -r requirements.txt

# Configure environment
cp ../.env.example ../.env
# Edit .env with your API keys

uvicorn src.main:app --reload --port 8080
```

#### Frontend

```bash
cd frontend
npm install

# Create frontend .env
echo "VITE_API_URL=http://localhost:8080" > .env

npm run dev
```

### Environment Variables

| Variable | Required | Description |
| :--- | :---: | :--- |
| `GEMINI_API_KEY` | ✅ | [Google AI Studio](https://aistudio.google.com/apikey) — free tier available |
| `GROQ_API_KEY` | ✅ | [Groq Console](https://console.groq.com/keys) — free tier available |
| `USE_GEMINI` | — | Set to `true` to use Gemini as primary model (default: `true`) |
| `USE_FIREBASE` | — | Set to `true` to enable Firebase Auth + Firestore |
| `FIREBASE_CREDENTIALS_PATH` | — | Path to Firebase Admin SDK JSON file |

---

## 📁 Directory Structure

```text
agentic-math-solver/
├── backend/
│   ├── src/
│   │   ├── agents/           # ADK agent definitions (Planner, Solver, Verifier, etc.)
│   │   ├── api/              # FastAPI routes (chat, progress, quiz, vision)
│   │   ├── graph/            # LangGraph state machine orchestration
│   │   ├── math/             # Symbolic math engine (SymPy)
│   │   ├── services/         # Qdrant, Firebase, and external service connectors
│   │   ├── config.py         # Centralized configuration
│   │   └── main.py           # FastAPI application entrypoint
│   ├── knowledge-base/       # NCERT markdown files for RAG retrieval
│   ├── Dockerfile            # Backend container image
│   └── requirements.txt      # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── components/       # React components (Chat, Quiz, Graphing, Dashboard)
│   │   ├── context/          # Firebase Auth state management
│   │   ├── App.tsx           # Main application shell
│   │   └── index.css         # Glassmorphism UI styles
│   ├── vercel.json           # Vercel SPA routing config
│   └── package.json          # Node dependencies
│
├── mcp-servers/              # Model Context Protocol tool servers
│   ├── calculator-mcp/       # Basic arithmetic operations
│   ├── graph-plotter-mcp/    # 2D function graph generation
│   ├── image-solver-mcp/     # Gemini Vision image processing
│   ├── pdf-reader-mcp/       # PDF text extraction
│   ├── python-executor-mcp/  # Sandboxed Python code execution
│   └── sympy-mcp/            # Symbolic math computation
│
├── tests/                    # 19 test suites (pytest)
├── docs/                     # Architecture documentation
├── screenshots/              # UI screenshots (dark & light mode)
├── .github/workflows/        # CI/CD pipeline
├── docker-compose.yml        # Multi-service orchestration
├── render.yaml               # Render.com deployment config
├── .env.example              # Environment variable template
├── CONTRIBUTING.md            # Contribution guidelines
├── CHANGELOG.md              # Version history
└── LICENSE                   # MIT License
```

---

## 🗺 Roadmap

- [x] Multi-agent LangGraph orchestration pipeline
- [x] MCP tool server integration (6 servers)
- [x] Multimodal input (camera + PDF)
- [x] NCERT RAG quiz engine with Qdrant
- [x] Firebase Auth + progress tracking dashboard
- [x] Premium dark-mode-first UI with glassmorphism
- [x] Docker containerization + CI/CD pipeline
- [x] Deployed to Vercel (frontend) + Hugging Face (backend)
- [ ] Voice input for math questions (Web Speech API)
- [ ] Multi-language support (Hindi, Spanish, French)
- [ ] Collaborative study rooms (WebSocket)
- [ ] Export solutions to PDF
- [ ] Spaced repetition algorithm for quiz scheduling
- [ ] Parent/teacher dashboard with student analytics

---

## 🤝 Contributing

Contributions are welcome! Please read the [Contributing Guide](CONTRIBUTING.md) for details on:

- Setting up your development environment
- Code style guidelines
- Pull request process
- Bug reports and feature requests

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

  **[⬆ Back to Top](#-agentic-math-solver)**

  <br />

  Built with ❤️ for students learning mathematics.

  <br />

  <a href="https://advanced-math-ai.vercel.app">
    <img src="https://img.shields.io/badge/Try_the_Live_Demo-000?style=for-the-badge&logo=vercel&logoColor=white" alt="Try Live Demo" />
  </a>

</div>