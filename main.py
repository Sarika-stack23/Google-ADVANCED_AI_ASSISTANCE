"""
╔══════════════════════════════════════════════════════════════════════╗
║          ADVANCED MATHEMATICS ASSISTANT — main.py                   ║
║  All 7 pipeline steps in one file                                   ║
║                                                                      ║
║  USAGE:                                                              ║
║    python3.11 -m streamlit run main.py   → Launch UI                ║
║    python3.11 main.py --setup            → Build knowledge base     ║
║    python3.11 main.py --test             → Run all tests            ║
║    python3.11 main.py --eval             → Evaluate RAG pipeline    ║
║    python3.11 main.py --rebuild          → Force rebuild KB         ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import os, re, sys, json, time, uuid, hashlib, logging, argparse, unittest, ast, tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from knowledge_base import MATH_KNOWLEDGE_BASE, CLASS_EXAMPLES
from dotenv import load_dotenv
# Load .env locally — works regardless of launch directory
load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=True)

# Streamlit Cloud: load secrets into environment variables
try:
    import streamlit as st
    for _k, _v in st.secrets.items():
        if _k not in os.environ:
            os.environ[_k] = str(_v)
except Exception:
    pass  # Not running on Streamlit Cloud or secrets not configured

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("math_assistant")

GROQ_API_KEY       = os.getenv("GROQ_API_KEY", "")
# llama-3.3-70b-versatile: powerful but low RPM on Groq free tier (30 RPM)
# llama3-8b-8192: higher RPM limit (30 RPM but faster + less likely to hit TPM limits)
# mixtral-8x7b-32768: good balance — use this if hitting rate limits
LLM_MODEL          = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
EMBEDDING_MODEL    = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
VECTOR_DB_TYPE     = os.getenv("VECTOR_DB_TYPE", "chroma").lower()
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
FAISS_INDEX_PATH   = os.getenv("FAISS_INDEX_PATH", "./faiss_index")
TOP_K_RESULTS      = int(os.getenv("TOP_K_RESULTS", "5"))
CHUNK_SIZE         = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP      = int(os.getenv("CHUNK_OVERLAP", "200"))
MONGODB_URI        = os.getenv("MONGODB_URI", "")
MONGODB_DB_NAME    = os.getenv("MONGODB_DB_NAME", "math_assistant")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", "chat_history")
COLLECTION_NAME    = "math_knowledge_base"

try:
    from langchain_core.documents import Document
except ImportError:
    try:
        from langchain.schema import Document
    except ImportError:
        class Document:
            def __init__(self, page_content: str, metadata: dict = None):
                self.page_content = page_content
                self.metadata = metadata or {}

try:
    from langchain_core.messages import HumanMessage, AIMessage
except ImportError:
    from langchain.schema import HumanMessage, AIMessage

try:
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
except ImportError:
    from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  STEP 1 — DATA SOURCES                                              ║
# ╚══════════════════════════════════════════════════════════════════════╝

class MathDataLoader:
    def __init__(self):
        self.documents = []

    def load_builtin_knowledge(self):
        logger.info(f"Loading {len(MATH_KNOWLEDGE_BASE)} built-in knowledge documents")
        return list(MATH_KNOWLEDGE_BASE)

    def load_pdf(self, pdf_path: str):
        try:
            from langchain_community.document_loaders import PyPDFLoader
            docs = PyPDFLoader(pdf_path).load()
            logger.info(f"Loaded {len(docs)} pages from: {pdf_path}")
            return docs
        except Exception as e:
            logger.error(f"Failed to load PDF {pdf_path}: {e}")
            return []

    def load_pdfs_from_directory(self, dir_path: str):
        try:
            from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
            docs = DirectoryLoader(dir_path, glob="**/*.pdf", loader_cls=PyPDFLoader).load()
            logger.info(f"Loaded {len(docs)} documents from: {dir_path}")
            return docs
        except Exception as e:
            logger.error(f"Failed to load PDFs from {dir_path}: {e}")
            return []

    def load_web_pages(self, urls: List[str]):
        from langchain_community.document_loaders import WebBaseLoader
        import socket
        docs = []
        for url in urls:
            try:
                loader = WebBaseLoader(url)
                loader.requests_kwargs = {"timeout": 15}
                docs.extend(loader.load())
                logger.info(f"Loaded: {url}")
            except Exception as e:
                logger.warning(f"Failed URL {url}: {e}")
        return docs

    def load_text_file(self, file_path: str):
        try:
            if file_path.endswith(".md"):
                from langchain_community.document_loaders import UnstructuredMarkdownLoader
                loader = UnstructuredMarkdownLoader(file_path)
            else:
                from langchain_community.document_loaders import TextLoader
                loader = TextLoader(file_path, encoding="utf-8")
            docs = loader.load()
            logger.info(f"Loaded: {file_path}")
            return docs
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            return []

    def load_all(self, pdf_paths=None, urls=None, text_paths=None, pdf_directory=None):
        all_docs = self.load_builtin_knowledge()
        if pdf_paths:
            for p in pdf_paths: all_docs.extend(self.load_pdf(p))
        if pdf_directory and os.path.exists(pdf_directory):
            all_docs.extend(self.load_pdfs_from_directory(pdf_directory))
        if urls:
            all_docs.extend(self.load_web_pages(urls))
        if text_paths:
            for p in text_paths: all_docs.extend(self.load_text_file(p))
        logger.info(f"Total documents loaded: {len(all_docs)}")
        self.documents = all_docs
        return all_docs


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  STEP 2 — DATA PREPROCESSING                                        ║
# ╚══════════════════════════════════════════════════════════════════════╝

class MathDataPreprocessor:
    TOPIC_KEYWORDS: Dict[str, List[str]] = {
        "calculus":       ["derivative", "integral", "differentiate", "integrate", "limit", "continuity", "taylor"],
        "linear_algebra": ["matrix", "vector", "eigenvalue", "determinant", "rank", "span", "basis"],
        "statistics":     ["probability", "distribution", "mean", "variance", "regression", "hypothesis"],
        "algebra":        ["polynomial", "equation", "quadratic", "factor", "root", "logarithm", "exponent"],
        "trigonometry":   ["sine", "cosine", "tangent", "angle", "radian", "unit circle", "trig"],
        "discrete_math":  ["graph", "combinatorics", "permutation", "combination", "modular", "prime"],
        "geometry":       ["triangle", "circle", "area", "volume", "perimeter", "pythagorean", "coordinate"],
        "number_theory":  ["prime", "divisor", "gcd", "lcm", "modular", "congruence", "integer"],
    }

    def __init__(self):
        self._seen_hashes: set = set()

    def _clean(self, text: str) -> str:
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]{2,}", " ", text)
        text = re.sub(r"Page\s+\d+\s+of\s+\d+", "", text, flags=re.IGNORECASE)
        text = re.sub(r"https?://\S+", "[URL]", text)
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
        replacements = {
            "\u2019": "'", "\u201c": '"', "\u201d": '"',
            "\u2013": "-", "\u2014": "--", "\u00a0": " ",
            "\u03c0": "pi", "\u221e": "infinity",
            "\u2264": "<=", "\u2265": ">="
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text.strip()

    def _detect_topic(self, text: str) -> str:
        tl = text.lower()
        scores = {t: sum(1 for kw in kws if kw in tl) for t, kws in self.TOPIC_KEYWORDS.items()}
        scores = {k: v for k, v in scores.items() if v > 0}
        return max(scores, key=scores.get) if scores else "general_math"

    def _difficulty(self, text: str) -> str:
        adv = ["eigenvalue", "differential equation", "fourier", "laplace", "manifold", "tensor"]
        mid = ["derivative", "integral", "matrix", "probability", "polynomial", "logarithm"]
        tl = text.lower()
        if sum(1 for t in adv if t in tl) >= 2: return "advanced"
        if sum(1 for t in mid if t in tl) >= 2: return "intermediate"
        return "beginner"

    def preprocess_document(self, doc):
        text = doc.page_content
        if len(text.strip()) < 50:
            return None
        text = self._clean(text)
        h = hashlib.md5(text.strip().lower().encode()).hexdigest()
        if h in self._seen_hashes:
            return None
        self._seen_hashes.add(h)
        meta = doc.metadata.copy()
        meta.update({
            "topic":        meta.get("topic") or self._detect_topic(text),
            "difficulty":   self._difficulty(text),
            "char_count":   len(text),
            "word_count":   len(text.split()),
            "content_hash": h,
        })
        return Document(page_content=text, metadata=meta)

    def preprocess_documents(self, documents):
        logger.info(f"Preprocessing {len(documents)} documents...")
        self._seen_hashes.clear()
        processed = [r for doc in documents if (r := self.preprocess_document(doc)) is not None]
        logger.info(f"Done: {len(processed)} kept, {len(documents)-len(processed)} skipped")
        return processed


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  STEP 3 — SPLITTING AND CHUNKING                                    ║
# ╚══════════════════════════════════════════════════════════════════════╝

class MathTextSplitter:
    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
        from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.recursive = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", "! ", "? ", "; ", ": ", " ", ""])
        self.markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[("#", "H1"), ("##", "H2"), ("###", "H3")])

    def split_document(self, doc):
        source = doc.metadata.get("source", "").lower()
        if source.endswith(".md") or "markdown" in source:
            try:
                splits = self.markdown_splitter.split_text(doc.page_content)
                chunks = [Document(page_content=s.page_content,
                                   metadata={**doc.metadata, **s.metadata}) for s in splits]
            except Exception:
                chunks = self.recursive.split_documents([doc])
        else:
            chunks = self.recursive.split_documents([doc])
        for i, chunk in enumerate(chunks):
            chunk.metadata.update({
                "chunk_index":  i,
                "total_chunks": len(chunks),
                "chunk_size":   len(chunk.page_content),
            })
        return chunks

    def split_documents(self, documents):
        logger.info(f"Splitting {len(documents)} documents...")
        all_chunks = []
        for doc in documents:
            all_chunks.extend(self.split_document(doc))
        logger.info(f"Created {len(all_chunks)} chunks")
        return all_chunks


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  STEP 4 — EMBEDDINGS, VECTOR DB & KNOWLEDGE BASE                   ║
# ╚══════════════════════════════════════════════════════════════════════╝

_EMBEDDINGS_CACHE = {}
def get_embeddings():
    if "model" not in _EMBEDDINGS_CACHE:
        from langchain_huggingface import HuggingFaceEmbeddings
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
        _EMBEDDINGS_CACHE["model"] = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True})
    return _EMBEDDINGS_CACHE["model"]


class MathVectorStore:
    def __init__(self):
        self.embeddings = get_embeddings()
        self.vectorstore = None
        self.db_type = VECTOR_DB_TYPE
        self._load_existing()

    def _load_existing(self):
        if self.db_type == "chroma":
            self._try_chroma()
        else:
            self._try_faiss()

    def _try_chroma(self, documents=None):
        try:
            from langchain_community.vectorstores import Chroma
            persist_path = Path(CHROMA_PERSIST_DIR)
            persist_path.mkdir(parents=True, exist_ok=True)
            if documents:
                self.vectorstore = Chroma.from_documents(
                    documents=documents, embedding=self.embeddings,
                    collection_name=COLLECTION_NAME,
                    persist_directory=str(persist_path))
                logger.info("ChromaDB created.")
            elif list(persist_path.glob("*.sqlite3")):
                self.vectorstore = Chroma(
                    collection_name=COLLECTION_NAME,
                    embedding_function=self.embeddings,
                    persist_directory=str(persist_path))
                logger.info(f"ChromaDB loaded ({self.vectorstore._collection.count()} docs)")
        except Exception as e:
            logger.warning(f"ChromaDB failed ({type(e).__name__}: {e}), switching to FAISS")
            self.db_type = "faiss"
            if documents:
                self._try_faiss(documents)

    def _try_faiss(self, documents=None):
        try:
            from langchain_community.vectorstores import FAISS
            index_path = Path(FAISS_INDEX_PATH)
            if documents:
                self.vectorstore = FAISS.from_documents(documents, self.embeddings)
                index_path.mkdir(parents=True, exist_ok=True)
                self.vectorstore.save_local(str(index_path))
                logger.info(f"FAISS saved to {index_path}")
            elif index_path.exists() and any(index_path.iterdir()):
                self.vectorstore = FAISS.load_local(
                    str(index_path), self.embeddings,
                    allow_dangerous_deserialization=True)
                logger.info("FAISS loaded.")
        except Exception as e:
            logger.error(f"FAISS failed: {e}")

    def build_knowledge_base(self, documents):
        logger.info(f"Building knowledge base with {len(documents)} chunks...")
        if self.db_type == "chroma":
            self._try_chroma(documents)
        else:
            self._try_faiss(documents)
        logger.info("Knowledge base ready.")

    def add_documents(self, documents):
        if self.vectorstore is None:
            self.build_knowledge_base(documents)
        else:
            self.vectorstore.add_documents(documents)

    def similarity_search(self, query: str, k: int = TOP_K_RESULTS, filter_topic: str = None):
        if self.vectorstore is None:
            return []
        try:
            if filter_topic and self.db_type == "chroma":
                return self.vectorstore.similarity_search(query, k=k, filter={"topic": filter_topic})
            return self.vectorstore.similarity_search(query, k=k)
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def as_retriever(self, k: int = TOP_K_RESULTS):
        return self.vectorstore.as_retriever(search_kwargs={"k": k}) if self.vectorstore else None

    def get_document_count(self) -> int:
        if self.vectorstore is None:
            return 0
        try:
            return (self.vectorstore._collection.count() if self.db_type == "chroma"
                    else self.vectorstore.index.ntotal)
        except Exception as e:
            logger.error(f"get_document_count failed: {e}")
            return 0

    def is_ready(self) -> bool:
        return self.vectorstore is not None and self.get_document_count() > 0


_PIPELINE_CACHE = {}
def build_pipeline(pdf_paths=None, urls=None, text_paths=None, force_rebuild=False) -> MathVectorStore:
    """Cached — runs once per process. Embedding model + KB build only happens on cold start."""
    if "store" in _PIPELINE_CACHE and not force_rebuild:
        return _PIPELINE_CACHE["store"]
    store = MathVectorStore()
    if store.is_ready() and not force_rebuild:
        logger.info(f"Knowledge base already built ({store.get_document_count()} docs).")
        _PIPELINE_CACHE["store"] = store
        return store
    raw_docs   = MathDataLoader().load_all(pdf_paths=pdf_paths or [], urls=urls or [], text_paths=text_paths or [])
    clean_docs = MathDataPreprocessor().preprocess_documents(raw_docs)
    chunks     = MathTextSplitter().split_documents(clean_docs)
    store.build_knowledge_base(chunks)
    _PIPELINE_CACHE["store"] = store
    return store


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  STEP 5 — QUERY PROCESSING & AI ENGINE                              ║
# ╚══════════════════════════════════════════════════════════════════════╝

SYSTEM_TEMPLATE = """You are an Indian mathematics teacher writing on a whiteboard.

