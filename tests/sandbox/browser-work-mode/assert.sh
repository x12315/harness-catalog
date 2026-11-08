#!/usr/bin/env bash
set -euo pipefail
D=${1:?run directory required}
test "$(< "$D/guest/tmp/ah.rc")" = 0
test -s "$D/gui.png"
test -s "$D/project-source.sha256"
python3 - "$D/guest/tmp/ah.out" <<'PY'
import json,sys
from pathlib import Path
rows=[]
for line in Path(sys.argv[1]).read_text().splitlines():
    try: rows.append(json.loads(line))
    except ValueError: pass
report=next(x for x in rows if isinstance(x,dict) and x.get('passed') is True)
assert len(report['checks']) == 6, report
assert report['visible_browser_windows'], report
print('Browser work mode CLI/DOM/window isolation: PASS; semantic LLM selection not tested')
PY
