# Reproducibility

The generator uses `random.Random(20261022)`, fixed reference timestamp `2026-10-30T12:00:00`, immutable zero-padded IDs and stable table ordering. `starter` and `full` profiles call the same generator; only scale differs. Each output directory contains `reproducibility_sha256.json`, a SHA-256 manifest of every generated output file except the manifest itself. To verify reproducibility, generate twice into two separate directories and compare manifests:

```bash
python generator/generate_data.py --profile starter --output /tmp/acr-a
python generator/generate_data.py --profile starter --output /tmp/acr-b
python - <<'PY'
import json
from pathlib import Path
x=json.loads(Path('/tmp/acr-a/reproducibility_sha256.json').read_text())
y=json.loads(Path('/tmp/acr-b/reproducibility_sha256.json').read_text())
assert x == y, 'Reproducibility check failed'
print(f'PASS: {len(x)} file checksums match')
PY
```

Checksums are expected to match for identical Python/runtime settings. No wall-clock timestamp is used in synthetic event generation.
