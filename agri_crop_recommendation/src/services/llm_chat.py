"""
LLM Farmer Chat
===============
Powers the /chat endpoint using Gemini to answer farmer questions
grounded in regional context (district name, state, season).

Uses gemini-2.0-flash-lite for free-tier compatibility.
Falls back gracefully with a clear message if the API is unavailable.
"""

import os
import logging
import re
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

MODEL_NAME = "gemini-2.0-flash-lite"

_gemini_client = None


def _get_client():
    global _gemini_client
    if _gemini_client is not None:
        return _gemini_client
    try:
        from google import genai
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return None
        _gemini_client = genai.Client(api_key=api_key)
        return _gemini_client
    except Exception as e:
        logger.warning(f"Gemini chat client failed to load: {e}")
        return None


# Short system persona injected into every prompt
_SYSTEM_PERSONA = (
    "You are an expert Indian agricultural advisor fluent in English, Hindi, and Marathi. "
    "You help small and marginal farmers with practical, accurate, and concise advice on crops, "
    "soil health, pest control, irrigation, market prices, government schemes, and seasonal planning. "
    "Always tailor your answer to the farmer's specific region and season. "
    "Keep responses under 150 words. Be warm, practical, and avoid jargon."
)


def answer_farmer_question(
    question: str,
    region_id: str = "",
    region_name: str = "",
    season: str = "",
) -> str:
    """
    Answer a farmer's free-form question using Gemini LLM.

    Returns the answer string, or a fallback message if unavailable.
    """
    client = _get_client()
    if client is None:
        return (
            "AI chat is not available — please add a GEMINI_API_KEY in your .env file "
            "to enable this feature. All other recommendation features work without it."
        )

    try:
        # Build context snippet
        ctx_parts = []
        if region_name:
            ctx_parts.append(f"District: {region_name}")
        elif region_id:
            ctx_parts.append(f"Region ID: {region_id}")
        if season:
            ctx_parts.append(f"Season: {season}")
        context = " | ".join(ctx_parts) if ctx_parts else "General Indian farming context"

        prompt = (
            f"{_SYSTEM_PERSONA}\n\n"
            f"Farmer context — {context}\n"
            f"Farmer's question: {question}\n\n"
            f"Provide a helpful, concise answer (max 150 words):"
        )

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )
        answer = response.text.strip()
        # Strip markdown fences if model wraps in them
        answer = re.sub(r"```[a-z]*\s*", "", answer).replace("```", "").strip()
        return answer

    except Exception as e:
        logger.warning(f"Chat response failed: {e}")
        return "I'm having trouble connecting to the AI service right now. Please try again in a moment."
