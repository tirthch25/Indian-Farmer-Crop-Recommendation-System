"""
LLM Regional Crop Filter
========================
Uses Gemini LLM to filter crops that are actually cultivated in a specific
Indian district/region, solving the 552-region coverage gap in the static
crop database.

Uses gemini-2.0-flash-lite for minimal token usage on free tier.
Falls back to unfiltered list gracefully if the API call fails.
"""

import os
import json
import logging
import re
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_gemini_client = None
MODEL_NAME = "gemini-2.0-flash-lite"


def _get_gemini_client():
    global _gemini_client
    if _gemini_client is not None:
        return _gemini_client
    try:
        from google import genai
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY not set — LLM filter disabled")
            return None
        _gemini_client = genai.Client(api_key=api_key)
        logger.info(f"Gemini client loaded ({MODEL_NAME})")
        return _gemini_client
    except Exception as e:
        logger.warning(f"Could not load Gemini client: {e}")
        return None


# Compact state-to-zone mapping for prompt context (keeps tokens low)
STATE_ZONE = {
    "MH": "Maharashtra/Marathwada: black cotton soil, semi-arid, crops: jowar, tur, cotton, soybean, bajra",
    "PB": "Punjab: alluvial soil, irrigated, crops: wheat, rice, maize, potato",
    "RJ": "Rajasthan: arid/sandy, crops: bajra, jowar, cluster bean, mustard",
    "UP": "Uttar Pradesh: fertile plain, crops: wheat, rice, sugarcane, potato, pulses",
    "GJ": "Gujarat: semi-arid coastal, crops: cotton, groundnut, castor, cumin, wheat",
    "MP": "Madhya Pradesh: black soil, crops: soybean, wheat, gram, jowar, maize",
    "KA": "Karnataka: diverse zones, crops: ragi, jowar, sugarcane, maize, vegetables",
    "TN": "Tamil Nadu: tropical, crops: rice, sugarcane, banana, groundnut, vegetables",
    "AP": "Andhra Pradesh: crops: rice, chilli, cotton, groundnut, tobacco",
    "TS": "Telangana: crops: cotton, paddy, maize, soybean, red gram",
    "WB": "West Bengal: humid, crops: rice, jute, potato, vegetables",
    "BR": "Bihar: alluvial, crops: rice, wheat, maize, lentil, vegetables",
    "HR": "Haryana: irrigated, crops: wheat, rice, sugarcane, oilseeds",
    "CG": "Chhattisgarh: tribal belt, crops: rice, maize, pulses",
    "OD": "Odisha: crops: rice, pulses, oilseeds, vegetables",
    "AS": "Assam: humid, crops: rice, jute, tea, mustard",
    "HP": "Himachal Pradesh: cool hills, crops: wheat, potato, vegetables, apple",
    "UK": "Uttarakhand: hills, crops: wheat, rice, potato, vegetables",
    "KL": "Kerala: tropical humid, crops: coconut, rubber, rice, banana, spices",
    "JH": "Jharkhand: tribal, crops: rice, maize, pulses",
}


def llm_filter_crops(
    crop_ids: List[str],
    crop_names: List[str],
    region_id: str,
    region_name: str,
    season: str,
    state: str = "",
) -> Optional[List[str]]:
    """
    Ask Gemini which crops from the list are actually cultivated in this region.

    Returns approved crop_id list, or None if LLM unavailable (caller falls back).
    """
    client = _get_gemini_client()
    if client is None:
        return None

    try:
        state_code = region_id.split("_")[0].upper() if region_id else ""
        zone_hint  = STATE_ZONE.get(state_code, "")

        # Compact crop list: "BAJRA_01=Bajra, JOWAR_01=Jowar, ..."
        crop_list_str = ", ".join(
            f"{cid}={name}" for cid, name in zip(crop_ids, crop_names)
        )

        # Short, token-efficient prompt
        prompt = (
            f"Indian agriculture expert. District: {region_name} ({state_code}). "
            f"Zone info: {zone_hint}. Season: {season}.\n"
            f"Crops: {crop_list_str}\n"
            f"Which crops are actually grown here? Remove crops unsuitable for this zone.\n"
            f"Reply ONLY JSON: {{\"ok\":[approved crop_ids],\"no\":[removed crop_ids]}}"
        )

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )
        text = response.text.strip()
        # Strip markdown fences if any
        text = re.sub(r"```(?:json)?\s*", "", text).replace("```", "").strip()

        data     = json.loads(text)
        approved = data.get("ok", [])
        removed  = data.get("no", [])

        if removed:
            logger.info(f"LLM removed for {region_name}: {removed}")

        valid_ids      = set(crop_ids)
        approved_valid = [c for c in approved if c in valid_ids]

        if not approved_valid:
            logger.warning("LLM returned empty list — falling back to all crops")
            return None

        logger.info(f"LLM gate: {len(crop_ids)} → {len(approved_valid)} crops for {region_name}")
        return approved_valid

    except json.JSONDecodeError as e:
        logger.warning(f"LLM JSON parse error: {e}")
        return None
    except Exception as e:
        logger.warning(f"LLM filter failed (fallback active): {e}")
        return None
