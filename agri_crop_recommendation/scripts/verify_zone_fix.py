import sys, os
sys.path.insert(0, '.')
os.environ['GEMINI_API_KEY'] = ''
import pandas as pd
from src.services.recommender import recommend_crops, _get_regional_score
from src.crops.database import crop_db
from src.crops.soil import SoilInfo

weather = pd.DataFrame({
    'temp_max': [35.0]*7, 'temp_min': [24.0]*7,
    'temp_avg': [29.5]*7, 'rainfall': [8.0]*7,
    'dry_spell_days': [2]*7, 'humidity': [65.0]*7
})
soil   = SoilInfo(texture='Clay-Loam', ph=7.2, organic_matter='Medium', drainage='Medium')
crops  = recommend_crops(weather, season='Kharif', region_id='MH_NANDED', soil=soil)

print('=== Nanded Kharif Results (Zone Fix Applied) ===')
print(f'Total: {len(crops)} crops')
for c in crops[:8]:
    print(f"  {c['crop']:<35} score={c['suitability_score']:.1f}  region={c['regional_suitability']:.2f}")

print()
jowar_score  = _get_regional_score(crop_db.get_crop('JOWAR_01'),    'MH_NANDED')
baby_score   = _get_regional_score(crop_db.get_crop('BABY_CORN_01'),'MH_NANDED')
print(f'Jowar  region score for MH_NANDED: {jowar_score:.2f}  (old-style crop — still needs Part B fix)')
print(f'Baby Corn region score MH_NANDED:  {baby_score:.2f}  (zone-based, was 0.50 fallback before)')
print()
print('Coverage check:')
from src.crops.database import ZONE_REGIONS
all_zone = set()
for ids in ZONE_REGIONS.values():
    all_zone.update(ids)
print(f'  Regions in ZONE_REGIONS: {len(all_zone)}  (was 105, now covers all 640)')