⚠️ NON-MATH QUESTIONS:
If NOT about mathematics → reply ONLY: "❌ I only teach math! Ask me any math problem."
Stop immediately. Nothing else.

════════════════════════════════════════
THE GOLDEN RULE — READ THIS FIRST:
════════════════════════════════════════

NEVER write paragraphs. NEVER write long sentences explaining theory.
Write SHORT lines. Like a teacher writing on a board.
Every line = one idea. One calculation. One small result.
If a student can't follow in 5 seconds → you wrote too much.

WRONG (too much theory, paragraph style):
"The Commutative Property of Addition states that when we add numbers,
the order does not matter. This means that 3+4 gives the same result
as 4+3, which we can verify by counting on a number line..."

RIGHT (whiteboard style):
Step 1 — Check: does order matter in addition?
   3 + 4 = 7
   4 + 3 = 7  ← same answer!
   ✓ Yes — order doesn't matter. This is called Commutative Property.

════════════════════════════════════════
FORMAT — FOLLOW EXACTLY EVERY TIME:
════════════════════════════════════════

[One short opening — max 1 line. Like reading the problem aloud.]
"Okay, quadratic equation. Let's use the formula."
"Right — we need HCF of two numbers."
"Alright, let's integrate this step by step."

━━━━━━━━━━━━━━━━━━━━━━━━━━━
Question: [restate question clearly]
━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 1 — [title: what and why, max 1 line]
   [calculation line 1]
   [calculation line 2]
   [short teacher note if needed — max 1 line]

Step 2 — [title]
   [calculation]
   [result]

[only as many steps as needed — no fake steps]

━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Answer: [final answer]
━━━━━━━━━━━━━━━━━━━━━━━━━━━

[One closing line max — "Key thing: watch the sign here!" or "Make sense?"]

════════════════════════════════════════
INSIDE EACH STEP — RULES:
════════════════════════════════════════

✅ DO write like this:
   a = 2, b = 5, c = -3
   b² - 4ac = 25 - 4(2)(-3) = 25 + 24 = 49   ← careful: minus×minus = plus!
   √49 = 7   ← clean number, good sign!
   x = (-5 ± 7) / 4

✅ DO add ONE short teacher reaction inline:
   "← careful here"   "← minus × minus = plus!"   "← nice, simplifies!"
   "← most students miss this"   "← remember this!"

❌ NEVER write:
   - Paragraphs or long sentences
   - Theory blocks explaining what a property IS
   - Repeated explanations of the same idea
   - More than 1 line of teacher commentary per step
   - Sentences like "In this case, we can see that..." or "This demonstrates..."
   - Definitions ("The quadratic formula is used when...")
   - History or background ("This property was discovered...")

════════════════════════════════════════
DETECT LEVEL — CHANGE DEPTH NOT STYLE:
════════════════════════════════════════

Class 1–5:
→ Ultra simple. Real objects. ("3 apples + 4 apples = 7 apples")
→ No jargon. Max 3 steps.
→ Lots of ✓ and encouragement inline.

Class 6–8:
→ Short friendly lines. Explain WHY in 3-4 words inline.
→ "← because negative × negative = positive"

Class 9–10:
→ Full working, every line shown.
→ One inline note on common exam mistake.
→ "← board exams always ask this"

Class 11–12:
→ State theorem/formula name once, then just use it.
→ Show every substitution clearly.

JEE Advanced:
→ Full clean solution first.
→ Then add:
   💡 Key Insight: [one line — the clever observation]
   ⏱️ Exam Tip: [one line — what to write quickly]

════════════════════════════════════════
SYMBOLS — STRICT:
════════════════════════════════════════

→ NEVER LaTeX or $. Unicode only.
→ √ not sqrt(). x² not x^2. π not pi. ± not +/-
→ Fractions: (a+b)/(c+d)
→ Hindi/Hinglish question → answer in same language

