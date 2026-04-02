"""
Live LLM test — run after quota resets.
python scripts/test_llm_live.py
"""
import sys, os
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv()   # loads real key from .env

print(f"API key loaded: {'Yes' if os.getenv('GEMINI_API_KEY') else 'NO - check .env'}")
print()

# ── Test LLM Filter live ──────────────────────────────────────────────────────
print("=== LIVE LLM Filter Test (Nanded Kharif) ===")
import src.services.llm_filter as lf
lf._gemini_client = None   # force fresh client

from src.services.llm_filter import llm_filter_crops

test_ids   = ['BAJRA_01','JOWAR_01','MOONG_01','SOYBEAN_01',
              'BABY_CORN_01','LETTUCE_01','SPINACH_01','MICROGREENS_01']
test_names = ['Bajra','Jowar','Moong','Soybean',
              'Baby Corn','Lettuce','Spinach','Microgreens']

result = llm_filter_crops(
    crop_ids=test_ids,
    crop_names=test_names,
    region_id='MH_NANDED',
    region_name='Nanded',
    season='Kharif',
    state='Maharashtra'
)

if result is not None:
    removed = [n for cid, n in zip(test_ids, test_names) if cid not in result]
    kept    = [n for cid, n in zip(test_ids, test_names) if cid in result]
    print(f"Kept ({len(kept)}):    {kept}")
    print(f"Removed ({len(removed)}): {removed}")
    print()
    print("Baby Corn removed?", 'BABY_CORN_01' not in result, "(expected: True)")
    print("Lettuce removed?",   'LETTUCE_01'   not in result, "(expected: True)")
    print("Jowar kept?",        'JOWAR_01'      in result,    "(expected: True)")
else:
    print("LLM returned None — quota still rate-limited, try again in a few minutes")

# ── Test LLM Explainer live ───────────────────────────────────────────────────
print("\n=== LIVE LLM Explainer Test ===")
import src.services.llm_explainer as le
le._gemini_client = None

from src.services.llm_explainer import generate_crop_explanation

exp = generate_crop_explanation(
    crop_name="Jowar (Sorghum)",
    region_name="Nanded",
    region_id="MH_NANDED",
    season="Kharif",
    suitability_score=94.7,
    avg_temp=29.5,
    expected_rainfall=750.0,
    soil_texture="Clay-Loam",
    soil_ph=7.2,
    risk_note="Low risk",
)

if exp:
    print("English:", exp.get("english"))
    print("Why good:", exp.get("why_good"))
    print("Watch out:", exp.get("watch_out"))
    if "marathi" in exp:
        print("Marathi:", exp.get("marathi"))
    print("\nPASS: LLM Explainer working!")
else:
    print("LLM Explainer returned empty — quota still limited, try again later")
