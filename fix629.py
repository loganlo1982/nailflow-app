#!/usr/bin/env python3
# LAMWEB 2.99.629 (LENH-629, CHAT tim goc 02/11): tin "missed call text back" tren duong Telnyx cham ~1 gio.
#  GOC: cl_textback_due() (+ cl_confirm_due) chi chay trong call_in.php?a=tick (SignalWire / web poke cua cron turn) va khi chu mo trang admin.
#       Duong Telnyx khong co gi goi -> tin cho toi cuoc goi ke / mo admin.
#  SUA: cron/tx-mp3.php (CLI, dang chay moi phut ~55 s khi Telnyx bat) goi cl_textback_due() + cl_confirm_due() moi 15 s NGAY TRONG tien trinh CLI (khong goi web).
#       inc/calls-job.php cl_textback: cron + trang chu cung luc -> ben thua thay tin da co (autosend.src UNIQUE 'ui:call:<id>') -> 'skip:taken', KHONG danh dau skip.
#  Khong doi: CL_TB_GAP 30 phut, kiem STOP / so salon / da booked, AI dien thoai, tien. Khong doi DB.
#  AN public_html: KHONG co file nao (calls-job.php la inc/; cron/tx-mp3.php: neu cron cua AN tro public_html/cron/tx-mp3.php va do la BAN CHEP rieng -> chep file moi vao do).
# Run (in the app folder):  python3 fix629.py <app dir>  /  python3 fix629.py <app dir> go
import sys, os, shutil, time, hashlib, json, subprocess
R = sys.argv[1].rstrip('/'); go = len(sys.argv) > 2 and sys.argv[2] == 'go'
def sha(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
F = json.loads(r'''{"inc/calls-job.php": {"base": "8255962e", "new": "687fa175", "A": [["require_once __DIR__ . '/autosend.php';\n    if (!as_ready()) return $skip('auto ", "require_once __DIR__ . '/autosend.php';\n    if (q('SELECT 1 FROM autosend WHERE src = ?', [($rq ? 'ui:callreq:' : 'ui:call:') . (int)$c['id']])->fetchColumn()) return 'skip:taken'; // (2.99.629) the cron and the owner's page at the same moment: the other one made it \u2013 never a 2nd text, the call is not marked \"skip\"\n    if (!as_ready()) return $skip('auto "], ["not one of the Auto send kind switches)\n    if (!$aid) return $skip('STOP / wrong number / not textable');\n    if (!q(\"UPDATE calls SET tb_state = ", "not one of the Auto send kind switches)\n    if (!$aid) return q('SELECT 1 FROM autosend WHERE src = ?', [($rq ? 'ui:callreq:' : 'ui:call:') . (int)$c['id']])->fetchColumn() ? 'skip:taken' : $skip('STOP / wrong number / not textable'); // (2.99.629) lost the race: the other one has it\n    if (!q(\"UPDATE calls SET tb_state = "]]}, "cron/tx-mp3.php": {"base": "be1ddc6f", "new": "ec66ff6b", "A": [["| !flock($lk, LOCK_EX | LOCK_NB)) exit;\n$end = time() + 55;\nwhile (time() < $end) { try { tx_cli_mp3(); } catch (Throwable $e) { error_log('612e tx mp3: ' . $e->getMessage()); } sleep(2); }\n", "| !flock($lk, LOCK_EX | LOCK_NB)) exit;\n/* (2.99.629 - LENH 629) the missed-call text back + YOU'RE BOOKED after the 10 minutes: here too, every 15 s, IN this CLI process (no web call).\n   Before, only call_in.php?a=tick (SignalWire / the turn cron's web poke) or the owner's page did it -> on Telnyx a text waited up to ~1 hour.\n   Never twice: cl_confirm_due claims each call (conf_done), a text back is one row per call (autosend.src UNIQUE 'ui:call:<id>'). */\nfunction tx_cron_calls(): void {\n    static $lib = false;\n    if (!$lib) { $r = dirname(__DIR__); if (!defined('NF_API_LIB')) define('NF_API_LIB', 1);\n        foreach (['/inc/backup.php', '/inc/import.php', '/inc/totp.php', '/inc/rebook.php', '/inc/gallery.php', '/inc/birthday.php', '/inc/paypal.php', '/inc/review.php', '/inc/giftcards.php',\n            '/inc/outbox.php', '/inc/logo.php', '/inc/reports.php', '/inc/checkout.php', '/inc/payroll.php', '/inc/export.php', '/inc/yearend.php', '/inc/referral.php', '/inc/promolinks.php',\n            '/inc/turnq.php', '/inc/apptoffers.php', '/inc/rewards.php', '/inc/api/_auth.php', '/inc/api/_menu.php', '/inc/api/_texts.php', '/inc/api/_kiosk.php', '/inc/api/_out.php'] as $f) require_once $r . $f;\n        require_once $r . '/api.php'; require_once $r . '/inc/calls-job.php'; $lib = true; } /* the same files as call_in.php cl_job_lib() */\n    $GLOBALS['actor'] = ['call', '\ud83d\udcde Call assistant']; cl_table(); cl_textback_due(); cl_confirm_due();\n}\n$end = time() + 55; $nextCalls = 0;\nwhile (time() < $end) { try { tx_cli_mp3(); } catch (Throwable $e) { error_log('612e tx mp3: ' . $e->getMessage()); }\n    if (time() >= $nextCalls) { $nextCalls = time() + 15; try { tx_cron_calls(); } catch (Throwable $e) { error_log('629 tx calls: ' . $e->getMessage()); } }\n    sleep(2); }\n"]]}}''')
NEWF = json.loads(r'''{}''')
plan = []; bad = 0
for f, x in F.items():
    p = f'{R}/{f}'; s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in x['A']]
    al = '2.99.629' in s; print(f, 'sha', sha(s), '(LAMWEB base', x['base'] + ')', 'anchors', *n, 'already', al)
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
    b = f'{bk}/' + f.replace('/', '__') + f'.pre-629-{st}'; shutil.copy2(p, b); m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m); done.append((p, b)); chk(p)
    print('NEW', f, sha(t), 'backup', b)
for f, t in NEWF.items():
    p = f'{R}/{f}'
    open(p, 'w', encoding='utf-8').write(t); made.append(p)
    os.chmod(p, 0o644)
    chk(p); print('MADE', f, sha(t))
print('OK 2.99.629 (tin missed call Telnyx gui boi cron tx-mp3 moi 15 s) - set APP_VERSION 2.99.629, restart php-fpm. AN public_html: chi kiem cron/tx-mp3.php co phai ban chep rieng.')
