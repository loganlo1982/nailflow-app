#!/usr/bin/env python3
# LAMWEB 2.99.637c (QA-0002 P1, CHAT 02/11 23:05): main_salon() doan "la American Nails" bang config KHONG co noindex -> tiem moi quen noindex chay nhu AN
#   (AI phone mo, so anh Logan thanh so test, menu ruou AN tren trang dat lich, the Bat dau 636 khong hien). Sua: main_salon() theo sites.php (site_is_main)
#   khi co sites.php; ban 1-copy cu nhu cu. gs_show / tour start.php / menu mau (svc_tpl_new_salon) dung !main_salon(). site_noindex (SEO) KHONG doi.
#   + api info perksEs (dong ruou tieng Tay Ban Nha) cung theo main_salon() nhu perks (truoc chi tieng Anh bi tat). Goc = ban sau 637b.
# Run:  python3 fix637c.py <release dir>   (kiem)   /   python3 fix637c.py <release dir> go
import sys, os, shutil, time, hashlib, json, subprocess
args = [a for a in sys.argv[1:]]
if not args: sys.exit('usage: python3 fix637c.py <release dir> [go]')
R = args[0].rstrip('/'); go = len(args) > 1 and args[1] == 'go'
def sha(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
F = json.loads(r"""{"inc/core/settings.php": {"base": "b2cac701", "new": "feafe284", "A": [["function main_salon(): bool { return empty(cfg()['noindex']); }", "function main_salon(): bool { if (function_exists('site_is_main') && ($m = site_is_main()) !== null) return $m; return empty(cfg()['noindex']); } // (2.99.637c QA-0002) shared layout: sites.php 'main' decides (a new salon whose config forgot 'noindex' is never American Nails); the old single copy: as before"]]}, "inc/getstarted.php": {"base": "b32d1645", "new": "9a734d60", "A": [["function gs_show(): bool { if (empty(cfg()['noindex']) ||", "function gs_show(): bool { if (main_salon() /* (2.99.637c QA-0002) was: no 'noindex' */ ||"]]}, "inc/api/public.php": {"base": "362a3276", "new": "798b2781", "A": [["'perksEs' => setting('perk_drinks_on') === '0' ? '' :", "'perksEs' => setting('perk_drinks_on') === '0' || !main_salon() /* (2.99.637c QA-0002: like 'perks' - the Spanish line too) */ ? '' :"]]}, "inc/api/start.php": {"base": "91dea5c2", "new": "6e8adfef", "A": [["$nw = !empty(cfg()['noindex']);", "$nw = !main_salon(); /* (2.99.637c QA-0002) */"]]}, "inc/svc-tpl.php": {"base": "07004d9d", "new": "5d35cc5a", "A": [["function svc_tpl_new_salon(): bool { return !empty(cfg()['noindex']); }", "function svc_tpl_new_salon(): bool { return !main_salon(); } // (2.99.637c QA-0002) was: config 'noindex'"]]}}""")
plan = []; bad = 0
for f, x in F.items():
    p = f'{R}/{f}'
    if not os.path.isfile(p): print(f, 'MISSING'); bad = 1; continue
    s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in x['A']]
    al = '2.99.637c' in s; print(f, 'sha', sha(s), '(LAMWEB base', x['base'] + ')', 'anchors', *n, 'already', al)
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
    b = f'{bk}/' + f.replace('/', '__') + f'.pre-637c-{st}'; shutil.copy2(p, b); m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m); done.append((p, b)); chk(p)
    print('NEW', f, sha(t), 'backup', b)
print('OK 2.99.637c (QA-0002) - restart php-fpm. Thu: AN Home khong co the Bat dau; tiem demo van co.')
