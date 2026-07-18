"""
Gemini Service — Google AI Studio integration for math tutoring.

Provides:
- GeminiService: Text-based math query processing with Gemini 2.0 Flash
- GeminiVisionService: Image math extraction using Gemini Vision
- Streaming support for token-by-token SSE delivery
- Automatic fallback from Gemini 2.0 Flash → Gemini 1.5 Flash on rate limits

Uses Google AI Studio free tier via the google-genai SDK.
"""

import time
import logging
from typing import Dict, Any, Optional, AsyncGenerator

from backend.src.config import settings
from backend.src.services.prompt_service import PromptService

logger = logging.getLogger("math_assistant.gemini")

_GEMINI_CLIENT = None

def _get_gemini_client():
    global _GEMINI_CLIENT
    if _GEMINI_CLIENT is None:
        from google import genai
        api_key = settings.gemini_api_key
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not set. Get a free key at https://aistudio.google.com/apikey "
                "and add it to your .env file."
            )
        _GEMINI_CLIENT = genai.Client(api_key=api_key)
        logger.info("Initialized google-genai Client")
    return _GEMINI_CLIENT

def _get_safety_settings():
    from google.genai import types
    return [
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
            threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
            threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        ),
    ]


class GeminiService:
    """Google Gemini text-based math query service with automatic fallback."""

    def __init__(self):
        self.primary_model = settings.gemini_primary_model
        self.fallback_model = settings.gemini_fallback_model
        self.prompt_service = PromptService()

    def query(self, user_input: str, context: str = "", chat_history: list = None) -> str:
        """Send a math query to Gemini and return the response."""
        from google.genai import types
        
        system_template = self.prompt_service.get_system_prompt()
        system_text = system_template.replace("{context}", context or "")

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

        models_to_try = [self.primary_model, self.fallback_model]
        last_error = None
        client = _get_gemini_client()

        config = types.GenerateContentConfig(
            temperature=settings.gemini_temperature,
            max_output_tokens=settings.gemini_max_tokens,
            safety_settings=_get_safety_settings()
        )

        for model_name in models_to_try:
            for attempt in range(2):
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=config
                    )

                    if response.text:
                        answer = response.text.strip()
                        if model_name != self.primary_model:
                            answer = f"*(Using fallback: {model_name})*\n\n" + answer
                        return answer
                    else:
                        raise Exception("Empty response or content blocked by safety filters.")

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

        logger.error(f"All Gemini models failed: {last_error}")
        return f"⚠️ Gemini API error: {last_error}"

    async def stream(self, user_input: str, context: str = "", chat_history: list = None) -> AsyncGenerator[str, None]:
        """Stream a response token by token for SSE delivery."""
        from google.genai import types
        
        system_template = self.prompt_service.get_system_prompt()
        system_text = system_template.replace("{context}", context or "")
        
        parts = [system_text + "\n\n"]
        if chat_history:
            for msg in chat_history:
                role = getattr(msg, "type", "human")
                content = getattr(msg, "content", str(msg))
                prefix = "Student: " if role == "human" else "Teacher: "
                parts.append(f"{prefix}{content}\n")
        parts.append(f"Student: {user_input}\nTeacher: ")
        prompt = "".join(parts)

        client = _get_gemini_client()
        config = types.GenerateContentConfig(
            temperature=settings.gemini_temperature,
            max_output_tokens=settings.gemini_max_tokens,
            safety_settings=_get_safety_settings()
        )

        try:
            response_stream = client.models.generate_content_stream(
                model=self.primary_model,
                contents=prompt,
                config=config
            )
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.error(f"Primary model {self.primary_model} streaming failed: {e}")
            logger.info(f"Falling back to {self.fallback_model}...")
            try:
                response_stream = client.models.generate_content_stream(
                    model=self.fallback_model,
                    contents=prompt,
                    config=config
                )
                for chunk in response_stream:
                    if chunk.text:
                        yield chunk.text
            except Exception as e2:
                logger.error(f"Fallback model {self.fallback_model} streaming also failed: {e2}")
                logger.info("Falling back to gemini-1.5-flash-8b...")
                try:
                    response_stream = client.models.generate_content_stream(
                        model="gemini-1.5-flash-8b",
                        contents=prompt,
                        config=config
                    )
                    for chunk in response_stream:
                        if chunk.text:
                            yield chunk.text
                except Exception as e3:
                    logger.error(f"All Gemini streaming models failed: {e3}")
                    yield f"\n\n⚠️ Streaming error: All Gemini models failed. You might be out of API quota."

class GeminiVisionService:
    """Gemini Vision for extracting math from images."""

    def __init__(self):
        self.model_name = settings.gemini_vision_model

    def extract_math_from_image(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
        from google.genai import types
        client = _get_gemini_client()

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

        config = types.GenerateContentConfig(safety_settings=_get_safety_settings())
        try:
            response = client.models.generate_content(
                model=self.model_name,
                contents=[
                    prompt,
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
                ],
                config=config
            )
            if response.text:
                return response.text.strip()
            return "Could not extract math from image."
        except Exception as e:
            logger.error(f"Vision extraction error: {e}")
            return f"Vision error: {e}"

    def extract_and_solve(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> Dict[str, str]:
        from google.genai import types
        client = _get_gemini_client()

        prompt = (
            "You are an Indian math teacher. Look at this image.\n\n"
            "Step 1: Extract the math problem from the image.\n"
            "Step 2: Solve it step-by-step in whiteboard style.\n\n"
            "Format your response as:\n"
            "EXTRACTED: [the math problem]\n"
            "---\n"
            "SOLUTION:\n[step-by-step solution]\n"
        )

        config = types.GenerateContentConfig(safety_settings=_get_safety_settings())
        try:
            response = client.models.generate_content(
                model=self.model_name,
                contents=[
                    prompt,
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
                ],
                config=config
            )
            text = response.text.strip() if response.text else ""

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
