#!/usr/bin/env python3
# CHAT 01/11 10:05 - answered calls (iPhone picked up) never read by the AI: AN #53 #54 stay status 'ring'.
# Root cause: cl_agent_rec queues an answered call only when status = 'talked', but nothing sets 'talked' on the SWML path -> status stays 'ring'.
# Fix: an answered/ringing 'call' whose recording finished is queued too (an AI-handled call is kind 'agent' -> not touched).
import sys, os, shutil, time, hashlib, subprocess
R = sys.argv[1].rstrip('/'); go = len(sys.argv) > 2 and sys.argv[2] == 'go'
p = f'{R}/inc/calls-agent.php'; s = open(p, encoding='utf-8').read()
def sha(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
a = "in_array((string)$c['kind'], ['call'], true) && (string)$c['status'] === 'talked')"
b = "in_array((string)$c['kind'], ['call'], true) && in_array((string)$c['status'], ['talked', 'ring'], true) /* (CHAT 01/11 rec) SWML never sets 'talked' */)"
print(sha(s), 'anchor', s.count(a), 'already', 'CHAT 01/11 rec' in s)
if s.count(a) != 1 or 'CHAT 01/11 rec' in s: sys.exit('STOP')
t = s.replace(a, b)
if not go: print('NEW would be', sha(t)); sys.exit(0)
bk = os.path.expanduser('~/app/old'); os.makedirs(bk, exist_ok=True); bb = f'{bk}/inc__calls-agent.php.pre-605c-' + time.strftime('%m%d%H%M'); shutil.copy2(p, bb)
m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m)
r = subprocess.run(['php', '-l', p], capture_output=True, text=True); print(r.stdout.strip())
if r.returncode: shutil.copy2(bb, p); sys.exit('PHP ERROR - put back')
print('NEW', sha(t))
