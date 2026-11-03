#!/usr/bin/env python3
# CHAT 2.99.637C (anh Logan 03/11 01:23 "file nao loi thi sua lien", khong doi giao dien):
#  QA-0007 (P1) inc/api/settings.php: Settings -> Turn bat/tat "Chia khach theo ky nang" / "Khach 2+ dich vu - chuyen tho" goi audit() 2 tham so (can 4)
#           -> ArgumentCountError 500, save_settings rollback -> khong luu duoc gi. Sua: audit(kind, target, truoc, sau).
#  QA-0008 (P2) inc/stophook.php ad_stop_in(): STOP qua Android chung o tiem khong phai "speaker" + khong biet so -> $r chua co -> ['ok'..] + $r = TypeError 500. Sua: $r = [].
#  2 file, moc 1 lan, khong doi DB / giao dien. Run: python3 fix637c.py <release dir> [go]
import sys, os, shutil, time, hashlib, json, subprocess
R = sys.argv[1].rstrip('/'); go = len(sys.argv) > 2 and sys.argv[2] == 'go'
def sha(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
F = json.loads(r"""{"inc/api/settings.php": [["audit('setting', 'Chia khách theo kỹ năng (thợ ít turn làm trước phần mình làm được): ' . ($v === '1' ? 'ON' : 'OFF'));", "audit('setting', 'Chia khách theo kỹ năng (thợ ít turn làm trước phần mình làm được)', $was === '1' ? 'ON' : 'OFF', $v === '1' ? 'ON' : 'OFF'); /* (2.99.637C - QA-0007) audit() needs before + after: 2 values made a 500 and nothing was saved */"], ["audit('setting', 'Khách 2+ dịch vụ – chuyển thợ: ' . ($v === '1' ? 'ON' : 'OFF')); }", "audit('setting', 'Khách 2+ dịch vụ – chuyển thợ', $was === '1' ? 'ON' : 'OFF', $v === '1' ? 'ON' : 'OFF'); } /* (2.99.637C - QA-0007) */"]], "inc/stophook.php": [["    $names = ad_stop_names(); $was = ad_stopped($p);\n    if ($start) {", "    $names = ad_stop_names(); $was = ad_stopped($p); $r = []; /* (2.99.637C - QA-0008) a salon that is not the speaker and does not know the number: nothing below sets $r */\n    if ($start) {"]]}""")
plan = []; bad = 0
for f, ab in F.items():
    p = f'{R}/{f}'; s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in ab]; al = '2.99.637C' in s
    print(f, 'sha', sha(s), 'anchors', *n, 'already', al)
    if al or n != [1] * len(n): bad = 1; continue
    t = s
    for a, b in ab: t = t.replace(a, b)
    plan.append((f, p, t))
if bad: sys.exit('STOP: an anchor is not found exactly once, or already patched - nothing changed')
if not go:
    for f, p, t in plan: print('NEW would be', f, sha(t))
    sys.exit('check only - run again with: go')
bk = os.path.expanduser('~/app/old'); os.makedirs(bk, exist_ok=True); st = time.strftime('%m%d%H%M'); done = []
def back(msg):
    for q, bb in done: shutil.copy2(bb, q)
    sys.exit('ERROR ' + msg + ' - every file put back')
for f, p, t in plan:
    b = f'{bk}/' + p.strip('/').replace('/', '__') + f'.pre-637c-{st}'; shutil.copy2(p, b); m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m); done.append((p, b))
    r = subprocess.run(['php', '-l', p], capture_output=True, text=True)
    if r.returncode: back('in ' + p + ': ' + (r.stdout + r.stderr)[:300])
    print('NEW', f, sha(t), 'backup', b)
print('OK 2.99.637C (QA-0007 + QA-0008) - set APP_VERSION 2.99.637, restart php-fpm.')
