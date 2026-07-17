# PROJECT ENHANCEMENT ROADMAP
## Advanced Mathematics Assistant - Production-Ready AI Agent Platform
### Google Build with AI x AI House Hackathon

---

> **Document Version:** 1.0.0
> **Analysis Date:** July 2026
> **Status:** AWAITING APPROVAL BEFORE PHASE 0 BEGINS

---

## Workflow Rules

- CURRENT STATE: Analysis Complete, Roadmap Delivered
- NEXT STEP: Await explicit approval before any code changes
- EXECUTION ORDER: Phase 0 -> Approval -> Phase 1 -> Approval -> ...
- RULE: Never work on multiple phases simultaneously

---
# 1. Executive Summary

## Current Project Overview

The **Advanced Mathematics Assistant** is a Streamlit-based educational tool built by Sarika (GitHub: Sarika-stack23) designed to help Indian school students (Class 6-12 + JEE) solve NCERT mathematics problems.

At its core, the application is a **RAG-powered chatbot** built on LLaMA 3.3 70B via Groq API, ChromaDB/FAISS (vector store), HuggingFace sentence-transformers (embeddings), LangChain (orchestration), SymPy (symbolic math), Streamlit (UI), and MongoDB Atlas (chat memory).

The knowledge base (knowledge_base.py) contains **505 hand-curated NCERT exercise questions** plus comprehensive topic documents for Class 6-12 and JEE Advanced totaling **6,121 lines** of structured, metadata-tagged Document objects.

## Existing Strengths

| Strength | Detail |
|---|---|
| Rich Domain Knowledge | 6,121-line hand-curated knowledge base with 505 NCERT exercises |
| Pedagogically Thoughtful | Whiteboard-style format, hint/steps/answer mode |
| Multi-modal Input | Camera scan (Tesseract OCR), PDF upload, text input |
| Good UI Polish | Dark/light mode, Google Fonts, Plotly graphs |
| Symbolic Computation | SymPy: differentiation, integration, equation solving |
| Auto Model Fallback | Switches between 3 Groq models on rate limit |
| Unit Tests | TestDataSources, TestPreprocessing, TestChunking, TestSymbolicEngine, TestMemory |
| DevContainer | GitHub Codespaces-ready devcontainer.json |
| Smart PDF Classifier | Rejects non-math PDFs |
| Session Streaks | Daily practice streak counter |

## Existing Weaknesses

| Weakness | Impact |
|---|---|
| God Object Anti-pattern | All 2,745 lines crammed into one main.py |
| No Authentication | Zero user identity, no persistent profiles |
| No Google AI | No Gemini, Vertex AI, Firebase, Cloud Run |
| Not Agent Architecture | Simple RAG chatbot, no planning or verification |
| Groq Dependency | Single third-party API, 100K tokens/day |
| Local Vector Store | ChromaDB on disk, ephemeral on Streamlit Cloud |
| No LangGraph | Single-shot LLM calls, no reasoning loops |
| No MCP | No structured tool exposure |
| No Qdrant | No hybrid search, no advanced filtering |
| No CI/CD | No GitHub Actions, no automated testing |
| No Observability | No cloud logging, no metrics, no tracing |
| CRITICAL: eval() in Graph Plotter | Direct eval() on user input (Line 876) - SECURITY VULNERABILITY |
| No Docker | Cannot containerize, no Cloud Run deployment |
| LaTeX Not Rendered | System prompt bans LaTeX, math shown as plain Unicode |
| No Streaming | LLM response appears all at once - poor UX |

**Current Hackathon Score: 3/10** - Architecturally unsuitable for an agentic AI hackathon.
**Target Score After Transformation: 9/10** - Rich domain, compelling UX, genuine student impact.

---
# 2. Repository Analysis

## Current Architecture (Single-File Monolith)

```
Browser --> Streamlit (main.py L924) --> Session State
                    |
                    v
         MathAIEngine (L666)
          |         |          |
          v         v          v
    LangChain   SymPy     MongoDBChatMemory (L525)
    + Groq      Engine
       |
       v
  MathVectorStore (L287): ChromaDB / FAISS
       |
       v
  knowledge_base.py (6,121 lines, hardcoded Document objects)
```
## Tech Stack (As-Is)

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| UI | Streamlit >=1.32.0 |
| LLM | LLaMA 3.3 70B via Groq API |
| LLM Fallback | llama3-8b-8192, mixtral-8x7b-32768 |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 (pinned ==2.7.0) |
| Vector DB | ChromaDB (primary), FAISS (fallback) |
| Orchestration | LangChain 0.2.x (pinned) |
| Symbolic Math | SymPy >=1.12 |
| Graphing | Plotly >=5.0.0 |
| Chat Memory | MongoDB Atlas via pymongo >=4.0.0 |
| OCR | Tesseract + pytesseract >=0.3.10 |
| Deployment | Streamlit Cloud (ephemeral filesystem!) |
| Auth | NONE |
| CI/CD | NONE |

## Folder Structure (Current: 10 Files Total)

```
Advanced Mathematics Assistant/
+-- main.py                 (2,745 lines: God Object with ALL logic)
+-- knowledge_base.py       (6,121 lines: hardcoded Document objects)
+-- requirements.txt        (44 dependency lines)
+-- packages.txt            (tesseract-ocr system package)
+-- runtime.txt             (python-3.11)
+-- env.example             (GROQ_API_KEY, MONGODB_URI, etc.)
+-- .gitignore
+-- README.md               (309 lines)
+-- .devcontainer/devcontainer.json
+-- screenshots/dark_mode.png, light_mode.png
```
## Backend: 7 Steps All in main.py

1. **MathDataLoader (L80)**: Loads NCERT knowledge base + optional PDFs/web pages
2. **MathDataPreprocessor (L156)**: Cleans text, deduplicates by MD5 hash, detects topic/difficulty
3. **MathTextSplitter (L232)**: Recursive character splitting, chunk_size=1000, overlap=200
4. **MathVectorStore (L287)**: ChromaDB or FAISS with process-level _PIPELINE_CACHE
5. **MathAIEngine (L666)**: query() -> context retrieval -> SymPy pre-check -> Groq with fallback
6. **run_streamlit_app (L924)**: 1,800+ lines: NCERT quiz, graph plotter, PDF upload, OCR, chat UI
7. **Unit Tests (L2589)**: 5 unittest classes: TestDataSources, TestPreprocessing, TestChunking, TestSymbolicEngine, TestMemory

## AI Workflow (Single-Shot, No Agent Loop)

```
User Input
  -> SymbolicMathEngine._symbolic_hint()   [regex: diff/int/solve patterns]
  -> MathVectorStore.similarity_search()   [ChromaDB cosine, k=3]
  -> MongoDBChatMemory.get_langchain_messages() [last 4 turns]
  -> Build messages: [SystemMessage+context] + [history] + [HumanMessage]
  -> Groq LLM (llama-3.3-70b-versatile)
     -> Retry 2x per model
     -> Fallback: llama3-8b-8192 -> mixtral-8x7b-32768
  -> Return {answer, sources, symbolic_hint, session_id}
```
## Critical Technical Details

**Prompt Injection Fix**: System prompt uses `str.replace("{context}", context)` NOT `format_messages()`. This prevents KeyError when math notation like {x|x>0} appears in retrieved context. Must be preserved carefully during refactoring.

**ChromaDB Persistence Issue**: Streamlit Cloud filesystem is ephemeral. ChromaDB SQLite files are lost on every redeploy. Vector store rebuilt from knowledge_base.py on every cold start (30-60 second delay). Fundamental architectural limitation.

**eval() Security Vulnerability (L876)**: `y = eval(re.sub(r'^',...), ns)`. The namespace is incomplete -- attacker can escape via __builtins__ reference chains. MUST be fixed in Phase 0.

**Git History**: 20+ commits, single contributor (Sarika Jivrajika), rapid development March-June 2026. Peak: April 2026 -- v3.13 added 1,545 lines to knowledge_base.py in a single commit.

---

# 3. Feature Gap Analysis

