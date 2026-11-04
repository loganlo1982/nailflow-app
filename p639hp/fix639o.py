#!/usr/bin/env python3
# fix639o.py - QA-0026 (P3): anyone could fill the PHP log with "Array to string conversion" (x[]= in the address, a JSON list where a word
# is expected; ?action[]= was a 500). Now such a list is treated as not sent. api.php + the web api.php copies (Love Nails ...).
# Run:  python3 fix639o.py <release dir> <web api.php copies>   (kiem)   /   ... go
import sys, os, shutil, time, hashlib, json, subprocess
args = [a for a in sys.argv[1:]]
if not args: sys.exit('usage: python3 fix639o.py <release dir> [go]')
go = args[-1] == 'go'
if go: args = args[:-1]
R = args[0].rstrip('/'); XP = [os.path.abspath(a) for a in args[1:]]
def sha(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
F = json.loads(r"""{"api.php": {"base": "eb66eeb1", "new": "afc22ca9", "A": [["if (!is_array($in)) $in = [];\n", "if (!is_array($in)) $in = [];\n/* (2.99.639o QA-0026) a list sent where a word is expected (x[]= in the address, or a JSON list for a word) = not sent: no \"Array to string\" in the log, no 500.\n   No action reads a list from the address; these JSON words are never lists anywhere. */\nforeach ($_GET as $gk => $gv) if (is_array($gv)) unset($_GET[$gk]); if (!is_string($action)) $action = '';\nforeach (['t', 'tm', 'date', 'name', 'phone', 'k', 'code', 'token', 'email', 'start', 'pin', 'q', 'id'] as $sk) if (isset($in[$sk]) && is_array($in[$sk])) unset($in[$sk]);\n"]]}}""")
plan = []; bad = 0
for f, x in F.items():
    p = f'{R}/{f}'
    if not os.path.isfile(p): print(f, 'MISSING'); bad = 1; continue
    s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in x['A']]
    al = '639o' in s; print(f, 'sha', sha(s), '(LAMWEB base', x['base'] + ')', 'anchors', *n, 'already', al)
    if al or n != [1] * len(n): bad = 1; continue
    t = s
    for a, b in x['A']: t = t.replace(a, b)
    plan.append((f, p, t))
XA = json.loads(r"""[["if (!is_array($in)) $in = [];\n", "if (!is_array($in)) $in = [];\n/* (2.99.639o QA-0026) a list sent where a word is expected (x[]= in the address, or a JSON list for a word) = not sent: no \"Array to string\" in the log, no 500.\n   No action reads a list from the address; these JSON words are never lists anywhere. */\nforeach ($_GET as $gk => $gv) if (is_array($gv)) unset($_GET[$gk]); if (!is_string($action)) $action = '';\nforeach (['t', 'tm', 'date', 'name', 'phone', 'k', 'code', 'token', 'email', 'start', 'pin', 'q', 'id'] as $sk) if (isset($in[$sk]) && is_array($in[$sk])) unset($in[$sk]);\n"]]""")
if XA and not XP: print('NOTE: this package also patches the web api.php copies (Love Nails ~/lovenails/api.php, ...) - give their paths after the release dir'); bad = 1
for p in XP:
    s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in XA]; al = '639o' in s; print(p, 'sha', sha(s), 'anchors', *n, 'already', al)
    if al or n != [1] * len(n): bad = 1; continue
    t = s
    for a, b in XA: t = t.replace(a, b)
    plan.append((p, p, t))
NEWF = json.loads(r"""{}""")
for f, t in NEWF.items():
    p = f'{R}/{f}'; ex = os.path.exists(p); print('NEW FILE', f, 'exists' if ex else 'ok', sha(t))
    if ex: bad = 1
if bad: sys.exit('STOP: an anchor is not found exactly once, already patched, or a new file is already there - nothing changed')
if not go:
    for f, p, t in plan: print('NEW would be', f, sha(t))
    sys.exit('check only - run again with: go')
bk = os.path.expanduser('~/app/old'); os.makedirs(bk, exist_ok=True); st = time.strftime('%m%d%H%M'); done = []
made = []
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
    b = f'{bk}/' + f.strip('/').replace('/', '__') + f'.pre-639o-{st}'; shutil.copy2(p, b); m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m); done.append((p, b)); chk(p)
    print('NEW', f, sha(t), 'backup', b)
for f, t in NEWF.items():
    p = f'{R}/{f}'; open(p, 'w', encoding='utf-8').write(t); made.append(p); os.chmod(p, 0o644); chk(p); print('MADE', f, sha(t))
print('OK 2.99.639o (QA-0026) - restart php-fpm.')
