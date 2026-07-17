# Changelog

All notable changes to the **Advanced Mathematics Assistant** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

### Phase 11 — Testing, Documentation & Polish

#### ✨ New Features

- **Documentation**: Rewrote `README.md` for the hackathon showcase and added a comprehensive `docs/ARCHITECTURE.md` file featuring a Mermaid state machine diagram.
- **E2E Testing**: Integrated Playwright into the frontend and added a baseline `login.spec.ts` UI test.
- **Integration Tests**: Added `tests/test_integration.py` to ensure core API contracts perform as expected with mocked dependencies.
- **CI/CD Security**: Added `pip-audit` to the `.github/workflows/ci.yml` pipeline to scan for dependency vulnerabilities on every push.
- **Demo Script**: Created a 3-minute hackathon demo storyboard to highlight the agentic features.

#### ✨ New Features

- **Modern Architecture**: Fully replaced legacy Streamlit frontend with a high-performance **React 19 + TypeScript + Vite** application.
- **Premium UI/UX**: Implemented a bespoke design system featuring glassmorphism, responsive grid layouts, and automatic dark/light mode switching based on `prefers-color-scheme`.
- **Live Streaming & LaTeX**: Integrated an SSE fetch consumer for the `/api/v1/chat/stream` endpoint with real-time `react-latex-next` (KaTeX) rendering of mathematical symbols.
- **NCERT Quiz Workflow**: Recreated the interactive problem-solving experience with "Give Hint", "Show Steps", "Show Answer", and an intuitive "Stuck? Ask AI" contextual menu.
- **Progress Tracking**: Built a new `ProgressDashboard` component displaying the user's current streak, accuracy metrics, and an activity heatmap.
- **Firebase Deployment**: Reconfigured `firebase.json` to deploy the new React Single Page Application (SPA).

#### ✨ New Features

- **MCP Integration**: Created 6 new MCP server tools (`sympy-mcp`, `calculator-mcp`, `graph-plotter-mcp`, `pdf-reader-mcp`, `python-executor-mcp`, `image-solver-mcp`) mapped via a local registry to `mcp-servers/`.
- **Python Sandbox**: Integrated `RestrictedPython` in `python-executor-mcp` to securely execute inline python code for complex math tasks, while successfully blocking imports like `os` and `subprocess`.
- **AgentExecutor Update**: Refactored `SolverAgent` (Google ADK) to dynamically use `create_tool_calling_agent` and `AgentExecutor` from LangChain when `USE_MCP=true` is set.
- **Tools Verification**: Added `test_mcp_servers.py` to end-to-end test the contract and logic of the 6 tools locally.

#### ✨ New Features

- **Dockerization**: Created a production-ready `Dockerfile` to containerize the FastAPI backend for Cloud Run.
- **CI/CD Pipelines**: Added GitHub Actions workflows:
  - `ci.yml`: Runs tests automatically on pull requests to `main`.
  - `deploy.yml`: Authenticates with Google Cloud, builds the Docker image, and deploys to Cloud Run on pushes to `main`.
- **Firebase Hosting**: Scaffolded `firebase.json` and a placeholder `index.html` to serve static frontend assets.
- **DDoS Protection**: Integrated `slowapi` to enforce a strict 20 requests/minute rate limit on all chat/vision API endpoints to protect the free tier from abuse.
- **Secret Management**: Removed reliance on local `.env` files for deployment by utilizing Google Cloud Secret Manager and GitHub Actions secrets.

#### ✨ New Features

- **Firestore Prompt Versioning**: Created `PromptService` to dynamically load the system prompt template from Firestore (`prompts` collection).
- **A/B Testing & Active Versioning**: `PromptService` supports passing an `ab_test_group` string to pull variations, and an `active_version` pointer inside the Firestore document to smoothly update prompts without code deployment.
- **Local Fallback**: Designed to fail open — if Firestore is unreachable, the API instantly falls back to a hardcoded local template to ensure zero downtime.
- **Safety Filters**: Updated `GeminiService` to use the newer `google.genai` SDK and activated `SafetySetting` filters against Harassment, Hate Speech, Dangerous Content, and Sexually Explicit queries using the Gemini standard built-in thresholds.
- **Offline LLM-as-Judge Evaluation**: Created `EvaluationService` using `gemini-2.5-flash` to evaluate RAG answer quality on a scale of 1-5 with deterministic reasoning output.
- **Cloud Logging**: Appended `google-cloud-logging` to dependencies and integrated structured cloud logging inside `config.py` when a GCP environment or Application Default Credentials (ADC) are detected, while gracefully falling back to standard stdout logging locally.

#### ✨ New Features

