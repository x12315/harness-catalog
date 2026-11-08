"""Real browser mode/isolation checks, only invoked inside disposable macOS guest."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import urllib.parse

work = Path(tempfile.mkdtemp(prefix='browser-mode-'))
config = work / 'config.json'
config.write_text(json.dumps({'headed': True}))
prefix = f'ahsb-mode-{os.getpid()}'
background, collaboration = prefix + '-bg', prefix + '-collab'
evidence = {'scope':'disposable macOS guest only; real CLI/DOM/window checks, not LLM semantic evaluation', 'checks':[]}

def cmd(args, timeout=30):
    return subprocess.run(args, text=True, capture_output=True, timeout=timeout, check=True).stdout.strip()

def browser(session, args, headed=None):
    argv = ['agent-browser', '--config', str(config), '--session', session, '--json']
    if headed is None:
        headed = session == collaboration
    argv += ['--headed', 'true' if headed else 'false']
    value = json.loads(cmd(argv + args))
    assert value['success'], value
    print(json.dumps({'operation':args[0],'session':session,'result':value}), flush=True)
    return value

def url(title):
    html = f'<!doctype html><title>{title}</title><h1>{title}</h1><label>Message<input id="message"></label><button id="echo">Echo</button><pre id="result">empty</pre>'
    html += '<script>document.getElementById("echo").onclick=()=>{document.getElementById("result").textContent=document.getElementById("message").value;};</script>'
    return 'data:text/html,' + urllib.parse.quote(html)

def text(session):
    return browser(session, ['get','text','#result'])['data']['text']

try:
    evidence['version'] = cmd(['agent-browser','--version'])
    bgtitle, cotitle = prefix + '-Background', prefix + '-Collaboration'
    browser(background, ['open',url(bgtitle)], headed=False)
    browser(background, ['fill','#message','background-independent'])
    browser(background, ['click','#echo'])
    assert text(background) == 'background-independent'
    browser(collaboration, ['open',url(cotitle)], headed=True)
    browser(collaboration, ['fill','#message','human-shared-page'])
    browser(collaboration, ['click','#echo'])
    assert text(collaboration) == 'human-shared-page'
    assert text(background) == 'background-independent'
    evidence['checks'].append('simultaneous_named_sessions_have_independent_DOM')
    code = """ObjC.import('CoreGraphics'); const ws=ObjC.deepUnwrap(ObjC.castRefToObject($.CGWindowListCopyWindowInfo(1,0))); JSON.stringify(ws.filter(w=>w.kCGWindowLayer===0 && w.kCGWindowAlpha>0).map(w=>({owner:w.kCGWindowOwnerName,title:w.kCGWindowName})));"""
    windows = json.loads(cmd(['/usr/bin/osascript','-l','JavaScript','-e',code]))
    assert any(w.get('title') == cotitle for w in windows), windows
    assert not any(w.get('title') == bgtitle for w in windows), windows
    evidence['visible_browser_windows'] = [w for w in windows if w.get('title') in [bgtitle,cotitle]]
    processes = cmd(['/bin/ps','-axww','-o','command=']).splitlines()
    headless = [p for p in processes if 'Chrome for Testing.app/Contents/MacOS/' in p and '--headless' in p]
    assert headless, 'No real headless Chrome process found'
    evidence['checks'] += ['explicit_headed_false_overrides_headed_true_config','collaboration_has_real_guest_window_background_has_none','headless_process_flag_observed']
    # Synthetic handover: human-equivalent edit inside the shared guest page,
    # then fresh DOM read. This is not evidence of an actual human takeover.
    browser(collaboration, ['fill','#message','edited-at-handover'])
    browser(collaboration, ['click','#echo'])
    assert text(collaboration) == 'edited-at-handover'
    assert text(background) == 'background-independent'
    evidence['checks'].append('synthetic_handover_fresh_read_preserves_other_session')
    browser(background, ['close'])
    assert text(collaboration) == 'edited-at-handover'
    evidence['checks'].append('closing_owned_background_preserves_collaboration')
    evidence['passed'] = True
    print(json.dumps(evidence, ensure_ascii=False))
finally:
    # Runner captures the remaining collaboration guest window then destroys VM.
    try:
        browser(background, ['close'])
    except Exception:
        pass
