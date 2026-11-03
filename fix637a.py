#!/usr/bin/env python3
# LAMWEB 2.99.637a (QA-0005 P1, CHAT 03/11 00:00): luat AN/MO 636 bi lach - chu tiem KHONG phai main xoa duoc dong STOP (sms_footer) qua
#   Settings -> SMS templates (sms_tpl_save / sms_tpl_restore). Sua: nf_only_guard chan 2 action do khi key nam trong NF_ONLY_KEYS (403 + audit nf_only);
#   danh sach mau tin cua chu tiem khong hien dong STOP. "Restore default" (co STOP) van mo. AN (main) nhu cu. Goc = ban DANG CHAY 2.99.636.
# Run:  python3 fix637a.py <release dir>   (kiem)   /   python3 fix637a.py <release dir> go
import sys, os, shutil, time, hashlib, json, subprocess
args = [a for a in sys.argv[1:]]
if not args: sys.exit('usage: python3 fix637a.py <release dir> [go]')
R = args[0].rstrip('/'); go = len(args) > 1 and args[1] == 'go'
def sha(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
F = json.loads(r"""{"inc/support.php": {"base": "79905f8b", "new": "16c1e931", "A": [["    if (in_array($a, NF_ONLY_ACTS, true)) { try { audit('nf_only', $a, '', 'refused \u2013 set up by NailFlow'); } catch (Throwable $e) {} fail(nf_only_say(), 403); }", "    if (in_array($a, NF_ONLY_ACTS, true)) { try { audit('nf_only', $a, '', 'refused \u2013 set up by NailFlow'); } catch (Throwable $e) {} fail(nf_only_say(), 403); }\n    if (in_array($a, ['sms_tpl_save', 'sms_tpl_restore'], true) && in_array((string)($GLOBALS['in']['key'] ?? ''), NF_ONLY_KEYS, true)) { // (2.99.637a QA-0005) the STOP line (sms_footer) through Settings -> SMS templates; \"Restore default\" (has STOP) stays open\n        try { audit('nf_only', $a, (string)$GLOBALS['in']['key'], 'refused \u2013 set up by NailFlow'); } catch (Throwable $e) {} fail(nf_only_say(), 403); }"]]}, "inc/api/_texts.php": {"base": "b50dc39a", "new": "c565903b", "A": [["    foreach (sms_tpls() as $k => $d) {\n        $o[] = ['key' => $k,", "    foreach (sms_tpls() as $k => $d) {\n        if (function_exists('nf_only') && nf_only() && in_array($k, NF_ONLY_KEYS, true)) continue; // (2.99.637a QA-0005) the STOP line: NailFlow's, not in the owner's list\n        $o[] = ['key' => $k,"]]}}""")
plan = []; bad = 0
for f, x in F.items():
    p = f'{R}/{f}'
    if not os.path.isfile(p): print(f, 'MISSING'); bad = 1; continue
    s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in x['A']]
    al = '2.99.637a' in s; print(f, 'sha', sha(s), '(LAMWEB base', x['base'] + ')', 'anchors', *n, 'already', al)
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
    b = f'{bk}/' + f.replace('/', '__') + f'.pre-637a-{st}'; shutil.copy2(p, b); m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m); done.append((p, b)); chk(p)
    print('NEW', f, sha(t), 'backup', b)
print('OK 2.99.637a (QA-0005) - restart php-fpm (APP_VERSION giu hoac 2.99.637). Thu: tiem khong phai main sms_tpl_save sms_footer -> 403.')
