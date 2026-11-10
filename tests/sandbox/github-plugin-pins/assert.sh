#!/usr/bin/env bash
set -euo pipefail
D=${1:?run directory required}
test "$(< "$D/guest/tmp/ah.rc")" = 0
test -s "$D/project-source.sha256"
python3 - "$D/guest/tmp/ah.out" "${AHSB_CASE_DIR:?}/pins.json" <<'PY'
import json,sys
from pathlib import Path
pins=json.loads(Path(sys.argv[2]).read_text())
rows=[]
for line in Path(sys.argv[1]).read_text().splitlines():
    try: value=json.loads(line)
    except ValueError: continue
    if isinstance(value,dict): rows.append(value)
guests=[r for r in rows if r.get('marker')=='github-plugin-pins/guest-result']
assert len(guests)==1, guests
guest=guests[0]
assert guest['passed'] is True and guest['vmm'] is True
assert guest['scope']=='disposable-macos-tart-install-resolve-only'
assert guest['settingsSnapshotsUnchanged'] is True
assert guest['pluginExecutionTested'] is False and guest['profileDeclarationsChanged'] is False
assert guest['modes']==['install','resolve']
assert len(guest['archiveSha256'])==64
reports=[r for r in rows if r.get('marker')=='github-plugin-pins/sdk-result']
assert [r['mode'] for r in reports]==['install','resolve']
for report in reports:
    assert report['passed'] is True and report['settingsStorage']=='inMemory'
    assert report['settingsPersisted'] is False and report['pluginsExecuted'] is False
    assert len(report['packages'])==len(pins)==2
    assert 'PI_CODING_AGENT_SETTINGS_OVERLAY' in report['ignoredEnvironment']
    for pin,pkg in zip(pins,report['packages']):
        for key in ['name','source','head','files','contentSetSha256']:
            assert pkg[key]==pin[key], (key,pkg)
        assert pkg['lockfileExcludedFromResourceHash'] is True
        assert isinstance(pkg['status'],str) and isinstance(pkg['generatedLockfile'],bool)
        resources=[r for r in report['resolved']['extensions'] if r['metadata']['source']==pin['source']]
        assert len(resources)==1 and resources[0]['enabled'] is True
        assert resources[0]['path']==pkg['installedPath']+'/'+pin['entry']
    installs=[c for c in report['commands'] if c.get('api')=='DefaultPackageManager.install']
    assert len(installs)==(2 if report['mode']=='install' else 0)
    assert len(report['resolved']['extensions'])==2
    assert all(report['resolved'][key]==[] for key in ['skills','prompts','themes'])
assert reports[0]['packages']==reports[1]['packages']
assert not any(r.get('marker')=='github-plugin-pins/progress' and r.get('type')=='error' for r in rows)
print('GitHub pins: real SDK install + installed-only resolution PASS; plugin execution not tested')
PY
