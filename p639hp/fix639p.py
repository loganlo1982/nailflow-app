#!/usr/bin/env python3
# fix639p.py - QA-0027 (P3): data the screens never send, from the owner: a price "1e309" -> INF (the service vanished online), a very long
# "not the same person" pair, colors_import without rows (warning). (appt_rename with a list = "ARRAY" is already fixed by 639o.) 3 files.
# Run:  python3 fix639p.py <release dir>   (kiem)   /   ... go
import sys, os, shutil, time, hashlib, json, subprocess
args = [a for a in sys.argv[1:]]
if not args: sys.exit('usage: python3 fix639p.py <release dir> [go]')
go = args[-1] == 'go'
if go: args = args[:-1]
R = args[0].rstrip('/'); XP = [os.path.abspath(a) for a in args[1:]]
def sha(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
F = json.loads(r"""{"inc/api/_menu.php": {"base": "34c027f9", "new": "f1122e85", "A": [["function money($v): float { return round(max(0, (float)$v), 2); }", "function money($v): float { $f = is_scalar($v) ? (float)$v : 0.0; return is_finite($f) ? round(max(0, min($f, 1000000)), 2) : 0.0; } /* (2.99.639p QA-0027) \"1e309\" was INF (the service vanished from the booking page); a list was 1 */"]]}, "inc/api/customers.php": {"base": "d281557a", "new": "9860e765", "A": [["    $l = dup_ignored(); $l[] = dup_key((string)($in['a'] ?? ''), (string)($in['b'] ?? ''));", "    $l = dup_ignored(); $l[] = dup_key(mb_substr(is_string($in['a'] ?? null) ? $in['a'] : '', 0, 20), mb_substr(is_string($in['b'] ?? null) ? $in['b'] : '', 0, 20)); /* (2.99.639p QA-0027) a pair = 2 numbers, never anything long */"]]}, "inc/api/colors.php": {"base": "28847df7", "new": "d3853046", "A": [["        $sent = []; foreach ((array)$in['rows'] as $x)", "        $sent = []; foreach ((array)($in['rows'] ?? []) /* 639p QA-0027 */ as $x)"]]}}""")
plan = []; bad = 0
for f, x in F.items():
    p = f'{R}/{f}'
    if not os.path.isfile(p): print(f, 'MISSING'); bad = 1; continue
    s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in x['A']]
    al = '639p' in s; print(f, 'sha', sha(s), '(LAMWEB base', x['base'] + ')', 'anchors', *n, 'already', al)
    if al or n != [1] * len(n): bad = 1; continue
    t = s
    for a, b in x['A']: t = t.replace(a, b)
    plan.append((f, p, t))
XA = json.loads(r"""[]""")
if XA and not XP: print('NOTE: this package also patches the web api.php copies (Love Nails ~/lovenails/api.php, ...) - give their paths after the release dir'); bad = 1
for p in XP:
    s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in XA]; al = '639p' in s; print(p, 'sha', sha(s), 'anchors', *n, 'already', al)
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
    b = f'{bk}/' + f.strip('/').replace('/', '__') + f'.pre-639p-{st}'; shutil.copy2(p, b); m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m); done.append((p, b)); chk(p)
    print('NEW', f, sha(t), 'backup', b)
for f, t in NEWF.items():
    p = f'{R}/{f}'; open(p, 'w', encoding='utf-8').write(t); made.append(p); os.chmod(p, 0o644); chk(p); print('MADE', f, sha(t))
print('OK 2.99.639p (QA-0027) - restart php-fpm.')
