"""
Gemini Service — Google AI Studio integration for math tutoring.

Provides:
- GeminiService: Text-based math query processing with Gemini 2.0 Flash
- GeminiVisionService: Image math extraction using Gemini Vision
- Streaming support for token-by-token SSE delivery
- Automatic fallback from Gemini 2.0 Flash → Gemini 1.5 Flash on rate limits

Uses Google AI Studio free tier (google-generativeai SDK).
"""

import re
import time
import logging
import base64
from typing import Dict, Any, Optional, AsyncGenerator

from backend.src.config import settings, SYSTEM_TEMPLATE

logger = logging.getLogger("math_assistant.gemini")

_GEMINI_CACHE = {}


def _get_gemini_model(model_name: str = None):
    """Get or create a cached Gemini GenerativeModel instance.

    Uses google-generativeai SDK (Google AI Studio free tier).
    """
    import google.generativeai as genai

    model_name = model_name or settings.gemini_primary_model
    if model_name not in _GEMINI_CACHE:
        api_key = settings.gemini_api_key
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not set. Get a free key at https://aistudio.google.com/apikey "
                "and add it to your .env file."
            )
        genai.configure(api_key=api_key)
        _GEMINI_CACHE[model_name] = genai.GenerativeModel(
            model_name=model_name,
            generation_config=genai.GenerationConfig(
                temperature=settings.gemini_temperature,
                max_output_tokens=settings.gemini_max_tokens,
            ),
        )
        logger.info(f"Initialized Gemini model: {model_name}")
    return _GEMINI_CACHE[model_name]


class GeminiService:
    """Google Gemini text-based math query service with automatic fallback."""

    def __init__(self):
        self.primary_model = settings.gemini_primary_model
        self.fallback_model = settings.gemini_fallback_model

    def query(self, user_input: str, context: str = "", chat_history: list = None) -> str:
        """Send a math query to Gemini and return the response.

        Args:
            user_input: The student's math question.
            context: RAG-retrieved knowledge base context.
            chat_history: List of previous messages for context.

        Returns:
            The LLM response string.
        """
        system_text = SYSTEM_TEMPLATE.replace("{context}", context or "")

        # Build conversation parts
        parts = [system_text + "\n\n"]
        if chat_history:
            for msg in chat_history:
                role = getattr(msg, "type", "human")
                content = getattr(msg, "content", str(msg))
                prefix = "Student: " if role == "human" else "Teacher: "
                parts.append(f"{prefix}{content}\n")
        parts.append(f"Student: {user_input}\nTeacher: ")

        prompt = "".join(parts)

        # Try primary model, then fallback
        models_to_try = [self.primary_model, self.fallback_model]
        last_error = None

        for model_name in models_to_try:
            model = _get_gemini_model(model_name)
            for attempt in range(2):
                try:
                    response = model.generate_content(prompt)

                    if response.text:
                        answer = response.text.strip()
                        if model_name != self.primary_model:
                            answer = f"*(Using fallback: {model_name})*\n\n" + answer
                        return answer
                    else:
                        # Check for blocked content
                        if response.prompt_feedback and response.prompt_feedback.block_reason:
                            raise Exception(f"Content blocked: {response.prompt_feedback.block_reason}")
                        raise Exception("Empty response from Gemini")

                except Exception as e:
                    last_error = e
                    err_str = str(e).lower()
                    logger.warning(f"Gemini {model_name} attempt {attempt+1} failed: {e}")

                    if "429" in str(e) or "resource_exhausted" in err_str or "quota" in err_str:
                        logger.info(f"Rate limit on {model_name}, trying fallback...")
                        time.sleep(1)
                        break  # Skip to next model
                    elif "timeout" in err_str or "deadline" in err_str:
                        time.sleep(1)
                        continue
                    else:
                        break  # Non-retryable

        # All models failed
        logger.error(f"All Gemini models failed: {last_error}")
        return f"⚠️ Gemini API error: {last_error}"

    async def stream(self, user_input: str, context: str = "", chat_history: list = None) -> AsyncGenerator[str, None]:
        """Stream a response token by token for SSE delivery.

        Yields chunks of text as they arrive from Gemini's streaming API.
        """
        system_text = SYSTEM_TEMPLATE.replace("{context}", context or "")
        parts = [system_text + "\n\n"]
        if chat_history:
            for msg in chat_history:
                role = getattr(msg, "type", "human")
                content = getattr(msg, "content", str(msg))
                prefix = "Student: " if role == "human" else "Teacher: "
                parts.append(f"{prefix}{content}\n")
        parts.append(f"Student: {user_input}\nTeacher: ")
        prompt = "".join(parts)

        model = _get_gemini_model(self.primary_model)
        try:
            response = model.generate_content(prompt, stream=True)
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"\n\n⚠️ Streaming error: {e}"


class GeminiVisionService:
    """Gemini Vision for extracting math from images (replaces Tesseract OCR)."""

    def __init__(self):
        self.model_name = settings.gemini_vision_model

    def extract_math_from_image(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
        """Extract mathematical content from an image using Gemini Vision.

        Args:
            image_bytes: Raw image bytes.
            mime_type: Image MIME type (image/jpeg, image/png, etc.).

        Returns:
            Extracted mathematical expression or problem text.
        """
        import google.generativeai as genai

        model = _get_gemini_model(self.model_name)

        prompt = (
            "You are a math OCR expert. Extract ALL mathematical content from this image.\n\n"
            "Rules:\n"
            "1. Convert handwritten or printed math into clean text.\n"
            "2. Use standard notation: x², √, π, ±, ∫, Σ, etc.\n"
            "3. If it's an equation, write it as: equation\n"
            "4. If it's a word problem, transcribe it exactly.\n"
            "5. If there are multiple problems, number them.\n"
            "6. Return ONLY the extracted math — no commentary.\n"
        )

        try:
            response = model.generate_content([
                prompt,
                {"mime_type": mime_type, "data": image_bytes},
            ])
            if response.text:
                return response.text.strip()
            return "Could not extract math from image."
        except Exception as e:
            logger.error(f"Vision extraction error: {e}")
            return f"Vision error: {e}"

    def extract_and_solve(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> Dict[str, str]:
        """Extract math from image and solve it in one call.

        Returns dict with 'extracted' (the raw math) and 'solution' (step-by-step).
        """
        import google.generativeai as genai

        model = _get_gemini_model(self.model_name)

        prompt = (
            "You are an Indian math teacher. Look at this image.\n\n"
            "Step 1: Extract the math problem from the image.\n"
            "Step 2: Solve it step-by-step in whiteboard style.\n\n"
            "Format your response as:\n"
            "EXTRACTED: [the math problem]\n"
            "---\n"
            "SOLUTION:\n[step-by-step solution]\n"
        )

        try:
            response = model.generate_content([
                prompt,
                {"mime_type": mime_type, "data": image_bytes},
            ])
            text = response.text.strip() if response.text else ""

            # Parse response
            if "EXTRACTED:" in text and "SOLUTION:" in text:
                parts = text.split("---", 1)
                extracted = parts[0].replace("EXTRACTED:", "").strip()
                solution = parts[1].replace("SOLUTION:", "").strip() if len(parts) > 1 else ""
            else:
                extracted = ""
                solution = text

            return {"extracted": extracted, "solution": solution}
        except Exception as e:
            logger.error(f"Extract and solve error: {e}")
            return {"extracted": "", "solution": f"⚠️ Error: {e}"}