## Production Readiness Gaps

| Gap | Current | Required |
|---|---|---|
| User Authentication | None | Firebase Auth (Google Sign-In) |
| User Profiles | None | Firestore per-user documents |
| Progress Tracking | Session-only streak (resets on refresh) | Persistent cross-session analytics |
| Error Monitoring | logging to stdout only | Cloud Logging, structured JSON logs |
| Health Endpoint | None | /health with DB connectivity check |
| Secrets Management | Streamlit Secrets / .env file | Cloud Run env vars + GitHub Secrets (free) |
| Rate Limiting | None (relies on Groq 100K/day limit) | Per-user per-minute quotas via Firebase |
| Input Validation | Minimal (PDF math check only) | Pydantic models, full sanitization |
| CI/CD | None | GitHub Actions: test-on-PR, deploy-on-main |
| DB Migrations | None | Firestore schema versioning |

## Agent Capability Gaps

| Capability | Current | Required |
|---|---|---|
| Planning | None | Planner agent decomposes multi-step problems |
| Memory | 4-message in-memory window (session only) | Long-term Firestore + Qdrant memory |
| Reasoning | Single LLM call | Multi-step CoT via LangGraph StateGraph |
| Tool Calling | Hardcoded SymPy calls | Structured MCP tool registry |
| Verification | None | Verification agent cross-checks every answer |
| Retrieval | ChromaDB cosine k=3 | Hybrid dense+sparse via Qdrant |
| Self-Correction | None | Agent detects errors and retries (max 2x) |
| Human Feedback | Buttons with no backend storage | Feedback stored in Firestore for RLHF |

## Missing Infrastructure

- **Docker**: No Dockerfile
- **CI/CD**: No GitHub Actions workflows
- **Cloud Run**: No containerized deployment
- **Firebase Hosting**: No hosting configuration
- **Cloud Monitoring**: No metrics dashboard
- **Qdrant**: Replaced by inferior local ChromaDB
- **LaTeX Renderer**: No KaTeX or MathJax
- **Response Streaming**: No SSE token streaming

---

# 4. Google AI Integration Opportunities

## 4.1 Gemini Models

**Why**: Replace Groq/LLaMA with Google flagship models. Gemini 2.0 Flash offers 1M context window, native multimodal input (eliminates Tesseract OCR), and 1M tokens/day free via AI Studio.

**Where**:
- MathAIEngine -> GeminiMathEngine
- Camera scan -> native Gemini Vision (no Tesseract)
- Gemini 2.0 Flash Thinking for JEE-level proofs
- Gemini 1.5 Flash for fast NCERT answering

**Benefits**: Native multimodal, superior math reasoning, free tier (1M tokens/day vs Groq 30K for LLaMA 3.3), maximum hackathon ecosystem alignment.

**Complexity**: Low (langchain-google-genai package)

## 4.2 Google AI Studio (Production)

**Why**: Free Gemini API access with built-in safety filters, prompt engineering tools, and model selection -- no billing required.

**Where**: All Gemini model calls via Google AI Studio free API, Firestore-based prompt versioning, Gemini built-in safety settings, local evaluation pipeline, Cloud Logging free tier.

**Benefits**: Prompt versioning with Firestore rollback, safety filtering (critical in student context), zero-cost model serving via free API quota.

**Complexity**: Low (API key from Google AI Studio, no GCP billing required)

## 4.3 Firebase

**Why**: Complete BaaS handling auth, database, hosting, analytics -- free-tier, Google-native.

**Where**: Firebase Auth (Google Sign-In), Firestore (replaces MongoDB), Firebase Hosting (React frontend), Cloud Functions (webhooks + scheduled rebuilds), Firebase Analytics.

**Benefits**: Replaces MongoDB Atlas (simpler, Google-native), enables personalization and progress tracking, real-time Firestore listeners.

**Complexity**: Medium

## 4.4 Cloud Run

**Why**: Serverless containers that scale 0-to-thousands. Replaces Streamlit Cloud with proper HTTP API architecture.

**Where**: FastAPI backend, ADK agent service, MCP server deployments.

**Benefits**: Auto-scaling for hackathon demo spikes, free tier (2M requests/month, 360K vCPU-seconds), proper frontend/backend separation.

**Complexity**: Medium

## 4.5 Google AI Studio

**Why**: Free Gemini API access for prototyping and prompt engineering during development.
**Complexity**: Very Low (API key only)

## 4.6 Google Agent Development Kit (ADK)

**Why**: Google's official framework for production multi-agent systems. Directly demonstrates 'Build with AI' theme.

**Where**: PlannerAgent, MathSolverAgent, VerificationAgent, RetrieverAgent, MemoryAgent -- each as an ADK agent.

**Benefits**: Official Google framework, built-in observability and debugging, structured agent interfaces with typed I/O.

**Complexity**: High (architectural refactor)

## 4.7 Model Context Protocol (MCP)

**Why**: Industry-standard tool protocol exposing capabilities as structured APIs callable by any AI agent.

**Where**: Calculator, Python executor (sandboxed), LaTeX renderer, graph plotter, PDF reader, SymPy symbolic math server.

**Benefits**: Decouples tools from agent logic, tools reusable across any agent or model.

**Complexity**: Medium

---

# 5. AI Agent Architecture

## Agent System Overview

```
User Input (text/image/PDF)
        |
        v
  ORCHESTRATOR (Google ADK AgentRunner)
        |
   PLANNER AGENT (Gemini 2.0 Flash)
   - Classify: ncert_exercise | concept | multi_part | image | symbolic
   - Detect class level (6-12, JEE)
   - Decompose multi-part problems into sub-tasks
   - Route to appropriate solver node
        |
   +----+----+
   |         |
RETRIEVER  MEMORY AGENT
 AGENT     (Firestore)
 (Qdrant   Short-term: last 10 turns per session
  Hybrid)  Long-term: weak topics, streak, preferences
   |         |
   +----+----+
        |
   MATH SOLVER AGENT
   Model: Gemini 2.0 Flash Thinking (JEE)
          Gemini 1.5 Flash (NCERT Class 6-12)
   Tools: MCP - SymPy, Python executor, Graph plotter
   Output: {steps[], final_answer, latex, plaintext, confidence}
        |
   VERIFICATION AGENT (Gemini 1.5 Flash)
   - Re-solves problem independently using SymPy
   - Compares result with Solver output
   - Flags discrepancies, assigns confidence score
   - On mismatch: triggers self-correction (max 2 retries)
        |
   RESPONSE FORMATTER
   - KaTeX LaTeX rendering
   - Difficulty badge
   - Save to Firestore
   - Update user progress
        |
   HUMAN FEEDBACK LOOP (async)
   Thumbs up/down/doubt/different approach -> Firestore
```
## Agent Specifications

### Planner Agent
- **Model**: Gemini 2.0 Flash
- **Input**: Raw user query + session context
- **Output**: {type, class_level, topics, sub_tasks, routing}
- **Categories**: ncert_exercise | concept_query | multi_part | image_problem | symbolic_compute

### Math Solver Agent
- **Model**: Gemini 2.0 Flash Thinking (JEE) / Gemini 1.5 Flash (NCERT)
- **Tools via MCP**: SymPy calculator, Python executor, graph plotter
- **Output**: {steps[], final_answer, latex, plaintext, confidence_score}

### Verification Agent
- **Model**: Gemini 1.5 Flash
- **Task**: Independently verify via SymPy. On discrepancy: flag and re-route Solver with error context.
- **Output**: {verified: bool, confidence: float, corrections: list}

### Retriever Agent
- **Backend**: Qdrant Cloud (hybrid dense+sparse)
- **Embedding**: text-embedding-004 (768-dim, Google-native)
- **Filters**: class_level, chapter, topic, exercise, difficulty

### Memory Agent
- **Short-term**: Last 10 turns in Firestore (per session)
- **Long-term**: User weak topics, completed exercises, preferences in Firestore
- **Semantic**: Past solved problems embedded in Qdrant user_solved_problems collection

