#!/usr/bin/env python3
# CHAT 01/11 06:50 - echo fix: the switchboard heard ITSELF (AN calls #43 #44: caller text = "thank you for calling American" / "your book today at 1").
# Root cause: <Say> was INSIDE <Gather> (barge-in) -> the phone line echo of our own voice is transcribed as the caller. Fix: speak first, then listen.
# + repeat_appt said "You're booked ..." for an EXISTING appointment -> "I see your appointment ...".
import sys, os, shutil, time, hashlib, subprocess
R = sys.argv[1].rstrip('/'); go = len(sys.argv) > 2 and sys.argv[2] == 'go'
def sha(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
E = {
 'inc/calls-ivr.php': [
  ("""return '<?xml version="1.0" encoding="UTF-8"?><Response><Gather input="speech" enhanced="true\"""",
   """return '<?xml version="1.0" encoding="UTF-8"?><Response>' . ($say !== '' ? '<Say voice="' . cl_x(cl_voice()) . '" language="en-US">' . cl_x($say) . '</Say>' : '') . '<Gather input="speech" enhanced="true\""""),
  ("""    . ($say !== '' ? '<Say voice="' . cl_x(cl_voice()) . '" language="en-US">' . cl_x($say) . '</Say>' : '') . '</Gather><Redirect method="POST">'""",
   """    . '</Gather><Redirect method="POST">' /* (CHAT 01/11 echo fix) speak first, then listen - the caller line echo was heard as the caller */""")],
 'inc/calls-talk.php': [
  ("""return cl_talk_say($id, $st, "You're booked " . implode(', and ', $l) . '. Anything else I can help with?');""",
   """return cl_talk_say($id, $st, 'I see your appointment ' . implode(', and ', $l) . '. Anything else I can help with?'); /* (CHAT 01/11) never "booked" for an existing one */""")]}
plan = []; bad = 0
for f, L in E.items():
    p = f'{R}/{f}'; s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in L]
    print(f, sha(s), 'anchors', n, 'already', 'CHAT 01/11' in s)
    if n != [1]*len(L) or 'CHAT 01/11' in s: bad = 1; continue
    t = s
    for a, b in L: t = t.replace(a, b)
    plan.append((p, t))
if bad: sys.exit('STOP - nothing changed')
if not go:
    for p, t in plan: print('NEW would be', p, sha(t))
    sys.exit(0)
bk = os.path.expanduser('~/app/old'); st = time.strftime('%m%d%H%M'); done = []
for p, t in plan:
    b = f'{bk}/' + p.split('/releases/')[-1].replace('/', '__') + f'.pre-606e-{st}'; shutil.copy2(p, b); done.append((p, b))
    m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m)
for p, b in done:
    r = subprocess.run(['php', '-l', p], capture_output=True, text=True); print(r.stdout.strip())
    if r.returncode:
        for q, bb in done: shutil.copy2(bb, q)
        sys.exit('PHP ERROR - all put back')
for p, t in plan: print('NEW', p, sha(t))
