#!/usr/bin/env python3
# LAMWEB 2.99.635B (LENH-635B, CHAT 02/11 21:50) - lam TRUOC 636.
#  1. QA-0001: tiem KHONG phai American Nails (site_is_main() === false) -> mac dinh admin_reset_phone = '' va as_iphone = '' (khong con so anh Logan).
#     AN (main) + ban cu khong shared: giu nhu cu. Gia tri tiem da ghi (Love Nails) khong doi. Sua: inc/core/settings.php settings() (1 dong).
#  2. API_ROUTES 3 file cung 1 tap action: release api.php + 21 action (AN/LN da co, route file + case co trong release) + DESK_ACTIONS turn_view;
#     ~/lovenails/api.php + tx_cfg tx_ids tx_setup. AN public_html/api.php: KHONG doi (da du).
# Run:  python3 fix635b.py <release dir> <lovenails api.php>          (kiem)
#       python3 fix635b.py <release dir> <lovenails api.php> go
#   vd: python3 fix635b.py ~/app/sites/an/current /home/uyurpyzubx0m/lovenails/api.php go
import sys, os, shutil, time, hashlib, json, subprocess
R = sys.argv[1].rstrip('/'); LNP = sys.argv[2]; go = len(sys.argv) > 3 and sys.argv[3] == 'go'
def sha(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
F = json.loads(r"""{"inc/core/settings.php": {"base": "d977bfca", "A": [["    $s = default_settings();\n    foreach (q('SELECT k, v FROM settings')", "    $s = default_settings();\n    if (function_exists('site_is_main') && site_is_main() === false) { $s['admin_reset_phone'] = ''; $s['as_iphone'] = ''; $s['salon_name'] = ''; } // (2.99.635B - QA-0001) a salon that is not American Nails: never Logan's phone (reset link, \"text us to confirm\") nor AN's name as its default\n    foreach (q('SELECT k, v FROM settings')"]]}, "api.php": {"base": "21baf8a9", "A": [["const API_ROUTES = [/* (2.99.632 - LENH 632) the salon setup link */ ", "const API_ROUTES = [/* (2.99.632 - LENH 632) the salon setup link */ /* (2.99.635B - LENH 635B) the same actions as AN / Love Nails' own api.php */ 'ck_app_exit' => 'qdesk', 'colorlib_brands' => 'colors', 'colorlib_get' => 'colors', 'colors_admin' => 'colors', 'colors_ai_on' => 'colors', 'colors_ai_read' => 'colors', 'colors_auto_save' => 'colors', 'colors_delete' => 'colors', 'colors_import' => 'colors', 'colors_list' => 'colors', 'colors_photo' => 'colors', 'colors_save' => 'colors', 'colors_undo' => 'colors', 'guest_info' => 'guestapi', 'guest_set' => 'guestapi', 'login_sms' => 'auth', 'oldok_info' => 'oldok', 'oldok_set' => 'oldok', 'oldok_undo' => 'oldok', 'tfa_info' => 'tfa', 'turn_view' => 'turnview', "], ["const DESK_ACTIONS = [/* (2.99.344 \u2013 l\u1ec7nh 578) */", "const DESK_ACTIONS = [/* (2.99.362 \u2013 l\u1ec7nh 604) L\u1ecbch theo turn */ 'turn_view', /* (2.99.344 \u2013 l\u1ec7nh 578) */"]]}, "@LN": {"base": "50b440c4", "A": [["const API_ROUTES = [/* (2.99.632 - LENH 632) the salon setup link */ ", "const API_ROUTES = [/* (2.99.632 - LENH 632) the salon setup link */ /* (2.99.635B - LENH 635B) Telnyx settings, as AN */ 'tx_cfg' => 'callstx', 'tx_ids' => 'callstx', 'tx_setup' => 'callstx', "]]}}""")
plan = []; bad = 0
for f, x in F.items():
    p = LNP if f == '@LN' else f'{R}/{f}'; s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in x['A']]
    al = '2.99.635B' in s; print(p, 'sha', sha(s), '(LAMWEB base', x['base'] + ')', 'anchors', *n, 'already', al)
    if al or n != [1] * len(n): bad = 1; continue
    t = s
    for a, b in x['A']: t = t.replace(a, b)
    plan.append((f, p, t))
if bad: sys.exit('STOP: an anchor is not found exactly once, or already patched - nothing changed')
if not go:
    for f, p, t in plan: print('NEW would be', p, sha(t))
    sys.exit('check only - run again with: go')
bk = os.path.expanduser('~/app/old'); os.makedirs(bk, exist_ok=True); st = time.strftime('%m%d%H%M'); done = []
def back(msg):
    for q, bb in done: shutil.copy2(bb, q)
    sys.exit('ERROR ' + msg + ' - every file put back')
for f, p, t in plan:
    b = f'{bk}/' + p.strip('/').replace('/', '__') + f'.pre-635b-{st}'; shutil.copy2(p, b); m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m); done.append((p, b))
    r = subprocess.run(['php', '-l', p], capture_output=True, text=True)
    if r.returncode: back('in ' + p + ': ' + (r.stdout + r.stderr)[:300])
    print('NEW', p, sha(t), 'backup', b)
print('OK 2.99.635B (QA-0001 + 3 api.php cung action) - APP_VERSION 2.99.635, restart php-fpm. Kiem: tiem moi khong con so 515-672-7879; Love Nails Settings -> Calls Telnyx mo duoc.')
