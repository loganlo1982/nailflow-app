#!/usr/bin/env python3
# fix639j.py - QA-0017 (P2): automatic promos could go out at night (promo hours took 00:00-23:59; a promo handed to the Android at
# 7:59 PM was kept 2 h). Now the hours stay inside 8:00 AM - 8:00 PM (saved + read) and a promo expires at the end of them. 3 files.
# Run:  python3 fix639j.py <release dir>   (kiem)   /   ... go
import sys, os, shutil, time, hashlib, json, subprocess
args = [a for a in sys.argv[1:]]
if not args: sys.exit('usage: python3 fix639j.py <release dir> [go]')
go = args[-1] == 'go'
if go: args = args[:-1]
R = args[0].rstrip('/'); XP = [os.path.abspath(a) for a in args[1:]]
def sha(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
F = json.loads(r"""{"inc/autosend.php": {"base": "62383795", "new": "185dfdcb", "A": [["        'promoMax' => as_promo_max(), 'from' => $hm(setting('as_promo_from'), '08:00'), 'to' => $hm(setting('as_promo_to'), '19:00'),", "        'promoMax' => as_promo_max(), 'from' => min(max($hm(setting('as_promo_from'), '08:00'), '08:00'), '20:00'), 'to' => min(max($hm(setting('as_promo_to'), '19:00'), '08:00'), '20:00') /* (2.99.639j QA-0017) promos only 8:00 AM - 8:00 PM, also hours saved before */,"]]}, "inc/api/autosend.php": {"base": "f7a8bab3", "new": "fb1b5276", "A": [["if (!preg_match('/^([01]\\d|2[0-3]):[0-5]\\d$/', $v)) fail('Time like 10:00.'); set_setting($key, $v); }", "if (!preg_match('/^([01]\\d|2[0-3]):[0-5]\\d$/', $v)) fail('Time like 10:00.'); if ($v < '08:00' || $v > '20:00') fail('Promo hours: 8:00 AM \u2013 8:00 PM.'); /* 639j QA-0017 */ set_setting($key, $v); }"]]}, "inc/android.php": {"base": "b72ee329", "new": "065f0874", "A": [["    return $ttl;\n}\n/** The time this Android text stops being worth sending", "    if (in_array((string)$x['kind'], ['bday', 'winback', 'refer', 'review'], true)) { /* (2.99.639j QA-0017) a promo: never after the end of the promo hours (a phone asleep until night does not send it) */\n        if (!function_exists('as_cfg')) require_once __DIR__ . '/autosend.php';\n        $end = (int)strtotime(date('Y-m-d') . ' ' . as_cfg()['to'] . ':00'); $ttl = min($ttl, max(60, $end - time())); }\n    return $ttl;\n}\n/** The time this Android text stops being worth sending"]]}}""")
plan = []; bad = 0
for f, x in F.items():
    p = f'{R}/{f}'
    if not os.path.isfile(p): print(f, 'MISSING'); bad = 1; continue
    s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in x['A']]
    al = '639j' in s; print(f, 'sha', sha(s), '(LAMWEB base', x['base'] + ')', 'anchors', *n, 'already', al)
    if al or n != [1] * len(n): bad = 1; continue
    t = s
    for a, b in x['A']: t = t.replace(a, b)
    plan.append((f, p, t))
XA = json.loads(r"""[]""")
if XA and not XP: print('NOTE: this package also patches the web api.php copies (Love Nails ~/lovenails/api.php, ...) - give their paths after the release dir'); bad = 1
for p in XP:
    s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in XA]; al = '639j' in s; print(p, 'sha', sha(s), 'anchors', *n, 'already', al)
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
    b = f'{bk}/' + f.strip('/').replace('/', '__') + f'.pre-639j-{st}'; shutil.copy2(p, b); m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m); done.append((p, b)); chk(p)
    print('NEW', f, sha(t), 'backup', b)
for f, t in NEWF.items():
    p = f'{R}/{f}'; open(p, 'w', encoding='utf-8').write(t); made.append(p); os.chmod(p, 0o644); chk(p); print('MADE', f, sha(t))
print('OK 2.99.639j (QA-0017) - restart php-fpm.')
