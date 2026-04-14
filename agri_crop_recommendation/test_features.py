import sys, os
sys.path.insert(0, '.')
from src.api.app import app
from fastapi.testclient import TestClient

client = TestClient(app)

# Test recommend endpoint
resp = client.post('/recommend', json={'region_id': 'MH_PUNE', 'irrigation': 'Full', 'planning_days': 90})
if resp.status_code == 200:
    data = resp.json()
    crops = data.get('recommended_crops', [])
    print(f'OK: Got {len(crops)} crops')
    if crops:
        c = crops[0]
        print(f'Top crop: {c["crop"]}')
        print(f'  Suitability: {c.get("suitability_score")}')
        print(f'  Score source: {c.get("score_source")}')
else:
    print(f'ERROR {resp.status_code}: {resp.text[:500]}')