- **Qdrant Vector Database**: Replaced ChromaDB and FAISS with Qdrant Cloud. Qdrant is natively supported in `:memory:` mode for testing and local usage without an API key.
- **Hybrid Search**: Configured `QdrantVectorStore` with `RetrievalMode.HYBRID`, fusing dense vectors (`text-embedding-004` via Gemini API) and sparse vectors (`fastembed` BM25).
- **Markdown Knowledge Base**: Migrated the monolithic 6000-line `knowledge_base.py` into 201 individual structured Markdown files in the `knowledge-base/` directory, allowing cleaner git tracking and easier manual updates.
- **Dynamic Metadata Filtering**: Configured Qdrant's payload filters so RAG can accurately filter documents by `class_level`, `chapter`, and `topic`.

#### 🧪 Testing
- Passed all existing RAG and Chunking tests.
- Added `test_qdrant.py` mocking the new `QdrantService` initialization and sparse/dense retrieval paths.
- Total tests passed: 62.

#### ✨ New Features

- **LangGraph StateGraph Integration**: Added `langgraph` and `langsmith` to wrap the Phase 4 ADK agents into a formal state machine (`math_graph.py`).
- **Parallel Retrieval**: The `retrieve_rag` and `retrieve_memory` nodes now run concurrently, optimizing retrieval latency.
- **Verification Retry Loop**: The `should_retry` conditional edge enforces a self-correction loop, prompting the solver to fix its mistakes up to 2 times if the verifier detects an error.
- **Observable Tracing**: LangSmith is fully supported. When `LANGCHAIN_API_KEY` is provided, every state mutation and token generation is logged to the dashboard.
- **Configurable Pipeline**: The API path is controlled by `USE_LANGGRAPH=True`, allowing graceful fallback to the ADK orchestrator or the original single-agent pipeline.

#### 🧪 Testing
- Added `tests/test_langgraph.py` to verify proper conditional edge routing (e.g. testing that failures loop back to the solver).
- Total tests passed: 59.

#### ✨ New Features

- **Multi-Agent Architecture**: Replaced the monolithic `MathAIEngine` with a 5-agent pipeline orchestrated by Google ADK (`google-adk==0.1.0`).
- **Planner Agent**: Classifies incoming queries by math topic and educational class level for targeted responses.
- **Memory Agent**: Interfaces directly with Firestore to fetch chat history and analyzes weak topics from the user's profile to adapt explanations.
- **Solver Agent**: Executes RAG retrieval and symbolic computation (SymPy) to construct the core mathematical solution.
- **Verifier Agent**: Automatically audits the Solver's output for mathematical or logical errors (e.g., catching `4+4=9`), triggering an internal retry if verification fails.
- **Formatter Agent**: Applies strict output templates, formatting solutions with teacher reactions, emojis, and LaTeX math mode.
- **Human Feedback Loop**: Added `save_user_feedback` API to Firestore for reinforcement learning data collection.

#### 🧪 Testing
- Added `tests/test_adk_agents.py` with mock ADK environments to unit-test Planner classification, Verifier error detection, and Memory topic retrieval.
- Total test count increased to 57 passing tests.

### Phase 3 — Firebase Integration

#### ✨ New Features

- **Firebase Authentication**: Protected all endpoints with `firebase_admin` ID token verification middleware. Added support for Google Sign-In backend verification.
- **Firestore Persistence**: Completely removed MongoDB (`pymongo`, `motor`) and migrated chat memory persistent storage to Google Cloud Firestore.
- **User Isolation**: Chat history is now tightly scoped to authenticated user IDs to prevent data leakage across sessions.
- **Progress Tracking API**: Added `/api/v1/progress` endpoints to track and persist daily streaks and total problems solved per user.
- **Security Rules**: Deployed `firestore.rules` to ensure strict row-level security for user data.

#### 🧪 Testing
- Added `tests/test_firebase.py` to verify authentication middleware logic and mock Firestore queries.
- Total test count increased to 54 passing tests.

### Phase 2 — Gemini Integration

#### ✨ New Features

- **Gemini Primary Engine**: Migrated from Groq (LLaMA) to Google Gemini (`gemini-2.0-flash`). Groq remains as an optional fallback when `USE_GEMINI=false`.
- **SSE Streaming Support**: Added `POST /api/v1/chat/stream` for real-time token-by-token response delivery using FastAPI `StreamingResponse`.
- **Gemini Vision OCR**: Added `POST /api/v1/vision/extract` endpoint using Gemini Vision to extract mathematical content and solve problems directly from images, replacing Tesseract OCR.
- **LaTeX Math Support**: Updated system prompt template to use proper LaTeX math mode (`$...$` and `$$...$$`) for all mathematical expressions instead of restricted unicode symbols.
- Added `.env.example` file for new setup credentials.

#### 🧪 Testing
- Added `tests/test_gemini.py` to verify text querying, fallback mechanisms, and vision extraction.
- Total test count increased to 50 passing tests.

### Phase 1 — Architecture Refactoring

#### 🏗️ Backend Decomposition

Decomposed the 2,800-line monolithic `main.py` into single-responsibility modules:

