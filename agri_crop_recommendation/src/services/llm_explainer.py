"""
LLM Crop Explainer
==================
Uses Gemini LLM to generate farmer-friendly explanations for top recommended crops.
Uses gemini-2.0-flash-lite with compact prompts for free-tier compatibility.
"""

import os
import json
import logging
import re
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

MARATHI_STATES = {"MH"}
HINDI_STATES   = {"UP", "MP", "RJ", "HR", "PB", "UK", "HP", "BR", "JH", "CG", "DL", "GJ"}
MODEL_NAME     = "gemini-2.0-flash-lite"

_gemini_client = None


def _get_gemini_client():
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
        logger.warning(f"Gemini explainer client failed: {e}")
        return None


def generate_crop_explanation(
    crop_name: str,
    region_name: str,
    region_id: str,
    season: str,
    suitability_score: float,
    avg_temp: float,
    expected_rainfall: float,
    soil_texture: str,
    soil_ph: float,
    risk_note: str,
    growing_tip: str = "",
) -> Dict[str, str]:
    """Generate a short farmer-friendly explanation for one crop. Returns {} on failure."""
    client = _get_gemini_client()
    if client is None:
        return {}

    try:
        state_code = region_id.split("_")[0].upper() if region_id else ""
        local_lang = None
        if state_code in MARATHI_STATES:
            local_lang = "Marathi"
        elif state_code in HINDI_STATES:
            local_lang = "Hindi"

        lang_part = f', "{local_lang.lower()}":"same in {local_lang}"' if local_lang else ""

        prompt = (
            f"Indian agri expert. Crop:{crop_name}, Region:{region_name}, Season:{season}. "
            f"Score:{suitability_score:.0f}/100, Temp:{avg_temp:.0f}C, Rain:{expected_rainfall:.0f}mm, "
            f"Soil:{soil_texture} pH{soil_ph:.1f}, Risk:{risk_note}.\n"
            f"Reply ONLY JSON: {{\"english\":\"2-sentence why this crop suits farmer here\","
            f"\"why_good\":\"best reason <10 words\",\"watch_out\":\"key tip <12 words\"{lang_part}}}"
        )

        response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
        text = response.text.strip()
        text = re.sub(r"```(?:json)?\s*", "", text).replace("```", "").strip()
        return json.loads(text)

    except Exception as e:
        logger.debug(f"LLM explanation failed for {crop_name}: {e}")
        return {}


def generate_bulk_explanations(
    crops: List[Dict],
    region_name: str,
    region_id: str,
    season: str,
    avg_temp: float,
    expected_rainfall: float,
    soil_texture: str,
    soil_ph: float,
    top_n: int = 3,
) -> List[Dict]:
    """Attach LLM explanations to top N crops; skip rest to save API quota."""
    for i, crop in enumerate(crops):
        if i >= top_n:
            break
        explanation = generate_crop_explanation(
            crop_name=crop.get("crop", ""),
            region_name=region_name,
            region_id=region_id,
            season=season,
            suitability_score=crop.get("suitability_score", 0),
            avg_temp=avg_temp,
            expected_rainfall=crop.get("expected_rainfall_mm", expected_rainfall),
            soil_texture=soil_texture,
            soil_ph=soil_ph,
            risk_note=crop.get("risk_note", "Low risk"),
            growing_tip=crop.get("growing_tip", ""),
        )
        crop["llm_explanation"] = explanation
    return crops
