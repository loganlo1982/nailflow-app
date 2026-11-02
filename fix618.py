#!/usr/bin/env python3
# LAMWEB 2.99.618 (LENH-618 BO SUNG - AI CALL test, loi S10): tx_log wrote the callers' full phone numbers into error_log (the first 10 payloads of each kind).
#  Now "+1******0201" (last 4 kept).  L3b tx_amd wrote 'vm' over a call vmpart had just moved ('vmai') -> a 2nd move to the AI: now only when not moved yet. CHANGED: inc/calls-tx.php only (live 2.99.616 d16b87a3). Nothing in the AN public_html copies.
# Run (in the app folder):  python3 fix618.py <app dir>  /  python3 fix618.py <app dir> go
import sys, os, shutil, time, hashlib, json, subprocess
R = sys.argv[1].rstrip('/'); go = len(sys.argv) > 2 and sys.argv[2] == 'go'
def sha(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
F = json.loads(r'''{"inc/calls-tx.php": {"base": "d16b87a3", "new": "787f57b6", "A": [["et_setting('tx_logn', json_encode($j));\n    error_log('612 tx ' . $kind . ' #' . ($n + 1) . ': ' . mb_substr(json_encode($data, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE), 0, 1500));\n}\n\n/* the request body: TeXML posts form", "et_setting('tx_logn', json_encode($j));\n    error_log('612 tx ' . $kind . ' #' . ($n + 1) . ': ' . mb_substr((string)preg_replace('/\\+1\\d{6}(\\d{4})/', '+1******$1', (string)json_encode($data, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE)), 0, 1500)); /* (2.99.618 S10) no full phone numbers in the log */\n}\n\n/* the request body: TeXML posts form"], [" 'machine') || str_contains($r, 'fax');\n    q('UPDATE calls SET screen = ? WHERE call_sid = ?', [$mach ? 'vm' : 'human', $sid]);\n    $hf = cl_dir() . '/txh-' . md5($sid)", " 'machine') || str_contains($r, 'fax');\n    q(\"UPDATE calls SET screen = ? WHERE call_sid = ? AND (screen IS NULL OR screen NOT IN ('vmai', 'person'))\", [$mach ? 'vm' : 'human', $sid]); /* (2.99.618 L3b) never over a call already moved by vmpart / screened */\n    $hf = cl_dir() . '/txh-' . md5($sid)"]]}}''')
NEWF = json.loads(r'''{}''')
plan = []; bad = 0
for f, x in F.items():
    p = f'{R}/{f}'; s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in x['A']]
    al = '2.99.618' in s; print(f, 'sha', sha(s), '(LAMWEB base', x['base'] + ')', 'anchors', *n, 'already', al)
    if al or n != [1] * len(n): bad = 1; continue
    t = s
    for a, b in x['A']: t = t.replace(a, b)
    plan.append((f, p, t))
for f, t in NEWF.items():
    p = f'{R}/{f}'; ex = os.path.exists(p); print('NEW', f, 'exists' if ex else 'ok', sha(t))
    if ex: bad = 1
if bad: sys.exit('STOP: an anchor is not found exactly once, already patched, or a new file is already there - nothing changed')
if not go:
    for f, p, t in plan: print('NEW would be', f, sha(t))
    sys.exit('check only - run again with: go')
bk = os.path.expanduser('~/app/old'); os.makedirs(bk, exist_ok=True); st = time.strftime('%m%d%H%M'); done = []; made = []
def back(msg):
    for q, bb in done: shutil.copy2(bb, q)
    for q in made:
        try: os.remove(q)
        except OSError: pass
    sys.exit('ERROR ' + msg + ' - every file put back, new files removed')
def chk(p):
    c = ['php', '-l', p] if p.endswith('.php') else (['node', '--check', p] if p.endswith('.js') and shutil.which('node') else None)
    if not c: return
    r = subprocess.run(c, capture_output=True, text=True)
    if r.returncode: back('in ' + p + ': ' + (r.stdout + r.stderr)[:300])
for f, p, t in plan:
    b = f'{bk}/' + f.replace('/', '__') + f'.pre-618-{st}'; shutil.copy2(p, b); m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m); done.append((p, b)); chk(p)
    print('NEW', f, sha(t), 'backup', b)
for f, t in NEWF.items():
    p = f'{R}/{f}'
    open(p, 'w', encoding='utf-8').write(t); made.append(p)
    os.chmod(p, 0o644)
    chk(p); print('MADE', f, sha(t))
print('OK 2.99.618 (no full phone numbers in the Telnyx log) - set APP_VERSION 2.99.618 (core.php), restart php-fpm. Nothing in the AN public_html copies.')
