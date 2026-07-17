#!/usr/bin/env python3
"""Script to write PROJECT_ENHANCEMENT_ROADMAP.md to the project directory."""

import pathlib

OUTPUT_PATH = pathlib.Path(r"c:\Users\ayush\OneDrive\Desktop\Advanced Mathematics Assistant\PROJECT_ENHANCEMENT_ROADMAP.md")

ROADMAP = r"""# PROJECT ENHANCEMENT ROADMAP
## Advanced Mathematics Assistant → Production-Ready AI Agent Platform
### Google Build with AI × AI House Hackathon

---

> **Document Version:** 1.0.0
> **Analysis Date:** July 2026
> **Author:** AI Architecture Team
> **Status:** AWAITING APPROVAL BEFORE PHASE 0 BEGINS

---

## IMPORTANT: Workflow Rules

- CURRENT STATE: Analysis Complete, Roadmap Delivered
- NEXT STEP: Await explicit approval before any code changes
- EXECUTION ORDER: Phase 0 → Approval → Phase 1 → Approval → ...
- RULE: Never work on multiple phases simultaneously

---

# 1. Executive Summary

## Current Project Overview

The **Advanced Mathematics Assistant** is a Streamlit-based educational tool built by Sarika (GitHub: `Sarika-stack23`) designed to help Indian school students (Class 6–12 + JEE) solve NCERT mathematics problems. The application is live at `advanced-mathematics-assistant-zvlizldwugwffind.streamlit.app`.

At its core, the application is a **RAG-powered chatbot** built on:
- **LLaMA 3.3 70B** via Groq API (LLM)
- **ChromaDB / FAISS** (vector store)
- **HuggingFace sentence-transformers** (embeddings)
- **LangChain** (orchestration)
- **SymPy** (symbolic math)
- **Streamlit** (UI)
- **MongoDB Atlas** (chat memory)

The knowledge base (`knowledge_base.py`) contains **505 hand-curated NCERT exercise questions** (Class 9 & 10) plus comprehensive topic documents for Class 6–12 and JEE Advanced — totaling **6,121 lines** of structured, metadata-tagged content embedded as LangChain `Document` objects.

## Existing Strengths

| Strength | Detail |
|---|---|
| **Rich Domain Knowledge** | 6,121-line hand-curated knowledge base with 505 NCERT exercises across Class 6-12 and JEE |
| **Pedagogically Thoughtful** | Whiteboard-style answer format, 5-second rule, hint/steps/answer mode |
| **Multi-modal Input** | Camera scan (Tesseract OCR), PDF upload, text input |
| **Good UI Polish** | Dark/light mode, custom CSS with Google Fonts, responsive layout, Plotly graphs |
| **Symbolic Computation** | SymPy integration for exact differentiation, integration, equation solving |
| **Streaming Fallback** | Auto-switches between 3 Groq models on rate limit hit |
| **Unit Tests** | TestDataSources, TestPreprocessing, TestChunking, TestSymbolicEngine, TestMemory |
| **DevContainer** | GitHub Codespaces-ready devcontainer.json |
| **Smart PDF Classifier** | Rejects non-math PDFs with document type detection |
| **Session Streaks** | Daily practice streak counter |

## Existing Weaknesses

| Weakness | Impact |
|---|---|
| **God Object Anti-pattern** | All 2,745 lines of logic crammed into one `main.py` — untestable, unmaintainable |
| **No Authentication** | Zero user identity — no login, no persistent profiles, no personalization |
| **No Google AI** | No Gemini, no Vertex AI, no Firebase, no Cloud Run — completely outside the target ecosystem |
| **Not Agent Architecture** | Simple RAG chatbot, not a multi-agent reasoning system — no planning, no tool calls |
| **Groq Dependency** | Single third-party API, daily token limits (100K/day), free-tier rate limits |
| **Local Vector Store** | ChromaDB on disk — not cloud-native, not shared across users |
| **No LangGraph** | Single-shot LLM calls — no conditional routing, no retries, no reasoning loops |
| **No MCP** | No structured tool exposure for calculators, code runners, graph plotters |
| **No Qdrant** | Inferior ChromaDB/FAISS with no advanced filtering, no hybrid search |
| **No CI/CD** | No GitHub Actions, no automated testing pipeline, no deployment automation |
| **No Observability** | No logging to cloud, no metrics, no tracing, no error monitoring |
| **eval() in Graph Plotter** | Direct eval() call on user input (Line 876) — critical security vulnerability |
| **No Docker** | Cannot containerize — no Dockerfile, no Cloud Run deployment |
| **LaTeX Not Rendered** | System prompt explicitly bans LaTeX — math is not displayed richly |
| **No Streaming Response** | LLM response appears all at once after full generation — poor UX |

## Suitability for Build with AI Hackathon

**Current Score: 3/10** — Technically functional but architecturally unsuitable for a hackathon about agentic AI. The project demonstrates RAG retrieval and LLM prompting but lacks agent architecture, Google AI ecosystem integration, and production engineering standards.

With proper transformation, it becomes a **9/10** submission: rich domain, compelling UX premise, genuine student impact, and a clear story for agentic AI in education.

---

# 2. Repository Analysis

## Current Architecture (ASCII Diagram)

```
Browser --> Streamlit (main.py L924) --> Session State
                    |
                    v
         MathAIEngine (line 666)
          |         |          |
          v         v          v
    LangChain   SymPy     MongoDBChatMemory
    + Groq      Engine    (line 525)
       |
       v
  MathVectorStore (line 287)
   ChromaDB / FAISS
       |
       v
  knowledge_base.py (6,121 lines, hardcoded)
```

## Tech Stack (As-Is)

| Layer | Technology | Version |
|---|---|---|
| Language | Python | 3.11+ |
| UI | Streamlit | >=1.32.0 |
| LLM | LLaMA 3.3 70B via Groq | langchain-groq >=0.1.0 |
| LLM Fallback | llama3-8b-8192, mixtral-8x7b-32768 | - |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 | ==2.7.0 (pinned) |
| Vector DB | ChromaDB (primary), FAISS (fallback) | chromadb>=0.4.0 |
| Orchestration | LangChain | 0.2.x (pinned) |
| Symbolic Math | SymPy | >=1.12 |
| Graphing | Plotly | >=5.0.0 |
| Chat Memory | MongoDB Atlas (pymongo) | >=4.0.0 |
| OCR | Tesseract + pytesseract | >=0.3.10 |
| Deployment | Streamlit Cloud | - |
| Auth | None | - |
| CI/CD | None | - |

## Dependency Graph

```
main.py
+-- knowledge_base.py          (data: 6,121 lines)
+-- langchain_core              (messages, documents, prompts)
+-- langchain_community         (PDF/web/markdown loaders)
+-- langchain_text_splitters    (RecursiveCharacterTextSplitter)
+-- langchain_groq              (ChatGroq LLM)
+-- langchain_huggingface       (HuggingFaceEmbeddings)
+-- chromadb                    (primary vector store)
+-- faiss-cpu                   (fallback vector store)
+-- sentence-transformers       (all-MiniLM-L6-v2)
+-- sympy                       (symbolic math)
+-- plotly                      (interactive graphs)
+-- pymongo + motor             (MongoDB memory)
+-- pypdf + unstructured        (PDF parsing)
+-- pillow + pytesseract        (OCR)
+-- streamlit                   (UI)
+-- numpy, scipy, matplotlib    (numerical)
```

## Folder Structure (Current)

```
Advanced Mathematics Assistant/
+-- main.py                 (2,745 lines — God Object)
+-- knowledge_base.py       (6,121 lines — hardcoded data)
+-- requirements.txt        (44 lines)
+-- packages.txt            (tesseract-ocr)
+-- runtime.txt             (python-3.11)
+-- env.example             (35 lines)
+-- .gitignore
+-- README.md               (309 lines)
+-- .devcontainer/
|   +-- devcontainer.json
+-- screenshots/
    +-- dark_mode.png
    +-- light_mode.png
```

**Total committed files: 10** (not counting .git)

## Backend Workflow (7 Steps in main.py)

1. **STEP 1 — Data Sources** (MathDataLoader, L80): Loads NCERT knowledge base from knowledge_base.py, optionally loads PDFs / web pages / text files.
2. **STEP 2 — Preprocessing** (MathDataPreprocessor, L156): Cleans text, deduplicates by MD5 hash, detects topic and difficulty.
3. **STEP 3 — Chunking** (MathTextSplitter, L232): Recursive character splitting. Chunk size 1000, overlap 200.
4. **STEP 4 — Vector Store** (MathVectorStore, L287): Stores chunks in ChromaDB or FAISS with process-level cache.
5. **STEP 5 — AI Engine** (MathAIEngine, L666): Single query() method that retrieves context → runs SymPy pre-check → calls Groq with fallback loop.
6. **STEP 6 — Streamlit UI** (run_streamlit_app, L924): 1,800+ lines including sidebar NCERT quiz, graph plotter, PDF upload, OCR scan.
7. **STEP 7 — Testing** (unittest classes, L2589): 5 test classes.

## AI Workflow

```
User Input
    |
    v
SymbolicMathEngine._symbolic_hint()   [regex pattern match]
    |
    v
MathVectorStore.similarity_search()   [ChromaDB cosine, k=3]
    |
    v
MongoDBChatMemory.get_langchain_messages() [last 4 messages]
    |
    v
Build messages: [System + context] + [history] + [HumanMessage]
    |
    v
Groq LLM (llama-3.3-70b-versatile)
  --> Retry 2x per model
  --> Fallback: llama3-8b-8192 --> mixtral-8x7b-32768
    |
    v
Return {answer, sources, symbolic_hint, session_id}
```

## API Flow

- **No REST API** — Everything is Streamlit session state
- **Groq API** — POST to api.groq.com
- **MongoDB Atlas** — pymongo MongoClient
- **HuggingFace** — Local model inference (CPU only)
- **ChromaDB** — Local SQLite files in ./chroma_db/

## Deployment Flow

```
Developer --> git push --> GitHub
                            |
                     Streamlit Cloud (auto-deploy)
                            |
                     python -m streamlit run main.py
                     Downloads HF model on cold start (~100MB)
                     Builds ChromaDB in-memory (ephemeral!)
```

**CRITICAL**: ChromaDB cannot persist between Streamlit Cloud deploys. Vector store is rebuilt on every cold start (30-60 second delay).

## Authentication Flow

**NONE.** Zero authentication. All users share the same anonymous session.

## Database Flow

```
MongoDB Atlas:
  Collection: chat_history
  Document: {session_id, role, content, timestamp}

ChromaDB (local):
  Collection: math_knowledge_base
  Metadata filters: topic, class_level, chapter, exercise

FAISS (fallback):
  Index file: ./faiss_index/
  No metadata filtering
```

## Current Mathematical Engine

| Capability | Implementation | Limitation |
|---|---|---|
| Differentiation | sympy.diff | Single variable only |
| Integration | sympy.integrate | Indefinite only |
| Equation Solving | sympy.solve | Single equation, single variable |
| Simplification | sympy.simplify | Expression only |
| Matrix Operations | sympy.Matrix | det, rank, eigenvals, trace |
| Graph Plotting | numpy + plotly | Static functions of x only |
| OCR | Tesseract --psm 6 | No LaTeX recognition |

## Current Prompting Mechanism

- **System prompt** (SYSTEM_TEMPLATE, L404): 120-line teacher persona prompt
- Enforces whiteboard-style formatting (steps, not paragraphs)
- Unicode math symbols only (no LaTeX/MathJax — explicitly banned)
- Level detection for Class 1-5, 6-8, 9-10, 11-12, JEE
- Non-math rejection guard
- Context injected via string `.replace("{context}", context)` (NOT format_messages() — avoids curly-brace crashes from math notation)

## Git History Summary

- 20+ commits, active development from March–June 2026
- Single contributor: Sarika Jivrajika
- Rapid iteration pattern (v2 → v3 → v3.2 within 2 months)
- Most recent: Added DevContainer (Jun 3, 2026)
- Peak activity: April 2026 (knowledge base expansion + UI overhaul)

---

# 3. Feature Gap Analysis

## Production Readiness Gaps

| Gap | Current | Required |
|---|---|---|
| User Authentication | None | Firebase Auth (Google Sign-In) |
| User Profiles | None | Firestore per-user documents |
| Progress Tracking | Session-only streak | Persistent cross-session analytics |
| Error Monitoring | logging to stdout | Cloud Logging, structured logs |
| Health Endpoint | None | /health with DB connectivity check |
| Secrets Management | Streamlit Secrets / .env | GCP Secret Manager |
| Rate Limiting | None | Per-user per-minute quotas |
| Input Validation | Minimal (math PDF check) | Pydantic models, sanitization |
| CI/CD | None | GitHub Actions |
| Database Migrations | None | Firestore schema versioning |

## Agent Capability Gaps

| Agent Capability | Current | Required |
|---|---|---|
| Planning | None | Planner decomposes multi-step problems |
| Memory | 4-message in-memory window | Long-term Firestore/Qdrant memory |
| Reasoning | Single LLM call | Multi-step CoT with LangGraph |
| Tool Calling | Hardcoded SymPy | Structured MCP tool registry |
| Verification | None | Verification agent cross-checks |
| Retrieval | ChromaDB k=3 | Hybrid dense+sparse via Qdrant |
| Self-Correction | None | Agent detects errors and retries |
| Human-in-Loop | 👍/👎 buttons (no backend) | Feedback stored for RLHF signals |

## Missing Infrastructure

| Component | Gap |
|---|---|
| Docker | No Dockerfile |
| CI/CD | No GitHub Actions |
| Cloud Run | No containerized deployment |
| Firebase Hosting | No hosting config |
| Monitoring | No Cloud Monitoring |
| Qdrant | Replaced by inferior local ChromaDB |
| LaTeX Renderer | No KaTeX/MathJax |
| Streaming | No SSE token streaming |

---

# 4. Google AI Integration Opportunities

## 4.1 Gemini Models

**Why**: Replace Groq/LLaMA with Google's flagship model family. Gemini 2.0 Flash offers 1M context window, native multimodal input (eliminates Tesseract OCR for images), and free tier via AI Studio.

**Where**:
- MathAIEngine → GeminiMathEngine
- Image input for camera scan → native Gemini Vision (no Tesseract needed)
- Gemini 2.0 Flash Thinking for complex JEE proofs
- Gemini 1.5 Flash for fast NCERT question answering

**Benefits**: Native multimodal, superior math reasoning, free tier 1M tokens/day (vs Groq 30K/day for LLaMA 3.3), Google ecosystem alignment for judges.

**Implementation Complexity**: Low (langchain-google-genai package)

## 4.2 Vertex AI

**Why**: Production-grade model serving, prompt management with version control, safety filters, model evaluation pipeline.

**Where**: Model registry for prompt templates, safety filters, evaluation pipeline, Cloud Logging for observability.

**Benefits**: Prompt versioning/A/B testing, automatic safety filtering (important in student context), SLA-backed serving.

**Implementation Complexity**: Medium

## 4.3 Firebase

**Why**: Complete BaaS solution handling auth, database, hosting, and analytics — all free-tier available, all Google-native.

**Where**:
- Firebase Auth: Google Sign-In for students and teachers
- Firestore: User profiles, chat history (replaces MongoDB), progress tracking
- Firebase Hosting: Static frontend assets
- Cloud Functions: Webhook handlers, scheduled RAG rebuilds
- Firebase Analytics: Usage metrics, learning analytics

**Benefits**: Replaces MongoDB (simpler, Google-native), student login enables personalization and progress tracking.

**Implementation Complexity**: Medium

## 4.4 Cloud Run

**Why**: Serverless containerized deployment that scales to zero and to thousands of concurrent users. Replaces Streamlit Cloud.

**Where**: FastAPI backend service, ADK agent service, MCP server deployments.

**Benefits**: Auto-scaling (handles hackathon traffic spikes), pay-per-use free tier (2M requests/month, 360K vCPU-seconds), proper HTTP API architecture.

**Implementation Complexity**: Medium

## 4.5 Google AI Studio

**Why**: Free access to Gemini models for prototyping and prompt engineering during development.

**Implementation Complexity**: Very Low (API key only)

## 4.6 Google Agent Development Kit (ADK)

**Why**: Google's official framework for building production-quality multi-agent systems. Directly demonstrates the "Build with AI" theme to judges.

**Where**:
- PlannerAgent: Decomposes user questions into sub-tasks
- MathSolverAgent: Core solving logic with MCP tool access
- VerificationAgent: Cross-checks answers for correctness
- RetrieverAgent: Manages Qdrant semantic search
- MemoryAgent: Long-term user memory management

**Benefits**: Official Google framework, maximum hackathon relevance, built-in observability and debugging.

**Implementation Complexity**: High (architectural refactor)

## 4.7 Model Context Protocol (MCP)

**Why**: Industry-standard tool protocol that exposes capabilities as structured tools callable by any AI agent.

**Where**: Calculator, Python executor, LaTeX renderer, graph plotter, PDF reader, unit converter, SymPy server.

**Benefits**: Decouples tools from agent logic, tools become reusable across any agent.

**Implementation Complexity**: Medium

---

# 5. AI Agent Architecture

## Agent System Overview (ASCII)

```
User Input (text/image/PDF)
        |
        v
  ORCHESTRATOR (ADK AgentRunner)
        |
   PLANNER AGENT
   - Classify question type
   - Detect class level (6-12, JEE)
   - Decompose multi-part problems
   - Route to appropriate agent
   Model: Gemini 2.0 Flash
        |
   +----+----+
   |         |
RETRIEVER  MEMORY
 AGENT      AGENT
 Qdrant    Firestore
 Hybrid    User ctx
 Search    History
   |         |
   +----+----+
        |
   MATH SOLVER AGENT
   - Context + user query
   - Calls MCP tools (SymPy/Python)
   - Generates whiteboard answer
   - Produces LaTeX + plaintext
   Model: Gemini 2.0 Flash Thinking (JEE)
          Gemini 1.5 Flash (NCERT)
        |
   VERIFICATION AGENT
   - Re-solves independently
   - Compares with SymPy result
   - Flags discrepancies
   - Adds confidence score
   Model: Gemini 1.5 Flash
        |
   RESPONSE FORMATTER
   - Render LaTeX (KaTeX)
   - Format whiteboard steps
   - Save to Firestore
   - Update user progress
        |
   HUMAN FEEDBACK LOOP
   👍 / 👎 / Doubt / Different approach
   Stored in Firestore for future signals
```

## Agent Specifications

### Planner Agent
- **Model**: Gemini 2.0 Flash
- **Input**: Raw user query + session context
- **Output**: Structured task `{type, class_level, topics, sub_tasks, routing}`
- **Classifies into**: ncert_exercise | concept_query | multi_part | image_problem | symbolic_compute

### Math Solver Agent
- **Model**: Gemini 2.0 Flash Thinking (JEE) / Gemini 1.5 Flash (NCERT)
- **Tools via MCP**: SymPy calculator, Python executor, graph plotter
- **Output**: `{steps[], final_answer, latex, plaintext, confidence}`

### Verification Agent
- **Model**: Gemini 1.5 Flash
- **Task**: Independently verify using SymPy. If discrepancy → flag → re-route Solver with error context.
- **Output**: `{verified: bool, confidence: float, corrections: []}`

### Retriever Agent
- **Backend**: Qdrant Cloud
- **Strategy**: Dense (text-embedding-004) + Sparse (BM25) hybrid
- **Filters**: class_level, chapter, topic, exercise, difficulty

### Memory Agent
- **Backend**: Firestore (short-term) + Qdrant (long-term semantic)
- **Short-term**: Last 10 conversation turns per session
- **Long-term**: User's weak topics, completed exercises, streak, preferences

## LangGraph State

```python
class MathAgentState(TypedDict):
    user_id: str
    session_id: str
    raw_query: str
    query_type: str
    class_level: str
    retrieved_docs: list
    user_context: dict
    solver_answer: dict
    verification_result: dict
    final_response: str
    feedback: Optional[str]
    error: Optional[str]
    retry_count: int
```

---

# 6. LangGraph Workflow

## Main Reasoning Graph (ASCII)

```
START
  |
  v
classify_question   [Gemini: type, level, complexity]
  |
  +-> [ncert_exercise] --> retrieve_ncert_context
  +-> [image_input]    --> process_image (Gemini Vision)
  +-> [symbolic]       --> run_mcp_sympy
  +-> [general]        --> retrieve_general_context
  |
  v [all paths merge]
parallel_retrieval   [Qdrant search || Memory fetch, concurrent]
  |
  v
route_by_level
  +-> [Class 6-8]   --> solve_basic  (Gemini 1.5 Flash)
  +-> [Class 9-10]  --> solve_ncert  (Gemini 1.5 Flash)
  +-> [Class 11-12] --> solve_senior (Gemini 2.0 Flash)
  +-> [JEE]         --> solve_jee    (Gemini 2.0 Flash Thinking)
  |
  v [all solver paths merge]
verify_answer   [SymPy cross-check + Gemini verification]
  |
  +-> [verified=True]  --> format_response
  +-> [verified=False] --> self_correct --> verify_answer (max 2 retries)
  |
  v
format_response   [LaTeX + plaintext + difficulty badge]
  |
  v
parallel_persist   [Firestore save || Qdrant upsert]
  |
  v
END
  |
  v [async, user-triggered]
collect_feedback  [👍/👎/❓/🔁 --> Firestore]
```

## Retry & Fallback Logic

```python
def should_retry(state: MathAgentState) -> str:
    if state["verification_result"]["verified"]:
        return "format_response"
    if state["retry_count"] >= 2:
        return "format_response_with_warning"
    return "self_correct"
```

---

# 7. Firebase Architecture

## Authentication

```
Firebase Auth
+-- Providers: Google Sign-In (primary), Email/Password (fallback)
+-- Custom Claims: {role: "student"|"teacher", class_level: "10"}
+-- Security Rules: Users can only read/write their own Firestore docs
+-- Session: ID tokens refreshed automatically
```

## Firestore Schema

```
firestore/
+-- users/{userId}/
|   +-- profile: {name, email, class_level, created_at}
|   +-- preferences: {theme, language}
|   +-- stats: {streak, total_solved, last_active}
|
+-- sessions/{sessionId}/
|   +-- user_id, created_at
|   +-- messages/{messageId}/
|       +-- role: "user"|"assistant"
|       +-- content, latex, sources, feedback, timestamp
|
+-- progress/{userId}/{classLevel}/{chapterId}/
|   +-- completed_exercises, weak_topics, last_attempted
|
+-- feedback/{feedbackId}/
    +-- user_id, session_id, message_id
    +-- type: "helpful"|"unhelpful"|"incorrect", timestamp
```

## Cloud Functions

```
functions/
+-- onUserCreate       --> Initialize Firestore user document
+-- scheduledRagRebuild --> Cron: rebuild Qdrant index weekly
+-- cleanOldSessions   --> Delete sessions older than 90 days
```

---

# 8. Vertex AI Integration

## Prompt Management
- All prompts stored in Vertex AI Prompt Registry with version history
- System prompts versioned (e.g., math-tutor-v2, verification-v1)
- A/B testing between prompt versions via Vertex AI Experiments
- Rollback capability if new prompt version degrades quality

## Safety Configuration

```python
safety_settings = [
    SafetySetting(HARM_CATEGORY_HATE_SPEECH, threshold="BLOCK_MEDIUM_AND_ABOVE"),
    SafetySetting(HARM_CATEGORY_DANGEROUS_CONTENT, threshold="BLOCK_LOW_AND_ABOVE"),
    SafetySetting(HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold="BLOCK_LOW_AND_ABOVE"),
]
```

## Model Selection Strategy

| Use Case | Model | Reason |
|---|---|---|
| NCERT Class 6-10 | Gemini 1.5 Flash | Fast, cheap, sufficient |
| NCERT Class 11-12 | Gemini 2.0 Flash | Better reasoning |
| JEE Advanced proofs | Gemini 2.0 Flash Thinking | Extended reasoning |
| Planner/Classifier | Gemini 1.5 Flash | Low latency |
| Verification | Gemini 1.5 Flash | Cross-check only |
| Embeddings | text-embedding-004 | Google-native, 768-dim |

## Evaluation Pipeline
- **Offline**: LLM-as-judge scoring answers for correctness, clarity, level-appropriateness
- **Online**: A/B experiment tracking via Vertex AI Experiments
- **RAG**: Retrieval precision@k, recall@k tracked per commit

---

# 9. Qdrant Integration

## Why Qdrant Over ChromaDB

| Criterion | ChromaDB (current) | Qdrant (target) |
|---|---|---|
| Cloud hosting | No | Yes (Qdrant Cloud free tier) |
| Hybrid search | No | Yes (dense + sparse BM25) |
| Payload filtering | Limited | Full JSON filter support |
| Performance at scale | <100K vectors OK | Millions of vectors |
| Persistence | Local SQLite | Cloud-native |
| Multitenancy | None | Collections per user/class |

## Collections Design

```
Qdrant Collections:
+-- math_knowledge_base     [NCERT content, shared]
|   Vectors: text-embedding-004 (768-dim)
|   Payload: {source, class_level, chapter, exercise, topic, difficulty}
|
+-- user_solved_problems    [per-user solved problems]
|   Vectors: query embeddings
|   Payload: {user_id, solved_at, confidence, feedback}
|
+-- theorem_library         [mathematical theorems/formulas]
    Vectors: text-embedding-004
    Payload: {theorem_name, area, class_level, proof_required}
```

## Hybrid Search

```python
results = client.query_points(
    collection_name="math_knowledge_base",
    prefetch=[
        Prefetch(query=dense_embedding, using="dense", limit=20),
        Prefetch(query=sparse_vector, using="sparse", limit=20),
    ],
    query=FusionQuery(fusion=Fusion.RRF),  # Reciprocal Rank Fusion
    limit=5,
    query_filter={"class_level": "class_10", "chapter": "ch6"},
)
```

---

# 10. MCP Integration

## MCP Server Architecture

```
MCP Servers (each runs as Cloud Run service):

+-- calculator-mcp       (Port 8010)
|   Tools: evaluate_expression, unit_convert, percentage_calc
|
+-- sympy-mcp            (Port 8011)
|   Tools: differentiate, integrate, solve_equation, simplify,
|          matrix_operations, expand_expression, factor_expression
|
+-- python-executor-mcp  (Port 8012)
|   Tools: run_python_code (sandboxed, math libraries only)
|
+-- graph-plotter-mcp    (Port 8013)
|   Tools: plot_function, plot_parametric, plot_3d, plot_scatter
|
+-- latex-compiler-mcp   (Port 8014)
|   Tools: render_latex_to_svg, validate_latex_expression
|
+-- pdf-reader-mcp       (Port 8015)
|   Tools: extract_text, extract_math_expressions, summarize_pdf
|
+-- image-solver-mcp     (Port 8016)
|   Tools: extract_math_from_image (Gemini Vision native)
|
+-- ncert-search-mcp     (Port 8017)
    Tools: search_exercise, get_chapter_summary, list_exercises
```

## MCP Tool Definition Example

```python
from mcp import FastMCP

mcp = FastMCP("sympy-math")

@mcp.tool()
def differentiate(expression: str, variable: str = "x") -> dict:
    """Differentiate a mathematical expression symbolically."""
    import sympy as sp
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

## Technology Shift: Streamlit → FastAPI + React

The Streamlit UI cannot support: real-time streaming, LaTeX rendering (KaTeX/MathJax), interactive notebook mode, PWA offline support, or a proper mobile experience.

### Target Frontend Stack

```
Frontend: React + Vite
+-- KaTeX    (LaTeX math rendering)
+-- Recharts (interactive graphs)
+-- Zustand  (client state)
+-- Firebase SDK (auth + Firestore real-time)

Backend: FastAPI
+-- /api/v1/chat       (streaming SSE)
+-- /api/v1/upload     (PDF/image)
+-- /api/v1/progress   (analytics)
+-- /api/v1/search     (Qdrant direct)
```

## Feature Improvements

| Feature | Current | Improved |
|---|---|---|
| Math Rendering | Plain Unicode | KaTeX renders beautiful LaTeX |
| Response | All-at-once | Streaming tokens (SSE) |
| Graphs | Plotly in sidebar | Interactive Recharts inline |
| History | Session only | Persistent, searchable, shareable |
| Notebook Mode | None | Jupyter-style editable cells |
| Progress Dashboard | None | Streak calendar, topic mastery charts |
| Teacher View | None | Class-level aggregate analytics |
| Mobile | Partially responsive | PWA with offline mode |
| Accessibility | None | WCAG 2.1 AA compliance |

---

# 12. Deployment

## Target Architecture (ASCII)

```
GitHub Actions CI/CD Pipeline
        |
        v
Build + Test + Push to GCP Artifact Registry
        |
        +-> Cloud Run: API Service (FastAPI)
        |        +-- /api/v1/chat (ADK agents)
        |        +-- /api/v1/upload
        |        +-- Scales 0-N instances automatically
        |
        +-> Firebase Hosting: Frontend (React)
        |        +-- CDN-distributed globally
        |
        +-> Cloud Run: MCP Servers (8 services)

External Services:
+-- Qdrant Cloud (vector store)
+-- Firebase Auth + Firestore
+-- Vertex AI (Gemini + embeddings)
+-- GCP Secret Manager (API keys)
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

## CI/CD (GitHub Actions)

```yaml
on:
  push:
    branches: [main]
jobs:
  test:
    steps:
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v --cov=src
  deploy:
    needs: test
    steps:
      - uses: google-github-actions/auth@v2
      - run: gcloud run deploy math-agent-api --source . --region us-central1
```

## Secrets Strategy

```
GCP Secret Manager (all API keys):
  GEMINI_API_KEY, FIREBASE_ADMIN_SDK_JSON, QDRANT_URL, QDRANT_API_KEY

Cloud Run Environment Variables (non-secret):
  ENVIRONMENT=production
  GCP_PROJECT_ID=math-assistant-prod
  VERTEX_AI_LOCATION=us-central1
```

---

# 13. Security Improvements

## Critical Vulnerability Fix (Phase 0 Priority)

**Current Risk** (main.py Line 876):
```python
y = eval(re.sub(r'\^', '**', expr), ns)  # UNSAFE
```

**Safe Fix** using SymPy:
```python
import sympy as sp
safe_expr = sp.sympify(re.sub(r'\^', '**', expr))
f = sp.lambdify(sp.Symbol('x'), safe_expr, modules=['numpy'])
y = f(x)  # SAFE: no arbitrary code execution
```

## Full Security Hardening

| Category | Implementation |
|---|---|
| Authentication | Firebase Auth with email verification |
| Authorization | Firestore Security Rules per user |
| Rate Limiting | Firebase App Check + Cloud Armor |
| Prompt Injection | Input validation + Gemini safety filters |
| Secrets | GCP Secret Manager (no .env in production) |
| Input Sanitization | Pydantic models for all API inputs |
| HTTPS | Enforced via Firebase Hosting + Cloud Run |
| CORS | Whitelist-only CORS on FastAPI |
| Dependency Scanning | Dependabot + pip-audit in CI |
| Container Security | Non-root user, read-only filesystem |

---

# 14. Performance Optimizations

## Caching Strategy

```
Request Cache (Cloud Memorystore / Redis):
+-- Embedding cache: hash(query) --> vector (avoid re-embedding)
+-- Response cache: hash(query + context) --> answer (30 min TTL)
+-- Qdrant cloud: always warm (no cold start)

Application Cache:
+-- LangChain callback cache (LLM response dedup)
```

## Streaming

```python
@app.get("/api/v1/chat/stream")
async def chat_stream(query: str, user_id: str):
    async def generate():
        async for chunk in gemini_agent.astream(query):
            yield f"data: {chunk.content}\n\n"
    return StreamingResponse(generate(), media_type="text/event-stream")
```

## Parallel Execution

```python
# Retriever + Memory fetch concurrently
graph.add_node("parallel_retrieval", RunnableParallel({
    "qdrant_docs": retriever_agent,
    "user_context": memory_agent,
}))
```

## Agent Optimization

- Gemini 1.5 Flash for quick tasks (5-10x cheaper than Pro)
- Cache identical queries by hash(query + class_level)
- Lazy MCP tool loading (only load server when needed)
- Pre-index all 505 NCERT questions at startup in Qdrant

---

# 15. Folder Structure Proposal

```
Advanced Mathematics Assistant/
|
+-- .github/
|   +-- workflows/
|       +-- ci.yml              [test + lint on PR]
|       +-- deploy.yml          [deploy to Cloud Run on main]
|
+-- backend/                    [FastAPI + ADK agents]
|   +-- Dockerfile
|   +-- requirements.txt
|   +-- src/
|   |   +-- main.py             [FastAPI app entry]
|   |   +-- api/v1/
|   |   |   +-- chat.py         [/chat endpoint - streaming]
|   |   |   +-- upload.py       [/upload - PDF/image]
|   |   |   +-- progress.py     [/progress - user analytics]
|   |   |   +-- search.py       [/search - Qdrant direct]
|   |   +-- agents/             [ADK multi-agent system]
|   |   |   +-- orchestrator.py
|   |   |   +-- planner_agent.py
|   |   |   +-- math_solver_agent.py
|   |   |   +-- verification_agent.py
|   |   |   +-- retriever_agent.py
|   |   |   +-- memory_agent.py
|   |   +-- graph/              [LangGraph workflow]
|   |   |   +-- math_graph.py   [main StateGraph]
|   |   |   +-- state.py        [MathAgentState TypedDict]
|   |   |   +-- nodes/
|   |   |       +-- classify.py, retrieve.py, solve.py, verify.py, format.py
|   |   +-- services/
|   |   |   +-- gemini_service.py   [Vertex AI / Gemini]
|   |   |   +-- qdrant_service.py   [Qdrant operations]
|   |   |   +-- firebase_service.py [Firestore + Auth admin]
|   |   |   +-- embedding_service.py [text-embedding-004]
|   |   +-- math/
|   |       +-- symbolic_engine.py  [SymPy - extracted from main.py]
|   |       +-- knowledge_indexer.py [Qdrant ingestion pipeline]
|   +-- tests/
|       +-- test_agents.py, test_graph.py, test_api.py, test_symbolic_engine.py
|
+-- mcp-servers/                [Model Context Protocol tools]
|   +-- sympy-mcp/
|   |   +-- Dockerfile, server.py, requirements.txt
|   +-- calculator-mcp/
|   +-- graph-plotter-mcp/
|   +-- pdf-reader-mcp/
|   +-- python-executor-mcp/
|   +-- image-solver-mcp/
|
+-- frontend/                   [React + Vite]
|   +-- src/
|   |   +-- components/
|   |   |   +-- Chat/ (ChatWindow, MessageBubble with KaTeX, StreamingMessage)
|   |   |   +-- NCERT/ (QuizPanel, QuestionCard)
|   |   |   +-- Math/ (GraphRenderer, LatexDisplay)
|   |   |   +-- Progress/ (StreakCalendar, TopicMastery)
|   |   |   +-- Auth/ (GoogleSignIn)
|   |   +-- hooks/ (useAuth, useChat, useProgress)
|   |   +-- store/ (chatStore Zustand)
|   +-- vite.config.ts, package.json
|
+-- knowledge-base/             [Migrated from knowledge_base.py]
|   +-- ncert/class_6/ ... class_12/ (*.md per chapter)
|   +-- jee/topics/*.md
|   +-- indexer.py              [Qdrant ingestion script]
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

> **CRITICAL**: Each phase requires explicit approval before the next phase begins.
> Never work on multiple phases simultaneously. Never assume approval.

---

## Phase 0 — Repository Audit & Security Fix

**Objectives**:
- Fix the critical eval() security vulnerability (main.py L876)
- Extract unit tests from main.py into standalone test files
- Document all existing code with inline comments
- Establish proper .gitignore and project configuration
- Create CHANGELOG.md

**Files Affected**:
- main.py (eval → SymPy fix on L876)
- requirements.txt (pin versions, add dev dependencies)
- .gitignore (add chroma_db/, faiss_index/, *.pyc, .env)
- Create tests/ directory
- Create CHANGELOG.md

**Estimated Effort**: 0.5 days

**Dependencies**: None — can start immediately after approval

**Risks**:
- sympify() + lambdify() may not cover all edge cases that eval() handled → need comprehensive math function coverage test

**Testing Checklist**:
- [ ] Graph plotter renders sin(x), x**2, log(x), sqrt(x) correctly
- [ ] Graph plotter cannot execute arbitrary Python
- [ ] All existing unit tests pass
- [ ] Coverage report generated

**Acceptance Criteria**:
- eval() removed from graph plotter
- All 5 existing test classes pass
- Security vulnerability documented and closed

**Rollback Strategy**: Git revert to commit before Phase 0 — single commit, trivially reversible

---

## Phase 1 — Architecture Refactoring

**Objectives**:
- Decompose main.py (2,745 lines) into logical modules
- Extract all business logic from Streamlit UI layer
- Set up FastAPI backend skeleton with /health and /api/v1/chat
- Keep Streamlit frontend functional during migration

**Files Affected**:
- main.py → split into backend/src/math/, backend/src/services/, backend/src/api/
- New: backend/Dockerfile
- New: docker-compose.yml

**Estimated Effort**: 2 days

**Dependencies**: Phase 0 complete

**Risks**: Streamlit session_state tightly coupled to UI rendering — extracting logic requires careful dependency tracking

**Testing Checklist**:
- [ ] FastAPI /health returns 200
- [ ] FastAPI /api/v1/chat returns correct response for "solve x^2-4=0"
- [ ] All original unit tests pass against new module structure
- [ ] Streamlit UI still functional with refactored backend

**Acceptance Criteria**:
- main.py reduced to UI-only code (<500 lines)
- FastAPI server starts and handles basic math queries
- Docker Compose starts both services

**Rollback Strategy**: Git revert Phase 1 commits; original main.py preserved in git history

---

## Phase 2 — Gemini Integration

**Objectives**:
- Replace Groq/LLaMA with Google Gemini models
- Implement native Gemini Vision for image input (eliminates Tesseract OCR)
- Add streaming response support (SSE from FastAPI)
- Update system prompt to enable LaTeX output

**Files Affected**:
- backend/src/services/gemini_service.py (NEW)
- backend/src/api/v1/chat.py (streaming endpoint)
- requirements.txt (add google-generativeai, langchain-google-genai)
- env.example (add GEMINI_API_KEY, remove GROQ_API_KEY)

**Estimated Effort**: 1.5 days

**Dependencies**: Phase 1 complete, Google AI Studio account with API key

**Risks**:
- Gemini response format differs from Groq — need adapter layer
- Free tier: 15 RPM — may cause issues under demo load
- LaTeX output requires frontend KaTeX renderer

**Testing Checklist**:
- [ ] Gemini 2.0 Flash responds to "solve 2x+3=7" with correct format
- [ ] Gemini Vision correctly extracts math from a test image
- [ ] Streaming SSE delivers tokens progressively
- [ ] Fallback to Gemini 1.5 Flash on rate limit works

**Acceptance Criteria**:
- Zero Groq API calls in production code paths
- Image math extraction works without Tesseract
- Streaming response visible via curl -N

**Rollback Strategy**: Feature flag USE_GEMINI=false falls back to Groq client

---

## Phase 3 — Firebase Integration

**Objectives**:
- Implement Firebase Auth (Google Sign-In)
- Replace MongoDB with Firestore for chat history
- Migrate daily streak to Firestore (persistent across sessions)
- Add user profiles and progress tracking schema
- Protect API endpoints with Firebase Auth middleware

**Files Affected**:
- backend/src/services/firebase_service.py (NEW)
- backend/src/api/middleware/auth.py (NEW)
- backend/src/api/v1/progress.py (NEW)
- firebase/firestore.rules (NEW)
- requirements.txt (add firebase-admin, remove pymongo/motor)

**Estimated Effort**: 2 days

**Dependencies**: Phase 2 complete, Firebase project created

**Risks**:
- Firestore free tier: 50K reads/day — monitor at scale
- Firebase Admin SDK requires service account (secret management needed)
- Anonymous sessions need migration path

**Testing Checklist**:
- [ ] Google Sign-In flow completes and creates Firestore user document
- [ ] Chat messages stored/retrieved from Firestore with correct user_id scoping
- [ ] Unauthenticated API request returns 401
- [ ] Streak persists across browser sessions for authenticated user
- [ ] Firestore Security Rules prevent cross-user data access

**Acceptance Criteria**:
- User can sign in with Google and see persistent chat history
- MongoDB dependency removed from requirements.txt
- Security Rules pass all tests in Firebase Emulator

**Rollback Strategy**: USE_FIREBASE=false falls back to in-memory/MongoDB

---

## Phase 4 — Google ADK Multi-Agent System

**Objectives**:
- Implement Planner, Math Solver, Verification, Retriever, Memory agents using ADK
- Replace single MathAIEngine.query() with multi-agent pipeline
- Add agent observability (ADK tracing)
- Implement human feedback loop with Firestore storage

**Files Affected**:
- backend/src/agents/ directory (ALL NEW)
- backend/src/api/v1/chat.py (route through orchestrator)
- requirements.txt (add google-adk)

**Estimated Effort**: 3 days (most complex phase)

**Dependencies**: Phase 3 complete

**Risks**:
- ADK is relatively new — API may change
- Multi-agent adds ~2-3s latency (3 agent calls instead of 1)
- Verification agent overhead must be measured

**Testing Checklist**:
- [ ] Planner classifies "solve x^2+5x+6=0" correctly
- [ ] Verification agent catches "4+4=9" and corrects it
- [ ] End-to-end latency <10s for Class 10 question
- [ ] ADK tracing shows full agent call chain
- [ ] Memory agent retrieves user's previous weak topics

**Acceptance Criteria**:
- All 5 agents operational and communicating via ADK
- Single MathAIEngine.query() replaced by ADK orchestration
- Agent trace visible in dashboard for every request

**Rollback Strategy**: USE_ADK=false routes to legacy single-agent path

---

## Phase 5 — LangGraph Workflow

**Objectives**:
- Implement full reasoning state machine using LangGraph
- Add conditional routing (by class level, question type)
- Implement retry-with-self-correction loop (max 2 retries)
- Add parallel retrieval (Qdrant + Firestore in parallel)
- LangGraph tracing via LangSmith or Cloud Logging

**Files Affected**:
- backend/src/graph/ directory (ALL NEW): math_graph.py, state.py, nodes/
- requirements.txt (add langgraph, langsmith)

**Estimated Effort**: 2.5 days

**Dependencies**: Phase 4 (ADK agents as graph nodes)

**Risks**:
- LangGraph async compatibility with ADK must be verified
- Graph visualization requires LangSmith API key
- Retry loop may cause 3x latency on failures

**Testing Checklist**:
- [ ] Graph correctly routes JEE question to solve_jee node
- [ ] Retry loop fires when verification fails
- [ ] Parallel retrieval completes in <2s
- [ ] LangGraph trace visible for full conversation turn

**Acceptance Criteria**:
- Full StateGraph with all nodes and edges defined
- At least one trace visible in tracing tool
- Graph handles 3 different question types correctly

**Rollback Strategy**: USE_LANGGRAPH=false routes through ADK orchestrator directly

---

## Phase 6 — Qdrant Integration

**Objectives**:
- Replace ChromaDB/FAISS with Qdrant Cloud
- Migrate all knowledge base content to structured Markdown → Qdrant
- Implement hybrid search (dense + sparse)
- Add metadata-based filtering (class, chapter, topic)

**Files Affected**:
- backend/src/services/qdrant_service.py (NEW)
- backend/src/math/knowledge_indexer.py (NEW)
- knowledge-base/ directory (NEW — structured Markdown)
- backend/src/services/embedding_service.py (switch to text-embedding-004)
- Remove chromadb, faiss-cpu from requirements

**Estimated Effort**: 2 days

**Dependencies**: Phase 5

**Risks**:
- Qdrant Cloud free tier: 1GB (sufficient, but monitor)
- Embedding switch changes vector space — full re-index needed
- BM25 sparse vectors need separate implementation

**Testing Checklist**:
- [ ] All 505 NCERT exercises indexed in Qdrant
- [ ] Search for "Basic Proportionality Theorem" returns Class 10 Ch6
- [ ] Metadata filter narrows results correctly
- [ ] Hybrid search outperforms pure dense on keyword-heavy queries

**Acceptance Criteria**:
- ChromaDB removed from codebase
- All knowledge base accessible via Qdrant with metadata filters
- Retrieval precision@5 >= 0.8 on 20-question test set

**Rollback Strategy**: VECTOR_DB=qdrant|chroma env var switches backend

---

## Phase 7 — Vertex AI Integration

**Objectives**:
- Migrate Gemini API calls from AI Studio to Vertex AI
- Implement prompt management in Vertex AI Prompt Registry
- Add Vertex AI safety filters
- Set up evaluation pipeline (LLM-as-judge)
- Integrate Cloud Logging for structured observability

**Files Affected**:
- backend/src/services/gemini_service.py (update to Vertex AI SDK)
- backend/src/services/evaluation_service.py (NEW)
- requirements.txt (add google-cloud-aiplatform)

**Estimated Effort**: 1.5 days

**Dependencies**: Phase 6, GCP project with Vertex AI enabled

**Risks**:
- GCP billing — set budget alert at $5 for hackathon
- IAM permissions complexity — service account needs Vertex AI User role

**Testing Checklist**:
- [ ] Gemini call goes through Vertex AI endpoint (verify in GCP Console)
- [ ] Safety filter blocks "explain how to cheat on exams"
- [ ] Prompt template retrieved from Vertex AI Prompt Registry at runtime
- [ ] Cloud Logging shows structured agent traces
- [ ] Evaluation pipeline scores 5 sample questions

**Acceptance Criteria**:
- All Gemini API calls routed through Vertex AI
- Structured logs visible in Cloud Logging for every agent call
- Safety filter actively tested and documented

**Rollback Strategy**: VERTEX_AI_ENABLED=false falls back to direct Gemini API

---

## Phase 8 — Cloud Run Deployment

**Objectives**:
- Deploy FastAPI backend to Cloud Run
- Deploy MCP servers to Cloud Run
- Set up Firebase Hosting for React frontend
- Configure GitHub Actions CI/CD pipeline
- Set up GCP Secret Manager for all API keys

**Files Affected**:
- Dockerfile (backend)
- mcp-servers/*/Dockerfile
- .github/workflows/ci.yml (NEW)
- .github/workflows/deploy.yml (NEW)
- firebase/firebase.json (hosting config)

**Estimated Effort**: 2 days

**Dependencies**: Phase 7 complete

**Risks**:
- Cloud Run cold start with ML dependencies — ensure embedding via Vertex AI API (not local)
- CORS configuration between Firebase Hosting and Cloud Run domains

**Testing Checklist**:
- [ ] docker build succeeds in <5 minutes
- [ ] Cloud Run service returns 200 on /health
- [ ] Frontend loads from Firebase Hosting with no console errors
- [ ] Full chat flow works end-to-end in production URL
- [ ] CI pipeline blocks merge on test failure

**Acceptance Criteria**:
- Live production URL (not localhost, not Streamlit Cloud)
- GitHub Actions green badge on main branch
- All API keys in Secret Manager (zero hardcoded credentials)

**Rollback Strategy**: Cloud Run traffic splitting: gcloud run services update-traffic --to-revisions PREV=100

---

## Phase 9 — MCP Servers

**Objectives**:
- Implement and deploy all 6 MCP servers
- Connect ADK agents to MCP tool registry
- Test each tool end-to-end
- Add sandboxed Python executor

**Files Affected**:
- mcp-servers/sympy-mcp/server.py (NEW)
- mcp-servers/calculator-mcp/server.py (NEW)
- mcp-servers/graph-plotter-mcp/server.py (NEW)
- mcp-servers/pdf-reader-mcp/server.py (NEW)
- mcp-servers/python-executor-mcp/server.py (NEW — sandboxed)
- mcp-servers/image-solver-mcp/server.py (NEW — Gemini Vision)
- backend/src/agents/math_solver_agent.py (add MCP tool calls)

**Estimated Effort**: 2.5 days

**Dependencies**: Phase 8 (Cloud Run for MCP services)

**Risks**:
- Python executor sandbox must be airtight (use RestrictedPython or subprocess with timeout)
- MCP protocol compatibility with ADK may need custom adapter
- Multiple Cloud Run services increase cost

**Testing Checklist**:
- [ ] sympy-mcp differentiate("x**3") returns {result: "3*x**2", latex: "3x^2"}
- [ ] python-executor-mcp cannot import os or import sys
- [ ] graph-plotter-mcp returns SVG for sin(x)
- [ ] image-solver-mcp extracts equation from test image
- [ ] Agent uses MCP tool (confirmed via trace)

**Acceptance Criteria**:
- All 6 MCP servers deployed and passing health checks
- Math solver uses at least 3 MCP tools in verified test session
- Python sandbox security audit complete

**Rollback Strategy**: USE_MCP=false disables tool calling; agent falls back to direct SymPy

---

## Phase 10 — React Frontend

**Objectives**:
- Build full React + Vite frontend to replace Streamlit
- Implement KaTeX LaTeX rendering
- Implement streaming chat (SSE consumer)
- Implement NCERT Quiz panel with 4-button help system
- Implement Progress Dashboard (streak calendar, topic mastery)
- Deploy to Firebase Hosting

**Files Affected**:
- frontend/src/ (ALL NEW)
- frontend/package.json, vite.config.ts
- firebase/firebase.json (hosting rules)

**Estimated Effort**: 4 days (largest frontend effort)

**Dependencies**: Phase 8 + Phase 9 (requires live API endpoints)

**Risks**:
- KaTeX rendering edge cases with complex LaTeX
- SSE streaming requires proper EventSource with reconnection
- Mobile responsiveness requires significant CSS work
- Lighthouse performance target requires image optimization

**Testing Checklist**:
- [ ] Google Sign-In works and persists across browser refresh
- [ ] Chat sends message, receives streaming response with LaTeX rendered
- [ ] NCERT Quiz panel renders Class 10 Ch6 exercises with 4 buttons
- [ ] Streak calendar shows correct days
- [ ] Mobile layout at 375px is usable
- [ ] Lighthouse: Performance >80, Accessibility >90

**Acceptance Criteria**:
- Streamlit removed from production code path
- Full feature parity with current Streamlit UI
- Dark/light theme working in React

**Rollback Strategy**: Streamlit preserved in legacy/ branch; Firebase Hosting can revert to Streamlit Cloud URL

---

## Phase 11 — Testing, Documentation & Hackathon Polish

**Objectives**:
- Write comprehensive test suite (unit + integration + e2e)
- Update README with architecture diagrams and live URL
- Create hackathon demo script and video (<3 minutes)
- Performance benchmarking (latency, throughput)
- Final security audit

**Files Affected**:
- backend/tests/ (expand coverage)
- README.md (complete rewrite for hackathon)
- docs/ARCHITECTURE.md
- .github/workflows/ci.yml (add e2e tests)

**Estimated Effort**: 2 days

**Dependencies**: All phases complete

**Testing Checklist**:
- [ ] Unit test coverage >70%
- [ ] Integration tests: auth flow, chat flow, progress tracking
- [ ] E2e test (Playwright): login → ask → verify → rate
- [ ] Load test: 50 concurrent users, avg latency <5s
- [ ] Security scan: pip-audit, Dependabot, manual prompt injection tests

**Acceptance Criteria**:
- All CI checks green
- Live demo URL works (used in submission)
- README explains agent architecture clearly for judges
- Demo video <3 minutes showing key differentiating features

**Rollback Strategy**: Documentation-only phase, no code rollback needed

---

## Phase Summary Table

| Phase | Focus | Effort | Key Deliverable |
|---|---|---|---|
| Phase 0 | Security fix + audit | 0.5 days | eval() removed, tests extracted |
| Phase 1 | Architecture refactor | 2 days | FastAPI skeleton, main.py decomposed |
| Phase 2 | Gemini integration | 1.5 days | Groq replaced, streaming added |
| Phase 3 | Firebase auth + Firestore | 2 days | User auth, persistent history |
| Phase 4 | ADK multi-agent system | 3 days | 5 agents operational |
| Phase 5 | LangGraph workflow | 2.5 days | Full StateGraph with retries |
| Phase 6 | Qdrant vector database | 2 days | Hybrid search, ChromaDB removed |
| Phase 7 | Vertex AI integration | 1.5 days | All Gemini via Vertex AI |
| Phase 8 | Cloud Run deployment | 2 days | Live production URL |
| Phase 9 | MCP servers | 2.5 days | 6 tools deployed |
| Phase 10 | React frontend | 4 days | Streamlit replaced |
| Phase 11 | Testing + polish | 2 days | Demo-ready submission |
| **TOTAL** | | **~25 days** | |

---

# 17. Final Vision

## What the Finished Application Will Be

The **Advanced Mathematics AI Agent Platform** will be a production-grade, multi-agent AI system for Indian school students — a genuine AI-first educational product, not merely an LLM chatbot with a chat box.

## The Student Experience

```
Student opens the app on mobile
--> Signs in with Google (one tap)
--> App greets them: "Welcome back! You're on a 7-day streak!"
--> App surfaces: "You had trouble with Trigonometry last week. Try this:"
--> Student selects Class 10 Ch8 Exercise 8.1 Q3
--> Taps "Hint"
--> Response streams in token-by-token, rendered with beautiful KaTeX LaTeX
--> Student doesn't understand --> taps "Different approach"
--> Agent tries a visual approach: plots the right triangle
--> Student gets it --> taps "Got it!"
--> Progress recorded. Weak topic removed. Streak extended.
```

## The Architecture Story (For Judges)

This project demonstrates every dimension of modern AI agent engineering:

1. **Multi-agent reasoning** (ADK): Not a single LLM call — a coordinated team of specialized agents
2. **Persistent memory** (Firestore + Qdrant): Agents remember the student's history across sessions
3. **Tool-augmented AI** (MCP): Agents use structured tools — SymPy for exact math, Python for computation
4. **Stateful workflows** (LangGraph): Conditional routing, retry-on-failure, parallel execution
5. **Google AI native** (Gemini + Vertex AI): Google's cutting-edge models in every agent
6. **Production deployment** (Cloud Run + Firebase): Real cloud infrastructure, not a prototype
7. **Safety and security** (Vertex AI safety, Firebase auth, Secret Manager): Production-grade security
8. **Vector intelligence** (Qdrant hybrid search): Retrieves the right NCERT content with precision
9. **Human feedback loop**: Student feedback drives continuous improvement signals

## Target Impact Metrics

| Metric | Target |
|---|---|
| NCERT questions available | 505 (Class 9-10), expandable to 2,000+ |
| Classes covered | Class 6-12 + JEE Advanced |
| Avg response latency | <8 seconds (including verification) |
| Answer accuracy (SymPy-verified) | >95% for algebraic questions |
| Concurrent users (Cloud Run) | 0-1,000 (auto-scaling) |
| Monthly active cost (GCP) | <$10 (free tiers) |
| Google AI technologies used | 7+ (Gemini, Vertex AI, Firebase, Cloud Run, ADK, text-embedding-004, Cloud Logging) |

## The Hackathon Pitch

"We took a good math tutoring chatbot and transformed it into a multi-agent AI tutoring system — one where a Planner understands what the student needs, a Retriever finds exactly the right NCERT concept, a Solver works through the problem step-by-step using Google's Gemini with access to real tools, and a Verifier ensures the answer is actually correct before the student sees it. Every component is Google-native, every answer is personalized, and every interaction makes the student smarter."

---

*This roadmap is the master planning document.*
*No code will be modified before this document receives explicit approval.*
*After approval, work begins strictly with Phase 0.*

---

**Document End — Awaiting Approval to Proceed to Phase 0**
"""

OUTPUT_PATH.write_text(ROADMAP, encoding="utf-8")
print(f"SUCCESS: Wrote {len(ROADMAP):,} characters to {OUTPUT_PATH}")
print(f"File size: {OUTPUT_PATH.stat().st_size:,} bytes")
