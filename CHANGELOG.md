# Changelog

All notable changes to the **Advanced Mathematics Assistant** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

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
