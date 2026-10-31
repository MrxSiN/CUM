"""Independent trusted-guest driver; the native BF planner chooses recovery steps."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def tool(path):
    return {'executable': path, 'sha256': hashlib.sha256(Path(path).read_bytes()).hexdigest()}


spec = json.loads(Path('/bindings/recovery.json').read_text())
openssl, wine = tool('/usr/bin/openssl'), tool('/usr/lib/wine/wine64')
for operand in ('21', '23', '25'):
    spec['bindings'][operand]['openssl'] = openssl
spec['planner_launcher'] = wine
spec['planner_timeout_seconds'] = 120


def invoke(binding, path):
    path.write_text(json.dumps(binding))
    return subprocess.run([sys.executable, '-I', '/runtime/runtime_entry.py', 'flow', str(path),
                           '--command', '2', '--mode', '1'], capture_output=True, timeout=240)


completed = invoke(spec, Path('/results/binding.json'))
if completed.returncode:
    sys.stderr.buffer.write(completed.stderr)
    raise SystemExit(completed.returncode)
assert json.loads(Path('/results/flow.json').read_text())['status'] == 'PASS'
negatives = []
for label, operand, field in (('project', '22', 'project_id'), ('release', '22', 'release_identity'),
                               ('identity-project', '24', 'project_id')):
    bad = copy.deepcopy(spec)
    bad['journal'] = '/results/' + label + '-flow.json'
    bad['bindings'][operand]['fields'][field] = 'unexpected-context'
    rejected = invoke(bad, Path('/results/' + label + '-binding.json'))
    assert rejected.returncode != 0
    journal = json.loads(Path(bad['journal']).read_text())
    assert not any(r['operand'] == 25 for r in journal['receipts'])
    negatives.append({'mutation': label, 'status': 'PASS', 'rejected_before_decryption': True,
                      'error': journal['error']['error']})
Path('/results/checks.json').write_text(json.dumps({'status': 'PASS', 'rejections': negatives}))
Path('/results/tools.json').write_text(json.dumps({'openssl': openssl, 'wine': wine,
    'openssl_version': subprocess.check_output([openssl['executable'], 'version']).decode().strip()}))
