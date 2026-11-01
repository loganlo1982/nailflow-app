#!/usr/bin/env python3
# CHAT 01/11 17:58 (anh Logan: tu 499 goi 1130, may khach dem ~7 giay roi iPhone tiem moi do chuong):
#  the greeting "Thank you for calling … This call may be recorded." (say, ~5-7 s) played BEFORE connect -> the iPhone rang only after it.
#  Now (salon iPhone set): the greeting is the connect RINGBACK (SignalWire: "Ringback to play to the caller while … destinations ring", play URIs)
#  -> the iPhone rings at once while the caller hears the greeting, then the ring tone. Closed / no iPhone: unchanged (greeting then the AI).
import sys, os, shutil, time, subprocess, hashlib
R = sys.argv[1].rstrip('/'); go = 'go' in sys.argv[2:]
f = R + '/inc/calls-agent.php'
A = "        $main[] = ['connect' => $con];"
B = ("        $con['ringback'] = ['say:' . cl_hello() . ($rec ? CL_NOTICE : ''), 'ring:us']; array_splice($main, 1, 1); /* (CHAT 01/11 606r) the greeting plays WHILE the iPhone rings (was ~7 s before the ring) */\n"
     "        $main[] = ['connect' => $con];")
t = open(f, encoding='utf-8').read(); print(f, hashlib.sha256(t.encode()).hexdigest()[:8], 'anchor', t.count(A), 'already', '606r' in t)
if t.count(A) != 1 or '606r' in t: sys.exit('ANCHOR FAIL')
n = t.replace(A, B); print('new sha', hashlib.sha256(n.encode()).hexdigest()[:8])
if not go: print('check only'); sys.exit()
od = os.path.expanduser('~/app/old'); os.makedirs(od, exist_ok=True)
b = od + '/inc__calls-agent.php.pre-606r-' + time.strftime('%m%d%H%M'); shutil.copy2(f, b)
open(f, 'w', encoding='utf-8').write(n)
r = subprocess.run(['php', '-l', f], capture_output=True, text=True)
if r.returncode: shutil.copy2(b, f); sys.exit('PHP FAIL - put back ' + r.stdout + r.stderr)
print('OK backup', b)