## LangGraph State Schema

```python
class MathAgentState(TypedDict):
    user_id: str
    session_id: str
    raw_query: str
    query_type: str          # ncert_exercise|concept|multi_part|image|symbolic
    class_level: str         # class_6 ... class_12 | jee
    retrieved_docs: list
    user_context: dict       # from Firestore: weak_topics, preferences
    solver_answer: dict      # steps[], final_answer, latex, confidence
    verification_result: dict  # verified bool, confidence, corrections
    final_response: str
    feedback: Optional[str]
    error: Optional[str]
    retry_count: int         # max 2 retries on verification failure
```
---

# 6. LangGraph Workflow

## Main Reasoning Graph

```
START
  |
  v
classify_question  [Gemini: detect type, level, complexity]
  |
  +-> [ncert_exercise] --> retrieve_ncert_context
  +-> [image_input]    --> process_image (Gemini Vision native)
  +-> [symbolic]       --> run_mcp_sympy
  +-> [general]        --> retrieve_general_context
  |
  v [all paths merge]
parallel_retrieval  [Qdrant hybrid search || Firestore memory] <- concurrent
  |
  v
route_by_level
  +-> [Class 6-8]   --> solve_basic  (Gemini 1.5 Flash)
  +-> [Class 9-10]  --> solve_ncert  (Gemini 1.5 Flash)
  +-> [Class 11-12] --> solve_senior (Gemini 2.0 Flash)
  +-> [JEE]         --> solve_jee    (Gemini 2.0 Flash Thinking)
  |
  v [all solver paths merge]
verify_answer  [SymPy cross-check + Gemini verification]
  |
  +-> [verified=True]         --> format_response
  +-> [verified=False, <2 retries] --> self_correct --> verify_answer
  +-> [verified=False, >=2 retries]--> format_with_confidence_warning
  |
  v
format_response  [LaTeX + plaintext + difficulty badge]
  |
  v
parallel_persist  [Firestore save || Qdrant upsert] <- concurrent
  |
  v
END
  |
  v [async, triggered by user action]
collect_feedback  [thumbs up/down/doubt/different approach -> Firestore]
```
## Retry and Fallback Logic

```python
def route_after_verify(state: MathAgentState) -> str:
    if state["verification_result"]["verified"]:
        return "format_response"
    if state["retry_count"] >= 2:
        return "format_with_confidence_warning"
    return "self_correct"

def self_correct(state: MathAgentState) -> MathAgentState:
    # Include previous failed attempt as context for correction
    state["retry_count"] += 1
    state["solver_answer"]["previous_attempt"] = state["solver_answer"]["final_answer"]
    return state
```
---

# 7. Firebase Architecture

## Authentication

```
Firebase Auth
- Providers: Google Sign-In (primary), Email/Password (fallback)
- Custom Claims: {role: "student"|"teacher", class_level: "10"}
- Security Rules: Users can only read/write their own Firestore documents
- Sessions: ID tokens auto-refreshed, stored in httpOnly cookies
```
## Firestore Schema

```
firestore/
+-- users/{userId}/
|   +-- profile: {name, email, class_level, created_at, avatar_url}
|   +-- preferences: {theme: "dark"|"light", language: "en"|"hi"}
|   +-- stats: {streak: int, total_solved: int, last_active: timestamp}
|
+-- sessions/{sessionId}/
|   +-- user_id, created_at
|   +-- messages/{messageId}/
|       +-- role: "user"|"assistant"
|       +-- content: string
|       +-- latex: string
|       +-- sources: array
|       +-- feedback: "up"|"down"|null
|       +-- timestamp
|
+-- progress/{userId}/{classLevel}/{chapterId}/
|   +-- completed_exercises: string[]
|   +-- weak_topics: string[]
|   +-- last_attempted: timestamp
|
+-- feedback/{feedbackId}/
    +-- user_id, session_id, message_id
    +-- type: "helpful"|"unhelpful"|"incorrect"
    +-- timestamp
```
## Cloud Functions

```
functions/
- onUserCreate        --> Initialize Firestore user document with defaults
- scheduledRagRebuild --> Cron (weekly): rebuild Qdrant index from knowledge base
- cleanOldSessions    --> Delete sessions older than 90 days
- exportFeedbackReport--> Generate teacher dashboard CSV on demand
```
---

# 8. Prompt Management, Safety & Evaluation

## Prompt Management (Firestore-Based, Free)
- All prompts stored in Firestore `prompt_templates/{promptId}` collection with full version history
- System prompts versioned: math-tutor-v2, verification-v1, planner-v1
- A/B testing between prompt versions via Firestore feature flags + local metrics
- Rollback available by updating active version pointer in Firestore

## Safety Configuration (Gemini Built-In, Free)

| Safety Category | Threshold |
|---|---|
| HARM_CATEGORY_HATE_SPEECH | BLOCK_MEDIUM_AND_ABOVE |
| HARM_CATEGORY_DANGEROUS_CONTENT | BLOCK_LOW_AND_ABOVE |
| HARM_CATEGORY_SEXUALLY_EXPLICIT | BLOCK_LOW_AND_ABOVE |
| HARM_CATEGORY_HARASSMENT | BLOCK_MEDIUM_AND_ABOVE |

## Model Selection Strategy (Google AI Studio Free Tier)

| Use Case | Model | Reason |
|---|---|---|
| NCERT Class 6-10 | Gemini 1.5 Flash | Fast, free, sufficient reasoning |
| NCERT Class 11-12 | Gemini 2.0 Flash | Better multi-step reasoning |
| JEE Advanced proofs | Gemini 2.0 Flash Thinking | Extended chain-of-thought reasoning |
| Planner/Classifier | Gemini 1.5 Flash | Low-latency classification task |
| Verification | Gemini 1.5 Flash | Simple cross-check, no heavy reasoning |
| Embeddings | text-embedding-004 | Google-native, 768-dim, free via AI Studio |

## Evaluation Pipeline (Local + Free Cloud Logging)
- **Offline**: LLM-as-judge scoring answers on correctness, clarity, level-appropriateness (local pytest-based)
- **Online**: A/B experiment tracking via Firestore metrics collection
- **RAG Quality**: Retrieval precision@k and recall@k tracked per CI commit

---

# 9. Qdrant Integration

## Why Qdrant Over ChromaDB

| Criterion | ChromaDB (current) | Qdrant (target) |
|---|---|---|
| Cloud hosting | No (local SQLite, ephemeral) | Yes (Qdrant Cloud free 1GB tier) |
| Hybrid search | No (dense only) | Yes (dense text-embedding-004 + sparse BM25) |
| Payload filtering | Limited | Full JSON filter support (AND/OR/nested) |
| Performance at scale | Degrades >500K vectors | Millions of vectors supported |
| API surface | Python SDK only | REST + gRPC + Python SDK |
| Persistence | Local SQLite (ephemeral on cloud) | Cloud-native, always-on |
| Multitenancy | None | Collections per topic/class/user |

## Collections Design

```
Qdrant Collections:

math_knowledge_base  [NCERT content, shared across all users]
  Vectors: text-embedding-004 (768 dimensions)
  Payload: {source, class_level, chapter, exercise, topic, difficulty, content_hash}

user_solved_problems  [per-user personalization and memory]
  Vectors: query embeddings (768 dimensions)
  Payload: {user_id, solved_at, confidence, feedback_type}

theorem_library  [mathematical theorems and formula reference]
  Vectors: text-embedding-004
  Payload: {theorem_name, mathematical_area, class_level, requires_proof}
```
## Hybrid Search Example

```python
results = client.query_points(
    collection_name="math_knowledge_base",
    prefetch=[
        Prefetch(query=dense_embedding, using="dense", limit=20),
        Prefetch(query=sparse_bm25_vector, using="sparse", limit=20),
    ],
    query=FusionQuery(fusion=Fusion.RRF),  # Reciprocal Rank Fusion
    limit=5,
    query_filter=Filter(must=[
        FieldCondition(key="class_level", match=MatchValue(value="class_10")),
        FieldCondition(key="chapter", match=MatchValue(value="ch6")),
    ]),
)
```
---

