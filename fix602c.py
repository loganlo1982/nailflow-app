#!/usr/bin/env python3
# CHAT 01/11 17:45 - LENH 602C (anh Logan "lam het"): the 602B phone switchboard (Love Nails), AN #45: "cancel ... 2 of them" -> AI cancel_one with no name ->
#  "who should I take off: Test, Test?" again and again. inc/calls-talk.php, the cancel block only:
#  1) cancel_one, no name, the caller said both / all / everyone / 2 of them / ambos / todos (and not "one of / just one") -> cancel_all (asked to confirm as before)
#  2) the same first names + "the first / second (one)" -> that person
#  3) still no one -> ONE question "cancel everyone, or just one person: A, B?" (same names: no list); a 2nd time -> the owner (no loop)
import sys, os, shutil, time, subprocess, hashlib
R = sys.argv[1].rstrip('/'); go = 'go' in sys.argv[2:]
f = R + '/inc/calls-talk.php'
A = "if ($act === 'cancel_one' && $n > 1) return cl_talk_say($id, $st, 'Sure – who should I take off: ' . implode(', ', array_map(fn($m) => cl_talk_first((string)$m['customer_name']), $mem)) . '?');"
B = ("if ($act === 'cancel_one' && $n > 1) { /* (CHAT 01/11 602C) */\n"
     "$tw = ' ' . cl_norm(cl_ivr_text($st)) . ' '; $nm = array_map(fn($m) => cl_talk_first((string)$m['customer_name']), $mem); $same = count(array_unique(array_map('mb_strtolower', $nm))) < count($nm);\n"
     "if (!preg_match('/ (one of|just one|only one|uno de|solo uno) /', $tw) && preg_match('/ (both|all|everyone|everybody|whole|all of (us|them)|(two|2|three|3|four|4|five|5) of (us|them)|ambos|todos|todas) /', $tw)) $act = 'cancel_all';\n"
     "elseif ($same && preg_match('/ (first|1st|primer|primera) /', $tw)) return cl_talk_ask($id, $st, ['type' => 'cancel', 'a' => (int)$a['id'], 'j' => ['intent' => 'cancel', 'cancel_part' => true, 'cancel_names' => [(string)$mem[0]['customer_name']], 'cancel_n' => 1] + $base, 'name' => $nm[0]], 'Just to confirm – cancel the first ' . $nm[0] . ' from ' . $when . ', and keep the others?');\n"
     "elseif ($same && preg_match('/ (second|2nd|segundo|segunda) /', $tw)) return cl_talk_ask($id, $st, ['type' => 'cancel', 'a' => (int)$a['id'], 'j' => ['intent' => 'cancel', 'cancel_part' => true, 'cancel_names' => [(string)$mem[1]['customer_name']], 'cancel_n' => 1] + $base, 'name' => $nm[1]], 'Just to confirm – cancel the second ' . $nm[1] . ' from ' . $when . ', and keep the others?');\n"
     "else { if (!empty($st['who1'])) return cl_talk_owner($c, $st, ''); $st['who1'] = 1;\n"
     "return cl_talk_say($id, $st, $same ? 'Sure – should I cancel everyone, or just one person? If one, the first or the second?' : 'Sure – cancel everyone, or just one person: ' . implode(', ', $nm) . '?'); }\n}")
t = open(f, encoding='utf-8').read(); print(f, hashlib.sha256(t.encode()).hexdigest()[:8], 'anchor', t.count(A), 'already', '602C' in t)
if t.count(A) != 1 or '602C' in t: sys.exit('ANCHOR FAIL')
n = t.replace(A, B); print('new sha', hashlib.sha256(n.encode()).hexdigest()[:8])
if not go: print('check only'); sys.exit()
od = os.path.expanduser('~/app/old'); os.makedirs(od, exist_ok=True)
b = od + '/inc__calls-talk.php.pre-602c-' + time.strftime('%m%d%H%M'); shutil.copy2(f, b)
open(f, 'w', encoding='utf-8').write(n)
r = subprocess.run(['php', '-l', f], capture_output=True, text=True)
if r.returncode: shutil.copy2(b, f); sys.exit('PHP FAIL - put back ' + r.stdout + r.stderr)
print('OK backup', b)
