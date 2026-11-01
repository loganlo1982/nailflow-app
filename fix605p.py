#!/usr/bin/env python3
# CHAT 01/11 07:25 - AI receptionist prompt fixes after anh Logan's real test calls (AN calls #46 #47 #48):
#  1) greeting said TWICE (SWML already plays "Thank you for calling ... may be recorded" -> the AI opened with it again)
#  2) #47 WRONG appointment cancelled: caller said "2 PM today", AI cancelled appt 1279 Tue 11/3 1 PM (and said "today at two"!)
#  3) #48 asked yes twice (read-back, then again after check_times) and repeated the whole closing after "thank you"
#  4) salon name read in CAPS from settings -> title case
import sys, os, shutil, time, hashlib, subprocess
R = sys.argv[1].rstrip('/'); go = len(sys.argv) > 2 and sys.argv[2] == 'go'
p = f'{R}/inc/calls-agent.php'; s = open(p, encoding='utf-8').read()
def sha(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
A = [
 ("""$s = $g['salon'] !== '' ? $g['salon'] : 'the salon';""",
  """$s = $g['salon'] !== '' ? mb_convert_case(mb_strtolower($g['salon']), MB_CASE_TITLE, 'UTF-8') : 'the salon'; /* (CHAT 01/11) not in CAPS */"""),
 (""". "# Open with\\n\\"Thank you for calling $s, this call may be recorded. Sorry we missed you – how can I help?\\"\\n\"""",
  """. "# Open with (the salon greeting and \\"this call may be recorded\\" were ALREADY played – NEVER repeat them)\\n\\"Sorry we missed you – how can I help?\\"\\n\""""),
 (""". "- Running late → late. Only their own appointments (the tools know the caller's number).\\n- End warmly: \\"You're all set! You'll get a text in a minute. Thanks for calling!\\" and stop talking.";""",
  """. "- Running late → late. Only their own appointments (the tools know the caller's number).\\n"
        . "- CANCEL / MOVE / ADD / CHANGE: first call find_appointments. Use ONLY an appointment from that list whose day AND time match what the caller said. Read back THAT appointment's real day and time (from the list), wait for yes, then act. If no appointment matches the caller's day/time, say so and tell them what you DO see – never pick another one. After the tool answers, repeat exactly the day/time the tool returned.\\n"
        . "- BOOK: call check_times FIRST (no question), then ONE short read-back, wait for yes, then book. Never ask yes twice for the same thing.\\n"
        . "- When it is done: ONE short goodbye, e.g. \\"You're all set – see you today at 2. Bye!\\" and stop. If they say thanks / okay / bye after that, only say \\"Bye!\\" – never repeat the summary.\";"""),
 ("""'conscience' => 'Never say a price. Never say booked, cancelled or moved before the tool says OK. Always read back and wait for yes before a change.'""",
  """'conscience' => 'Never say a price. Never say booked, cancelled or moved before the tool says OK. Always read back and wait for yes before a change. Only cancel or move the appointment whose day and time the caller said; say the day and time the tool returned. Never repeat the greeting. Keep goodbyes to one short line.'"""),
]
n = [s.count(a) for a, _ in A]; print(p, sha(s), 'anchors', n, 'already', 'CHAT 01/11' in s)
if n != [1]*len(A) or 'CHAT 01/11' in s: sys.exit('STOP - nothing changed')
t = s
for a, b in A: t = t.replace(a, b)
if not go: print('NEW would be', sha(t)); sys.exit(0)
bk = os.path.expanduser('~/app/old'); os.makedirs(bk, exist_ok=True); b = f'{bk}/inc__calls-agent.php.pre-605p-' + time.strftime('%m%d%H%M'); shutil.copy2(p, b)
m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m)
r = subprocess.run(['php', '-l', p], capture_output=True, text=True); print(r.stdout.strip())
if r.returncode: shutil.copy2(b, p); sys.exit('PHP ERROR - put back')
print('NEW', sha(t), 'backup', b)
