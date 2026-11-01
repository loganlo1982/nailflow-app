#!/usr/bin/env python3
# CHAT 2.99.601 - HQ Calls search: SignalWire search answers e164 + capabilities as a LIST (docs: phone-numbers/search) -> 598 read 'number' + capabilities['voice'] -> every number skipped ("No number free").
import sys, os, shutil, time, hashlib, subprocess
R = sys.argv[1].rstrip('/'); go = len(sys.argv) > 2 and sys.argv[2] == 'go'
p = f'{R}/inc/hq-calls.php'; s = open(p, encoding='utf-8').read()
def sha(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
a1 = "$e = hq_norm_phone((string)($x['number'] ?? '')); if (strlen($e) !== 12 || empty($x['capabilities']['voice'])) continue;"
b1 = "$e = hq_norm_phone((string)($x['e164'] ?? ($x['number'] ?? ''))); $cap = (array)($x['capabilities'] ?? []); $has = fn($k) => in_array($k, $cap, true) || !empty($cap[$k]); /* (2.99.601) SignalWire: e164 + capabilities list */ if (strlen($e) !== 12 || !$has('voice')) continue;"
a2 = "'city' => trim((string)($x['city'] ?? '') . ' ' . (string)($x['region'] ?? '')), 'score' => hqc_score($e), 'sms' => !empty($x['capabilities']['sms'])]; }"
b2 = "'city' => trim((string)($x['rate_center'] ?? ($x['city'] ?? '')) . ' ' . (string)($x['region'] ?? '')), 'score' => hqc_score($e), 'sms' => $has('sms')]; }"
n = [s.count(a1), s.count(a2)]; print(p, sha(s), 'anchors', n, 'already', '2.99.601' in s)
if n != [1, 1] or '2.99.601' in s: sys.exit('STOP')
t = s.replace(a1, b1).replace(a2, b2)
if not go: print('NEW would be', sha(t)); sys.exit('check only')
bk = os.path.expanduser('~/app/old'); st = time.strftime('%m%d%H%M'); b = f'{bk}/inc__hq-calls.php.pre-601-{st}'; shutil.copy2(p, b)
m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m)
r = subprocess.run(['php', '-l', p], capture_output=True, text=True); print(r.stdout.strip())
if r.returncode: shutil.copy2(b, p); sys.exit('PHP ERROR - put back')
print('NEW', sha(t), 'backup', b)