# 10. MCP Integration

## MCP Server Architecture

```
8 MCP Servers (each deployed as Cloud Run service):

calculator-mcp       [Port 8010]
  Tools: evaluate_expression, unit_convert, percentage_calc

sympy-mcp            [Port 8011]
  Tools: differentiate, integrate, solve_equation, simplify,
         matrix_operations, expand_expression, factor_expression

python-executor-mcp  [Port 8012]
  Tools: run_python_code (RestrictedPython sandbox, math libs only)

graph-plotter-mcp    [Port 8013]
  Tools: plot_function, plot_parametric, plot_3d, plot_scatter

latex-compiler-mcp   [Port 8014]
  Tools: render_latex_to_svg, validate_latex_expression

pdf-reader-mcp       [Port 8015]
  Tools: extract_text, extract_math_expressions, summarize_pdf

image-solver-mcp     [Port 8016]
  Tools: extract_math_from_image (Gemini Vision native - no Tesseract)

ncert-search-mcp     [Port 8017]
  Tools: search_exercise, get_chapter_summary, list_exercises
```
## MCP Tool Definition Example (sympy-mcp)

```python
from mcp.server.fastmcp import FastMCP
import sympy as sp

mcp = FastMCP("sympy-math")

@mcp.tool()
def differentiate(expression: str, variable: str = "x") -> dict:
    """Differentiate a mathematical expression symbolically.
    
    Args:
        expression: Math expression string (e.g., "x**3 + 2*x")
        variable: Variable to differentiate with respect to
    
    Returns:
        dict with: result (str), latex (str), steps (str)
    """
    var = sp.Symbol(variable)
    expr = sp.sympify(expression)
    derivative = sp.diff(expr, var)
    return {
        "result": str(derivative),
        "latex": sp.latex(derivative),
        "steps": f"d/d{variable}({expression}) = {derivative}"
    }
```
---

# 11. UI/UX Improvements

## Technology Shift: Streamlit -> FastAPI + React

Streamlit cannot support: real-time SSE token streaming, KaTeX/MathJax LaTeX rendering, interactive notebook mode, PWA offline support, or proper mobile UX.

## Target Stack

```
Frontend: React + Vite
  - KaTeX (LaTeX math rendering in browser, replaces plain Unicode)
  - Recharts (interactive math graphs embedded inline in chat)
  - Zustand (lightweight client state management)
  - Firebase SDK (auth + Firestore real-time listeners)

Backend: FastAPI
  - /api/v1/chat      (streaming SSE response, token-by-token)
  - /api/v1/upload    (PDF/image processing)
  - /api/v1/progress  (user analytics and progress data)
  - /api/v1/search    (Qdrant direct semantic search)
```
## Feature Comparison

| Feature | Current Streamlit | Improved React |
|---|---|---|
| Math Rendering | Plain Unicode (no LaTeX) | KaTeX renders beautiful equations inline |
| Response Delivery | All-at-once batch (poor UX) | Streaming tokens via SSE (token-by-token) |
| Graphs | Plotly in sidebar (disconnected) | Interactive Recharts embedded inline in chat |
| Chat History | Session memory only (lost on reload) | Persistent Firestore, searchable, shareable |
| Notebook Mode | None | Jupyter-style editable cells per problem |
| Progress Dashboard | None | Streak calendar heatmap, topic mastery charts |
| Teacher View | None | Class-level aggregate analytics dashboard |
| Mobile Support | Partially responsive | Full PWA with offline cached NCERT content |
| Accessibility | None | WCAG 2.1 AA compliance |
| Internationalization | Hindi/Hinglish in prompt only | Full i18n framework (Hindi, Tamil, Marathi) |

---

# 12. Deployment Architecture

## Production Infrastructure

```
GitHub (source code)
  |
  v
GitHub Actions CI/CD
  - On PR: test + lint (blocks merge on failure)
  - On main merge: build + push + deploy
  |
  v
GitHub Container Registry (Docker images with SHA tags, free)
  |
  +-> Cloud Run: API Service (FastAPI + ADK agents)
  |     - Scales 0-N instances automatically
  |     - /api/v1/* endpoints with Firebase auth middleware
  |
  +-> Cloud Run: MCP Servers (8 tool services)
  |     - sympy-mcp, calculator-mcp, graph-plotter-mcp, etc.
  |
  +-> Firebase Hosting: React Frontend
        - CDN-distributed globally
        - HTTPS enforced by default

Data Services:
  - Qdrant Cloud (vector store, 1GB free tier)
  - Firebase Auth + Firestore (user data and chat history)
  - Google AI Studio (Gemini models + text-embedding-004, free tier)
  - Cloud Run env vars + GitHub Secrets (all API keys, free)
```
## Dockerfile (API Service)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
EXPOSE 8080
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
```
## GitHub Actions CI/CD

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r backend/requirements.txt
      - run: pytest backend/tests/ -v --cov=src --cov-report=xml

  deploy:
    needs: test
    if: github.ref == refs/heads/main
    steps:
      - uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
      - run: |
          gcloud run deploy math-agent-api \
            --source backend/ \
            --region us-central1 \
            --allow-unauthenticated
```
## Secrets Strategy (Free)

```
Cloud Run Environment Variables (secrets set via gcloud CLI, free):
  GEMINI_API_KEY
  FIREBASE_ADMIN_SDK_JSON
  QDRANT_URL
  QDRANT_API_KEY

GitHub Actions Secrets (CI/CD secrets, free):
  GCP_SA_KEY
  GEMINI_API_KEY

Cloud Run Environment Variables (non-secret config):
  ENVIRONMENT=production
  GCP_PROJECT_ID=math-assistant-prod
```
---

# 13. Security Improvements

## CRITICAL: Fix eval() Vulnerability (Phase 0 Priority #1)

**Current vulnerable code (main.py Line 876)**:

```python
y = eval(re.sub(r'^',..., expr), ns)   # DANGEROUS: namespace is incomplete
```

**Safe replacement using SymPy lambdify**:

```python
import sympy as sp
safe_expr = sp.sympify(re.sub(r'^',..., expr))
f = sp.lambdify(sp.Symbol("x"), safe_expr, modules=["numpy"])
y = f(x)   # SAFE: no arbitrary code execution possible
```

## Full Security Hardening Plan

| Category | Implementation |
|---|---|
| Authentication | Firebase Auth with email verification requirement |
| Authorization | Firestore Security Rules: users access only their own data |
| Rate Limiting | Firebase App Check + FastAPI rate-limiting middleware (slowapi, free) |
| Prompt Injection | Input validation + Gemini built-in safety filters |
| Secrets | Cloud Run env vars + GitHub Secrets - zero hardcoded credentials (free) |
| Input Validation | Pydantic models for all FastAPI request/response schemas |
| HTTPS | Enforced by Firebase Hosting + Cloud Run by default |
| CORS | Whitelist-only CORS on FastAPI (production domains only) |
| Dependency Scanning | Dependabot + pip-audit in CI/CD pipeline |
| Container Security | Non-root user, minimal python:3.11-slim base image |

---

# 14. Performance Optimizations

## Caching Strategy

```
Request-Level Cache (In-Memory LRU via cachetools, free):
  - Embedding cache: hash(query) --> cached vector (30 min TTL)
  - Response cache: hash(query + class_level + chapter) --> answer (30 min TTL)
  - Qdrant Cloud: always warm (no cold start unlike local ChromaDB)

Application-Level:
  - LangChain callback cache for LLM response deduplication
  - Pre-embedded NCERT questions in Qdrant at service startup
```

## Token Streaming

```python
@app.get("/api/v1/chat/stream")
async def chat_stream(query: str, user_id: str):
    async def generate():
        async for chunk in gemini_agent.astream(query):
            yield f"data: {chunk.content}\n\n"
    return StreamingResponse(generate(), media_type="text/event-stream")
```

## Parallel Execution via LangGraph

