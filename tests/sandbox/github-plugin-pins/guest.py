"""Install-only SDK acceptance; run exclusively in a disposable macOS Tart guest."""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile

CASE = Path('/tmp/ahsb-push/tests/sandbox/github-plugin-pins')
ARCHIVE = Path('/tmp/ahsb-push/pi-sdk-runtime.tar.gz')


def run(args, **kwargs):
    print(json.dumps({'marker': 'github-plugin-pins/command', 'argv': args}), flush=True)
    return subprocess.run(args, text=True, capture_output=True, timeout=600, **kwargs)


def require(args):
    result = run(args, check=True)
    return result.stdout.strip()


assert platform.system() == 'Darwin', 'Disposable macOS guest required'
assert require(['/usr/sbin/sysctl', '-n', 'kern.hv_vmm_present']) == '1', 'VMM required; refusing bare host'
for tool in ['node', 'npm', 'git', 'tar']:
    assert shutil.which(tool), 'NOT_READY: missing ' + tool
node = shutil.which('node')
node_version = require([node, '--version'])
assert tuple(map(int, node_version.lstrip('v').split('.'))) >= (22, 19, 0), 'NOT_READY: Node >=22.19 required'
assert ARCHIVE.is_file() and not ARCHIVE.is_symlink(), 'Missing supplied SDK runtime archive'
job = Path(tempfile.mkdtemp(prefix='github-plugin-pins-')).resolve()
runtime, agent, cwd, home = [job / part for part in ['runtime', 'agent', 'cwd', 'home']]
for directory in [runtime, agent, cwd, home]:
    directory.mkdir()
with tarfile.open(ARCHIVE, 'r:gz') as archive:
    members = archive.getmembers()
    for member in members:
        path = PurePosixPath(member.name)
        assert not path.is_absolute() and '..' not in path.parts, 'Invalid archive path'
        assert path.parts and path.parts[0] == 'node_modules', 'Archive root must be node_modules/'
        assert member.isfile() or member.isdir() or member.issym() or member.islnk(), 'Unsupported archive member'
        if member.issym() or member.islnk():
            assert not PurePosixPath(member.linkname).is_absolute(), 'Archive must be relocatable'
            target = (runtime / path.parent / member.linkname) if member.issym() else (runtime / member.linkname)
            assert os.path.commonpath([runtime, target.resolve()]) == str(runtime), 'Archive link escapes runtime'
require(['/usr/bin/tar', '-xzf', str(ARCHIVE), '-C', str(runtime)])
sdk_package = runtime / 'node_modules/@earendil-works/pi-coding-agent'
for file in ['dist/core/package-manager.js', 'dist/core/settings-manager.js', 'package.json']:
    assert (sdk_package / file).is_file(), 'Supplied runtime has no real SDK: ' + file
sentinels = [agent / 'settings.json', home / '.pi/agent/settings.json', cwd / '.pi/settings.json', job / 'overlay.json']
for file in sentinels:
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text('deliberately invalid JSON: must not be read or persisted\n')
snapshot = {str(file.relative_to(job)): hashlib.sha256(file.read_bytes()).hexdigest() for file in sentinels}
env = {
    'PATH': os.environ['PATH'], 'HOME': str(home), 'TMPDIR': str(job),
    'SDK_ROOT': str(runtime), 'PLUGIN_AGENT_DIR': str(agent), 'PLUGIN_CWD': str(cwd),
    'PI_CODING_AGENT_DIR': '/nonexistent-inherited-profile',
    'PI_CODING_AGENT_SETTINGS_DIR': str(home / '.pi/agent'),
    'PI_CODING_AGENT_SETTINGS_OVERLAY': str(job / 'overlay.json'),
    'PI_CODING_AGENT_SETTINGS_OVERLAY_FIELDS': '["packages"]',
}
archive_hash = hashlib.sha256()
with ARCHIVE.open('rb') as archive_file:
    for chunk in iter(lambda: archive_file.read(1024 * 1024), b''):
        archive_hash.update(chunk)
reports = []
for mode in ['install', 'resolve']:
    result = run([node, str(CASE / 'install-only.mjs'), mode], env=env, cwd=cwd)
    print(result.stdout, end='', flush=True)
    print(result.stderr, end='', file=sys.stderr, flush=True)
    assert result.returncode == 0, 'Real SDK operation failed: ' + mode
    rows = []
    for line in result.stdout.splitlines():
        try:
            value = json.loads(line)
        except ValueError:
            continue
        if isinstance(value, dict) and value.get('marker') == 'github-plugin-pins/sdk-result':
            rows.append(value)
    assert len(rows) == 1 and rows[0]['passed'] is True and rows[0]['mode'] == mode
    reports.append(rows[0])
    assert snapshot == {str(file.relative_to(job)): hashlib.sha256(file.read_bytes()).hexdigest() for file in sentinels}
assert reports[0]['packages'] == reports[1]['packages'], 'Resolve changed installed package state'
assert reports[0]['resolved'] == reports[1]['resolved']
assert snapshot == {str(file.relative_to(job)): hashlib.sha256(file.read_bytes()).hexdigest() for file in sentinels}
assert not (agent / 'auth.json').exists() and not (agent / 'sessions').exists()
print(json.dumps({
    'marker': 'github-plugin-pins/guest-result', 'passed': True,
    'scope': 'disposable-macos-tart-install-resolve-only',
    'vmm': True, 'node': node_version, 'archiveSha256': archive_hash.hexdigest(),
    'settingsSnapshotsUnchanged': True, 'settingsSnapshot': snapshot,
    'pluginExecutionTested': False, 'profileDeclarationsChanged': False,
    'modes': ['install', 'resolve'],
}), flush=True)
