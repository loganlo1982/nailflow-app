#!/usr/bin/env python3
# LAMWEB 2.99.639a (QA-0012 P1 TIEN, TRA-LOI-QA0012 CHAT 19:15 chon (a)): "Fix service prices" GIAM gia 2 lan -> REFUND 2 lan
#   (giam gia chi ghi refund, gia dong khong doi -> mo lai van thay gia cu -> luu lai = refund them).
#   Sua 1 dong inc/checkout-edit.php receipt_money_edit: hoa don DA CO refund -> GIAM gia bi tu choi ("refund the difference instead") - nhu dang chan TANG gia.
#   Lan giam dau, Refund thuong, tang gia hoa don chua refund: nhu cu. Khong doi giao dien. Goc = LIVE 2.99.353 (637 + 638a..d2 + fixC638a).
# Run:  python3 fix639a.py <release dir>   (kiem)   /   ... go
import sys, os, shutil, time, hashlib, json, subprocess
args = [a for a in sys.argv[1:]]
if not args: sys.exit('usage: python3 fix639a.py <release dir> [go]')
go = args[-1] == 'go'
if go: args = args[:-1]
R = args[0].rstrip('/'); XP = [os.path.abspath(a) for a in args[1:]]
def sha(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
F = json.loads(r"""{"inc/checkout-edit.php": {"base": "5149ee9a", "new": "d4ea05c4", "A": [["    if ($d < 0) { // \u2212 less: the Refund that exists, on the techs whose lines went down\n", "    if ($d < 0) { // \u2212 less: the Refund that exists, on the techs whose lines went down\n        if ((float)$r['refund'] > 0.004) fail(TV('This receipt already has a refund \u2013 refund the difference instead (Refund).', 'Ho\u00e1 \u0111\u01a1n \u0111\u00e3 c\u00f3 refund \u2013 ho\u00e0n ph\u1ea7n ch\u00eanh l\u1ec7ch b\u1eb1ng Refund.')); // (2.99.639a QA-0012) the line prices never change on a refund: lowering again refunded twice\n"]]}}""")
plan = []; bad = 0
for f, x in F.items():
    p = f'{R}/{f}'
    if not os.path.isfile(p): print(f, 'MISSING'); bad = 1; continue
    s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in x['A']]
    al = '2.99.639a' in s; print(f, 'sha', sha(s), '(LAMWEB base', x['base'] + ')', 'anchors', *n, 'already', al)
    if al or n != [1] * len(n): bad = 1; continue
    t = s
    for a, b in x['A']: t = t.replace(a, b)
    plan.append((f, p, t))
XA = json.loads(r"""[]""")
if XA and not XP: print('NOTE: this package also patches the web api.php copies (Love Nails ~/lovenails/api.php, ...) - give their paths after the release dir'); bad = 1
for p in XP:
    s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in XA]; al = '2.99.639a' in s; print(p, 'sha', sha(s), 'anchors', *n, 'already', al)
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
    b = f'{bk}/' + f.strip('/').replace('/', '__') + f'.pre-639a-{st}'; shutil.copy2(p, b); m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m); done.append((p, b)); chk(p)
    print('NEW', f, sha(t), 'backup', b)
for f, t in NEWF.items():
    p = f'{R}/{f}'; open(p, 'w', encoding='utf-8').write(t); made.append(p); os.chmod(p, 0o644); chk(p); print('MADE', f, sha(t))
print('OK 2.99.639a (QA-0012) - restart php-fpm.')