```python
# Retriever + Memory fetch run concurrently, saving 1-2s per request
graph.add_node("parallel_retrieval", RunnableParallel({
    "qdrant_docs": retriever_agent,
    "user_context": memory_agent,
}))
```

## Cost Optimization
- Gemini 1.5 Flash for quick tasks (5-10x cheaper than Flash Thinking)
- Cache identical queries by hash(query + class_level) -> 30 min TTL
- Lazy MCP tool loading: connect to MCP server only when tool is needed
- Cloud Run scales to zero when idle (zero cost during off-hours)
- Qdrant Cloud: one-time indexing cost, fast reads from cloud-hosted vectors

---

# 15. Proposed Folder Structure

```
Advanced Mathematics Assistant/
|
+-- .github/
|   +-- workflows/
|       +-- ci.yml              [test + lint on every PR]
|       +-- deploy.yml          [deploy to Cloud Run on main merge]
|
+-- backend/                    [FastAPI + ADK agents + LangGraph]
|   +-- Dockerfile
|   +-- requirements.txt
|   +-- src/
|   |   +-- main.py             [FastAPI app entry point]
|   |   +-- config.py           [Pydantic Settings from environment]
|   |   +-- api/
|   |   |   +-- v1/
|   |   |   |   +-- chat.py     [/chat - streaming SSE endpoint]
|   |   |   |   +-- upload.py   [/upload - PDF/image processing]
|   |   |   |   +-- progress.py [/progress - user analytics]
|   |   |   |   +-- search.py   [/search - Qdrant direct search]
|   |   |   +-- middleware/
|   |   |       +-- auth.py     [Firebase ID token validation]
|   |   |       +-- rate_limit.py
|   |   +-- agents/             [ADK multi-agent system]
|   |   |   +-- orchestrator.py
|   |   |   +-- planner_agent.py
|   |   |   +-- math_solver_agent.py
|   |   |   +-- verification_agent.py
|   |   |   +-- retriever_agent.py
|   |   |   +-- memory_agent.py
|   |   +-- graph/             [LangGraph workflow]
|   |   |   +-- math_graph.py  [main StateGraph definition]
|   |   |   +-- state.py       [MathAgentState TypedDict]
|   |   |   +-- nodes/
|   |   |       +-- classify.py, retrieve.py, solve.py, verify.py, format.py
|   |   +-- services/
|   |   |   +-- gemini_service.py   [Google AI Studio / Gemini client (free)]
|   |   |   +-- qdrant_service.py   [Qdrant Cloud operations]
|   |   |   +-- firebase_service.py [Firestore + Auth Admin SDK]
|   |   |   +-- embedding_service.py [text-embedding-004 client]
|   |   +-- math/
|   |       +-- symbolic_engine.py  [SymPy engine, extracted from main.py]
|   |       +-- knowledge_indexer.py [Qdrant ingestion pipeline]
|   +-- tests/
|       +-- test_agents.py
|       +-- test_graph.py
|       +-- test_api.py
|       +-- test_symbolic_engine.py
|
+-- mcp-servers/                [Model Context Protocol tool servers]
|   +-- sympy-mcp/ (Dockerfile, server.py, requirements.txt)
|   +-- calculator-mcp/
|   +-- graph-plotter-mcp/
|   +-- pdf-reader-mcp/
|   +-- python-executor-mcp/    [RestrictedPython sandbox]
|   +-- image-solver-mcp/       [Gemini Vision]
|
+-- frontend/                   [React + Vite]
|   +-- src/
|   |   +-- components/
|   |   |   +-- Chat/ (ChatWindow, MessageBubble with KaTeX, StreamingMessage)
|   |   |   +-- NCERT/ (QuizPanel, QuestionCard with 4-button help system)
|   |   |   +-- Math/ (GraphRenderer, LatexDisplay)
|   |   |   +-- Progress/ (StreakCalendar, TopicMastery heatmap)
|   |   |   +-- Auth/ (GoogleSignIn)
|   |   +-- hooks/
|   |   |   +-- useAuth.ts     [Firebase auth state hook]
|   |   |   +-- useChat.ts     [SSE streaming hook with reconnection]
|   |   |   +-- useProgress.ts [Firestore real-time listener]
|   |   +-- store/
|   |       +-- chatStore.ts   [Zustand global state]
|   +-- vite.config.ts
|   +-- package.json
|
+-- knowledge-base/             [Migrated from monolithic knowledge_base.py]
|   +-- ncert/
|   |   +-- class_6/ (ch1.md...ch14.md)
|   |   +-- class_7/ (ch1.md...ch15.md)
|   |   +-- class_8/ ... class_12/
|   +-- jee/topics/*.md
|   +-- indexer.py             [Qdrant ingestion script]
|
+-- firebase/
|   +-- firebase.json, firestore.rules, firestore.indexes.json
|   +-- functions/src/ (onUserCreate.ts, scheduledRagRebuild.ts)
|
+-- PROJECT_ENHANCEMENT_ROADMAP.md
+-- README.md
+-- .gitignore
+-- docker-compose.yml          [Local dev orchestration]
```
---

# 16. Development Phases

> **CRITICAL RULE**: Each phase requires explicit approval before the next begins.
> Never work on multiple phases simultaneously. Never assume approval.

---

## Phase 0: Repository Audit and Security Fix

**Objectives**:
1. Fix the critical eval() security vulnerability (main.py Line 876)
2. Extract unit tests from main.py into standalone test files in tests/
3. Add proper .gitignore entries (chroma_db/, faiss_index/, .env, __pycache__/)
4. Create CHANGELOG.md documenting the transformation starting point

**Files Affected**:
- main.py: Replace eval() at L876 with sp.sympify() + sp.lambdify()
- requirements.txt: Add pytest, pytest-cov as dev dependencies
- .gitignore: Add chroma_db/, faiss_index/, *.pyc, __pycache__/
- tests/: New directory with 5 test classes extracted from main.py
- CHANGELOG.md: New file documenting transformation

**Estimated Effort**: 0.5 days

**Dependencies**: None -- can begin immediately after roadmap approval

**Risks**:
- sp.sympify() + sp.lambdify() must cover all plottable functions: sin, cos, tan, log, sqrt, exp, abs, pi, e -- need comprehensive test coverage

**Testing Checklist**:
- [ ] Graph plotter renders sin(x), x**2, log(x), sqrt(x), exp(x) correctly
- [ ] Graph plotter CANNOT execute arbitrary Python (test: attempt os/sys access)
- [ ] All 5 original test classes pass without modification
- [ ] pytest --cov generates coverage report baseline

**Acceptance Criteria**:
- Zero occurrences of bare eval() in any production code path
- All 5 original test classes pass unchanged
- Security vulnerability documented and marked closed in CHANGELOG

**Rollback Strategy**: git revert Phase 0 commit -- single commit, reversible in under 30 seconds

---

## Phase 1: Architecture Refactoring

**Objectives**:
1. Decompose main.py (2,745 lines) into logical, single-responsibility modules
2. Extract all business logic completely out of the Streamlit UI rendering layer
3. Set up FastAPI backend skeleton with /health and /api/v1/chat (non-streaming)
4. Maintain Streamlit frontend fully functional throughout the entire migration

**Files Affected**:
- main.py --> split into: backend/src/math/symbolic_engine.py
-          backend/src/services/vector_service.py
-          backend/src/services/memory_service.py
-          backend/src/math/knowledge_indexer.py
-          backend/src/api/v1/chat.py
-          backend/src/main.py (FastAPI app)
- NEW: backend/Dockerfile
- NEW: docker-compose.yml

**Estimated Effort**: 2 days

**Dependencies**: Phase 0 complete

**Risks**:
- Streamlit session_state is tightly coupled to rendering -- must trace all state dependencies carefully before extracting
- MongoDB memory service needs mock for isolated unit testing

**Testing Checklist**:
- [ ] FastAPI GET /health returns HTTP 200 with {status: "ok", kb_docs: N}
- [ ] FastAPI POST /api/v1/chat returns correct solution for "solve x^2-4=0"
- [ ] All original unit tests pass against new module structure
- [ ] Streamlit UI still fully functional end-to-end with refactored backend
- [ ] docker-compose up starts both services without errors

