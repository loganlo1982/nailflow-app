#!/usr/bin/env python3
# LAMWEB 2.99.623 = 610-1 (BAO-CAO-610, LENH 610 + 619): appt_ts() = the appointment time by the SALON's clock (mktime). Before: midnight + minutes -> 1 hour off
#  on the 2 days a year the clocks change (calendar .ics, reminders, the no-confirm auto-cancel, auto send, calls "time passed"). Test: book610 #10 FAILS before, PASSES after.
#  CHANGED: inc/core/log-helpers.php (1 function). AN public_html: nothing.
# Run (in the app folder):  python3 fix623.py <app dir>  /  python3 fix623.py <app dir> go
import sys, os, shutil, time, hashlib, json, subprocess
R = sys.argv[1].rstrip('/'); go = len(sys.argv) > 2 and sys.argv[2] == 'go'
def sha(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
F = json.loads(r'''{"inc/core/log-helpers.php": {"base": "0416feee", "new": "988f36f6", "A": [["}$/', $d) && strtotime($d) !== false; }\nfunction appt_ts(array $a): int { return strtotime($a['appt_date'] . ' 00:00') + (int)$a['start_min'] * 60; }\n/** When, for notifications: \"Today, 2:0", "}$/', $d) && strtotime($d) !== false; }\nfunction appt_ts(array $a): int { $p = array_map('intval', explode('-', (string)$a['appt_date'])) + [0, 0, 0]; $m = (int)$a['start_min']; return mktime(intdiv($m, 60), $m % 60, 0, $p[1], $p[2], $p[0]); } /* (2.99.623 = 610-1) the salon's clock time: right on the days the clocks change too (was midnight + minutes: 1 h off on those days) */\n/** When, for notifications: \"Today, 2:0"]]}}''')
NEWF = json.loads(r'''{}''')
plan = []; bad = 0
for f, x in F.items():
    p = f'{R}/{f}'; s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in x['A']]
    al = '2.99.623' in s; print(f, 'sha', sha(s), '(LAMWEB base', x['base'] + ')', 'anchors', *n, 'already', al)
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
    b = f'{bk}/' + f.replace('/', '__') + f'.pre-623-{st}'; shutil.copy2(p, b); m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m); done.append((p, b)); chk(p)
    print('NEW', f, sha(t), 'backup', b)
for f, t in NEWF.items():
    p = f'{R}/{f}'
    open(p, 'w', encoding='utf-8').write(t); made.append(p)
    os.chmod(p, 0o644)
    chk(p); print('MADE', f, sha(t))
print('OK 2.99.623 (610-1 appointment time on the days the clocks change) - set APP_VERSION 2.99.623, restart php-fpm. Nothing in the AN public_html copies.')
