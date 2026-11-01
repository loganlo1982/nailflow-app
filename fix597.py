#!/usr/bin/env python3
# LAMWEB 2.99.597 - LOI 597 (anh Logan 20:42): HQ -> salon -> "Xin vao ho tro" -> the 6-digit code to the owner cell came minutes late (#913: 3 min 55 s).
#  Root cause: hq_sup_code puts the text on the MAIN salon's autosend list; the "send now" was only the HQ page's fetch('/api.php?action=sup_kick'),
#  which since 2.99.409 goes to the HQ ADDRESS (hq.json 'host') where salon pages are refused -> the text waited for the next cron round.
#  Fix (inc/hq.php only): after the insert HQ asks the MAIN salon's own address for that kick (server to server, 8 s max; no answer -> cron as before).
# Run (in the app folder):  python3 fix597.py <app dir>       -> check only
#                           python3 fix597.py <app dir> go    -> backup to ~/app/old + patch (php -l / node --check; put back if one fails)
import sys, os, shutil, time, hashlib, json, subprocess
R = sys.argv[1].rstrip('/'); go = len(sys.argv) > 2 and sys.argv[2] == 'go'
def sha(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
F = json.loads(r'''{"inc/hq.php": {"base": "c9071de9", "new": "4967f6d7", "A": [["de (AN HQ)', date('Y-m-d H:i:s')]);\n    return ['ok' => true, 'to' => '\u2026' . substr($cell, -4), 'minutes' => HQ_SUP_CODE_MIN];\n}\n/** The code the owner read out (or n", "de (AN HQ)', date('Y-m-d H:i:s')]);\n    hq_sup_kick_main($mc); // (2.99.597 - LOI 597) sent NOW (like the owner sign-in code) - not at the next cron round (0-5 min)\n    return ['ok' => true, 'to' => '\u2026' . substr($cell, -4), 'minutes' => HQ_SUP_CODE_MIN];\n}\n/* (2.99.597 - LOI 597, anh Logan 20:42 \"m\u00e3 t\u1edbi r\u1ea5t l\u00e2u\") the page's own kick (fetch '/api.php?action=sup_kick') goes to the HQ ADDRESS since 2.99.409\n   (hq.json 'host') - salon pages are refused there, so the code waited for the next cron round (#913: 3 min 55 s). HQ is standalone (no salon code loaded):\n   it asks the MAIN salon's own address for the same kick (sup_kick: only the 'sup:' texts of the last 3 minutes are sent - harmless, no login needed).\n   Never fails the code: no answer \u2192 the cron sends it as before. */\nfunction hq_sup_kick_main(array $mc): void {\n    $u = rtrim((string)($mc['site_url'] ?? ''), '/'); if (!preg_match('#^https?://#', $u)) return;\n    try { $ch = curl_init($u . '/api.php?action=sup_kick'); curl_setopt_array($ch, [CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 8, CURLOPT_CONNECTTIMEOUT => 4, CURLOPT_NOSIGNAL => true, CURLOPT_HTTPHEADER => ['Cache-Control: no-store']]);\n        $r = curl_exec($ch); $code = (int)curl_getinfo($ch, CURLINFO_HTTP_CODE); curl_close($ch);\n        if ($code !== 200) error_log('597 sup kick: http ' . $code); } catch (Throwable $e) { error_log('597 sup kick: ' . $e->getMessage()); }\n}\n/** The code the owner read out (or n"]]}}''')
NEWF = json.loads(r'''{}''')
plan = []; bad = 0
for f, x in F.items():
    p = f'{R}/{f}'; s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in x['A']]
    al = '2.99.597' in s; print(f, 'sha', sha(s), '(LAMWEB base', x['base'] + ')', 'anchors', *n, 'already', al)
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
    c = ['php', '-l', p] if p.endswith('.php') else (['node', '--check', p] if shutil.which('node') else None)
    if not c: return
    r = subprocess.run(c, capture_output=True, text=True)
    if r.returncode: back('in ' + p + ': ' + (r.stdout + r.stderr)[:300])
for f, p, t in plan:
    b = f'{bk}/' + f.replace('/', '__') + f'.pre-597-{st}'; shutil.copy2(p, b); m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m); done.append((p, b)); chk(p)
    print('NEW', f, sha(t), 'backup', b)
for f, t in NEWF.items():
    p = f'{R}/{f}'
    open(p, 'w', encoding='utf-8').write(t); made.append(p)
    os.chmod(p, 0o644)
    chk(p); print('MADE', f, sha(t))
print('OK 2.99.597 - set APP_VERSION 2.99.597 (core.php) as usual, restart php-fpm')
