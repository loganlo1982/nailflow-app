#!/usr/bin/env python3
# CHAT 01/11 18:18: since ~17:49 every connect to the salon iPhone fails in 3-6 s with connect_failed_reason=error (callers 499 AND 601), no outbound leg.
#  The leg showed the CALLER's number as caller ID (not ours). Now: from = the SignalWire number that was called (ours) -> the carrier accepts it.
#  The owner still sees who called in the app / push (unchanged).
import sys, os, shutil, time, subprocess, hashlib
R = sys.argv[1].rstrip('/'); go = 'go' in sys.argv[2:]
f = R + '/inc/calls-agent.php'
A = "        $con = ['to' => $fwd, 'timeout' => cl_ring(), 'answer_on_bridge' => true,"
B = "        $con = ['to' => $fwd, 'timeout' => cl_ring(), 'answer_on_bridge' => true] + (strlen($to) === 12 ? ['from' => $to] : []) + [ /* (CHAT 01/11 606y) caller ID = our SignalWire number */"
t = open(f, encoding='utf-8').read(); print(f, hashlib.sha256(t.encode()).hexdigest()[:8], 'anchor', t.count(A))
if t.count(A) != 1: sys.exit('ANCHOR FAIL')
n = t.replace(A, B); print('new sha', hashlib.sha256(n.encode()).hexdigest()[:8])
if not go: print('check only'); sys.exit()
od = os.path.expanduser('~/app/old'); os.makedirs(od, exist_ok=True)
b = od + '/inc__calls-agent.php.pre-606y-' + time.strftime('%m%d%H%M'); shutil.copy2(f, b)
open(f, 'w', encoding='utf-8').write(n)
r = subprocess.run(['php', '-l', f], capture_output=True, text=True)
if r.returncode: shutil.copy2(b, f); sys.exit('PHP FAIL - put back ' + r.stdout + r.stderr)
print('OK backup', b)
