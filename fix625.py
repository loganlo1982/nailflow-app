#!/usr/bin/env python3
# CHAT 2.99.625 (anh Logan 02/11 11:27, BAO-CAO-AI-LE-TAN-0211 muc D): the AI receptionist asks only what is missing (one question at a time),
# answers the opening hours itself, a group = each first name, no time fits -> note + callback. CHANGED: inc/calls-agent.php (cl_agent_prompt) only.
# Run: python3 fix625.py <app dir>   /   python3 fix625.py <app dir> go
import sys, os, shutil, time, hashlib, subprocess
R = sys.argv[1].rstrip('/'); go = len(sys.argv) > 2 and sys.argv[2] == 'go'
def sha(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
f = 'inc/calls-agent.php'
A = [
 ('        . "\\n# Rules (hard)\\n- Never say a price, a discount or a promotion; never give medical advice.\\n',
  '        . "\\n# Asking\\n- Use everything the caller has told you (name, service, people, day, time, tech) – never ask again for something they said.\\n'
  '- Ask only what is still missing, ONE short question per turn, in this order: service(s) → who it is for (for 2 or more people: each first name and service) → day and time. Don\'t ask about a tech: use the one they name, otherwise any tech.\\n'
  '- If no time works after you offered the 2 times: add_note with what they want, then call transfer_owner with reason \\"no time fits\\".\\n" /* (2.99.625 anh Logan 02/11: ask only what is missing; hours; group names; no time fits -> callback) */\n'
  '        . "# Rules (hard)\\n- Never say a price, a discount or a promotion; never give medical advice.\\n'),
 ('        . "- A question that is not about their appointment (prices, hours, walk-ins, address…), Spanish',
  '        . "- Opening hours: answer from the Days list (e.g. \\"We\'re open today until 7\\").\\n- A question that is not about their appointment (prices, walk-ins, address…), Spanish'),
]
p = f'{R}/{f}'; s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in A]; al = '2.99.625' in s
print(f, 'sha', sha(s), 'anchors', *n, 'already', al)
if al or n != [1] * len(A): sys.exit('STOP: anchor not found exactly once or already patched - nothing changed')
t = s
for a, b in A: t = t.replace(a, b)
if not go: print('NEW would be', f, sha(t)); sys.exit('check only - run again with: go')
bk = os.path.expanduser('~/app/old'); os.makedirs(bk, exist_ok=True); b = f'{bk}/inc__calls-agent.php.pre-625-' + time.strftime('%m%d%H%M')
shutil.copy2(p, b); m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m)
r = subprocess.run(['php', '-l', p], capture_output=True, text=True)
if r.returncode: shutil.copy2(b, p); sys.exit('ERROR php -l: ' + (r.stdout + r.stderr)[:300] + ' - put back')
print('NEW', f, sha(t), 'backup', b); print('OK 2.99.625 - set APP_VERSION 2.99.625, restart php-fpm, then Update AI (Telnyx)')
