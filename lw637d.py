#!/usr/bin/env python3
# LAMWEB 2.99.637d (QA-0003 P2, CHAT 02/11 23:05) - ban 2 sau ra soat: tiem MOI chua co code_prefix -> ma xac nhan "CONFIRM AN-..." (chu cua American Nails).
#   Sua: code_pre_new() (inc/core/settings.php): tiem KHONG phai main, chua co code_prefix, CHUA CO LICH NAO, co ten -> luu code_prefix = 2 chu tu ten
#   (Rose Nails -> RN; khong bao gio AN, khong trung tiem khac dung chung Android). Goi khi luu salon_name (set_setting) + api info (tiem dat ten truoc ban nay).
#   Tiem DA co lich ma chua co code_prefix: giu AN nhu cu (khach con tra loi CONFIRM AN-...). Moi cho DOC code_prefix (api.php 4 ban, tin, Android, SMS Server) KHONG doi.
#   Goc = ban sau 637c (can main_salon 637c).
# Run:  python3 fix637d.py <release dir>   (kiem)   /   python3 fix637d.py <release dir> go
import sys, os, shutil, time, hashlib, json, subprocess
args = [a for a in sys.argv[1:]]
if not args: sys.exit('usage: python3 fix637d.py <release dir> [go]')
R = args[0].rstrip('/'); go = len(args) > 1 and args[1] == 'go'
def sha(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
F = json.loads(r"""{"inc/core/settings.php": {"base": "feafe284", "new": "9a0e0874", "A": [["    q(is_sqlite() ? 'INSERT INTO settings (k, v) VALUES (?, ?) ON CONFLICT(k) DO UPDATE SET v = excluded.v' : 'INSERT INTO settings (k, v) VALUES (?, ?) ON DUPLICATE KEY UPDATE v = VALUES(v)', [$k, $v]);\n    settings(true);\n}", "    q(is_sqlite() ? 'INSERT INTO settings (k, v) VALUES (?, ?) ON CONFLICT(k) DO UPDATE SET v = excluded.v' : 'INSERT INTO settings (k, v) VALUES (?, ?) ON DUPLICATE KEY UPDATE v = VALUES(v)', [$k, $v]);\n    settings(true);\n    if ($k === 'salon_name') code_pre_new(); // (2.99.637d QA-0003) a new salon gets its own code letters when it is named\n}"], ["function main_salon(): bool { if (function_exists('site_is_main') && ($m = site_is_main()) !== null) return $m; return empty(cfg()['noindex']); }", "function main_salon(): bool { if (function_exists('site_is_main') && ($m = site_is_main()) !== null) return $m; return empty(cfg()['noindex']); }\n/** (2.99.637d QA-0003) A NEW salon (not American Nails, no code_prefix yet, NO appointment yet = no code ever texted) with a name: its own 2 letters\n    in code_prefix (CONFIRM RN-123), never AN (American Nails') nor the letters of another salon on the shared Android. Kept: a rename later changes nothing.\n    A salon that already has appointments and no code_prefix keeps AN as before (its customers may still answer \"CONFIRM AN-...\"). Everything that reads\n    code_prefix (api.php, texts, shared Android, SMS Server id) is unchanged. Called when the salon name is saved and by the booking page (api info). */\nfunction code_pre_new(): void {\n    try {\n        if (main_salon() || preg_match('/^[A-Z]{2}$/', strtoupper(trim((string)setting('code_prefix'))))) return;\n        $w = array_values(array_filter(preg_split('/\\s+/', strtoupper(trim((string)preg_replace('/[^A-Za-z]+/', ' ', (string)setting('salon_name'))))) ?: [], fn($x) => $x !== '' && !in_array($x, ['AND', 'THE', 'OF', 'AT'], true)));\n        if (!$w || q('SELECT 1 FROM appointments LIMIT 1')->fetchColumn()) return;\n        $no = ['AN']; if (is_file(APP_ROOT . '/inc/shareddev.php')) { require_once APP_ROOT . '/inc/shareddev.php'; foreach (sd_peers() as $x) $no[] = (string)$x['prefix']; }\n        $two = $w[0] . ($w[1] ?? ''); $c = [substr($w[0], 0, 1) . (isset($w[1]) ? substr($w[1], 0, 1) : substr($w[0], 1, 1)), substr($w[0], 0, 2)];\n        for ($i = 1; $i < strlen($two); $i++) $c[] = substr($two, 0, 1) . substr($two, $i, 1);\n        foreach ($c as $p) if (preg_match('/^[A-Z]{2}$/', $p) && !in_array($p, $no, true)) { set_setting('code_prefix', $p); return; }\n    } catch (Throwable $e) { error_log('code_pre_new: ' . $e->getMessage()); } // never stops saving the name\n}"]]}, "inc/api/public.php": {"base": "798b2781", "new": "807e4cc7", "A": [["json_out(['codePre' => preg_match('/^[A-Z]{2}$/', strtoupper((string)setting('code_prefix')))", "if (function_exists('code_pre_new')) code_pre_new(); /* (2.99.637d QA-0003) a salon named before this version */\n    json_out(['codePre' => preg_match('/^[A-Z]{2}$/', strtoupper((string)setting('code_prefix')))"]]}}""")
plan = []; bad = 0
for f, x in F.items():
    p = f'{R}/{f}'
    if not os.path.isfile(p): print(f, 'MISSING'); bad = 1; continue
    s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in x['A']]
    al = '2.99.637d' in s; print(f, 'sha', sha(s), '(LAMWEB base', x['base'] + ')', 'anchors', *n, 'already', al)
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
    b = f'{bk}/' + f.replace('/', '__') + f'.pre-637d-{st}'; shutil.copy2(p, b); m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m); done.append((p, b)); chk(p)
    print('NEW', f, sha(t), 'backup', b)
print('OK 2.99.637d (QA-0003) - restart php-fpm. Thu: tiem moi luu ten -> setting code_prefix = 2 chu; tiem cu khong doi.')
