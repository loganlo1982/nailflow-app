#!/usr/bin/env python3
# fix639i.py - QA-0016 (P2): the AI phone text "1 of the group cancelled" (ref cxlpart:) was always dropped ("Still booked that day")
# and the short style rebuilt it as a plain Cancelled. Now it stays and goes with its own words. 3 files.
# Run:  python3 fix639i.py <release dir>   (kiem)   /   ... go
import sys, os, shutil, time, hashlib, json, subprocess
args = [a for a in sys.argv[1:]]
if not args: sys.exit('usage: python3 fix639i.py <release dir> [go]')
go = args[-1] == 'go'
if go: args = args[:-1]
R = args[0].rstrip('/'); XP = [os.path.abspath(a) for a in args[1:]]
def sha(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
F = json.loads(r"""{"inc/outbox-2.php": {"base": "fc6f9769", "new": "23cfb468", "A": [["            elseif (($rw = out_rebooked_why($a)) !== '') $why = ucfirst($rw); // (2.99.178; 2.99.188 same day only)\n", "            elseif (!str_starts_with((string)$o['ref'], 'cxlpart:') /* (2.99.639i QA-0016) 1 of a group cancelled: the others ARE still booked - that is the text */ && ($rw = out_rebooked_why($a)) !== '') $why = ucfirst($rw); // (2.99.178; 2.99.188 same day only)\n"], ["            elseif (appt_ts($a) <= time()) $why = 'Appointment time passed';\n            else $body = out_appt_body('cancel', $a);\n", "            elseif (appt_ts($a) <= time()) $why = 'Appointment time passed';\n            elseif (!str_starts_with((string)$o['ref'], 'cxlpart:')) $body = out_appt_body('cancel', $a); /* 639i: the part-cancel keeps its own words */\n"]]}, "inc/autosend.php": {"base": "c69c34a0", "new": "62383795", "A": [["        if (($rw = out_rebooked_why($a)) !== '') return $rw; /* (2.99.188", "        if (!str_starts_with((string)$o['ref'], 'cxlpart:') /* (2.99.639i QA-0016) */ && ($rw = out_rebooked_why($a)) !== '') return $rw; /* (2.99.188"]]}, "inc/sms-short.php": {"base": "1d2e600d", "new": "dbd6973c", "A": [["&& !str_starts_with($ref, 'techout') && !str_starts_with($ref, 'closed:') && !str_starts_with($ref, 'manual:') && ($a = q(", "&& !str_starts_with($ref, 'techout') && !str_starts_with($ref, 'closed:') && !str_starts_with($ref, 'manual:') && !str_starts_with($ref, 'cxlpart:') /* 639i */ && ($a = q("]]}}""")
plan = []; bad = 0
for f, x in F.items():
    p = f'{R}/{f}'
    if not os.path.isfile(p): print(f, 'MISSING'); bad = 1; continue
    s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in x['A']]
    al = '639i' in s; print(f, 'sha', sha(s), '(LAMWEB base', x['base'] + ')', 'anchors', *n, 'already', al)
    if al or n != [1] * len(n): bad = 1; continue
    t = s
    for a, b in x['A']: t = t.replace(a, b)
    plan.append((f, p, t))
XA = json.loads(r"""[]""")
if XA and not XP: print('NOTE: this package also patches the web api.php copies (Love Nails ~/lovenails/api.php, ...) - give their paths after the release dir'); bad = 1
for p in XP:
    s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in XA]; al = '639i' in s; print(p, 'sha', sha(s), 'anchors', *n, 'already', al)
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
    b = f'{bk}/' + f.strip('/').replace('/', '__') + f'.pre-639i-{st}'; shutil.copy2(p, b); m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m); done.append((p, b)); chk(p)
    print('NEW', f, sha(t), 'backup', b)
for f, t in NEWF.items():
    p = f'{R}/{f}'; open(p, 'w', encoding='utf-8').write(t); made.append(p); os.chmod(p, 0o644); chk(p); print('MADE', f, sha(t))
print('OK 2.99.639i (QA-0016) - restart php-fpm.')
