#!/usr/bin/env python3
# CHAT 01/11 10:20 - AN #54 answered call: only the CALLER was in the recording (text_s empty) -> "No OK from the salon heard".
# SWML record_call records one direction unless told: add direction 'both' (caller + what the caller hears = the salon), stereo kept.
import sys, os, shutil, time, hashlib, subprocess
R = sys.argv[1].rstrip('/'); go = len(sys.argv) > 2 and sys.argv[2] == 'go'
p = f'{R}/inc/calls-agent.php'; s = open(p, encoding='utf-8').read()
def sha(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
a = "['record_call' => ['stereo' => true, 'format' => 'wav', 'status_url'"
b = "['record_call' => ['stereo' => true, 'direction' => 'both' /* (CHAT 01/11 dir) caller + salon */, 'format' => 'wav', 'status_url'"
print(sha(s), 'anchor', s.count(a), 'already', 'CHAT 01/11 dir' in s)
if s.count(a) != 1 or 'CHAT 01/11 dir' in s: sys.exit('STOP')
t = s.replace(a, b)
if not go: print('NEW would be', sha(t)); sys.exit(0)
bk = os.path.expanduser('~/app/old'); os.makedirs(bk, exist_ok=True); bb = f'{bk}/inc__calls-agent.php.pre-605d-' + time.strftime('%m%d%H%M'); shutil.copy2(p, bb)
m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m)
r = subprocess.run(['php', '-l', p], capture_output=True, text=True); print(r.stdout.strip())
if r.returncode: shutil.copy2(bb, p); sys.exit('PHP ERROR - put back')
print('NEW', sha(t))
