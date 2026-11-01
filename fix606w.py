#!/usr/bin/env python3
# CHAT 01/11 17:30 (anh Logan dong y): AI rule - a weekday + a date that do not match ("Tuesday, November 1st" but 11/1 is a Sunday) -> the WEEKDAY wins
#  (the date of that weekday nearest to the date said, never in the past). inc/calls-job.php CL_AI_RULES, one line added. AN #69.
import sys, os, shutil, time, subprocess, hashlib
R = sys.argv[1].rstrip('/'); go = 'go' in sys.argv[2:]
f = R + '/inc/calls-job.php'
A = '. "same_services: true only when the caller said everyone gets the same ('
B = ('. "date: when the caller (or the salon) says a WEEKDAY and a date that do not match (\\"Tuesday, November 1st\\" but November 1st is a Sunday in the Salon days list), the WEEKDAY wins: '
     'date = that weekday nearest to the date said, today or later (\\"Tuesday, November 1st\\" -> the Tuesday of that week). A speech-to-text slip on the number is more likely than on the weekday. If the two channels give different dates, also pick the one that matches the weekday.\\n" /* (CHAT 01/11 606w) */\n' + A)
t = open(f, encoding='utf-8').read(); print(f, hashlib.sha256(t.encode()).hexdigest()[:8], 'anchor', t.count(A), 'already', '606w' in t)
if t.count(A) != 1 or '606w' in t: sys.exit('ANCHOR FAIL')
n = t.replace(A, B); print('new sha', hashlib.sha256(n.encode()).hexdigest()[:8])
if not go: print('check only'); sys.exit()
od = os.path.expanduser('~/app/old'); os.makedirs(od, exist_ok=True)
b = od + '/inc__calls-job.php.pre-606w-' + time.strftime('%m%d%H%M'); shutil.copy2(f, b)
open(f, 'w', encoding='utf-8').write(n)
r = subprocess.run(['php', '-l', f], capture_output=True, text=True)
if r.returncode: shutil.copy2(b, f); sys.exit('PHP FAIL - put back ' + r.stdout + r.stderr)
print('OK backup', b)
