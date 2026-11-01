#!/usr/bin/env python3
# CHAT 01/11 10:55 - ROOT CAUSE "No OK from the salon heard" (AN #55): in cl_ai_schema() two '//' comments sit in the MIDDLE of a line,
#  so the keys after them are commented out: new_date, new_time, customer_name, customer_phone, service_ids, service_text (since 594-B)
#  and salon_side, salon_agreed (since 602). The OpenAI schema is strict -> the AI can never answer salon_agreed -> every answered call = "No OK".
#  Fix: the two comments become /* */ so the keys come back. Nothing else changes.
import sys, os, shutil, time, subprocess, hashlib
R = sys.argv[1].rstrip('/'); go = len(sys.argv) > 2 and sys.argv[2] == 'go'
f = R + '/inc/calls-job.php'; t = open(f, encoding='utf-8').read()
print('sha', hashlib.sha256(t.encode()).hexdigest()[:8])
A = [("'add_n' => $i, // (2.99.594-B) 'new_date' => $s,", "'add_n' => $i, /* (2.99.594-B) */ 'new_date' => $s,"),
     ("// (2.99.602) 'salon_side' => ['type' => 'string', 'enum' => ['person', 'voicemail', 'none']], 'salon_agreed' => ['type' => 'boolean'],", "/* (2.99.602) */ 'salon_side' => ['type' => 'string', 'enum' => ['person', 'voicemail', 'none']], 'salon_agreed' => ['type' => 'boolean'], // (CHAT 01/11 606s) these keys were commented out by the // before them")]
print('anchors', [t.count(a) for a, _ in A])
if any(t.count(a) != 1 for a, _ in A): sys.exit('ANCHOR FAIL')
n = t
for a, b in A: n = n.replace(a, b)
print('new sha', hashlib.sha256(n.encode()).hexdigest()[:8])
if not go: print('check only'); sys.exit()
od = os.path.expanduser('~/app/old'); os.makedirs(od, exist_ok=True)
b = od + '/inc__calls-job.php.pre-606s-' + time.strftime('%m%d%H%M'); shutil.copy2(f, b)
open(f, 'w', encoding='utf-8').write(n)
r = subprocess.run(['php', '-l', f], capture_output=True, text=True)
if r.returncode: shutil.copy2(b, f); sys.exit('PHP FAIL - put back ' + r.stdout + r.stderr)
print('OK backup', b)
