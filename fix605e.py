#!/usr/bin/env python3
# CHAT 01/11 07:52 - AN #50: the caller said nothing; the AI heard ITS OWN greeting ("Sorry. We missed you Okay.") as the caller -> answered itself. Echo rule in the prompt.
import sys, os, shutil, time, hashlib, subprocess
R = sys.argv[1].rstrip('/'); go = len(sys.argv) > 2 and sys.argv[2] == 'go'
p = f'{R}/inc/calls-agent.php'; s = open(p, encoding='utf-8').read()
def sha(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
a = """\\"Sorry we missed you – how can I help?\\"\\n\""""
b = """\\"Sorry we missed you – how can I help?\\"\\n# Echo (phone lines echo your own voice)\\nIf what you hear is the same or almost the same as what YOU just said (e.g. \\"sorry we missed you\\", \\"how can I help\\", your own read-back), it is an ECHO, not the caller: do not answer it, say nothing and keep listening. Only answer real new words from the caller.\\n\""""
print(sha(s), 'anchor', s.count(a), 'already', 'ECHO, not the caller' in s)
if s.count(a) != 1 or 'ECHO, not the caller' in s: sys.exit('STOP')
t = s.replace(a, b)
if not go: print('NEW would be', sha(t)); sys.exit(0)
bk = os.path.expanduser('~/app/old'); os.makedirs(bk, exist_ok=True); bb = f'{bk}/inc__calls-agent.php.pre-605e-' + time.strftime('%m%d%H%M'); shutil.copy2(p, bb)
m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m)
r = subprocess.run(['php', '-l', p], capture_output=True, text=True); print(r.stdout.strip())
if r.returncode: shutil.copy2(bb, p); sys.exit('PHP ERROR - put back')
print('NEW', sha(t))
