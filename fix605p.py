#!/usr/bin/env python3
# CHAT 01/11 - 605B prompt edits asked by LAMWEB: (a) "After your goodbye, call end_call." (b) drop the spoken "Sorry we missed you" opener line (static_greeting plays it)
import sys, os, re, shutil, time, subprocess, hashlib
R = sys.argv[1].rstrip('/'); go = len(sys.argv) > 2 and sys.argv[2] == 'go'
f = R + '/inc/calls-agent.php'; t = open(f, encoding='utf-8').read()
print('sha', hashlib.sha256(t.encode()).hexdigest()[:8])
a_old = 'never repeat the summary.'
a_new = 'never repeat the summary. After your goodbye, call end_call.'
m = re.search(r'# Open with \(the salon greeting and \\"this call may be recorded\\" were ALREADY played .{1,3} NEVER repeat them\)\\n\\"Sorry we missed you .{1,3} how can I help\?\\"\\n', t)
print('a', t.count(a_old), 'b', 1 if m else 0, 'already', 'call end_call.' in t)
if t.count(a_old) != 1 or not m: sys.exit('ANCHOR FAIL')
n = t.replace(a_old, a_new)
n = n.replace(m.group(0), '# Opening (the salon greeting, \\"this call may be recorded\\" and \\"Sorry we missed you - how can I help?\\" were ALREADY played - NEVER repeat them; just listen)\\n')
print('new sha', hashlib.sha256(n.encode()).hexdigest()[:8])
if not go: print('check only'); sys.exit()
od = os.path.expanduser('~/app/old'); os.makedirs(od, exist_ok=True)
b = od + '/inc__calls-agent.php.pre-606p-' + time.strftime('%m%d%H%M'); shutil.copy2(f, b)
open(f, 'w', encoding='utf-8').write(n)
r = subprocess.run(['php', '-l', f], capture_output=True, text=True)
if r.returncode: shutil.copy2(b, f); sys.exit('PHP FAIL - put back ' + r.stdout + r.stderr)
print('OK backup', b)
