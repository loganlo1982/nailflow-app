#!/usr/bin/env python3
# CHAT 01/11 17:35 (anh Logan dong y): a weekday + a date that do not match ("Tuesday, November 1st" but 11/1 is a Sunday) -> the WEEKDAY wins.
#  Done in PHP (the AI ignored a prompt rule in the test on AN #69): only when the call names exactly ONE weekday (EN / ES) and no "today / tomorrow";
#  the date moves to that weekday within -3..+3 days of the AI's date, never in the past (else the next one). inc/calls-job.php only.
import sys, os, shutil, time, subprocess, hashlib
R = sys.argv[1].rstrip('/'); go = 'go' in sys.argv[2:]
f = R + '/inc/calls-job.php'
A1 = "$ai = cl_ai_after($c, cl_ai($c));"
B1 = "$ai = cl_weekday_fix($c, cl_ai_after($c, cl_ai($c))); /* (CHAT 01/11 606w) weekday wins */"
A2 = "\n/* ---------- 4. the AI reads what was said"
B2 = r'''
/** (CHAT 01/11 606w) the caller said ONE weekday and the AI's date is another weekday ("Tuesday, November 1st", 11/1 = Sunday): speech-to-text slips on the number
   more than on the weekday -> the date of that weekday nearest to the AI's date (-3..+3 days), never before today (then the next one). "today" / "tomorrow" said -> unchanged. */
function cl_weekday_fix(array $c, array $j): array {
$d = (string)($j['date'] ?? ''); if (!preg_match('/^\d{4}-\d{2}-\d{2}$/', $d)) return $j;
$t = mb_strtolower(' ' . $c['text_c'] . ' ' . $c['text_s'] . ' ');
if (preg_match('/\b(today|tomorrow|tonight|hoy|ma(n|ñ)ana)\b/u', $t)) return $j;
$names = [1 => ['monday', 'lunes'], 2 => ['tuesday', 'martes'], 3 => ['wednesday', 'miercoles', 'miércoles'], 4 => ['thursday', 'jueves'], 5 => ['friday', 'viernes'], 6 => ['saturday', 'sabado', 'sábado'], 7 => ['sunday', 'domingo']];
$said = []; foreach ($names as $n => $ws) foreach ($ws as $w) if (preg_match('/\b' . $w . 's?\b/u', $t)) $said[$n] = true;
if (count($said) !== 1) return $j;
$want = (int)array_key_first($said); $ts = strtotime($d . ' 12:00:00'); $have = (int)date('N', $ts);
if ($have === $want) return $j;
$diff = $want - $have; if ($diff > 3) $diff -= 7; if ($diff < -3) $diff += 7;
$nd = date('Y-m-d', strtotime(($diff >= 0 ? '+' : '') . $diff . ' day', $ts));
if ($nd < date('Y-m-d')) $nd = date('Y-m-d', strtotime(($diff + 7 >= 0 ? '+' : '') . ($diff + 7) . ' day', $ts));
$j['date'] = $nd; $j['date_fix'] = $d . ' -> ' . $nd . ' (weekday said)';
return $j;
}
''' + A2
t = open(f, encoding='utf-8').read(); print(f, hashlib.sha256(t.encode()).hexdigest()[:8], 'anchors', t.count(A1), t.count(A2), 'already', 'cl_weekday_fix' in t)
if t.count(A1) != 1 or t.count(A2) != 1 or 'cl_weekday_fix' in t: sys.exit('ANCHOR FAIL')
n = t.replace(A1, B1).replace(A2, B2, 1); print('new sha', hashlib.sha256(n.encode()).hexdigest()[:8])
if not go: print('check only'); sys.exit()
od = os.path.expanduser('~/app/old'); os.makedirs(od, exist_ok=True)
b = od + '/inc__calls-job.php.pre-606w-' + time.strftime('%m%d%H%M'); shutil.copy2(f, b)
open(f, 'w', encoding='utf-8').write(n)
r = subprocess.run(['php', '-l', f], capture_output=True, text=True)
if r.returncode: shutil.copy2(b, f); sys.exit('PHP FAIL - put back ' + r.stdout + r.stderr)
print('OK backup', b)