**Acceptance Criteria**:
- main.py reduced to UI-only rendering code (target: under 500 lines)
- FastAPI server starts cleanly and handles basic math queries correctly
- Docker Compose brings up both services in under 2 minutes

**Rollback Strategy**: git revert Phase 1 commits; original main.py preserved unchanged in git history

---

## Phase 2: Gemini Integration

**Objectives**:
1. Replace Groq/LLaMA with Google Gemini models (Gemini 2.0 Flash + 1.5 Flash)
2. Implement native Gemini Vision for image math extraction (eliminates Tesseract OCR)
3. Add SSE streaming response endpoint (token-by-token delivery)
4. Update system prompt to enable LaTeX output (unban dollar-sign notation)

**Files Affected**:
- NEW: backend/src/services/gemini_service.py
- MODIFY: backend/src/api/v1/chat.py (add /stream SSE endpoint)
- MODIFY: backend/requirements.txt (add google-generativeai, langchain-google-genai)
- MODIFY: env.example (add GEMINI_API_KEY; deprecate GROQ_API_KEY)

**Estimated Effort**: 1.5 days

**Dependencies**: Phase 1 complete; Google AI Studio account with Gemini API key

**Risks**:
- Gemini response format differs from Groq API -- adapter layer needed
- Free tier: 15 RPM for Gemini 1.5 -- may bottleneck under concurrent demo load
- LaTeX in responses needs frontend KaTeX for proper rendering (partial Phase 10 dependency)

**Testing Checklist**:
- [ ] Gemini 2.0 Flash responds to "solve 2x+3=7" with correct whiteboard-style steps
- [ ] Gemini Vision correctly extracts math equation from test JPG image without Tesseract
- [ ] SSE streaming endpoint delivers tokens progressively (verify with curl -N)
- [ ] Fallback to Gemini 1.5 Flash works correctly when rate limit is hit

**Acceptance Criteria**:
- Zero Groq API calls remain in any production code path
- Image math extraction works end-to-end without Tesseract installed
- Streaming response verifiable: curl -N http://localhost:8080/api/v1/chat/stream

**Rollback Strategy**: Feature flag USE_GEMINI=false falls back to Groq ChatGroq client

---

## Phase 3: Firebase Integration

**Objectives**:
1. Implement Firebase Auth with Google Sign-In flow
2. Replace MongoDB Atlas with Firestore for all chat history persistence
3. Migrate daily streak counter to Firestore (persists across browser sessions)
4. Add user profiles and progress tracking Firestore schema
5. Protect all API endpoints with Firebase ID token validation middleware

**Files Affected**:
- NEW: backend/src/services/firebase_service.py
- NEW: backend/src/api/middleware/auth.py
- NEW: backend/src/api/v1/progress.py
- NEW: firebase/firestore.rules
- MODIFY: backend/requirements.txt (add firebase-admin; remove pymongo, motor)

**Estimated Effort**: 2 days

**Dependencies**: Phase 2 complete; Firebase project created in GCP Console

**Risks**:
- Firestore free tier: 50K reads/day, 20K writes/day -- monitor in staging
- Firebase Admin SDK requires service account JSON (must be in Cloud Run env vars, never committed)
- Anonymous session data has no migration path -- inform users old history is not migrated

**Testing Checklist**:
- [ ] Google Sign-In flow completes and creates user document in Firestore
- [ ] Chat messages stored with correct user_id scoping (no cross-user data leakage)
- [ ] Unauthenticated API request returns HTTP 401 with clear error message
- [ ] Streak counter persists correctly after browser close and reopen
- [ ] Firestore Security Rules tested in Firebase Emulator: user cannot read other users data

**Acceptance Criteria**:
- User can sign in with Google and see their persistent chat history
- MongoDB completely removed from requirements.txt and env.example
- Firestore Security Rules pass 100% of emulator test cases

**Rollback Strategy**: USE_FIREBASE=false env var falls back to in-memory/MongoDB

---

## Phase 4: Google ADK Multi-Agent System

**Objectives**:
1. Implement 5 specialized agents using Google ADK framework
2. Replace single MathAIEngine.query() with ADK multi-agent orchestration pipeline
3. Add ADK tracing and observability dashboard for all agent calls
4. Implement human feedback loop with storage in Firestore

**Files Affected**:
- NEW: backend/src/agents/ directory (orchestrator + 5 agent files)
- MODIFY: backend/src/api/v1/chat.py (route through ADK orchestrator)
- MODIFY: backend/requirements.txt (add google-adk)

**Estimated Effort**: 3 days (most architecturally complex phase)

**Dependencies**: Phase 3 complete

**Risks**:
- ADK is relatively new (2025) -- documentation gaps may require workarounds
- Multi-agent pipeline adds 2-3s latency vs single LLM call -- must stay under 10s total
- ADK async runtime must be verified for compatibility with FastAPI async event loop
- Verification agent overhead must be measured before committing to architecture

**Testing Checklist**:
- [ ] Planner classifies "solve x^2+5x+6=0" as {type: ncert_exercise, class: 10}
- [ ] Verification agent catches deliberate error "4+4=9" and flags it as incorrect
- [ ] End-to-end latency under 10 seconds for a Class 10 NCERT question
- [ ] ADK tracing dashboard shows full agent call chain for each request
- [ ] Memory agent correctly retrieves previously identified user weak topics

**Acceptance Criteria**:
- All 5 agents operational and producing correct outputs independently
- Original MathAIEngine.query() fully replaced by ADK orchestration
- Agent trace visible in ADK dashboard for every API request

**Rollback Strategy**: USE_ADK=false flag routes to legacy single-agent path preserved from Phase 2

---

## Phase 5: LangGraph Workflow

**Objectives**:
1. Implement full reasoning state machine using LangGraph StateGraph
2. Implement conditional routing (by class level and question type)
3. Implement retry-with-self-correction loop (maximum 2 retries on verification failure)
4. Add parallel retrieval (Qdrant + Firestore memory run concurrently)
5. LangGraph tracing via LangSmith or Cloud Logging integration

**Files Affected**:
- NEW: backend/src/graph/ directory
- NEW: backend/src/graph/math_graph.py (StateGraph definition)
- NEW: backend/src/graph/state.py (MathAgentState TypedDict)
- NEW: backend/src/graph/nodes/ (classify, retrieve, solve, verify, format nodes)
- MODIFY: backend/requirements.txt (add langgraph, langsmith)

**Estimated Effort**: 2.5 days

**Dependencies**: Phase 4 complete (ADK agents serve as individual graph nodes)

**Risks**:
- LangGraph async compatibility with ADK async runtime must be verified first
- LangSmith API key needed for graph visualization -- set up before implementation
- Retry loop can cause up to 3x latency on verification failure -- set hard 15s timeout

**Testing Checklist**:
- [ ] Graph correctly routes JEE question to solve_jee node (Gemini 2.0 Flash Thinking)
- [ ] Retry loop fires exactly when verification fails, stops at max 2 retries
- [ ] Parallel retrieval (Qdrant + Firestore) completes in under 2 seconds
- [ ] LangGraph trace shows full graph traversal for a complete conversation turn
- [ ] Graph survives node exception without crashing the entire pipeline

**Acceptance Criteria**:
- Full StateGraph with all nodes defined, edges connected, conditional routing working
- At least one trace visible in tracing tool for each of the 3 question types
- Graph handles node-level exceptions gracefully without pipeline crash

**Rollback Strategy**: USE_LANGGRAPH=false routes directly through ADK orchestrator

---

## Phase 6: Qdrant Integration

**Objectives**:
1. Replace ChromaDB/FAISS with Qdrant Cloud as the vector store
2. Migrate all 6,121 lines of knowledge_base.py to structured Markdown files
3. Implement hybrid search (dense text-embedding-004 + sparse BM25)
4. Add metadata filtering by class_level, chapter, topic, difficulty
5. Set up user_solved_problems collection for personalization

