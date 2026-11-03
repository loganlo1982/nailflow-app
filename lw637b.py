#!/usr/bin/env python3
# LAMWEB 2.99.637b (QA-0004 P1, CHAT 02/11 23:20): dat lich duoc vao NGAY KHONG CO (31/11, 30/02...) - valid_date() dung strtotime (PHP doi 31/11 -> 01/12).
#   Sua 1 dong inc/core/log-helpers.php: valid_date = YYYY-MM-DD + checkdate(). 55 cho dung valid_date deu theo: booking page (slots, book), doi gio,
#   AI dien thoai (cl_agent_dt, said_date, IVR), nhap khach. Goc = ban sau 637a (file nay 637a khong doi -> chay duoc ca tren 2.99.636).
# Run:  python3 fix637b.py <release dir>   (kiem)   /   python3 fix637b.py <release dir> go
import sys, os, shutil, time, hashlib, json, subprocess
args = [a for a in sys.argv[1:]]
if not args: sys.exit('usage: python3 fix637b.py <release dir> [go]')
R = args[0].rstrip('/'); go = len(args) > 1 and args[1] == 'go'
def sha(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
F = json.loads(r"""{"inc/core/log-helpers.php": {"base": "988f36f6", "new": "a874cbe2", "A": [["function valid_date(string $d): bool { return (bool)preg_match('/^\\d{4}-\\d{2}-\\d{2}$/', $d) && strtotime($d) !== false; }", "function valid_date(string $d): bool { return (bool)preg_match('/^(\\d{4})-(\\d{2})-(\\d{2})$/', $d, $m) && checkdate((int)$m[2], (int)$m[3], (int)$m[1]); } // (2.99.637b QA-0004) a day that exists: strtotime() turned 2026-11-31 into 12/01 and said yes"]]}}""")
plan = []; bad = 0
for f, x in F.items():
    p = f'{R}/{f}'
    if not os.path.isfile(p): print(f, 'MISSING'); bad = 1; continue
    s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in x['A']]
    al = '2.99.637b' in s; print(f, 'sha', sha(s), '(LAMWEB base', x['base'] + ')', 'anchors', *n, 'already', al)
    if al or n != [1] * len(n): bad = 1; continue
    t = s
    for a, b in x['A']: t = t.replace(a, b)
    plan.append((f, p, t))
if bad: sys.exit('STOP: an anchor is not found exactly once or already patched - nothing changed')
if not go:
    for f, p, t in plan: print('NEW would be', f, sha(t))
    sys.exit('check only - run again with: go')
bk = os.path.expanduser('~/app/old'); os.makedirs(bk, exist_ok=True); st = time.strftime('%m%d%H%M'); done = []
def back(msg):
    for q, bb in done: shutil.copy2(bb, q)
    sys.exit('ERROR ' + msg + ' - every file put back')
def chk(p):
    c = ['php', '-l', p] if p.endswith('.php') else (['node', '--check', p] if p.endswith('.js') and shutil.which('node') else None)
    if not c: return
    r = subprocess.run(c, capture_output=True, text=True)
    if r.returncode: back('in ' + p + ': ' + (r.stdout + r.stderr)[:300])
for f, p, t in plan:
    b = f'{bk}/' + f.replace('/', '__') + f'.pre-637b-{st}'; shutil.copy2(p, b); m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m); done.append((p, b)); chk(p)
    print('NEW', f, sha(t), 'backup', b)
print('OK 2.99.637b (QA-0004) - restart php-fpm. Thu: api slots date=2026-11-31 -> "Bad date".')
