"""
Application configuration — Pydantic Settings loaded from environment variables.

All configuration values are centralized here. Modules import from this file
instead of reading os.environ directly. This is the single source of truth
for all runtime configuration across the backend.
"""

import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

# Ensure .env is loaded for local development
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env", override=True)


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── LLM Configuration ──────────────────────────────────────────────
    groq_api_key: str = ""
    llm_model: str = "llama-3.3-70b-versatile"
    groq_model_fallbacks: List[str] = [
        "llama-3.3-70b-versatile",
        "llama3-8b-8192",
        "mixtral-8x7b-32768",
    ]

    # ── Gemini Configuration ───────────────────────────────────────────
    gemini_api_key: str = ""
    use_gemini: bool = True  # Feature flag: True = Gemini primary, False = Groq
    gemini_primary_model: str = "gemini-2.0-flash"
    gemini_fallback_model: str = "gemini-1.5-flash"
    gemini_vision_model: str = "gemini-2.0-flash"
    gemini_temperature: float = 0.1
    gemini_max_tokens: int = 2048

    # ── Embeddings ─────────────────────────────────────────────────────
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # ── Vector Database ────────────────────────────────────────────────
    vector_db_type: str = "chroma"
    chroma_persist_dir: str = "./chroma_db"
    faiss_index_path: str = "./faiss_index"
    top_k_results: int = 5
    chunk_size: int = 1000
    chunk_overlap: int = 200
    collection_name: str = "math_knowledge_base"

    # ── Firebase ───────────────────────────────────────────────────────
    use_firebase: bool = True
    firebase_credentials_path: str = ""

    # ── ADK Multi-Agent ────────────────────────────────────────────────
    use_adk: bool = True

    # ── LangGraph ──────────────────────────────────────────────────────
    use_langgraph: bool = True
    langchain_api_key: str = ""

    # ── Vector DB ──────────────────────────────────────────────────────
    vector_db: str = "qdrant"
    qdrant_url: str = ":memory:"
    qdrant_api_key: str = ""


    # ── Server ─────────────────────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8080
    environment: str = "development"
    log_level: str = "INFO"


# Singleton settings instance
settings = Settings()

def setup_logging():
    import logging
    import os
    
    # Check if running in a GCP environment (Cloud Run, App Engine) or has ADC setup
    use_cloud_logging = os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("GOOGLE_CLOUD_PROJECT")
    
    if use_cloud_logging:
        try:
            import google.cloud.logging
            client = google.cloud.logging.Client()
            client.setup_logging()
            logging.info("Google Cloud Logging integrated successfully.")
            return
        except ImportError:
            logging.warning("google-cloud-logging not installed. Falling back to standard logging.")
        except Exception as e:
            logging.warning(f"Failed to initialize Cloud Logging: {e}. Falling back to standard logging.")
            
    # Standard local logging fallback
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

# Initialize logging when config is imported
setup_logging()


# ── System Prompt Template ─────────────────────────────────────────────
# Extracted from main.py L404-L522. This is the master prompt template
# used by MathAIEngine to instruct the LLM on response format.

SYSTEM_TEMPLATE = r"""
You are an elite Indian mathematics teacher for Class 6 to 12 and JEE aspirants.
Your goal is to explain math concepts and solve problems step-by-step.ly ONLY: "❌ I only teach math! Ask me any math problem."
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

→ USE LaTeX math mode ($...$ for inline, $$...$$ for block) for all mathematical expressions.
→ Example: $x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$
→ Use proper LaTeX symbols (e.g. \sqrt, \pi, \pm, \int)
→ Hindi/Hinglish question → answer in same language

Context from knowledge base:
{context}
"""