- **`backend/src/config.py`** — Centralized Pydantic Settings + system prompt template
- **`backend/src/math/symbolic_engine.py`** — SymPy symbolic math (differentiate, integrate, solve, simplify, matrix ops)
- **`backend/src/math/knowledge_indexer.py`** — MathDataLoader + MathDataPreprocessor + MathTextSplitter
- **`backend/src/math/graph_utils.py`** — Safe expression evaluator (Phase 0 fix) + OCR helper
- **`backend/src/services/memory_service.py`** — MongoDB chat memory with in-memory fallback
- **`backend/src/services/vector_service.py`** — ChromaDB/FAISS vector store + build pipeline
- **`backend/src/services/llm_service.py`** — Groq LLM factory + MathAIEngine orchestrator

#### 🌐 FastAPI Backend

- **`backend/src/main.py`** — FastAPI application with CORS, lifespan events
- **`backend/src/api/v1/chat.py`** — REST endpoints:
  - `POST /api/v1/chat` — Process math queries through full RAG pipeline
  - `GET /api/v1/history/{session_id}` — Retrieve chat history
  - `DELETE /api/v1/history/{session_id}` — Clear session history
  - `GET /health` — Health check with KB document count
- Pydantic request/response models for type-safe API contracts

#### 🐳 Docker

- **`backend/Dockerfile`** — Python 3.11-slim, non-root user, port 8080
- **`docker-compose.yml`** — Multi-service: FastAPI backend + Streamlit frontend with health checks
- **`backend/requirements.txt`** — Dedicated backend dependency manifest

#### 🧪 New Tests

- **`tests/test_api.py`** — 6 tests for FastAPI endpoints (health, root, chat validation)

---



### Phase 0 — Repository Audit & Security Fix

#### 🔒 Security

- **CRITICAL FIX**: Removed dangerous `eval()` call in graph plotter (`main.py:L876`)
  - **Vulnerability**: `eval(re.sub(r'\^', '**', expr), ns)` with an incomplete namespace allowed arbitrary Python code execution through the graph plotter input field. An attacker could escape the `__builtins__: {}` sandbox via reference chain attacks.
  - **OWASP Classification**: A03:2021 — Injection
  - **Fix**: Replaced with `_safe_evaluate_expression()` using `sympy.sympify()` + `sympy.lambdify()`. SymPy's parser only understands mathematical syntax and cannot execute arbitrary Python code.
  - **Additional Defense**: Added blocklist pattern matching for `__import__`, `exec`, `eval`, `compile`, `open`, `getattr`, `setattr`, `subprocess`, `os.`, `sys.`, and other dangerous constructs.
  - **Status**: ✅ CLOSED — Verified by 12 attack-pattern tests and 17 safe-expression tests

#### 🧪 Testing

- Extracted 5 existing unittest classes from `main.py` (L2589-L2670) into standalone test files:
  - `tests/test_data_sources.py` — `TestDataSources` (knowledge base loading)
  - `tests/test_preprocessing.py` — `TestPreprocessing` (text cleaning, dedup, topic detection)
  - `tests/test_chunking.py` — `TestChunking` (text splitting, metadata preservation)
  - `tests/test_symbolic_engine.py` — `TestSymbolicEngine` (differentiation, integration, solving)
  - `tests/test_memory.py` — `TestMemory` (chat history add/retrieve)
- Created new `tests/test_graph_security.py` with 29 test cases for the eval() fix:
  - 17 tests verifying safe mathematical expressions (sin, cos, tan, log, sqrt, exp, abs, arcsin, sinh, cosh, tanh, pi, e, polynomials, caret notation, constants, composites)
  - 12 tests verifying malicious inputs are blocked (os, sys, subprocess, open, exec, eval, compile, getattr, globals, pathlib, __builtins__, __import__)
- Added `pytest>=7.0.0` and `pytest-cov>=4.0.0` to `requirements.txt`

#### 📁 Project Housekeeping

- Updated `.gitignore` with: `.pytest_cache/`, `htmlcov/`, `.coverage`, `*.egg-info/`, `dist/`, `build/`
- Created this `CHANGELOG.md` to document the transformation journey

---

## [Pre-Transformation] — June 2026

### Original Project State

- **Architecture**: Single-file monolith (`main.py` — 2,745 lines)
- **LLM**: LLaMA 3.3 70B via Groq API
- **Vector Store**: ChromaDB (primary) / FAISS (fallback) — local, ephemeral
- **Embeddings**: HuggingFace sentence-transformers/all-MiniLM-L6-v2
- **Chat Memory**: MongoDB Atlas
- **UI**: Streamlit
- **Authentication**: None
- **CI/CD**: None
- **Docker**: None
- **Google AI**: None
- **Hackathon Score**: 3/10

### Known Issues at Transformation Start

- [x] `eval()` security vulnerability in graph plotter (L876) — **FIXED in Phase 0**
- [ ] God Object anti-pattern (all logic in one file)
- [ ] No user authentication
- [ ] No Google AI ecosystem integration (Gemini, Firebase, Cloud Run, ADK)
- [ ] No agent architecture (single-shot RAG, not multi-agent)
- [ ] Local vector store (not cloud-persistent)
- [ ] No CI/CD pipeline
- [ ] No Docker containerization
