#!/usr/bin/env python3
# LAMWEB 2.99.573 (anh Logan 00:55 CDT: test booking 00:54 -> the notification came LATE and was ANOTHER booking: "New bo... Alyson D. - ... Today 11:00 AM").
# How it can happen (code read): a "New booking" / customer notification is HELD (inc/nb-hold.php) until the customer's text is delivered, at most 45 s,
# and only let go by: the Android's Sent/Delivered webhook, cron/turn.php (every minute), or ANY next web request (nb_tick -> nb_release_due).
# If cron/turn.php is not running (night / stopped), a hold stays until the next request: Alyson's held notification went out when anh Logan's test
# booking request came (00:54) -> it looked like the wrong notification; his own Test notification was then held the same way (no cron to let it go).
# FIX (safe, small): never hold when the cron is not alive (cron_turn_at older than 150 s) -> sent at once (as before 2.99.306), one line in nb_log.
# Run: python3 fix573.py <release dir> [go]   (check / backup to ~/app/old + patch + php -l, put back by itself if it fails)
import sys, os, shutil, subprocess, time, hashlib
TAG = '573'
rel = sys.argv[1].rstrip('/'); go = len(sys.argv) > 2 and sys.argv[2] == 'go'
f = 'inc/nb-hold.php'; p = f'{rel}/{f}'; s = open(p, encoding='utf-8').read()
A = "function nb_hold_add(int $asId, array $calls): void {\n"
B = (A + "    $ca = (string)(q(\"SELECT v FROM settings WHERE k = 'cron_turn_at'\")->fetchColumn() ?: ''); // (2.99." + TAG + ") cron/turn.php not alive (night / stopped): nobody lets a hold go -> send now, never held\n"
         "    if ($ca === '' || strtotime($ca) < time() - 150) { nb_log('KHONG GIU (cron/turn.php khong chay tu ' . ($ca ?: '?') . ') - gui ngay ' . count($calls) . ' thong bao'); nb_run($calls); return; }\n")
def sha(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
n = s.count(A); print(f, 'sha', sha(s), 'anchor x', n, 'already', ('2.99.' + TAG + ')') in s)
if n != 1 or ('2.99.' + TAG + ')') in s: sys.exit('STOP: anchor not found exactly once (or already patched) - nothing changed')
t = s.replace(A, B)
if not go: print('NEW would be', sha(t)); sys.exit('check only - run again with: go')
bk = os.path.expanduser('~/app/old'); os.makedirs(bk, exist_ok=True); st = time.strftime('%m%d%H%M'); b = f'{bk}/nb-hold.php.pre-{TAG}-{st}'
shutil.copy2(p, b); m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m)
r = subprocess.run(['php', '-l', p], capture_output=True, text=True); print(r.stdout.strip() or r.stderr.strip())
if 'No syntax errors' not in r.stdout: shutil.copy2(b, p); sys.exit('PHP ERROR - put back')
print('NEW', sha(t), 'backup', b)