**Files Affected**:
- NEW: backend/src/services/qdrant_service.py
- NEW: backend/src/math/knowledge_indexer.py
- NEW: knowledge-base/ directory (Markdown files per chapter)
- MODIFY: backend/src/services/embedding_service.py (switch to text-embedding-004)
- MODIFY: backend/requirements.txt (add qdrant-client; remove chromadb, faiss-cpu)

**Estimated Effort**: 2 days

**Dependencies**: Phase 5 complete

**Risks**:
- Qdrant Cloud free tier: 1GB storage -- sufficient for current KB but monitor growth
- Switching embeddings (HuggingFace -> text-embedding-004) changes vector space -- full re-index required
- BM25 sparse vectors require separate computation (fastembed or rank-bm25 library)

**Testing Checklist**:
- [ ] All 505 NCERT exercises indexed and retrievable in Qdrant
- [ ] Search for "Basic Proportionality Theorem" returns Class 10 Ch6 (not Ch8)
- [ ] Metadata filter {class_level: "class_10", chapter: "ch6"} narrows results correctly
- [ ] Hybrid search outperforms pure dense search on 10 keyword-heavy test queries

**Acceptance Criteria**:
- ChromaDB and FAISS completely removed from codebase
- All knowledge base content accessible via Qdrant with metadata filters
- Retrieval precision@5 >= 0.80 on 20-question held-out test set

**Rollback Strategy**: VECTOR_DB=qdrant|chroma environment variable switches backend instantly

---

## Phase 7: Prompt Management, Safety & Evaluation (Free Tier)

**Objectives**:
1. Implement Firestore-based prompt template versioning with rollback support
2. Configure Gemini built-in safety filters on all model invocations (free via AI Studio)
3. Set up offline evaluation pipeline (LLM-as-judge for answer quality, local pytest-based)
4. Integrate Cloud Logging free tier for structured observability of all agent calls
5. Implement prompt A/B testing via Firestore feature flags

**Files Affected**:
- MODIFY: backend/src/services/gemini_service.py (add safety config + prompt loading)
- NEW: backend/src/services/prompt_service.py (Firestore prompt versioning)
- NEW: backend/src/services/evaluation_service.py (local LLM-as-judge)
- MODIFY: backend/requirements.txt (add google-cloud-logging)

**Estimated Effort**: 1.5 days

**Dependencies**: Phase 6 complete; Google AI Studio API key

**Risks**:
- Firestore free tier: 50K reads/day -- prompt template reads are lightweight but monitor
- Cloud Logging free tier: 50 GiB/month -- sufficient for development and hackathon demo
- Gemini safety filters may block legitimate math content containing keywords -- test edge cases

**Testing Checklist**:
- [ ] Gemini API calls use configured safety settings (verify in response metadata)
- [ ] Safety filter blocks test prompt "explain how to cheat on board exams"
- [ ] Prompt template loaded from Firestore and applied correctly at runtime
- [ ] Structured JSON log visible in Cloud Logging for every agent invocation
- [ ] Evaluation pipeline scores 5 sample questions with LLM-as-judge

**Acceptance Criteria**:
- All Gemini API calls include safety configuration (via google-genai SDK)
- Prompt templates versioned in Firestore with active version pointer
- Structured logs visible in Cloud Logging free tier with latency and model metadata
- Safety filter behavior documented and tested in CHANGELOG

**Rollback Strategy**: Prompt version pointer in Firestore reverted to previous version instantly

---

## Phase 8: Cloud Run Deployment

**Objectives**:
1. Deploy FastAPI backend to Cloud Run (production environment)
2. Set up Firebase Hosting for React frontend (initially with placeholder)
3. Configure GitHub Actions CI/CD (test-on-PR, deploy-on-main)
4. Store all API keys in Cloud Run env vars + GitHub Secrets (free, remove from .env files)
5. Configure FastAPI rate-limiting middleware for DDoS protection (slowapi, free)

