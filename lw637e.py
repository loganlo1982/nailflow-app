#!/usr/bin/env python3
# LAMWEB 2.99.637e (QA-0006 P2, CHAT 03/11 00:05): nhat ky (audit_log.ip) cua Love Nails ghi IP server 72.167.37.112 cho moi lan (qua proxy).
#   Sua: client_ip() (inc/core/log-helpers.php) = X-Forwarded-For cuoi (do proxy cua minh them) KHI REMOTE_ADDR la 72.167.37.112/127.0.0.1/::1, con lai
#   REMOTE_ADDR (khach khac khong gia duoc). audit() + ip_key() (khoa dang nhap, gioi han link) dung chung client_ip(). Khoa dang nhap da theo XFF tu 2.99.395.
#   Goc = ban sau 637d (log-helpers can valid_date cua 637b).
# Run:  python3 fix637e.py <release dir>   (kiem)   /   python3 fix637e.py <release dir> go
import sys, os, shutil, time, hashlib, json, subprocess
args = [a for a in sys.argv[1:]]
if not args: sys.exit('usage: python3 fix637e.py <release dir> [go]')
R = args[0].rstrip('/'); go = len(args) > 1 and args[1] == 'go'
def sha(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
F = json.loads(r"""{"inc/core/log-helpers.php": {"base": "a874cbe2", "new": "a112a9f5", "A": [["function valid_date(string $d): bool { return (bool)preg_match('/^(\\d{4})-(\\d{2})-(\\d{2})$/', $d, $m) && checkdate((int)$m[2], (int)$m[3], (int)$m[1]); }", "/** (2.99.637e QA-0006) the visitor's address. Behind this server's own proxy (lovenails.nailflowapp.com: REMOTE_ADDR = 72.167.37.112 / 127.0.0.1): the LAST\n    X-Forwarded-For entry (the one our proxy added - what the visitor sent before it cannot fool us); anyone else: REMOTE_ADDR (the header is ignored). */\nfunction client_ip(): string {\n    $ra = (string)($_SERVER['REMOTE_ADDR'] ?? '');\n    if (in_array($ra, ['72.167.37.112', '127.0.0.1', '::1'], true) && !empty($_SERVER['HTTP_X_FORWARDED_FOR'])) { $xf = array_map('trim', explode(',', (string)$_SERVER['HTTP_X_FORWARDED_FOR'])); $c = (string)end($xf); if (filter_var($c, FILTER_VALIDATE_IP)) return $c; }\n    return $ra;\n}\nfunction valid_date(string $d): bool { return (bool)preg_match('/^(\\d{4})-(\\d{2})-(\\d{2})$/', $d, $m) && checkdate((int)$m[2], (int)$m[3], (int)$m[1]); }"]]}, "inc/audit.php": {"base": "3f374c5e", "new": "1c0bdc7a", "A": [["mb_substr((string)($_SERVER['REMOTE_ADDR'] ?? ''), 0, 45)]);", "mb_substr(function_exists('client_ip') ? client_ip() : (string)($_SERVER['REMOTE_ADDR'] ?? ''), 0, 45) /* (2.99.637e QA-0006) the visitor, not our proxy */]);"]]}, "inc/api/_auth.php": {"base": "6d075a42", "new": "41e694f6", "A": [["    $ra = (string)($_SERVER['REMOTE_ADDR'] ?? '');\n    if (in_array($ra, ['72.167.37.112', '127.0.0.1', '::1'], true) && !empty($_SERVER['HTTP_X_FORWARDED_FOR'])) { $xf = array_map('trim', explode(',', (string)$_SERVER['HTTP_X_FORWARDED_FOR'])); $c = (string)end($xf); if (filter_var($c, FILTER_VALIDATE_IP)) $ra = $c; } // (2.99.395) lovenails.nailflowapp.com comes through this server's own proxy: the visitor = the last address it added\n", "    $ra = client_ip(); // (2.99.637e QA-0006) the same rule as the log (was written here since 2.99.395)\n"]]}}""")
plan = []; bad = 0
for f, x in F.items():
    p = f'{R}/{f}'
    if not os.path.isfile(p): print(f, 'MISSING'); bad = 1; continue
    s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in x['A']]
    al = '2.99.637e' in s; print(f, 'sha', sha(s), '(LAMWEB base', x['base'] + ')', 'anchors', *n, 'already', al)
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
    b = f'{bk}/' + f.replace('/', '__') + f'.pre-637e-{st}'; shutil.copy2(p, b); m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m); done.append((p, b)); chk(p)
    print('NEW', f, sha(t), 'backup', b)
print('OK 2.99.637e (QA-0006) - restart php-fpm. Thu: dang nhap Love Nails -> Activity/audit ip = IP that.')