Context from knowledge base:
{context}
"""


class MongoDBChatMemory:
    def __init__(self, session_id: str = "default"):
        self.session_id = session_id
        self.collection = None
        self._memory: List[Dict] = []
        self._connect()

    def _connect(self):
        if not MONGODB_URI:
            return
        try:
            from pymongo import MongoClient
            client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
            client.admin.command("ping")
            self.collection = client[MONGODB_DB_NAME][MONGODB_COLLECTION]
            logger.info("MongoDB connected")
        except Exception as e:
            logger.warning(f"MongoDB unavailable ({e}), using in-memory history")

    def add_message(self, role: str, content: str):
        msg = {"session_id": self.session_id, "role": role,
               "content": content, "timestamp": datetime.now(timezone.utc)}
        if self.collection is not None:
            try:
                self.collection.insert_one(msg)
                return
            except Exception:
                pass
        self._memory.append(msg)

    def get_history(self, limit: int = 20) -> List[Dict]:
        if self.collection is not None:
            try:
                msgs = list(self.collection.find(
                    {"session_id": self.session_id}).sort("timestamp", -1).limit(limit))
                msgs.reverse()
                return msgs
            except Exception:
                pass
        return self._memory[-limit:]

    def get_langchain_messages(self, limit: int = 10):
        history = self.get_history(limit)
        result = []
        for msg in history:
            if msg["role"] == "human":
                result.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                result.append(AIMessage(content=msg["content"]))
        return result

    def clear_history(self):
        if self.collection is not None:
            try:
                self.collection.delete_many({"session_id": self.session_id})
            except Exception:
                pass
        self._memory.clear()


class SymbolicMathEngine:
    @staticmethod
    def differentiate(expression: str, variable: str = "x") -> Optional[str]:
        try:
            import sympy as sp
            var = sp.Symbol(variable)
            expr = sp.sympify(re.sub(r'\^', '**', expression.strip()))
            return f"d/d{variable}[{expression}] = {sp.simplify(sp.diff(expr, var))}"
        except Exception:
            return None

    @staticmethod
    def integrate(expression: str, variable: str = "x") -> Optional[str]:
        try:
            import sympy as sp
            var = sp.Symbol(variable)
            expr = sp.sympify(re.sub(r'\^', '**', expression.strip()))
            return f"integral({expression}) d{variable} = {sp.integrate(expr, var)} + C"
        except Exception:
            return None

    @staticmethod
    def solve_equation(equation: str, variable: str = "x") -> Optional[str]:
        try:
            import sympy as sp
            var = sp.Symbol(variable)
            eq_str = re.sub(r'\^', '**', equation.strip())
            if "=" in eq_str:
                lhs, rhs = eq_str.split("=", 1)
                eq = sp.Eq(sp.sympify(lhs), sp.sympify(rhs))
            else:
                eq = sp.sympify(eq_str)
            return f"Solutions for {variable}: {sp.solve(eq, var)}"
        except Exception:
            return None

    @staticmethod
    def try_solve(expression: str) -> Optional[str]:
        try:
            import sympy as sp
            x, y, z, t = sp.symbols('x y z t')
            expr_str = re.sub(r'\^', '**', expression.strip())
            result = sp.simplify(sp.sympify(expr_str, locals={
                'x': x, 'y': y, 'z': z, 't': t,
                'sin': sp.sin, 'cos': sp.cos, 'exp': sp.exp,
                'log': sp.log, 'sqrt': sp.sqrt, 'pi': sp.pi}))
            return str(result)
        except Exception:
            return None

    @staticmethod
    def matrix_operations(matrix_str: str) -> Optional[Dict[str, Any]]:
        try:
            import sympy as sp
            M = sp.Matrix(ast.literal_eval(matrix_str))
            return {"determinant": str(M.det()), "rank": M.rank(),
                    "eigenvalues": str(M.eigenvals()), "trace": str(M.trace())}
        except Exception:
            return None


_LLM_CACHE = {}
# Fallback model order — if primary hits daily token limit, auto-switch
GROQ_MODEL_FALLBACKS = [
    os.getenv("LLM_MODEL", "llama-3.3-70b-versatile"),
    "llama3-8b-8192",
    "mixtral-8x7b-32768",
]

def _get_llm(model=None):
    key = model or GROQ_MODEL_FALLBACKS[0]
    if key not in _LLM_CACHE:
        from langchain_groq import ChatGroq
        api_key = os.getenv("GROQ_API_KEY", "") or GROQ_API_KEY
        if not api_key:
            raise ValueError("GROQ_API_KEY not set. Add it to your .env file.")
        logger.info(f"Initializing Groq LLM: {key}")
        _LLM_CACHE[key] = ChatGroq(groq_api_key=api_key, model_name=key,
                                    temperature=0.1, max_tokens=2048)
    return _LLM_CACHE[key]

class MathAIEngine:
    def __init__(self, vector_store: MathVectorStore = None, session_id: str = "default"):
        self.llm          = self._init_llm()
        self.vector_store = vector_store
        self.memory       = MongoDBChatMemory(session_id=session_id)
        self.symbolic     = SymbolicMathEngine()
        self.session_id   = session_id

    def _init_llm(self):
        # Eagerly init the primary model; fallbacks are created on demand
        return _get_llm(GROQ_MODEL_FALLBACKS[0])

    def _retrieve_context(self, query: str) -> Tuple[list, str]:
        if not self.vector_store or not self.vector_store.is_ready():
            return [], "No knowledge base available. Using general mathematical knowledge."
        docs = self.vector_store.similarity_search(query, k=3)
        if not docs:
            return [], "No specific context found."
        parts = [f"[Reference {i+1} - {d.metadata.get('topic','math')}]\n{d.page_content}"
                 for i, d in enumerate(docs)]
        return docs, "\n\n---\n\n".join(parts)

    def _symbolic_hint(self, query: str) -> Optional[str]:
        ql = query.lower()
        for pattern, action in [
            (r"(?:differentiate|derivative of|d/dx)\s+(.+?)(?:\s+with respect|\s*$)", "diff"),
            (r"(?:integrate|integral of)\s+(.+?)(?:\s+with respect|\s+dx|\s*$)", "int"),
            (r"solve\s+(.+?)\s+(?:for|=)", "solve"),
        ]:
            m = re.search(pattern, ql)
            if m:
                expr = m.group(1).strip()
                result = (self.symbolic.differentiate(expr) if action == "diff"
                          else self.symbolic.integrate(expr) if action == "int"
                          else self.symbolic.solve_equation(expr))
                if result:
                    return f"[Symbolic verification: {result}]"
        return None

    def query(self, user_input: str) -> Dict[str, Any]:
        hint        = self._symbolic_hint(user_input)
        source_docs, context = self._retrieve_context(user_input)
        chat_history = self.memory.get_langchain_messages(limit=4)

        # Build the messages list manually — NEVER pass math content through
        # LangChain format_messages(), because curly braces in math (e.g. {x|x>0},
        # set notation, matrices) are treated as template variables and crash with
        # a KeyError, silently swallowed → user sees no answer at all.
        system_text = SYSTEM_TEMPLATE.replace("{context}", context)
        llm_messages = []
        # System message — use LangChain tuple form which bypasses brace parsing
        from langchain_core.messages import SystemMessage
        llm_messages.append(SystemMessage(content=system_text))
        # Inject chat history
        for msg in chat_history:
            llm_messages.append(msg)
        # Current user question
        llm_messages.append(HumanMessage(content=user_input))

        # Store human message BEFORE LLM call so history order is correct
        self.memory.add_message("human", user_input)

        # Auto-retry with model fallback — if daily limit hit, switch to next model
        answer      = None
        last_error  = None
        used_models = []
        for model_name in GROQ_MODEL_FALLBACKS:
            if model_name in used_models:
                continue
            used_models.append(model_name)
            llm = _get_llm(model_name)
            for _attempt in range(2):  # 2 attempts per model
                try:
                    raw = llm.invoke(llm_messages).content
                    if raw and not any(p in raw.lower() for p in
                                       ["rate limit", "too many requests", "service unavailable"]):
                        answer = raw
                        if model_name != GROQ_MODEL_FALLBACKS[0]:
                            answer = f"*(Using fallback model: {model_name})*\n\n" + answer
                        break
                    else:
                        raise Exception(raw or "Empty response")
                except Exception as e:
                    last_error = e
                    err = str(e).lower()
                    full_err = str(e)
                    logger.warning(f"Model {model_name} attempt {_attempt+1} failed: {e}")
                    if "per day" in full_err or "tokens per day" in full_err:
                        # Daily limit — skip to next model immediately
                        logger.info(f"Daily limit on {model_name}, trying next model...")
                        break
                    elif "429" in full_err or "rate_limit" in err:
                        time.sleep(2 ** _attempt)
                        continue
                    elif "timeout" in err or "connect" in err or "503" in err:
                        time.sleep(1)
                        continue
                    else:
                        break  # non-retryable
            if answer:
                break

        if answer is None:
            full_err = str(last_error)
            err      = full_err.lower()
            logger.error(f"LLM failed: [{type(last_error).__name__}] {full_err}")

            if "401" in full_err or "invalid_api_key" in err:
                answer = "⚠️ Invalid API key. Check GROQ_API_KEY in your .env file."
            elif "429" in full_err or "rate_limit_exceeded" in err:
                # Extract the retry time from Groq's message if present
                import re as _re
                retry_match = _re.search(r'try again in (.+?)\.', full_err)
                retry_info  = f" Groq says: try again in **{retry_match.group(1)}**." if retry_match else ""
                # Check if it is TPD (daily) or TPM (per minute)
                if "per day" in full_err or "tokens per day" in full_err or "TPD" in full_err:
                    answer = f"⚠️ **Daily token limit reached** (Groq free tier: 100,000 tokens/day).{retry_info}\n\nTo keep using the app now, change your `.env`:\n```\nLLM_MODEL=llama3-8b-8192\n```\nThen restart Streamlit. The 8B model has a separate 500k/day quota."
                else:
                    answer = f"⚠️ **Rate limit hit** (too many requests per minute).{retry_info} Wait 20–30 seconds and try again."
            elif "context_length" in err or ("context" in err and "length" in err):
                answer = "⚠️ Question + context too long. Try a shorter question."
            elif "connect" in err or "connection" in err:
                answer = "⚠️ Cannot reach Groq API. Check your internet connection."
            elif "timeout" in err:
                answer = "⚠️ Request timed out. Try again."
            else:
                answer = f"⚠️ Error ({type(last_error).__name__}): {full_err}"

        self.memory.add_message("assistant", answer)

        sources = [{"topic":      d.metadata.get("topic", "unknown"),
                    "source":     d.metadata.get("source", "kb"),
                    "difficulty": d.metadata.get("difficulty", "unknown")}
                   for d in source_docs]

        return {"answer": answer, "sources": sources, "symbolic_hint": hint,
                "session_id": self.session_id, "context_docs": len(source_docs)}

    def clear_memory(self):
        self.memory.clear_history()

    def get_history(self):
        return self.memory.get_history(limit=50)


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  OCR / IMAGE SCAN HELPER                                            ║
# ╚══════════════════════════════════════════════════════════════════════╝

def ocr_extract_text(image) -> str:
    try:
        from PIL import Image
        import PIL.ImageEnhance as enhance
        import pytesseract
        # Set tesseract binary path for common install locations
        for _tess_path in [
            "/opt/homebrew/bin/tesseract",   # macOS Apple Silicon (brew)
            "/usr/local/bin/tesseract",       # macOS Intel (brew)
            "/usr/bin/tesseract",             # Linux
        ]:
            if os.path.exists(_tess_path):
                pytesseract.pytesseract.tesseract_cmd = _tess_path
                break
        gray      = image.convert("L")
        contrast  = enhance.Contrast(gray).enhance(2.0)
        sharpened = enhance.Sharpness(contrast).enhance(2.0)
        text = pytesseract.image_to_string(sharpened, config='--psm 6').strip()
        text = ' '.join(text.replace('\n', ' ').split())
        return text
    except ImportError:
        return "ERROR_NO_PYTESSERACT"
    except Exception as e:
        logger.error(f"OCR error: {e}")
        return ""

def _safe_evaluate_expression(expr_str: str, x_array):
    """Safely evaluate a mathematical expression string over a numpy array.

    Uses SymPy's sympify() to parse the expression (rejecting arbitrary Python)
    and lambdify() to convert it to a numpy-callable function. This is safe
    because sympify() only understands mathematical syntax, not arbitrary code.

    Args:
        expr_str: Mathematical expression string (e.g., "sin(x)", "x**2 + 1").
        x_array: numpy array of x values to evaluate the expression over.

    Returns:
        numpy array of y values.

    Raises:
        ValueError: If the expression contains disallowed constructs.
        sympy.SympifyError: If the expression cannot be parsed as math.
    """
    import sympy as sp
    import numpy as np

    # Reject expressions containing dangerous patterns before parsing
    _BLOCKED_PATTERNS = [
        "__", "import", "exec", "eval", "compile", "open", "getattr",
        "setattr", "delattr", "globals", "locals", "vars", "dir",
        "breakpoint", "exit", "quit", "input", "print", "os.",
        "sys.", "subprocess", "shutil", "pathlib",
    ]
    expr_lower = expr_str.lower().replace(" ", "")
    for pattern in _BLOCKED_PATTERNS:
        if pattern in expr_lower:
            raise ValueError(f"Blocked: expression contains disallowed pattern '{pattern}'")

    # Replace caret with power operator
    sanitized = re.sub(r'\^', '**', expr_str.strip())

    # Define allowed SymPy symbols and functions for parsing
    x = sp.Symbol("x")
    _local_dict = {
        "x": x, "e": sp.E, "pi": sp.pi,
        "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
        "exp": sp.exp, "log": sp.log, "ln": sp.log,
        "sqrt": sp.sqrt, "abs": sp.Abs,
        "arcsin": sp.asin, "arccos": sp.acos, "arctan": sp.atan,
        "asin": sp.asin, "acos": sp.acos, "atan": sp.atan,
        "sinh": sp.sinh, "cosh": sp.cosh, "tanh": sp.tanh,
        "sec": sp.sec, "csc": sp.csc, "cot": sp.cot,
        "ceiling": sp.ceiling, "floor": sp.floor,
    }

    # Parse through SymPy — rejects arbitrary Python code
    sym_expr = sp.sympify(sanitized, locals=_local_dict)

    # Convert to numpy-callable function — safe, no code execution
    f = sp.lambdify(x, sym_expr, modules=["numpy"])
    y = f(x_array)

    # Ensure result is array (handles constant expressions like "5" or "pi")
    if not hasattr(y, "__len__"):
        y = np.full_like(x_array, float(y))

    return y


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  STEP 6 — STREAMLIT UI                                              ║
# ╚══════════════════════════════════════════════════════════════════════╝

def render_graph(expression: str, x_range: tuple = (-10, 10), title: str = ""):
    import streamlit as st
    try:
        import numpy as np
        import plotly.graph_objects as go

        _dark   = st.session_state.get("theme", "dark") == "dark"
        _bg     = "#0d1220" if _dark else "#ffffff"
        _paper  = "#080c14" if _dark else "#f8fafc"
        _grid   = "#1e293b" if _dark else "#e2e8f0"
        _text   = "#94a3b8" if _dark else "#475569"
        _colors = ["#4f8ef7", "#4ecca3", "#f5c842", "#ff6b6b", "#c792ea"]

        x = np.linspace(x_range[0], x_range[1], 1000)

        fig = go.Figure()
        plotted = 0

        for idx, expr in enumerate(expression.split(",")[:5]):
            expr = expr.strip()
            try:
                # SAFE: uses SymPy sympify+lambdify instead of eval()
                y = _safe_evaluate_expression(expr, x)
                y = np.where(np.abs(y) > 1e10, np.nan, y)
                fig.add_trace(go.Scatter(
                    x=x, y=y,
                    mode="lines",
                    name=f"y = {expr}",
                    line=dict(color=_colors[idx % len(_colors)], width=2.5),
                    hovertemplate=f"y = {expr}<br>x = %{{x:.3f}}<br>y = %{{y:.3f}}<extra></extra>",
                ))
                plotted += 1
            except Exception:
                st.warning(f"Could not plot: {expr}")

        if plotted == 0:
            return

        fig.update_layout(
            title=dict(text=title, font=dict(color=_text, size=14)) if title else None,
            paper_bgcolor=_paper,
            plot_bgcolor=_bg,
            font=dict(color=_text, family="DM Sans"),
            xaxis=dict(
                showgrid=True, gridcolor=_grid, gridwidth=0.5,
                zeroline=True, zerolinecolor=_text, zerolinewidth=1,
                tickfont=dict(color=_text), title="x",
                showspikes=True, spikecolor=_text, spikethickness=1,
            ),
            yaxis=dict(
                showgrid=True, gridcolor=_grid, gridwidth=0.5,
                zeroline=True, zerolinecolor=_text, zerolinewidth=1,
                tickfont=dict(color=_text), title="y",
                showspikes=True, spikecolor=_text, spikethickness=1,
            ),
            legend=dict(
                bgcolor=_bg, bordercolor=_grid, borderwidth=1,
                font=dict(color=_text),
            ),
            hovermode="x unified",
            margin=dict(l=50, r=20, t=40 if title else 20, b=50),
            height=420,
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Graph error: {e}")


def run_streamlit_app():
    import streamlit as st

    st.set_page_config(page_title="Advanced Mathematics Assistant",
                       page_icon="∫", layout="wide")

    # ── Theme: dark (default) or light ────────────────────────────────
    if "theme" not in st.session_state:
        st.session_state.theme = "dark"

    dark = st.session_state.theme == "dark"
    theme_vars = """
    :root {
        --bg:       #080c14;
        --bg2:      #0d1220;
        --card:     #111827;
        --card2:    #161f30;
        --blue:     #3b82f6;
        --blue2:    #60a5fa;
        --cyan:     #22d3ee;
        --green:    #10b981;
        --gold:     #f59e0b;
        --purple:   #8b5cf6;
        --tx:       #f1f5f9;
        --tx2:      #94a3b8;
        --tx3:      #475569;
        --border:   #1e293b;
        --border2:  #243044;
        --glow:     rgba(59,130,246,0.15);
    }""" if dark else """
    :root {
        --bg:       #f8fafc;
        --bg2:      #f1f5f9;
        --card:     #ffffff;
        --card2:    #f8fafc;
        --blue:     #2563eb;
        --blue2:    #1d4ed8;
        --cyan:     #0891b2;
        --green:    #059669;
        --gold:     #d97706;
        --purple:   #7c3aed;
        --tx:       #0f172a;
        --tx2:      #475569;
        --tx3:      #94a3b8;
        --border:   #e2e8f0;
        --border2:  #cbd5e1;
        --glow:     rgba(37,99,235,0.1);
    }"""

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');
    {theme_vars}

    /* ── Base ── */
    .stApp {{ background-color: var(--bg) !important; color: var(--tx) !important; font-family: 'DM Sans', sans-serif; }}
    .main .block-container {{ padding-top: 1.5rem !important; max-width: 900px; }}
    section[data-testid="stSidebar"] {{ background: var(--bg2) !important; border-right: 1px solid var(--border) !important; }}
    section[data-testid="stSidebar"] .block-container {{ padding-top: 1.5rem !important; }}

    /* ── Light mode global text fixes ── */
    .stMarkdown p, .stMarkdown li, .stMarkdown span,
    .stMarkdown strong, .stMarkdown em,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stMarkdownContainer"] span,
    [data-testid="stMarkdownContainer"] strong,
    [data-testid="stMarkdownContainer"] em {{
        color: var(--tx) !important;
    }}

    /* ── Hero Header ── */
    .hero-wrap {{
        text-align: center;
        padding: 2.5rem 1rem 1.5rem;
        position: relative;
    }}
    .hero-badge {{
        display: inline-block;
        font-family: 'DM Mono', monospace;
        font-size: 0.68rem;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: var(--cyan);
        background: rgba(34,211,238,0.12);
        border: 1px solid rgba(34,211,238,0.35);
        padding: 4px 14px;
        border-radius: 100px;
        margin-bottom: 1rem;
    }}
    .hero-title {{
        font-family: 'Syne', sans-serif;
        font-size: 2.6rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        background: {'linear-gradient(135deg, #f1f5f9 0%, #60a5fa 50%, #22d3ee 100%)' if dark else 'linear-gradient(135deg, #0f172a 0%, #2563eb 50%, #0891b2 100%)'};
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 0 0.5rem;
        line-height: 1.15;
    }}
    .hero-sub {{
        font-size: 1rem;
        color: var(--tx2);
        font-weight: 300;
        letter-spacing: 0.01em;
        margin-bottom: 0.3rem;
    }}
    .hero-stats {{
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin-top: 1.2rem;
        padding-top: 1.2rem;
        border-top: 1px solid var(--border);
    }}
    .stat-item {{ text-align: center; }}
    .stat-num {{
        font-family: 'Syne', sans-serif;
        font-size: 1.3rem;
        font-weight: 700;
        color: var(--blue2);
    }}
    .stat-label {{
        font-size: 0.7rem;
        color: var(--tx3);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-family: 'DM Mono', monospace;
    }}

    /* ── Sidebar ── */
    .sidebar-logo {{
        font-family: 'Syne', sans-serif;
        font-size: 1.3rem;
        font-weight: 800;
        color: var(--tx);
        letter-spacing: -0.02em;
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 0.2rem;
    }}
    .sidebar-logo span {{ color: var(--cyan); }}
    .sidebar-section {{
        font-family: 'DM Mono', monospace;
        font-size: 0.62rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--tx3);
        margin: 1.2rem 0 0.6rem;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid var(--border);
    }}
    .status-pill {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.75rem;
        font-family: 'DM Mono', monospace;
        padding: 5px 12px;
        border-radius: 100px;
        width: 100%;
        margin-bottom: 0.5rem;
    }}
    .status-ok  {{ background: rgba(16,185,129,0.12); color: #059669; border: 1px solid rgba(16,185,129,0.35); }}
    .status-err {{ background: rgba(239,68,68,0.12);  color: #dc2626; border: 1px solid rgba(239,68,68,0.35); }}
    .dot {{ width: 6px; height: 6px; border-radius: 50%; background: currentColor; display: inline-block; }}
    .dot-pulse {{ animation: pulse 1.5s infinite; }}
    @keyframes pulse {{ 0%,100%{{opacity:1}} 50%{{opacity:0.4}} }}

    /* ── Chat Messages ── */
    .msg-user {{
        background: var(--card2);
        border: 1px solid var(--border2);
        border-left: 3px solid var(--blue);
        padding: 1rem 1.2rem;
        border-radius: 4px 16px 16px 16px;
        margin: 0.8rem 0;
        font-size: 0.95rem;
        line-height: 1.6;
        color: var(--tx);
    }}
    .msg-user-name {{
        font-family: 'DM Mono', monospace;
        font-size: 0.65rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--blue2);
        margin-bottom: 0.4rem;
    }}
    .msg-ai-label {{
        display: flex;
        align-items: center;
        gap: 8px;
        margin: 1.5rem 0 0.5rem;
    }}
    .msg-ai-line {{
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, var(--green), transparent);
    }}
    .msg-ai-tag {{
        font-family: 'DM Mono', monospace;
        font-size: 0.62rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--green);
    }}

    /* ── Topic Tags ── */
    .tag {{
        display: inline-block;
        background: rgba(59,130,246,0.12);
        color: var(--blue2);
        font-size: 0.65rem;
        font-family: 'DM Mono', monospace;
        padding: 3px 10px;
        border-radius: 100px;
        margin: 2px 3px;
        border: 1px solid rgba(59,130,246,0.35);
        letter-spacing: 0.05em;
    }}

    /* ── Input Area ── */
    .input-wrap {{
        background: var(--card);
        border: 1px solid var(--border2);
        border-radius: 16px;
        padding: 1rem 1.2rem 0.8rem;
        margin-top: 1rem;
        box-shadow: 0 0 40px rgba(59,130,246,0.05);
    }}
    .input-label {{
        font-family: 'DM Mono', monospace;
        font-size: 0.62rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--tx3);
        margin-bottom: 0.5rem;
    }}

    /* ── Welcome Screen ── */
    .welcome-wrap {{
        text-align: center;
        padding: 3rem 1.5rem;
    }}
    .welcome-symbols {{
        font-size: 2.2rem;
        letter-spacing: 0.5rem;
        margin-bottom: 1.5rem;
        opacity: 0.6;
    }}
    .welcome-title {{
        font-family: 'Syne', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--tx);
        margin-bottom: 0.5rem;
    }}
    .welcome-sub {{
        color: var(--tx2);
        font-size: 0.9rem;
        line-height: 1.7;
        max-width: 500px;
        margin: 0 auto 1.5rem;
    }}
    .feature-grid {{
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 0.8rem;
        max-width: 500px;
        margin: 0 auto;
    }}
    .feature-card {{
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 0.9rem 1rem;
        text-align: left;
    }}
    .feature-icon {{ font-size: 1.3rem; margin-bottom: 0.3rem; }}
    .feature-title {{
        font-family: 'Syne', sans-serif;
        font-size: 0.8rem;
        font-weight: 700;
        color: var(--tx);
        margin-bottom: 0.2rem;
    }}
    .feature-desc {{ font-size: 0.72rem; color: var(--tx2); line-height: 1.4; }}

    /* ── Buttons ── */
    .stButton > button {{
        background: linear-gradient(135deg, #1d4ed8, #2563eb) !important;
        color: #fff !important;
        border: 1px solid rgba(96,165,250,0.3) !important;
        border-radius: 10px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.01em !important;
        transition: all 0.2s !important;
        padding: 0.45rem 1rem !important;
    }}
    .stButton > button:hover {{
        background: linear-gradient(135deg, #2563eb, #3b82f6) !important;
        border-color: rgba(96,165,250,0.6) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 20px rgba(59,130,246,0.3) !important;
    }}
    /* ── Sidebar buttons (Quick Examples, Plot, Compute etc) — ORIGINAL style ── */
    .stButton > button[kind="secondary"],
    [data-testid="baseButton-secondary"] {{
        background: var(--card2) !important;
        border: 1px solid var(--border2) !important;
        color: var(--tx2) !important;
    }}
    .stButton > button[kind="secondary"]:hover,
    [data-testid="baseButton-secondary"]:hover {{
        background: var(--border2) !important;
        color: var(--tx) !important;
    }}

    /* ── 4 specific buttons: 👍 👎 ✏️ Edit + theme toggle ── */
    .main [data-testid="baseButton-secondary"] {{
        background: {'#2d3748' if dark else 'transparent'} !important;
        border: 1px solid {'#4a5568' if dark else '#94a3b8'} !important;
        color: {'#f1f5f9' if dark else '#1e293b'} !important;
    }}
    .main [data-testid="baseButton-secondary"]:hover {{
        background: {'#4a5568' if dark else '#e2e8f0'} !important;
        border-color: {'#60a5fa' if dark else '#2563eb'} !important;
        color: {'#60a5fa' if dark else '#1e293b'} !important;
    }}
    section[data-testid="stSidebar"] [data-testid="column"] [data-testid="baseButton-secondary"] {{
        background: {'#2d3748' if dark else 'transparent'} !important;
        border: 1px solid {'#4a5568' if dark else '#94a3b8'} !important;
        color: {'#f1f5f9' if dark else '#1e293b'} !important;
    }}
    section[data-testid="stSidebar"] [data-testid="column"] [data-testid="baseButton-secondary"]:hover {{
        background: {'#4a5568' if dark else '#e2e8f0'} !important;
        border-color: {'#60a5fa' if dark else '#2563eb'} !important;
        color: {'#60a5fa' if dark else '#1e293b'} !important;
    }}
    /* ── Toast message text ── */
    [data-testid="stToast"] {{
        background: {'#1e293b' if dark else '#ffffff'} !important;
        color: {'#ffffff' if dark else '#0f172a'} !important;
    }}
    [data-testid="stToast"] p,
    [data-testid="stToast"] span,
    [data-testid="stToast"] div {{
        color: {'#ffffff' if dark else '#0f172a'} !important;
    }}
    /* ── Tooltip popup text (help= on buttons) ── */
    div[data-testid="stTooltipContent"],
    div[data-testid="stTooltipContent"] p,
    div[data-testid="stTooltipContent"] span,
    [role="tooltip"],
    [role="tooltip"] p {{
        background: #1e293b !important;
        color: #f1f5f9 !important;
        border: 1px solid #334155 !important;
        border-radius: 6px !important;
        font-size: 0.75rem !important;
    }}


    /* ── Inputs ── */
    .stTextArea textarea, .stTextInput input {{
        background: var(--bg2) !important;
        color: var(--tx) !important;
        caret-color: var(--blue) !important;
        border: 1px solid var(--border2) !important;
        border-radius: 10px !important;
        font-family: 'DM Mono', monospace !important;
        font-size: 0.88rem !important;
    }}
    .stTextArea textarea::placeholder, .stTextInput input::placeholder {{
        color: var(--tx3) !important;
        opacity: 1 !important;
    }}
    .stTextArea textarea:focus, .stTextInput input:focus {{
        border-color: var(--blue) !important;
        box-shadow: 0 0 0 2px rgba(59,130,246,0.15) !important;
    }}
    .stSelectbox > div > div {{
        background: var(--bg2) !important;
        border: 1px solid var(--border2) !important;
        border-radius: 10px !important;
        color: var(--tx) !important;
    }}
    /* ── File Uploader & Browse button ── */
    .stFileUploader {{
        background: var(--card) !important;
        border: 1px dashed var(--border2) !important;
        border-radius: 12px !important;
    }}
    [data-testid="stFileUploadDropzone"] button,
    .stFileUploader button,
    [data-testid="baseButton-secondary"][kind="secondary"] {{
        background: var(--card2) !important;
        color: var(--tx) !important;
        border: 1px solid var(--border2) !important;
        border-radius: 8px !important;
    }}
    [data-testid="stFileUploadDropzone"] button:hover,
    .stFileUploader button:hover {{
        background: var(--border2) !important;
        color: var(--tx) !important;
        border-color: var(--blue) !important;
    }}
    [data-testid="stFileUploadDropzone"] span,
    [data-testid="stFileUploadDropzone"] p,
    [data-testid="stFileUploadDropzone"] small,
    .stFileUploader span,
    .stFileUploader p,
    .stFileUploader small {{
        color: var(--tx2) !important;
    }}

    /* ── Dividers & misc ── */
    hr {{ border-color: var(--border) !important; opacity: 0.5 !important; }}
    .stCaption {{ color: var(--tx3) !important; font-family: 'DM Mono', monospace !important; font-size: 0.7rem !important; }}
    .stExpander {{ background: var(--card) !important; border: 1px solid var(--border) !important; border-radius: 10px !important; }}
    .stAlert {{ border-radius: 10px !important; }}
    .stMetric {{ background: var(--card) !important; border: 1px solid var(--border) !important; border-radius: 10px !important; padding: 0.6rem !important; }}
    .stMetric label, [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] p {{
        color: var(--tx3) !important; font-family: 'DM Mono', monospace !important;
        font-size: 0.65rem !important; text-transform: uppercase !important; letter-spacing: 0.08em !important;
    }}
    [data-testid="stMetricValue"], [data-testid="stMetricValue"] > div,
    .stMetric [data-testid="metric-container"] > div:last-child {{
        color: var(--blue2) !important; font-family: 'Syne', sans-serif !important;
        font-size: 1.4rem !important; font-weight: 700 !important;
    }}

    /* ── Scrollbar ── */
    ::-webkit-scrollbar {{ width: 5px; }}
    ::-webkit-scrollbar-track {{ background: var(--bg); }}
    ::-webkit-scrollbar-thumb {{ background: var(--border2); border-radius: 10px; }}

    /* ── Mobile tweaks ── */
    @media (max-width: 768px) {{
        .hero-title {{ font-size: 1.8rem !important; }}
        .hero-sub {{ font-size: 0.82rem !important; }}
        .feature-grid {{ grid-template-columns: 1fr !important; }}
        .main .block-container {{ padding: 0.5rem !important; }}
        .stButton > button {{ min-height: 44px !important; font-size: 0.9rem !important; }}
        .stTextArea textarea {{ font-size: 0.95rem !important; min-height: 60px !important; }}
        .msg-user {{ font-size: 0.88rem !important; padding: 0.75rem !important; }}
        .hero-stats {{ gap: 1rem !important; }}
        .stat-num {{ font-size: 1rem !important; }}
    }}

    /* ── Radio ── */
    .stRadio > div {{ gap: 0.4rem !important; }}
    .stRadio > div label {{ padding: 4px 8px; border-radius: 8px; cursor: pointer; }}
    .stRadio > div label p {{ font-size: 0.82rem !important; color: var(--tx2) !important; font-family: 'DM Sans', sans-serif !important; }}

    /* ════════════════════════════════════════════════════════
       FIX 1 — Expander label & content text in BOTH themes
       ════════════════════════════════════════════════════════ */
    /* Expander toggle/summary text */
    .stExpander details summary,
    .stExpander details summary p,
    .stExpander details summary span,
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary p {{
        color: var(--tx) !important;
        background: var(--card) !important;
    }}
    /* Expander body */
    .stExpander details,
    [data-testid="stExpander"] details,
    [data-testid="stExpanderDetails"],
    .stExpander details > div {{
        background: var(--card) !important;
        color: var(--tx) !important;
    }}
    /* Text inside expander */
    .stExpander p,
    .stExpander li,
    .stExpander span,
    [data-testid="stExpanderDetails"] p,
    [data-testid="stExpanderDetails"] li {{
        color: var(--tx) !important;
    }}

    /* ════════════════════════════════════════════════════════
       FIX 2 — st.code inside expander (copy text block)
       ════════════════════════════════════════════════════════ */
    .stExpander pre,
    .stExpander pre code,
    [data-testid="stExpanderDetails"] pre,
    [data-testid="stExpanderDetails"] pre code,
    [data-testid="stCode"] pre,
    [data-testid="stCode"] code {{
        background: var(--bg2) !important;
        color: var(--tx) !important;
        border: 1px solid var(--border2) !important;
        border-radius: 8px !important;
        font-family: 'DM Mono', monospace !important;
        font-size: 0.82rem !important;
        line-height: 1.75 !important;
        white-space: pre-wrap !important;
        word-break: break-word !important;
    }}
    /* Copy button on st.code */
    [data-testid="stCode"] button {{
        background: var(--card2) !important;
        color: var(--tx2) !important;
        border: 1px solid var(--border2) !important;
        border-radius: 6px !important;
    }}
    [data-testid="stCode"] button:hover {{
        background: var(--border2) !important;
        color: var(--tx) !important;
    }}

    /* ════════════════════════════════════════════════════════
       FIX 3 — st.warning / st.error / st.info visibility
       Always show proper contrast regardless of theme
       ════════════════════════════════════════════════════════ */
    [data-testid="stAlert"] {{
        border-radius: 10px !important;
    }}
    /* Warning — amber */
    [data-testid="stAlert"][data-baseweb="notification"][kind="warning"],
    div[data-testid="stAlert"].st-ae {{
        background: rgba(245,158,11,0.12) !important;
        border: 1px solid rgba(245,158,11,0.5) !important;
    }}
    [data-testid="stAlert"] p,
    [data-testid="stAlert"] div,
    [data-testid="stAlert"] span,
    div.stAlert p {{
        color: var(--tx) !important;
        opacity: 1 !important;
    }}
    /* Force warning icon & text colour in light mode */
    .element-container .stAlert > div {{
        color: var(--tx) !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    for k, v in [("session_id", str(uuid.uuid4())[:8]), ("messages", []),
                 ("engine", None), ("kb_ready", False),
                 ("query_count", 0), ("pending", None),
                 ("today_count", 0), ("streak", 1),
                 ("last_date", str(datetime.now(timezone.utc).date()))]:
        if k not in st.session_state:
            st.session_state[k] = v

    # ── Update streak daily ──────────────────────────────────────────
    _today = str(datetime.now(timezone.utc).date())
    if st.session_state.get("last_date") != _today:
        st.session_state.last_date   = _today
        st.session_state.today_count = 0
        _yesterday = str((datetime.now(timezone.utc).date() - __import__('datetime').timedelta(days=1)))
        if st.session_state.get("prev_date") == _yesterday:
            st.session_state.streak = st.session_state.get("streak", 1) + 1
        else:
            st.session_state.streak = 1
    st.session_state["prev_date"] = _today

    with st.sidebar:
        # ── Logo + Theme Toggle ───────────────────────────────────────
        logo_col, theme_col = st.columns([3, 1])
        with logo_col:
            st.markdown("""
            <div class="sidebar-logo">
                <span>∫</span> MathAI
            </div>
            <div style="font-family:'DM Mono',monospace;font-size:0.65rem;color:var(--tx2);margin-bottom:0.5rem;">
                Advanced Mathematics Assistant
            </div>
            """, unsafe_allow_html=True)
        with theme_col:
            st.markdown("<br>", unsafe_allow_html=True)
            theme_icon = "☀️" if dark else "🌙"
            if st.button(theme_icon, key="theme_toggle", help="Toggle dark/light mode"):
                st.session_state.theme = "light" if dark else "dark"
                st.rerun()

        if GROQ_API_KEY and GROQ_API_KEY != "your_groq_api_key_here":
            st.markdown(f'<div class="status-pill status-ok"><span class="dot dot-pulse"></span> Groq LLM · {LLM_MODEL.split("-")[0].upper()}</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-family:DM Mono,monospace;font-size:0.6rem;color:var(--tx3);margin-top:-0.3rem;padding-left:2px;">Free tier: 30 req/min · auto-retry on</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-pill status-err"><span class="dot"></span> No API Key — check .env</div>', unsafe_allow_html=True)

        # ── NCERT Practice Section ────────────────────────────────────
        st.markdown(
            "<div style='font-family:DM Mono,monospace;font-size:0.6rem;"
            "text-transform:uppercase;letter-spacing:0.1em;color:var(--tx2);"
            "margin:0.3rem 0 0.5rem;'>📚 NCERT Practice</div>",
            unsafe_allow_html=True
        )

        # Class selector — only 2 labels for now
        _cls_opts = ["Class 9", "Class 10"]
        _cls_icons = {"Class 9": "📒", "Class 10": "📓"}
        _cls_display = [f"{_cls_icons[c]} {c}" for c in _cls_opts]
        _sel_cls_disp = st.selectbox(
            "Class:", options=_cls_display,
            key="class_selector_v2", label_visibility="collapsed"
        )
        selected_class = "📒 Class 9" if "9" in _sel_cls_disp else "📓 Class 10"

        # Keep TOPIC_FILTER_MAP for classic examples (used later)
        TOPIC_FILTER_MAP = {"All Topics": None}
        selected_topic = "All Topics" 
        # ── QUIZ SECTION: Class → Chapter → Exercise → Questions ────
        # Cache quiz map by doc count — rebuilds only if knowledge_base changes
        import re as _re
        _doc_count = len(MATH_KNOWLEDGE_BASE)
        if (st.session_state.get("_qmap_count") != _doc_count
                or "class_9" not in st.session_state.get("_qmap_data", {})
                or "class_10" not in st.session_state.get("_qmap_data", {})):
            _qmap_build = {}
            for _doc in MATH_KNOWLEDGE_BASE:
                _m = _doc.metadata
                _cl = _m.get("class_level","")
                _ch = _m.get("chapter","")
                _ex = _m.get("exercise","")
                if not (_cl and _ch and _ex):
                    continue
                _qs = _re.findall(r'Q\d+[^\n]*(?:\n(?!Q\d+)[^\n]*)*', _doc.page_content)
                if _qs:
                    _qmap_build.setdefault(_cl, {}).setdefault(_ch, {})[_ex] = _qs
            st.session_state["_qmap_data"]  = _qmap_build
            st.session_state["_qmap_count"] = _doc_count
        _QUIZ_MAP = st.session_state["_qmap_data"]

        # Class key from selected_class (has emoji like "📒 Class 9")
        _class_key = "class_10" if "10" in str(selected_class) else "class_9"
        _avail_ch  = _QUIZ_MAP.get(_class_key, {})

        # Chapter names display map
        _CH_NAMES = {
            "class_9": {
                "ch1":"Ch1 · Number Systems","ch2":"Ch2 · Polynomials",
                "ch3":"Ch3 · Coordinate Geometry","ch4":"Ch4 · Linear Equations",
                "ch5":"Ch5 · Euclid's Geometry","ch6":"Ch6 · Lines & Angles",
                "ch7":"Ch7 · Triangles","ch8":"Ch8 · Quadrilaterals",
                "ch9":"Ch9 · Circles","ch10":"Ch10 · Heron's Formula",
                "ch11":"Ch11 · Surface Areas","ch12":"Ch12 · Statistics",
            },
            "class_10": {
                "ch1":"Ch1 · Real Numbers","ch2":"Ch2 · Polynomials",
                "ch3":"Ch3 · Linear Equations","ch4":"Ch4 · Quadratic Equations",
                "ch5":"Ch5 · Arithmetic Progressions","ch6":"Ch6 · Triangles",
                "ch7":"Ch7 · Coordinate Geometry","ch8":"Ch8 · Trigonometry",
                "ch9":"Ch9 · Applications of Trig","ch10":"Ch10 · Circles",
                "ch11":"Ch11 · Areas & Circles","ch12":"Ch12 · Surface Areas",
                "ch13":"Ch13 · Statistics","ch14":"Ch14 · Probability",
            },
        }
        _ch_keys = sorted(_avail_ch.keys(),
            key=lambda x: int(x.replace("ch","")) if x.replace("ch","").isdigit() else 99)
        _ch_opts  = [_CH_NAMES.get(_class_key,{}).get(c, c.upper()) for c in _ch_keys]

        if not _ch_keys:
            st.markdown(
                "<div style='font-size:0.72rem;color:var(--tx2);padding:0.3rem;'>No exercises found.</div>",
                unsafe_allow_html=True)
        else:
            # ── Chapter selectbox — key includes class so it resets on class change
            _sel_ch_disp = st.selectbox(
                "Chapter:", options=_ch_opts,
                key=f"qz_ch_{_class_key}",
                label_visibility="collapsed"
            )
            _sel_ch_key = _ch_keys[_ch_opts.index(_sel_ch_disp)]

            # ── Exercise selectbox — key includes chapter so it resets on chapter change
            _exs = sorted(_avail_ch.get(_sel_ch_key, {}).keys())
            if not _exs:
                st.markdown(
                    "<div style='font-size:0.72rem;color:var(--tx2);'>No exercises found.</div>",
                    unsafe_allow_html=True)
            else:
                _sel_ex = st.selectbox(
                    "Exercise:", options=_exs,
                    key=f"qz_ex_{_class_key}_{_sel_ch_key}",
                    label_visibility="collapsed"
                )

                # ── Get questions for this exact exercise
                _qs_list = _avail_ch.get(_sel_ch_key, {}).get(_sel_ex, [])

                if not _qs_list:
                    st.markdown(
                        "<div style='font-size:0.72rem;color:var(--tx2);'>No questions found.</div>",
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        f"<div style='font-family:DM Mono,monospace;font-size:0.58rem;"
                        f"text-transform:uppercase;letter-spacing:0.07em;color:var(--tx2);"
                        f"margin:0.5rem 0 0.4rem;'>{len(_qs_list)} questions</div>",
                        unsafe_allow_html=True
                    )

                    # ── Active question highlight card ────────────────
                    _active_text = st.session_state.get("qz_active_text", "")
                    _active_qnum = st.session_state.get("qz_active_qnum", "")
                    _show_stuck  = st.session_state.get("qz_show_stuck", False)
                    _show_fu     = st.session_state.get("qz_show_fu", False)

                    if _active_text and _active_qnum:
                        _aq_first = _active_text.split("\n")[0][:60].strip()
                        st.markdown(
                            f"<div style='background:rgba(99,102,241,0.1);border:1.5px solid "
                            f"rgba(99,102,241,0.4);border-radius:10px;padding:0.5rem 0.7rem;"
                            f"margin:0.4rem 0 0.5rem;'>"
                            f"<div style='font-size:0.58rem;font-family:DM Mono,monospace;"
                            f"text-transform:uppercase;letter-spacing:0.07em;color:rgba(99,102,241,0.9);"
                            f"margin-bottom:0.2rem;'>📌 Active Question</div>"
                            f"<div style='font-size:0.7rem;font-weight:600;color:var(--tx);"
                            f"line-height:1.4;'>{_aq_first}</div></div>",
                            unsafe_allow_html=True
                        )

                    import re as _re2
                    # ── Render each question with inline stuck menu ───
                    for _qi, _qtext in enumerate(_qs_list):
                        _first  = _qtext.split("\n")[0][:55].strip()
                        _nm     = _re2.match(r'(Q\d+)', _first)
                        _qnum   = _nm.group(1) if _nm else f"Q{_qi+1}"
                        _rest   = _first[len(_qnum):].strip('. ').strip()[:38]
                        _label  = f"{_qnum}. {_rest}..." if _rest else _qnum
                        _q_only = _qtext.split("Answer:")[0].strip()
                        _is_active   = (_qnum == _active_qnum)
                        _stuck_here  = _is_active and _show_stuck
                        _fu_here     = _is_active and _show_fu
                        _q_stored_i  = _qtext.split("Answer:")[0].strip()

                        # Question label — highlight if active
                        _qlabel_style = (
                            "font-size:0.71rem;font-weight:700;color:#818cf8;"
                            "margin:0.55rem 0 0.12rem;padding-left:2px;line-height:1.4;"
                        ) if _is_active else (
                            "font-size:0.71rem;font-weight:600;color:var(--tx);"
                            "margin:0.55rem 0 0.12rem;padding-left:2px;line-height:1.4;"
                        )
                        st.markdown(
                            f"<div style='{_qlabel_style}'>{_label}</div>",
                            unsafe_allow_html=True
                        )

                        # 4 buttons in 2×2 grid
                        _b1, _b2 = st.columns(2)
                        _bk = f"qz_{_class_key}_{_sel_ch_key}_{_sel_ex}_{_qi}"

                        with _b1:
                            if st.button("💡 Hint", key=f"{_bk}_h", use_container_width=True):
                                st.session_state["qz_active_text"] = _qtext
                                st.session_state["qz_active_qnum"] = _qnum
                                st.session_state["qz_show_stuck"]  = False
                                st.session_state["qz_show_fu"]     = True
                                st.session_state["quiz_replace"]   = True
                                st.session_state.pending = (
                                    f"Give ONE small hint — just a nudge, no steps or answer:\n{_q_only}"
                                )
                                st.rerun()
                            if st.button("✅ Answer", key=f"{_bk}_a", use_container_width=True, type="primary"):
                                st.session_state["qz_active_text"] = _qtext
                                st.session_state["qz_active_qnum"] = _qnum
                                st.session_state["qz_show_stuck"]  = False
                                st.session_state["qz_show_fu"]     = True
                                st.session_state["quiz_replace"]   = True
                                st.session_state.pending = (
                                    f"Explain step by step like a whiteboard teacher:\n{_qtext}"
                                )
                                st.rerun()
                        with _b2:
                            if st.button("📖 Steps", key=f"{_bk}_s", use_container_width=True):
                                st.session_state["qz_active_text"] = _qtext
                                st.session_state["qz_active_qnum"] = _qnum
                                st.session_state["qz_show_stuck"]  = False
                                st.session_state["qz_show_fu"]     = True
                                st.session_state["quiz_replace"]   = True
                                st.session_state.pending = (
                                    f"Show the method only — no final answer:\n{_q_only}"
                                )
                                st.rerun()
                            if st.button("❓ Ask AI", key=f"{_bk}_q", use_container_width=True):
                                st.session_state["qz_active_text"] = _qtext
                                st.session_state["qz_active_qnum"] = _qnum
                                st.session_state["qz_show_stuck"]  = True
                                st.session_state["qz_show_fu"]     = False
                                st.rerun()

                        # ── INLINE stuck menu — shows right under THIS question ──
                        if _stuck_here:
                            st.markdown(
                                f"<div style='background:rgba(99,102,241,0.08);border:1px solid "
                                f"rgba(99,102,241,0.3);border-radius:9px;padding:0.45rem 0.6rem;"
                                f"margin:0.3rem 0 0.2rem;font-size:0.65rem;font-weight:700;"
                                f"color:rgba(99,102,241,0.9);text-transform:uppercase;"
                                f"letter-spacing:0.06em;'>Where are you stuck?</div>",
                                unsafe_allow_html=True
                            )
                            _stuck_list = [
                                ("🔢 No idea where to start",
                                 f"Student has no idea where to begin. Give ONE clear starting "
                                 f"point — just the very first step, nothing more:\n{_q_stored_i}"),
                                ("➡️ Stuck in the middle",
                                 f"Student got stuck halfway. Explain the key middle step that "
                                 f"is usually hardest in this type of question:\n{_q_stored_i}"),
                                ("❌ My answer is different",
                                 f"List the 3 most common mistakes in this question, "
                                 f"then show correct approach:\n{_qtext}"),
                                ("🤔 Don't understand concept",
                                 f"Explain the concept simply with a real-life example first, "
                                 f"then apply to this question:\n{_q_stored_i}"),
                                ("📐 Show easier example first",
                                 f"Create a simpler version, solve it step by step, then show "
                                 f"how same method applies to original:\n{_q_stored_i}"),
                            ]
                            for _sl, _sp in _stuck_list:
                                if st.button(_sl, key=f"sk_{_qnum}_{_bk}_{_sl[:5]}",
                                             use_container_width=True):
                                    st.session_state["qz_show_stuck"] = False
                                    st.session_state["qz_show_fu"]    = True
                                    st.session_state["quiz_replace"]  = True
                                    st.session_state.pending = _sp
                                    st.rerun()
                            if st.button("✅ Full answer", key=f"sk_{_qnum}_{_bk}_full",
                                         use_container_width=True, type="primary"):
                                st.session_state["qz_show_stuck"] = False
                                st.session_state["qz_show_fu"]    = True
                                st.session_state["quiz_replace"]  = True
                                st.session_state.pending = (
                                    f"Explain step by step like a whiteboard teacher:\n{_qtext}"
                                )
                                st.rerun()

                        # ── INLINE follow-up — shows right under THIS question ──
                        if _fu_here:
                            st.markdown(
                                f"<div style='background:rgba(16,185,129,0.07);border:1px solid "
                                f"rgba(16,185,129,0.25);border-radius:9px;padding:0.45rem 0.6rem;"
                                f"margin:0.3rem 0 0.2rem;font-size:0.65rem;font-weight:700;"
                                f"color:rgba(16,185,129,0.9);text-transform:uppercase;"
                                f"letter-spacing:0.06em;'>💬 Did that help?</div>",
                                unsafe_allow_html=True
                            )
                            _fa, _fb = st.columns(2)
                            _fk = f"fu_{_qnum}_{_bk}"
                            with _fa:
                                if st.button("✅ Yes!", key=f"{_fk}_y",
                                             use_container_width=True, type="primary"):
                                    st.session_state["qz_active_text"] = ""
                                    st.session_state["qz_active_qnum"] = ""
                                    st.session_state["qz_show_fu"]     = False
                                    st.session_state["quiz_replace"]   = True
                                    st.session_state.pending = (
                                        "Student understood. Give 1-line encouragement only."
                                    )
                                    st.rerun()
                                if st.button("❓ Doubt", key=f"{_fk}_d",
                                             use_container_width=True):
                                    st.session_state["qz_show_fu"]  = False
                                    st.session_state["quiz_replace"] = True
                                    st.session_state.pending = (
                                        f"Student has a doubt. Ask which step is confusing:\n{_q_stored_i}"
                                    )
                                    st.rerun()
                            with _fb:
                                if st.button("🔁 Differently", key=f"{_fk}_r",
                                             use_container_width=True):
                                    st.session_state["qz_show_fu"]  = False
                                    st.session_state["quiz_replace"] = True
                                    st.session_state.pending = (
                                        f"Explain using completely different approach — "
                                        f"real-life analogy or simpler method:\n{_qtext}"
                                    )
                                    st.rerun()
                                if st.button("✅ Full Ans", key=f"{_fk}_f",
                                             use_container_width=True):
                                    st.session_state["qz_show_fu"]     = False
                                    st.session_state["quiz_replace"]   = True
                                    st.session_state.pending = (
                                        f"Explain complete solution step by step:\n{_qtext}"
                                    )
                                    st.rerun()

                    # ── Part A: Follow-up after hint/steps/stuck ──────
                    if _active_text and _show_fu:
                        st.markdown(
                            f"<div style='background:rgba(16,185,129,0.07);border:1px solid "
                            f"rgba(16,185,129,0.25);border-radius:9px;padding:0.5rem 0.7rem;"
                            f"margin:0.5rem 0 0.3rem;font-size:0.68rem;font-weight:700;"
                            f"color:var(--tx2);text-transform:uppercase;letter-spacing:0.06em;'>"
                            f"💬 Did that help?</div>",
                            unsafe_allow_html=True
                        )
                        _fa, _fb = st.columns(2)
                        _fk = f"fu_{_active_qnum}"
                        with _fa:
                            if st.button("✅ Yes, got it!", key=f"{_fk}_y",
                                         use_container_width=True, type="primary"):
                                st.session_state["qz_active_text"] = ""
                                st.session_state["qz_active_qnum"] = ""
                                st.session_state["qz_show_fu"]     = False
                                st.session_state["quiz_replace"]   = True
                                st.session_state.pending = (
                                    "Student understood. Give a 1-line encouraging response only."
                                )
                                st.rerun()
                            if st.button("❓ I have a doubt", key=f"{_fk}_d",
                                         use_container_width=True):
                                st.session_state["qz_show_fu"]  = False
                                st.session_state["quiz_replace"] = True
                                st.session_state.pending = (
                                    f"Student has a doubt about {_active_qnum}. "
                                    f"Ask which step is confusing, then wait:\n{_q_stored}"
                                )
                                st.rerun()
                        with _fb:
                            if st.button("🔁 Explain differently", key=f"{_fk}_r",
                                         use_container_width=True):
                                st.session_state["qz_show_fu"]  = False
                                st.session_state["quiz_replace"] = True
                                st.session_state.pending = (
                                    f"Explain using a completely different approach — "
                                    f"real-life analogy or simpler method:\n{_active_text}"
                                )
                                st.rerun()
                            if st.button("✅ Full Answer", key=f"{_fk}_f",
                                         use_container_width=True):
                                st.session_state["qz_show_fu"]     = False
                                st.session_state["quiz_replace"]   = True
                                st.session_state.pending = (
                                    f"Explain complete solution step by step:\n{_active_text}"
                                )
                                st.rerun()

        _show_classic = st.checkbox("📚 Chapter examples", key="show_classic_chapters", value=False)
        if _show_classic and selected_class in CLASS_EXAMPLES:
            chapters = CLASS_EXAMPLES[selected_class]
            topic_keywords = TOPIC_FILTER_MAP.get(selected_topic)
            for chapter_name, question in chapters.items():
                if topic_keywords:
                    chapter_lower = chapter_name.lower() + " " + question.lower()
                    if not any(kw in chapter_lower for kw in topic_keywords):
                        continue
                if st.button(chapter_name, key=f"ch_{chapter_name}", use_container_width=True):
                    st.session_state.pending = question
                    st.rerun()

        st.markdown('<div class="sidebar-section">Graph Plotter</div>', unsafe_allow_html=True)
        gexpr  = st.text_input("Function(s):", placeholder="x**2, sin(x)")
        grange = st.slider("x range", -20, 20, (-10, 10))
        gtitle = st.text_input("Title:", placeholder="My Graph")
        if st.button("📊 Plot", use_container_width=True) and gexpr:
            render_graph(gexpr, grange, gtitle)

        st.markdown('<div class="sidebar-section">Symbolic Compute</div>', unsafe_allow_html=True)
        sym_in  = st.text_input("Expression:", placeholder="x**3 + 2*x")
        sym_act = st.selectbox("Action:", ["Differentiate", "Integrate", "Solve (=0)", "Simplify"])
        if st.button("⚡ Compute", use_container_width=True) and sym_in:
            sym = SymbolicMathEngine()
            result = (sym.differentiate(sym_in)        if sym_act == "Differentiate" else
                      sym.integrate(sym_in)             if sym_act == "Integrate"    else
                      sym.solve_equation(sym_in + "=0") if sym_act == "Solve (=0)"  else
                      sym.try_solve(sym_in))
            if result:
                st.success(result)
            else:
                st.warning("Could not compute symbolically")

        st.markdown('<div class="sidebar-section">Upload PDF</div>', unsafe_allow_html=True)
        uploaded_pdf = st.file_uploader(
            "Choose PDF file", type=["pdf"], label_visibility="collapsed")

        if uploaded_pdf is not None:
            pdf_hash = hashlib.md5(uploaded_pdf.getvalue()).hexdigest()

            # ── Only process once per unique uploaded file ─────────────
            if st.session_state.get("last_pdf_hash") != pdf_hash:
                st.session_state.last_pdf_hash     = pdf_hash
                st.session_state.pdf_status        = None
                st.session_state.pdf_detected_type = None

                # Use tempfile to avoid name collisions across concurrent sessions
                suffix = Path(uploaded_pdf.name).suffix or ".pdf"
                tmp_fd, tmp_path = tempfile.mkstemp(suffix=suffix)
                with os.fdopen(tmp_fd, "wb") as f2:
                    f2.write(uploaded_pdf.getvalue())

                with st.spinner("📖 Reading PDF..."):
                    try:
                        pdf_docs    = MathDataLoader().load_pdf(tmp_path)
                        all_text    = " ".join(d.page_content.lower() for d in pdf_docs)
                        total_words = len(all_text.split())

                        if not pdf_docs or total_words < 30:
                            st.session_state.pdf_status = "empty"
                        else:
                            # ── Strict math-only keywords (not in everyday English) ──
                            STRICT_MATH = [
                                "equation", "derivative", "integral", "differentiate",
                                "integrate", "calculus", "algebra", "trigonometry",
                                "polynomial", "quadratic", "eigenvalue", "determinant",
                                "theorem", "logarithm", "exponent", "coefficient",
                                "binomial", "permutation", "combination", "modular",
                                "arithmetic", "geometry", "probability", "variance",
                                "matrix", "gradient", "divergence", "laplace", "fourier",
                                "numerator", "denominator", "hypotenuse", "asymptote",
                                "parabola", "hyperbola", "ellipse", "congruent",
                                "factorize", "simplify", "differentiation", "integration",
                                "d/dx", "dy/dx", "f(x)", "g(x)", "ax²", "bx+c",
                                "∫", "∑", "∂", "√", "∞", "±", "²", "³",
                            ]
                            math_hits  = sum(1 for kw in STRICT_MATH if kw in all_text)
                            math_lines = len(re.findall(
                                r'\b\d+[\+\-\*/\^=]\d+\b|=\s*[\d\-]|\bx\s*=|\by\s*=', all_text))
                            is_math_pdf = (math_hits >= 4) or (math_hits >= 2 and math_lines >= 3)

                            if not is_math_pdf:
                                DOC_TYPES = {
                                    "📄 Resume / CV": [
                                        "experience", "skills", "education", "resume",
                                        "curriculum vitae", "employment", "linkedin",
                                        "references", "internship", "bachelor", "master",
                                        "gpa", "cgpa", "projects", "achievements",
                                        "objective", "career", "certification"],
                                    "📰 News / Article": [
                                        "published", "reporter", "journalist", "editor",
                                        "breaking news", "according to", "press release",
                                        "subscribe", "headline", "sources said"],
                                    "📖 Story / Novel / Essay": [
                                        "chapter", "once upon", "he said", "she said",
                                        "fiction", "narrative", "plot", "character",
                                        "dialogue", "protagonist", "author"],
                                    "🧾 Invoice / Receipt": [
                                        "invoice", "receipt", "total amount", "payment",
                                        "billing", "gst", "quantity", "order number",
                                        "due date", "subtotal", "discount", "vendor"],
                                    "⚖️ Legal Document": [
                                        "hereby", "clause", "agreement", "whereas",
                                        "plaintiff", "defendant", "jurisdiction",
                                        "contract", "liability", "terms and conditions"],
                                    "🍽️ Recipe / Food": [
                                        "ingredients", "tablespoon", "teaspoon", "bake",
                                        "recipe", "preheat", "oven", "serving", "cuisine",
                                        "cook", "boil", "fry", "garnish"],
                                    "💼 Business / Report": [
                                        "revenue", "profit", "quarterly", "stakeholder",
                                        "strategy", "market share", "fiscal", "kpi",
                                        "roi", "budget", "forecast", "annual report"],
                                    "🔬 Science (Non-Math)": [
                                        "biology", "chemistry", "organism", "cell",
                                        "molecule", "species", "evolution", "experiment",
                                        "hypothesis", "dna", "protein", "ecosystem"],
                                }
                                detected_type = "📁 Unknown document type"
                                best_score    = 0
                                for dtype, kws in DOC_TYPES.items():
                                    score = sum(1 for kw in kws if kw in all_text)
                                    if score > best_score:
                                        best_score    = score
                                        detected_type = dtype
                                if total_words < 100:
                                    detected_type = "🖼️ Scanned / Image-based PDF (no readable text)"

                                st.session_state.pdf_status        = "wrong"
                                st.session_state.pdf_detected_type = detected_type
                                st.session_state.pdf_math_hits     = math_hits
                            else:
                                clean  = MathDataPreprocessor().preprocess_documents(pdf_docs)
                                chunks = MathTextSplitter().split_documents(clean)
                                if st.session_state.engine and chunks:
                                    st.session_state.engine.vector_store.add_documents(chunks)
                                    st.session_state.pdf_status    = "ok"
                                    st.session_state.pdf_pages     = len(pdf_docs)
                                    st.session_state.pdf_math_hits = math_hits
                                else:
                                    st.session_state.pdf_status = "empty"

                    except Exception as e:
                        st.session_state.pdf_status = f"error:{e}"
                    finally:
                        if os.path.exists(tmp_path):
                            os.remove(tmp_path)

            # ── Show stored result (persists across all reruns) ─────────
            status = st.session_state.get("pdf_status")

            if status == "empty":
                st.markdown(f"""
                <div style="background:{'rgba(239,68,68,0.12)' if dark else '#fff1f2'};
                    border:1px solid {'rgba(239,68,68,0.45)' if dark else '#fca5a5'};
                    border-radius:10px;padding:0.9rem 1rem;margin:0.4rem 0;">
                    <div style="color:{'#f87171' if dark else '#dc2626'};font-weight:600;font-size:0.85rem;">
                        ❌ PDF is empty or unreadable
                    </div>
                    <div style="color:{'#fca5a5' if dark else '#991b1b'};font-size:0.75rem;margin-top:0.3rem;">
                        No text could be extracted. Try a different PDF.
                    </div>
                </div>""", unsafe_allow_html=True)

            elif status == "wrong":
                detected_type = st.session_state.get("pdf_detected_type", "📁 Unknown")
                math_hits     = st.session_state.get("pdf_math_hits", 0)
                st.markdown(f"""
                <div style="background:{'rgba(239,68,68,0.12)' if dark else '#fff1f2'};
                    border:1px solid {'rgba(239,68,68,0.45)' if dark else '#fca5a5'};
                    border-radius:10px;padding:0.9rem 1rem;margin:0.4rem 0;">
                    <div style="color:{'#f87171' if dark else '#dc2626'};font-weight:600;font-size:0.85rem;margin-bottom:0.4rem;">
                        ❌ Wrong PDF — Not a Math document
                    </div>
                    <div style="color:{'#fca5a5' if dark else '#991b1b'};font-size:0.78rem;line-height:1.8;">
                        <b>Detected as:</b> {detected_type}<br>
                        <b>Math keywords found:</b> {math_hits} (need at least 4)<br><br>
                        Please upload a <b>maths textbook, question paper, or class notes</b>.
                    </div>
                </div>""", unsafe_allow_html=True)

            elif status == "ok":
                pages     = st.session_state.get("pdf_pages", "?")
                math_hits = st.session_state.get("pdf_math_hits", 0)
                st.success(f"✅ Loaded {pages} page(s) · {math_hits} math keywords!")
                st.markdown("**Ask about this PDF:**")
                if st.button("📝 Solve all problems in this PDF", use_container_width=True, type="primary"):
                    st.session_state.pending = "Solve all the math problems from the uploaded PDF step by step"
                    st.rerun()
                if st.button("📋 Summarize this PDF", use_container_width=True):
                    st.session_state.pending = "Summarize the key math concepts from the uploaded PDF"
                    st.rerun()
                if st.button("❓ What topics are in this PDF?", use_container_width=True):
                    st.session_state.pending = "What math topics are covered in the uploaded PDF?"
                    st.rerun()

            elif status and str(status).startswith("error:"):
                st.error(f"PDF error: {str(status)[6:]}")


        st.markdown('<div class="sidebar-section">Scan Problem</div>', unsafe_allow_html=True)

        scan_method = st.radio(
            "Choose input:",
            ["📷 Use Camera", "🖼️ Upload Image"],
            horizontal=True,
            label_visibility="collapsed")

        scanned_image = None
        if scan_method == "📷 Use Camera":
            scanned_image = st.camera_input(
                "Point at math problem and capture", label_visibility="collapsed")
        else:
            scanned_image = st.file_uploader(
                "Upload photo of math problem",
                type=["png", "jpg", "jpeg", "webp"],
                label_visibility="collapsed",
                key="img_uploader")

        if scanned_image is not None:
            try:
                from PIL import Image as PILImage
                image = PILImage.open(scanned_image)
                st.image(image, caption="📸 Captured Image", use_container_width=True)

                img_hash = hashlib.md5(scanned_image.getvalue()).hexdigest()
                is_new_image = st.session_state.get("last_img_hash") != img_hash

                # ── Check pytesseract AND tesseract binary ──
                _tess_available = False
                try:
                    import pytesseract as _tess
                    import subprocess
                    # Try known binary paths first
                    for _tp in [
                        "/opt/homebrew/bin/tesseract",   # macOS Apple Silicon
                        "/usr/local/bin/tesseract",       # macOS Intel
                        "/usr/bin/tesseract",             # Linux / Streamlit Cloud
                        "/usr/local/share/tessdata/../../../bin/tesseract",
                    ]:
                        if os.path.exists(_tp):
                            _tess.pytesseract.tesseract_cmd = _tp
                            _tess_available = True
                            break
                    # Fallback: try running tesseract from PATH
                    if not _tess_available:
                        _r = subprocess.run(
                            ["tesseract", "--version"],
                            capture_output=True, timeout=5
                        )
                        if _r.returncode == 0:
                            _tess_available = True
                    # Final fallback: find tesseract using `which`
                    if not _tess_available:
                        _r = subprocess.run(
                            ["which", "tesseract"],
                            capture_output=True, timeout=5
                        )
                        if _r.returncode == 0:
                            _tp = _r.stdout.decode().strip()
                            if _tp:
                                _tess.pytesseract.tesseract_cmd = _tp
                                _tess_available = True
                except Exception:
                    _tess_available = False

                if not _tess_available:
                    # Show setup notice only once — collapse it after first view
                    _tess_warned = st.session_state.get("tess_warning_shown", False)
                    if not _tess_warned:
                        st.session_state.tess_warning_shown = True
                    with st.expander("⚙️ One-time setup: enable camera scan", expanded=not _tess_warned):
                        st.markdown(f"""
                        <div style="background:{'rgba(245,158,11,0.1)' if dark else '#fffbeb'};
                            border:1px solid {'rgba(245,158,11,0.4)' if dark else '#fcd34d'};
                            border-radius:8px;padding:0.8rem 1rem;margin-bottom:0.6rem;">
                            <div style="color:{'#fbbf24' if dark else '#b45309'};font-weight:600;font-size:0.85rem;margin-bottom:0.3rem;">
                                📷 OCR not installed — camera scan disabled
                            </div>
                            <div style="color:{'#fde68a' if dark else '#92400e'};font-size:0.75rem;line-height:1.75;">
                                To enable photo scanning, run <b>one</b> of these in your terminal and restart:
                            </div>
                        </div>""", unsafe_allow_html=True)
                        _tab_mac, _tab_linux, _tab_win = st.tabs(["🍎 macOS", "🐧 Linux", "🪟 Windows"])
                        with _tab_mac:
                            st.code("pip install pytesseract pillow\nbrew install tesseract", language="bash")
                        with _tab_linux:
                            st.code("pip install pytesseract pillow\nsudo apt install tesseract-ocr", language="bash")
                        with _tab_win:
                            st.code("pip install pytesseract pillow", language="bash")
                            st.markdown("<div style='font-size:0.75rem;color:var(--tx2);margin-top:0.3rem;'>Then download the Tesseract installer:<br><a href='https://github.com/UB-Mannheim/tesseract/wiki' target='_blank'>github.com/UB-Mannheim/tesseract/wiki</a></div>", unsafe_allow_html=True)
                        st.caption("After installing, restart Streamlit and camera scan will work automatically.")
                    st.markdown("<div style='color:var(--tx2);font-size:0.82rem;margin-top:0.4rem;'>✏️ Type your math problem manually instead:</div>", unsafe_allow_html=True)
                    manual_ocr = st.text_input(
                        "Type problem here:",
                        placeholder="e.g. Solve x² + 5x + 6 = 0",
                        key=f"manual_ocr_{img_hash}",
                        label_visibility="collapsed")
                    if st.button("🧮 Solve Manually", key=f"manual_ocr_solve_{img_hash}", use_container_width=True, type="primary"):
                        if manual_ocr.strip():
                            st.session_state.pending = f"Solve this math problem step by step: {manual_ocr}"
                            st.rerun()
                        else:
                            st.error("Please type a problem first!")

                else:
                    # pytesseract is available — run OCR now
                    if is_new_image:
                        with st.spinner("🔍 Reading math problem from image..."):
                            extracted = ocr_extract_text(image)
                        st.session_state.last_img_hash    = img_hash
                        st.session_state.last_ocr_text    = extracted
                        st.session_state.ocr_auto_solved  = False
                    else:
                        extracted = st.session_state.get("last_ocr_text", "")

                    if extracted and extracted.strip():
                        # validate OCR text is actually math before accepting
                        txt_low = extracted.lower()
                        MATH_OCR_SIGNALS = [
                            # operators & symbols
                            "=", "+", "-", "*", "/", "^", "²", "³", "√",
                            "∫", "∑", "∂", "±", "∞", "π",
                            # keywords
                            "solve", "find", "equation", "integral", "derivative",
                            "differentiate", "integrate", "matrix", "vector",
                            "quadratic", "polynomial", "theorem", "proof",
                            "calculate", "simplify", "factorize", "evaluate",
                            "sin", "cos", "tan", "log", "ln",
                            "f(x)", "g(x)", "d/dx", "dy/dx", "lim",
                            "dx", "dy", "x²", "x^2", "ax", "bx",
                        ]
                        # Count signals present in extracted text
                        ocr_math_hits = sum(1 for s in MATH_OCR_SIGNALS if s in txt_low or s in extracted)
                        # Also check: has at least one digit near an operator
                        has_math_pattern = bool(re.search(
                            r'\d[\+\-\*/=^]|[\+\-\*/=^]\d|\bx\b|\by\b', extracted))
                        is_math_image = ocr_math_hits >= 2 or has_math_pattern

                        if is_math_image:
                            st.success("✅ Math problem detected!")
                            st.info(f"📝 **Detected:** {extracted}")
                            st.markdown("<small style='color:var(--tx2)'>✏️ Edit if needed:</small>",
                                        unsafe_allow_html=True)
                            edited = st.text_input(
                                "Edit:", value=extracted,
                                key=f"edit_{img_hash}",
                                label_visibility="collapsed")
                            b1, b2 = st.columns(2)
                            with b1:
                                if st.button("🧮 Solve", key=f"solve_{img_hash}", use_container_width=True, type="primary"):
                                    st.session_state.pending = f"Solve this math problem step by step: {edited}"
                                    st.session_state.ocr_auto_solved = True
                                    st.rerun()
                                if st.button("📋 Summarize", key=f"sum_{img_hash}", use_container_width=True):
                                    st.session_state.pending = f"Summarize and explain this math problem: {edited}"
                                    st.session_state.ocr_auto_solved = True
                                    st.rerun()
                            with b2:
                                if st.button("💡 Hint", key=f"hint_{img_hash}", use_container_width=True):
                                    st.session_state.pending = f"Give me a hint to solve: {edited}"
                                    st.session_state.ocr_auto_solved = True
                                    st.rerun()
                                if st.button("📊 Similar", key=f"sim_{img_hash}", use_container_width=True):
                                    st.session_state.pending = f"Show similar example problems like: {edited}"
                                    st.session_state.ocr_auto_solved = True
                                    st.rerun()
                            if is_new_image and not st.session_state.get("ocr_auto_solved", False):
                                st.session_state.ocr_auto_solved = True
                                st.session_state.pending = f"Solve this math problem step by step: {extracted}"
                                st.rerun()

                        else:
                            # OCR found text but it's NOT math (photo, selfie, food, etc.)
                            st.markdown(f"""
                            <div style="background:{'rgba(239,68,68,0.12)' if dark else '#fff1f2'};
                                border:1px solid {'rgba(239,68,68,0.45)' if dark else '#fca5a5'};
                                border-radius:10px;padding:0.9rem 1rem;margin:0.5rem 0;">
                                <div style="color:{'#f87171' if dark else '#dc2626'};font-weight:600;font-size:0.88rem;margin-bottom:0.35rem;">
                                    ❌ This is not a Math image
                                </div>
                                <div style="color:{'#fca5a5' if dark else '#991b1b'};font-size:0.78rem;line-height:1.65;">
                                    Text was found but no math content detected.<br>
                                    <b>Math signals found:</b> {ocr_math_hits} (need at least 2)<br><br>
                                    Please upload an image of a <b>math problem, equation, or question paper</b>.
                                </div>
                            </div>""", unsafe_allow_html=True)
                            st.markdown(f"<div style='color:var(--tx2);font-size:0.82rem;margin-top:0.4rem;'>✏️ Or type your problem manually:</div>", unsafe_allow_html=True)
                            manual = st.text_input(
                                "Type problem here:",
                                placeholder="e.g. Solve x² + 5x + 6 = 0",
                                key=f"manual_{img_hash}",
                                label_visibility="collapsed")
                            if st.button("🧮 Solve Manually", key=f"manual_solve_{img_hash}", use_container_width=True, type="primary"):
                                if manual.strip():
                                    st.session_state.pending = f"Solve this math problem step by step: {manual}"
                                    st.rerun()
                                else:
                                    st.error("Please type a problem first!")

                    else:
                        # OCR found nothing at all (blank image, photo with no text)
                        st.markdown(f"""
                        <div style="background:{'rgba(239,68,68,0.12)' if dark else '#fff1f2'};
                            border:1px solid {'rgba(239,68,68,0.45)' if dark else '#fca5a5'};
                            border-radius:10px;padding:0.9rem 1rem;margin:0.5rem 0;">
                            <div style="color:{'#f87171' if dark else '#dc2626'};font-weight:600;font-size:0.88rem;margin-bottom:0.35rem;">
                                ❌ No text found in this image
                            </div>
                            <div style="color:{'#fca5a5' if dark else '#991b1b'};font-size:0.78rem;line-height:1.65;">
                                This looks like a photo or image without any readable text.<br><br>
                                • Make sure the image contains a <b>written or printed math problem</b><br>
                                • Ensure good lighting and focus<br>
                                • Avoid selfies, landscapes, or non-math images
                            </div>
                        </div>""", unsafe_allow_html=True)
                        st.markdown(f"<div style='color:var(--tx2);font-size:0.82rem;margin-top:0.4rem;'>✏️ Type your problem manually instead:</div>", unsafe_allow_html=True)
                        manual2 = st.text_input(
                            "Type problem here:",
                            placeholder="e.g. Solve x² + 5x + 6 = 0",
                            key=f"manual2_{img_hash}",
                            label_visibility="collapsed")
                        if st.button("🧮 Solve Manually", key=f"manual_solve2_{img_hash}", use_container_width=True, type="primary"):
                            if manual2.strip():
                                st.session_state.pending = f"Solve this math problem step by step: {manual2}"
                                st.rerun()
                            else:
                                st.error("Please type a problem first!")

            except ImportError:
                st.error("❌ Pillow not installed. Run: pip install pillow")
            except Exception as e:
                st.error(f"Scan error: {e}")
                st.info("💡 Try uploading a clearer image or type your problem manually.")

        st.markdown('<div class="sidebar-section">Session</div>', unsafe_allow_html=True)
        _cb  = "#111827" if dark else "#ffffff"
        _cbr = "#1e293b" if dark else "#e2e8f0"
        _lc  = "#475569" if dark else "#94a3b8"
        _nc  = "#60a5fa" if dark else "#2563eb"

        # ── Streak and today count ────────────────────────────────────
        _streak      = st.session_state.get("streak", 1)
        _today_count = st.session_state.get("today_count", 0)
        _streak_icon = "🔥" if _streak >= 3 else "📅"
        st.markdown(f"""
        <div style="display:flex;gap:0.5rem;margin-bottom:0.5rem;">
            <div style="flex:1;background:{_cb};border:1px solid {_cbr};border-radius:10px;padding:0.55rem 0.7rem;">
                <div style="font-family:'DM Mono',monospace;font-size:0.6rem;text-transform:uppercase;letter-spacing:0.08em;color:{_lc};margin-bottom:0.2rem;">Today</div>
                <div style="font-family:'Syne',sans-serif;font-size:1.35rem;font-weight:700;color:{_nc};">🧮 {_today_count}</div>
            </div>
            <div style="flex:1;background:{_cb};border:1px solid {_cbr};border-radius:10px;padding:0.55rem 0.7rem;">
                <div style="font-family:'DM Mono',monospace;font-size:0.6rem;text-transform:uppercase;letter-spacing:0.08em;color:{_lc};margin-bottom:0.2rem;">Streak</div>
                <div style="font-family:'Syne',sans-serif;font-size:1.35rem;font-weight:700;color:{_nc};">{_streak_icon} {_streak}d</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="display:flex;gap:0.5rem;margin-bottom:0.6rem;">
            <div style="flex:1;background:{_cb};border:1px solid {_cbr};border-radius:10px;padding:0.55rem 0.7rem;">
                <div style="font-family:'DM Mono',monospace;font-size:0.6rem;text-transform:uppercase;letter-spacing:0.08em;color:{_lc};margin-bottom:0.2rem;">Queries</div>
                <div style="font-family:'Syne',sans-serif;font-size:1.35rem;font-weight:700;color:{_nc};">{st.session_state.query_count}</div>
            </div>
            <div style="flex:1;background:{_cb};border:1px solid {_cbr};border-radius:10px;padding:0.55rem 0.7rem;">
                <div style="font-family:'DM Mono',monospace;font-size:0.6rem;text-transform:uppercase;letter-spacing:0.08em;color:{_lc};margin-bottom:0.2rem;">Messages</div>
                <div style="font-family:'Syne',sans-serif;font-size:1.35rem;font-weight:700;color:{_nc};">{len(st.session_state.messages)}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages       = []
            st.session_state.query_count    = 0
            st.session_state.last_user_input = ""
            if st.session_state.engine:
                st.session_state.engine.clear_memory()
            st.rerun()

    st.markdown("""
    <div class="hero-wrap">
        <div class="hero-badge">⚡ Powered by LLaMA 3.3 · Groq · RAG</div>
        <h1 class="hero-title">Advanced Mathematics<br>Assistant</h1>
        <p class="hero-sub">Step-by-step AI solutions · Symbolic computation · Graph plotting</p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.engine is None:
        _init_placeholder = st.empty()
        _init_placeholder.info("⚡ Starting up… loading AI model (first run takes ~10 seconds, then it's instant)")
        try:
            store = build_pipeline()
            engine = MathAIEngine(vector_store=store, session_id=st.session_state.session_id)
            st.session_state.engine   = engine
            st.session_state.kb_ready = True
            _init_placeholder.empty()
        except Exception as e:
            _init_placeholder.empty()
            st.error(f"Init error: {e}")
            st.info("Make sure GROQ_API_KEY is set in .env and all packages are installed.")
            st.stop()

    if st.session_state.kb_ready and st.session_state.engine:
        doc_count = (st.session_state.engine.vector_store.get_document_count()
                     if st.session_state.engine.vector_store else 0)
        st.markdown(f"""
        <div style="text-align:center;margin-bottom:0.5rem;">
            <span style="font-family:'DM Mono',monospace;font-size:0.65rem;color:var(--tx2);letter-spacing:0.08em;">
                📚 {doc_count} CHUNKS &nbsp;·&nbsp; {LLM_MODEL} &nbsp;·&nbsp; SESSION {st.session_state.session_id.upper()}
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    if not st.session_state.messages:
        dark = st.session_state.get("theme","dark") == "dark"
        _card = "#1e293b" if dark else "#f8fafc"
        _border = "rgba(99,102,241,0.25)" if dark else "rgba(99,102,241,0.2)"
        _tx = "#f1f5f9" if dark else "#1e293b"
        _tx2 = "#94a3b8" if dark else "#64748b"
        _accent = "#6366f1"

        st.markdown(f"""
        <div style="max-width:680px;margin:1.5rem auto 0;padding:0 0.5rem;">

          <!-- Header -->
          <div style="text-align:center;margin-bottom:1.8rem;">
            <div style="font-size:2.2rem;margin-bottom:0.4rem;">🧮</div>
            <div style="font-family:'Syne',sans-serif;font-size:1.5rem;font-weight:700;
                        color:{_tx};margin-bottom:0.3rem;">
              Your Smart Maths Assistant
            </div>
            <div style="font-size:0.85rem;color:{_tx2};line-height:1.6;">
              Stuck on a question? Get clear step-by-step solutions instantly.<br>
              NCERT Class 9 &amp; 10 · Step-by-step · No typing needed
            </div>
          </div>

          <!-- 3 ways to use -->
          <div style="font-family:'DM Mono',monospace;font-size:0.6rem;text-transform:uppercase;
                      letter-spacing:0.1em;color:{_tx2};margin-bottom:0.6rem;text-align:center;">
            How do you want to study today?
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:0.6rem;margin-bottom:1.5rem;">
            <div style="background:{_card};border:1px solid {_border};border-radius:12px;
                        padding:1rem 0.7rem;text-align:center;">
              <div style="font-size:1.5rem;margin-bottom:0.4rem;">📚</div>
              <div style="font-size:0.78rem;font-weight:700;color:{_tx};margin-bottom:0.25rem;">
                Practice NCERT
              </div>
              <div style="font-size:0.68rem;color:{_tx2};line-height:1.5;">
                Pick class → chapter → exercise → tap Hint, Steps or Answer
              </div>
              <div style="margin-top:0.5rem;font-size:0.63rem;color:{_accent};font-weight:600;">
                ← Use sidebar
              </div>
            </div>
            <div style="background:{_card};border:1px solid {_border};border-radius:12px;
                        padding:1rem 0.7rem;text-align:center;">
              <div style="font-size:1.5rem;margin-bottom:0.4rem;">💬</div>
              <div style="font-size:0.78rem;font-weight:700;color:{_tx};margin-bottom:0.25rem;">
                Ask Anything
              </div>
              <div style="font-size:0.68rem;color:{_tx2};line-height:1.5;">
                Type any maths question below and get instant step-by-step solution
              </div>
              <div style="margin-top:0.5rem;font-size:0.63rem;color:{_accent};font-weight:600;">
                ↓ Type below
              </div>
            </div>
            <div style="background:{_card};border:1px solid {_border};border-radius:12px;
                        padding:1rem 0.7rem;text-align:center;">
              <div style="font-size:1.5rem;margin-bottom:0.4rem;">📷</div>
              <div style="font-size:0.78rem;font-weight:700;color:{_tx};margin-bottom:0.25rem;">
                Scan Problem
              </div>
              <div style="font-size:0.68rem;color:{_tx2};line-height:1.5;">
                Take photo of any textbook question — AI reads and solves it
              </div>
              <div style="margin-top:0.5rem;font-size:0.63rem;color:{_accent};font-weight:600;">
                ← Use sidebar
              </div>
            </div>
          </div>

        </div>
        """, unsafe_allow_html=True)

    for i, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            # For quiz messages, show a clean label instead of raw prompt
            _raw = msg.get("content", "")
            if msg.get("is_quiz") and len(_raw) > 120:
                # Extract just the question number and first line
                import re as _re_disp
                _qm = _re_disp.match(r'(?:.*?\n)?(Q\d+[^\n]{0,60})', _raw)
                _display = _qm.group(1) if _qm else _raw[:80] + "..."
            else:
                _display = _raw
            import html as _html_mod
            _safe = _html_mod.escape(_display)
            st.markdown(f"""
            <div class="msg-user">
                <div class="msg-user-name">▸ You</div>
                <div style="white-space:pre-wrap;">{_safe}</div>
            </div>""", unsafe_allow_html=True)
            edit_col, _ = st.columns([1, 9])
            with edit_col:
                if st.button("✏️ Edit", key=f"edit_msg_{i}", help="Edit this question"):
                    st.session_state["user_input"] = msg["content"]
                    st.rerun()
        else:
            st.markdown("""
            <div class="msg-ai-label">
                <div class="msg-ai-tag">∫ MathAI</div>
                <div class="msg-ai-line"></div>
            </div>""", unsafe_allow_html=True)
            st.markdown(msg["content"])

            # ── Clean plain text for sharing ────────────────────────
            clean = msg["content"]
            clean = re.sub(r'\$\$(.+?)\$\$', r'\1', clean, flags=re.DOTALL)
            clean = re.sub(r'\$(.+?)\$', r'\1', clean)
            clean = re.sub(r'━+', '─────────────────────', clean)
            clean = re.sub(r'\*\*(.+?)\*\*', r'\1', clean)
            clean = re.sub(r'\*(.+?)\*', r'\1', clean)
            clean = re.sub(r'\\boxed\{(.+?)\}', r'[ \1 ]', clean)
            clean = re.sub(r'\\frac\{(.+?)\}\{(.+?)\}', r'(\1)/(\2)', clean)
            clean = re.sub(r'\\(pm|mp)', r'±', clean)
            clean = re.sub(r'\\sqrt\{(.+?)\}', r'√(\1)', clean)
            clean = re.sub(r'\\text\{(.+?)\}', r'\1', clean)
            clean = re.sub(r'\\[a-zA-Z]+', '', clean)

            # ── One-click share button ───────────────────────────────
            if st.button("📤 Share answer", key=f"share_{i}", help="Click to copy the solution"):
                st.session_state[f"show_copy_{i}"] = not st.session_state.get(f"show_copy_{i}", False)
            if st.session_state.get(f"show_copy_{i}", False):
                st.code(clean, language=None)

            if msg.get("sources"):
                tags = "".join(
                    f'<span class="tag">{s["topic"].replace("_"," ").title()}</span>'
                    for s in msg["sources"])
                st.markdown(f'<div style="margin:0.3rem 0 0.5rem">{tags}</div>', unsafe_allow_html=True)

            # ── Feedback buttons ──────────────────────────────────────
            fb_col1, fb_col2, fb_col3 = st.columns([1, 1, 8])
            with fb_col1:
                if st.button("👍", key=f"up_{i}", help="Helpful"):
                    st.toast("Thanks for the feedback! 🎉")
            with fb_col2:
                if st.button("👎", key=f"dn_{i}", help="Not helpful"):
                    st.toast("Thanks! We'll improve. 🙏")

    st.markdown('<div class="input-label">Ask a question</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_area(
            "Question:", height=90,
            placeholder="e.g.  Solve 2x² + 5x - 3 = 0   ·   Find derivative of x³·sin(x)   ·   Explain eigenvalues",
            key="user_input", label_visibility="collapsed")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        send = st.button("Solve →", use_container_width=True, type="primary")

    pending_query = st.session_state.get("pending")
    if pending_query:
        st.session_state.pending = None

        # If this is a quiz button click (not a fresh user question),
        # REPLACE the last quiz exchange instead of adding new messages
        _quiz_replace = st.session_state.pop("quiz_replace", False)
        if _quiz_replace and len(st.session_state.messages) >= 2:
            # Remove last user+AI pair if they were quiz messages
            if st.session_state.messages[-1].get("role") == "assistant" \
               and st.session_state.messages[-2].get("role") == "user" \
               and st.session_state.messages[-2].get("is_quiz", False):
                st.session_state.messages.pop()  # remove AI
                st.session_state.messages.pop()  # remove user

        st.session_state.messages.append({
            "role": "user",
            "content": pending_query,
            "is_quiz": _quiz_replace,
        })
        st.session_state.query_count += 1
        st.session_state.today_count = st.session_state.get("today_count", 0) + 1
        with st.spinner("🧮 Computing solution..."):
            result = st.session_state.engine.query(pending_query)
        st.session_state.messages.append({
            "role":          "assistant",
            "content":       result["answer"],
            "sources":       result.get("sources", []),
            "symbolic_hint": result.get("symbolic_hint"),
        })
        st.rerun()

    elif send and user_input.strip():
        # Route through pending — same safe pattern used by Quick Examples.
        # NEVER mutate st.session_state["user_input"] here: that key is bound
        # to the text_area widget and setting it mid-run causes Streamlit to
        # abort the script silently before query() is ever called.
        st.session_state.pending = user_input.strip()
        st.rerun()

    with st.expander("💡 Tips", expanded=False):
        st.markdown("""
        - **Type question** → click Solve → get whiteboard-style step-by-step solution
        - **NCERT Practice** → sidebar: pick class → chapter → exercise → tap Hint/Steps/Answer
        - **📷 Camera** → snap photo of handwritten problem → auto solves!
        - **🖼️ Upload Image** → upload screenshot or photo of any problem
        - **📄 PDF Upload** → upload textbook or notes → 3 action buttons appear!
        - **📊 Graph** → type `sin(x), cos(x)` in sidebar → interactive Plotly graph with zoom + hover
        - **⚡ Symbolic** → use Compute for instant derivatives, integrals, equation solving
        - **📤 Share** → click Share answer below any solution to copy and send to friends
        - **🔥 Streak** → solve problems daily to build your streak!
        """)


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  STEP 7 — TESTING                                                   ║
# ╚══════════════════════════════════════════════════════════════════════╝

class TestDataSources(unittest.TestCase):
    def test_builtin_knowledge(self):
        docs = MathDataLoader().load_builtin_knowledge()
        self.assertGreater(len(docs), 0)
        self.assertTrue(all(len(d.page_content) > 50 for d in docs))
        self.assertTrue(all("topic" in d.metadata for d in docs))

class TestPreprocessing(unittest.TestCase):
    def setUp(self):
        self.pp = MathDataPreprocessor()

    def test_cleans_whitespace(self):
        doc = Document(page_content="Hello   World\n\n\n\nMath content here is important", metadata={})
        result = self.pp.preprocess_document(doc)
        self.assertIsNotNone(result)
        self.assertNotIn("\n\n\n", result.page_content)

    def test_deduplication(self):
        doc = Document(page_content="The derivative of x squared is 2x. " * 10, metadata={})
        self.assertIsNotNone(self.pp.preprocess_document(doc))
        self.assertIsNone(self.pp.preprocess_document(doc))

    def test_topic_detection(self):
        doc = Document(page_content="The derivative and integral of functions in calculus.", metadata={})
        result = self.pp.preprocess_document(doc)
        self.assertEqual(result.metadata["topic"], "calculus")

    def test_skips_short(self):
        self.assertIsNone(MathDataPreprocessor().preprocess_document(
            Document(page_content="too short", metadata={})))

class TestChunking(unittest.TestCase):
    def setUp(self):
        self.splitter = MathTextSplitter(chunk_size=200, chunk_overlap=20)

    def test_splits_large_doc(self):
        doc = Document(page_content="Math paragraph with content. " * 60, metadata={"source": "test"})
        self.assertGreater(len(self.splitter.split_document(doc)), 1)

    def test_metadata_preserved(self):
        doc = Document(page_content="x " * 500, metadata={"source": "test.pdf", "topic": "algebra"})
        for chunk in self.splitter.split_document(doc):
            self.assertEqual(chunk.metadata.get("topic"), "algebra")
            self.assertIn("chunk_index", chunk.metadata)

class TestSymbolicEngine(unittest.TestCase):
    def setUp(self):
        self.sym = SymbolicMathEngine()

    def test_differentiate(self):
        result = self.sym.differentiate("x**3")
        self.assertIsNotNone(result)
        self.assertIn("3*x**2", result.replace(" ", ""))

    def test_integrate(self):
        result = self.sym.integrate("x**2")
        self.assertIsNotNone(result)
        self.assertIn("x**3", result)

    def test_solve(self):
        result = self.sym.solve_equation("x**2 - 4 = 0")
        self.assertIsNotNone(result)
        self.assertIn("2", result)

    def test_simplify(self):
        result = self.sym.try_solve("(x**2 - 1)/(x - 1)")
        self.assertIsNotNone(result)
        self.assertIn("x + 1", result)

class TestMemory(unittest.TestCase):
    def test_add_retrieve(self):
        mem = MongoDBChatMemory(session_id="test")
        mem.add_message("human", "What is a derivative?")
        mem.add_message("assistant", "Rate of change.")
        self.assertGreaterEqual(len(mem.get_history()), 2)

    def test_langchain_messages(self):
        mem = MongoDBChatMemory(session_id="test_lc")
        mem.add_message("human", "Test")
        mem.add_message("assistant", "Answer")
        msgs = mem.get_langchain_messages()
        self.assertTrue(any(isinstance(m, HumanMessage) for m in msgs))


def run_tests() -> bool:
    print("\n" + "="*60 + "\n  RUNNING TEST SUITE\n" + "="*60)
    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()
    for cls in [TestDataSources, TestPreprocessing, TestChunking, TestSymbolicEngine, TestMemory]:
        suite.addTests(loader.loadTestsFromTestCase(cls))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return result.wasSuccessful()


def run_evaluation():
    print("\n" + "="*60 + "\n  RAG PIPELINE EVALUATION\n" + "="*60)
    store = build_pipeline()
    test_cases = [
        {"q": "What is the power rule for derivatives?",  "keywords": ["power", "derivative", "n*x"]},
        {"q": "How do you find eigenvalues of a matrix?", "keywords": ["eigenvalue", "determinant", "characteristic"]},
        {"q": "What is Bayes theorem?",                   "keywords": ["probability", "conditional", "P(A|B)"]},
        {"q": "What is the quadratic formula?",           "keywords": ["quadratic", "formula", "discriminant"]},
    ]
    scores = []
    for tc in test_cases:
        docs     = store.similarity_search(tc["q"], k=3)
        combined = " ".join(d.page_content.lower() for d in docs)
        hits     = sum(1 for kw in tc["keywords"] if kw.lower() in combined)
        score    = hits / len(tc["keywords"])
        scores.append(score)
        print(f"  Q: {tc['q'][:50]}... → {score:.2f} ({hits}/{len(tc['keywords'])} keywords)")
    print(f"\n  Average retrieval score: {sum(scores)/len(scores):.3f}")
    sym      = SymbolicMathEngine()
    sym_tests = [
        (sym.differentiate("x**3"),           "3*x**2"),
        (sym.integrate("x**2"),               "x**3"),
        (sym.solve_equation("x**2 - 4 = 0"),  "2"),
    ]
    passed = sum(1 for r, e in sym_tests if r and e in r.replace(" ", ""))
    print(f"  Symbolic engine: {passed}/{len(sym_tests)} tests passed")


def main():
    if any("streamlit" in arg for arg in sys.argv):
        run_streamlit_app()
        return

    parser = argparse.ArgumentParser(description="Advanced Mathematics Assistant")
    parser.add_argument("--setup",   action="store_true", help="Build knowledge base")
    parser.add_argument("--rebuild", action="store_true", help="Force rebuild knowledge base")
    parser.add_argument("--test",    action="store_true", help="Run unit tests")
    parser.add_argument("--eval",    action="store_true", help="Evaluate RAG pipeline")
    args = parser.parse_args()

    print("="*60 + "\n  🧮  Advanced Mathematics Assistant\n" + "="*60)

    if args.test:
        sys.exit(0 if run_tests() else 1)
    elif args.eval:
        run_evaluation()
    elif args.setup or args.rebuild:
        store = build_pipeline(force_rebuild=args.rebuild)
        print(f"\n✅ Knowledge base ready — {store.get_document_count()} chunks indexed")
    else:
        print("\nTo launch the UI:\n")
        print("  python3.11 -m streamlit run main.py\n")


try:
    import streamlit as st
    if hasattr(st, "session_state"):
        run_streamlit_app()
except Exception:
    pass

if __name__ == "__main__":
    main()