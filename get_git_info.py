import subprocess
import json

data = {
    'branch': subprocess.getoutput('git branch'),
    'refs': subprocess.getoutput('git show-ref'),
    'remote': subprocess.getoutput('git remote -v'),
    'status': subprocess.getoutput('git status')
}

with open('git_info.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)
