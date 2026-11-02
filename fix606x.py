#!/usr/bin/env python3
# CHAT 01/11 18:05: AN #72 #73 - connect to the salon iPhone failed in ~1-4 s with NO outbound leg in SignalWire's logs (no ring). Find the reason:
#  connect's result "default" (failed) now first calls a=missed&why=%{connect_failed_reason} (SignalWire sets connect_failed_reason) -> in the access log. Behaviour unchanged.
import sys, os, shutil, time, subprocess, hashlib
R = sys.argv[1].rstrip('/'); go = 'go' in sys.argv[2:]
f = R + '/inc/calls-agent.php'
A = "'default' => [['execute' => ['dest' => 'after']]]]];"
B = "'default' => [['request' => ['url' => cl_agent_url('missed', $q) . '&why=%{connect_failed_reason}', 'method' => 'POST']], ['execute' => ['dest' => 'after']]]]]; /* (CHAT 01/11 606x) log why the iPhone leg failed */"
t = open(f, encoding='utf-8').read(); print(f, hashlib.sha256(t.encode()).hexdigest()[:8], 'anchor', t.count(A))
if t.count(A) != 1: sys.exit('ANCHOR FAIL')
n = t.replace(A, B); print('new sha', hashlib.sha256(n.encode()).hexdigest()[:8])
if not go: print('check only'); sys.exit()
od = os.path.expanduser('~/app/old'); os.makedirs(od, exist_ok=True)
b = od + '/inc__calls-agent.php.pre-606x-' + time.strftime('%m%d%H%M'); shutil.copy2(f, b)
open(f, 'w', encoding='utf-8').write(n)
r = subprocess.run(['php', '-l', f], capture_output=True, text=True)
if r.returncode: shutil.copy2(b, f); sys.exit('PHP FAIL - put back ' + r.stdout + r.stderr)
print('OK backup', b)