**Files Affected**:
- NEW: backend/Dockerfile (production-ready)
- NEW: mcp-servers/*/Dockerfile (for future MCP deployments)
- NEW: .github/workflows/ci.yml
- NEW: .github/workflows/deploy.yml
- MODIFY: firebase/firebase.json (hosting configuration)

**Estimated Effort**: 2 days

**Dependencies**: Phase 7 complete

**Risks**:
- Cloud Run cold start with large ML deps -- embeddings must use Google AI Studio API (free), not local torch
- CORS: Firebase Hosting domain and Cloud Run domain must be properly whitelisted
- GitHub Actions service account must follow minimal-privilege IAM principle

**Testing Checklist**:
- [ ] docker build completes successfully in under 5 minutes
- [ ] Cloud Run service URL returns HTTP 200 on GET /health
- [ ] Firebase Hosting serves placeholder frontend with no console errors
- [ ] Full chat flow works end-to-end via production URL (not localhost)
- [ ] CI pipeline runs on PR creation and blocks merge on test failure
- [ ] Deploy pipeline triggers automatically on main branch merge and succeeds

**Acceptance Criteria**:
- Live production URL accessible from any browser worldwide
- GitHub Actions green badge visible on main branch in repository
- Zero hardcoded API credentials in any committed file (all in Cloud Run env vars + GitHub Secrets)

**Rollback Strategy**: Cloud Run traffic splitting: gcloud run services update-traffic --to-revisions PREV=100

---

## Phase 9: MCP Servers

**Objectives**:
1. Implement and deploy all 6 MCP server tool services
2. Connect ADK Math Solver agent to the MCP tool registry
3. End-to-end test each tool with its complete input/output contract
4. Implement RestrictedPython sandbox for the Python code executor

**Files Affected**:
- NEW: mcp-servers/sympy-mcp/server.py
- NEW: mcp-servers/calculator-mcp/server.py
- NEW: mcp-servers/graph-plotter-mcp/server.py
- NEW: mcp-servers/pdf-reader-mcp/server.py
- NEW: mcp-servers/python-executor-mcp/server.py (RestrictedPython sandbox)
- NEW: mcp-servers/image-solver-mcp/server.py (Gemini Vision)
- MODIFY: backend/src/agents/math_solver_agent.py (add MCP tool calls)

**Estimated Effort**: 2.5 days

**Dependencies**: Phase 8 complete (Cloud Run deployment for MCP services)

**Risks**:
- Python executor sandbox: RestrictedPython must prevent os/sys/subprocess access -- security-critical
- MCP protocol version compatibility with ADK client must be verified before implementation
- 6 additional Cloud Run services increase operational complexity and monitoring requirements

**Testing Checklist**:
- [ ] sympy-mcp: differentiate("x**3") returns {result: "3*x**2", latex: "3x^{2}"}
- [ ] python-executor-mcp: "import os" raises SecurityError and does not execute
- [ ] graph-plotter-mcp: plot_function("sin(x)") returns valid SVG string
- [ ] image-solver-mcp: extracts "2x + 3 = 7" from provided test image correctly
- [ ] Math Solver agent uses sympy-mcp for differentiation (confirmed via ADK trace)

**Acceptance Criteria**:
- All 6 MCP servers deployed to Cloud Run with passing health checks
- Math Solver demonstrably uses at least 3 different MCP tools in one test session
- Python sandbox security audit complete and documented in CHANGELOG

**Rollback Strategy**: USE_MCP=false disables tool calling; agent falls back to direct SymPy calls

---

## Phase 10: React Frontend

**Objectives**:
1. Build complete React + Vite frontend to replace Streamlit entirely
2. Implement KaTeX LaTeX math rendering for all AI responses
3. Implement SSE streaming chat consumer (token-by-token display)
4. Implement full NCERT Quiz panel with 4-button help system (Hint/Steps/Answer/Ask AI)
5. Implement Progress Dashboard with streak calendar and topic mastery heatmap
6. Deploy to Firebase Hosting replacing Streamlit Cloud dependency

**Files Affected**:
- NEW: frontend/ directory (all React source files and configuration)
- MODIFY: firebase/firebase.json (update hosting to point to frontend/dist)

**Estimated Effort**: 4 days (largest single phase)

**Dependencies**: Phase 8 + Phase 9 (requires working live API endpoints)

**Risks**:
- KaTeX rendering: edge cases with complex multi-line LaTeX expressions
- SSE reconnection: EventSource must handle network interruptions gracefully
- Mobile layout: 375px viewport requires significant additional CSS effort
- NCERT Quiz panel: must preserve full 4-button/stuck menu/follow-up UX from Streamlit

**Testing Checklist**:
- [ ] Google Sign-In works and session persists across browser page refresh
- [ ] Chat: message sent, streaming response received, LaTeX rendered correctly
- [ ] NCERT Quiz: Class 10 Ch6 exercises load with Hint, Steps, Answer, Ask AI buttons
- [ ] Stuck menu: 5 options appear after clicking Ask AI, each sends correct prompt
- [ ] Streak calendar shows correct days on Progress Dashboard
- [ ] Lighthouse: Performance >80, Accessibility >90, Best Practices >90
- [ ] Mobile at 375px viewport: usable layout, no overflow, touch targets >=44px

**Acceptance Criteria**:
- Streamlit completely removed from production code path
- Full feature parity with current Streamlit UI (all 10 features in README)
- Dark/light theme working in React with correct design system
- Firebase Hosting serves React app (no more Streamlit Cloud dependency)

**Rollback Strategy**: Streamlit preserved in legacy/ branch; Firebase Hosting can revert in minutes

---

## Phase 11: Testing, Documentation, and Hackathon Polish

**Objectives**:
1. Achieve unit test coverage >70% across entire backend
2. Write integration tests for auth flow, full chat flow, and progress tracking
3. Write Playwright e2e tests for complete user journey
4. Rewrite README.md for hackathon audience with architecture diagrams and live URL
5. Create 3-minute demo video showcasing agentic AI capabilities
6. Performance benchmark: 50 concurrent users, average latency <5s
7. Final security audit

**Files Affected**:
- MODIFY: backend/tests/ (expand to full coverage)
- MODIFY: README.md (complete rewrite for hackathon)
- NEW: docs/ARCHITECTURE.md
- MODIFY: .github/workflows/ci.yml (add Playwright e2e tests)

**Estimated Effort**: 2 days

**Dependencies**: All previous phases complete

**Risks**:
- Demo traffic spike during live hackathon presentation -- verify Cloud Run auto-scaling behavior
- Video recording and editing requires screen capture tool and post-processing time

**Testing Checklist**:
- [ ] Backend unit test coverage >= 70% (pytest --cov-report confirms)
- [ ] Integration test: full auth flow (sign in -> chat -> progress saved correctly)
- [ ] E2e Playwright: complete journey from login to receiving a rated answer
- [ ] Load test: 50 concurrent users with average latency under 5 seconds
- [ ] pip-audit: zero critical CVEs in production dependencies
- [ ] 5 manual prompt injection attempts all blocked by Gemini safety filters

**Acceptance Criteria**:
- All CI checks green on main branch
- Live demo URL functional and used as hackathon submission URL
- README explains multi-agent architecture clearly for judges (with diagrams)
- Demo video under 3 minutes showing: login, NCERT quiz, AI solve, streak progress

**Rollback Strategy**: Documentation-only phase -- no code rollback needed

---

## Development Phase Summary

| Phase | Focus | Effort | Key Deliverable |
|---|---|---|---|
| Phase 0 | Security fix + audit | 0.5 days | eval() removed, tests extracted |
| Phase 1 | Architecture refactor | 2 days | FastAPI skeleton, main.py decomposed |
| Phase 2 | Gemini integration | 1.5 days | Groq replaced, SSE streaming added |
| Phase 3 | Firebase auth + Firestore | 2 days | User auth, persistent history |
| Phase 4 | ADK multi-agent system | 3 days | 5 specialized agents operational |
| Phase 5 | LangGraph workflow | 2.5 days | Full StateGraph with retry logic |
| Phase 6 | Qdrant vector database | 2 days | Hybrid search, ChromaDB removed |
| Phase 7 | Prompt management, safety & eval | 1.5 days | Prompt versioning, safety filters, evaluation |
| Phase 8 | Cloud Run deployment | 2 days | Live production URL established |
| Phase 9 | MCP servers | 2.5 days | 6 tool servers deployed |
| Phase 10 | React frontend | 4 days | Streamlit completely replaced |
| Phase 11 | Testing + polish | 2 days | Hackathon-ready submission |
| **TOTAL** |  | **~25 days** |  |

---

# 17. Final Vision

## What the Finished Application Will Be

The Advanced Mathematics AI Agent Platform will be a production-grade, multi-agent AI system for Indian school students -- a genuine AI-first educational product, not merely an LLM chatbot with a text input box.

## The Student Experience

```
Student opens app on mobile
--> Signs in with Google (one tap, Google Sign-In)
--> App: "Welcome back! You're on a 7-day streak!"
--> App surfaces: "You struggled with Trigonometry last week. Try this:"
--> Student selects Class 10 Ch8 Exercise 8.1 Question 3
--> Taps "Hint"
--> Response streams in token-by-token
--> Beautiful KaTeX LaTeX renders: sin(theta), the right triangle diagram
--> Student does not understand --> taps "Different Approach"
--> Agent plots the right triangle inline in chat using graph-plotter MCP
--> Student understands --> taps "Got it!"
--> Progress recorded in Firestore
--> Weak topic "Trigonometry" removed from weakness list
--> Streak extended to 8 days
```

## What Makes This a Strong Hackathon Submission

**Multi-agent reasoning (ADK)**: Not a single LLM call. A coordinated team of specialized agents each doing one thing well.

**Persistent memory (Firestore + Qdrant)**: Agents remember the student's history across every session -- not just the current conversation.

**Tool-augmented AI (MCP)**: Agents use real tools: SymPy for exact symbolic math, Python for numerical computation, Gemini Vision for images.

**Stateful workflows (LangGraph)**: Conditional routing, retry-on-failure, parallel execution -- not a simple prompt-response loop.

**Google AI native (Gemini + Google AI Studio)**: Google's cutting-edge models in every agent via free AI Studio API with Cloud Logging.

**Production deployment (Cloud Run + Firebase)**: Real cloud infrastructure with CI/CD and proper security -- not a hackathon prototype on Streamlit Cloud.

**Safety and security (Gemini safety filters + Firebase Auth)**: Production-grade security posture appropriate for a student-facing application.

**Vector intelligence (Qdrant hybrid search)**: Retrieves the right NCERT content with mathematical and semantic precision.

**Human feedback loop**: Student feedback stored in Firestore and ready for future fine-tuning RLHF signals.

## Target Impact Metrics at Launch

| Metric | Target |
|---|---|
| NCERT questions available | 505 (Class 9-10), expandable to 2,000+ |
| Classes covered | Class 6-12 + JEE Advanced |
| Average response latency | Under 8 seconds end-to-end (including verification) |
| Answer accuracy (SymPy-verified) | Greater than 95% for algebraic questions |
| Concurrent users | 0 to 1,000 (Cloud Run auto-scaling) |
| Monthly GCP cost | Under $10 (all services on free tiers) |
| Google AI technologies used | 7+ (Gemini, Google AI Studio, Firebase, Cloud Run, ADK, text-embedding-004, Cloud Logging) |

## The One-Sentence Hackathon Pitch

> "We transformed a good math tutoring chatbot into a production multi-agent AI tutoring system where a **Planner** understands what the student needs, a **Retriever** finds exactly the right NCERT content, a **Solver** works through each problem using Gemini with real mathematical tools, and a **Verifier** confirms the answer is correct before the student ever sees it -- all powered by Google's AI ecosystem, all deployed on GCP, all designed to make every student smarter."

---

*This is the master planning document.*
*No code changes before explicit approval.*
*After approval: begin strictly with Phase 0.*

---

**Document End -- Awaiting Approval to Proceed to Phase 0**
