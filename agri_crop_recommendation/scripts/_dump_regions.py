import json
from collections import defaultdict

d = json.load(open('data/reference/regions.json'))
by_state = defaultdict(list)
for r in d['regions']:
    state = r['region_id'].split('_')[0]
    by_state[state].append(r['region_id'])

for state, ids in sorted(by_state.items()):
    formatted = ', '.join(f'"{i}"' for i in ids)
    print(f"# {state} ({len(ids)})")
    print(formatted)
    print()
