#!/usr/bin/env python3
# fix639l.py - QA-0019 (P2, security): Quick checkout had its own tech-PIN counter (5 wrong -> 15 min, again and again) with NO 24 h lock.
# Now it uses the same tech PIN locks as /tech/ too (pin_locked / pin_locked_day / pin_fail / pin_clear). 1 file.
# Run:  python3 fix639l.py <release dir>   (kiem)   /   ... go
import sys, os, shutil, time, hashlib, json, subprocess
args = [a for a in sys.argv[1:]]
if not args: sys.exit('usage: python3 fix639l.py <release dir> [go]')
go = args[-1] == 'go'
if go: args = args[:-1]
R = args[0].rstrip('/'); XP = [os.path.abspath(a) for a in args[1:]]
def sha(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
F = json.loads(r"""{"inc/quick-checkout.php": {"base": "8eba0a89", "new": "6c971c02", "A": [["    $pin = preg_replace('/\\D/', '', (string)($in['pin'] ?? ''));\n    if ($pin === '' || !password_verify($pin, (string)$s['pin_hash'])) {\n        q('INSERT INTO login_attempts (ip, at) VALUES (?, ?)', ['QP:' . $sid, time()]);\n", "    if (function_exists('pin_locked_day') && (pin_locked($sid) || pin_locked_day($sid))) fail(TV('Too many wrong PINs \u2013 ' . $s['name'] . ' is locked. Try again later or ask the owner.', 'Sai PIN qu\u00e1 nhi\u1ec1u \u2013 ' . $s['name'] . ' \u0111ang b\u1ecb kho\u00e1. Th\u1eed l\u1ea1i sau ho\u1eb7c nh\u1edd ch\u1ee7 ti\u1ec7m.'), 429); /* (2.99.639l QA-0019) the same tech PIN locks as /tech/ (15 min, 24 h) */\n    $pin = preg_replace('/\\D/', '', (string)($in['pin'] ?? ''));\n    if ($pin === '' || !password_verify($pin, (string)$s['pin_hash'])) {\n        if (function_exists('pin_fail')) pin_fail($sid); /* 639l: counts toward the 24 h lock too */\n        q('INSERT INTO login_attempts (ip, at) VALUES (?, ?)', ['QP:' . $sid, time()]);\n"], ["    q('DELETE FROM login_attempts WHERE ip = ?', ['QP:' . $sid]);\n    return ['ok' => true, 'staff' => $sid, 'ptok' =>", "    q('DELETE FROM login_attempts WHERE ip = ?', ['QP:' . $sid]); if (function_exists('pin_clear')) pin_clear($sid); /* 639l */\n    return ['ok' => true, 'staff' => $sid, 'ptok' =>"]]}}""")
plan = []; bad = 0
for f, x in F.items():
    p = f'{R}/{f}'
    if not os.path.isfile(p): print(f, 'MISSING'); bad = 1; continue
    s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in x['A']]
    al = '639l' in s; print(f, 'sha', sha(s), '(LAMWEB base', x['base'] + ')', 'anchors', *n, 'already', al)
    if al or n != [1] * len(n): bad = 1; continue
    t = s
    for a, b in x['A']: t = t.replace(a, b)
    plan.append((f, p, t))
XA = json.loads(r"""[]""")
if XA and not XP: print('NOTE: this package also patches the web api.php copies (Love Nails ~/lovenails/api.php, ...) - give their paths after the release dir'); bad = 1
for p in XP:
    s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in XA]; al = '639l' in s; print(p, 'sha', sha(s), 'anchors', *n, 'already', al)
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
    b = f'{bk}/' + f.strip('/').replace('/', '__') + f'.pre-639l-{st}'; shutil.copy2(p, b); m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m); done.append((p, b)); chk(p)
    print('NEW', f, sha(t), 'backup', b)
for f, t in NEWF.items():
    p = f'{R}/{f}'; open(p, 'w', encoding='utf-8').write(t); made.append(p); os.chmod(p, 0o644); chk(p); print('MADE', f, sha(t))
print('OK 2.99.639l (QA-0019) - restart php-fpm.')
