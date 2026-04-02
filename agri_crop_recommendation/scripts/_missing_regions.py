import sys, json
sys.path.insert(0, '.')
from src.crops.database import ZONE_REGIONS

all_zone_ids = set()
for zone, ids in ZONE_REGIONS.items():
    all_zone_ids.update(ids)

d = json.load(open('data/reference/regions.json'))
all_region_ids = set(r['region_id'] for r in d['regions'])
missing = sorted(all_region_ids - all_zone_ids)
print(f'Missing ({len(missing)}):')
for m in missing:
    print(m)
