#!/usr/bin/env python3
# CHAT 01/11 07:45 - anh Logan: EVERY call rings the owner's phone first (also outside opening hours); declined / no answer in 20 s -> the switchboard (AI).
import sys, os, shutil, time, hashlib, subprocess
R = sys.argv[1].rstrip('/'); go = len(sys.argv) > 2 and sys.argv[2] == 'go'
def sha(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
E = {'inc/calls-agent.php': [("if ($fwd !== '' && !cl_closed_now()) {", "if ($fwd !== '') { /* (CHAT 01/11 ring) anh Logan: always ring first, also when closed */")],
     'inc/calls.php': [("$sid !== '' && cl_closed_now()) {", "$sid !== '' && false /* (CHAT 01/11 ring) anh Logan: always ring the iPhone first */ && cl_closed_now()) {")]}
plan = []; bad = 0
for f, L in E.items():
    p = f'{R}/{f}'; s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in L]
    print(f, sha(s), 'anchors', n, 'already', 'CHAT 01/11 ring' in s)
    if n != [1]*len(L) or 'CHAT 01/11 ring' in s: bad = 1; continue
    t = s
    for a, b in L: t = t.replace(a, b)
    plan.append((p, f, t))
if bad: sys.exit('STOP - nothing changed')
if not go:
    for p, f, t in plan: print('NEW would be', f, sha(t))
    sys.exit(0)
bk = os.path.expanduser('~/app/old'); os.makedirs(bk, exist_ok=True); st = time.strftime('%m%d%H%M'); done = []
for p, f, t in plan:
    b = f'{bk}/' + f.replace('/', '__') + f'.pre-605r-{st}'; shutil.copy2(p, b); done.append((p, b))
    m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m)
for p, b in done:
    r = subprocess.run(['php', '-l', p], capture_output=True, text=True); print(r.stdout.strip())
    if r.returncode:
        for q, bb in done: shutil.copy2(bb, q)
        sys.exit('PHP ERROR - all put back')
for p, f, t in plan: print('NEW', f, sha(t))
