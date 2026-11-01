#!/usr/bin/env python3
# (CHAT rebase 31/10 21:00: replies.php anchor starts at ($via - 592 made it elseif)
# LAMWEB 2.99.572 (CHAT -> LAMWEB: bo dong 'Da tu huy hen' + 1 thong bao huy, anh Logan 23:12 / 00:39):
# a customer texts CANCEL -> ONE notification to the owner, AT ONCE: "<salon> - <customer> cancelled Sat 10/31 12:00 PM (text)"; no 2nd 'message' push for that text;
# the red line "X Da tu huy hen ... - Undo" no longer in the conversation (Messages, every salon). The calendar cancels as before; Undo stays on the appointment.
# ROOT CAUSE of the late 'cantcome' (~1 min): nb_cap_end() HOLDS the owner's push until the customer's answer text is delivered (nb-hold, <= 45 s),
#   but that text (selfcxl) itself waits 2 min (AS_CANCEL_WAIT) -> the hold runs out and the cron (every minute) lets it go -> ~1 min. Now: a cancel is never held.
# Also (anh Logan 00:43): a text to a customer had the salon name TWICE ('Love Nails / Ok / - Love Nails'): sd_sign() (shared Android) added '- <salon>' at the end
#   although sms_brand / sms_brand_inline already put the name on the first line -> now the end signature only when the first line has no name.
# Files: inc/shareddev.php (no 2nd name), inc/nb-hold.php (cancel not held), inc/android.php (no 'message' push for a cancel text that got its own cancel notice),
#        inc/replies.php (the notice text in English for a texted cancel), assets/admin/messages.js (the red line hidden).
# Run: python3 fix572.py <release dir>        -> check only
#      python3 fix572.py <release dir> go     -> backup to ~/app/old + patch + php -l (all files put back by itself if one fails)
import sys, os, shutil, subprocess, time, hashlib
TAG = '572'
rel = sys.argv[1].rstrip('/'); go = len(sys.argv) > 2 and sys.argv[2] == 'go'
X = "\u274c"
P = [
 ('inc/nb-hold.php',
  "    if ($hold) { try { nb_hold_add($hold, $calls); return; }",
  "    foreach ($calls as $c) if (($c[0] ?? '') === 'admin' && ($c[1] ?? '') === 'cantcome') { $hold = 0; break; } // (2.99." + TAG + ") a customer CANCELLED: the owner is told at once (never held for the answer text)\n"
  "    if ($hold) { try { nb_hold_add($hold, $calls); return; }"),
 ('inc/android.php',
  "        if (!empty($r['mid'])) { require_once __DIR__ . '/inbox.php'; ib_new_text($from, $text, (int)$r['mid']); }",
  "        if (!empty($r['mid']) && !in_array((string)($r['result'] ?? ''), ['cancelled', 'cancelled-late', 'many', 'resched', 'off', 'started'], true)) { require_once __DIR__ . '/inbox.php'; ib_new_text($from, $text, (int)$r['mid']); } /* (2.99." + TAG + ") a CANCEL text: only its own cancel notice (1 push), no 2nd 'message' push */"),
 ('inc/replies.php',
  "($via !== '') { $t = '" + X + " ' . $who . ' hu\u1ef7 h\u1eb9n ' . rp_when($a) . ($via === 'web' ? ' (qua web)' : ' (qua tin nh\u1eafn)') . ($late ? ' \u2013 HU\u1ef6 S\u00c1T GI\u1edc' : '');",
  "($via !== '') { $t = $via === 'web' ? '" + X + " ' . $who . ' hu\u1ef7 h\u1eb9n ' . rp_when($a) . ' (qua web)' . ($late ? ' \u2013 HU\u1ef6 S\u00c1T GI\u1edc' : '') : '" + X + " ' . $who . ' cancelled ' . rp_when($a) . ($late ? ' \u2013 late cancel' : ''); // (2.99." + TAG + ") texted cancel: '<customer> cancelled Sat 10/31 12:00 PM'"),
 ('inc/shareddev.php',
  "    $line = '\u2014 ' . $nm . ($ph !== '' ? ' ' . $ph : '');",
  "    $top = strtok(ltrim($body), \"\\n\"); if (is_string($top) && (mb_stripos($top, $nm) === 0 || (function_exists('gsm7_clean') && mb_stripos($top, gsm7_clean($nm)) === 0))) return $body; // (2.99." + TAG + ") the salon's name already on the first line: never a 2nd '- <salon>' at the end\n"
  "    $line = '\u2014 ' . $nm . ($ph !== '' ? ' ' . $ph : '');"),
 ('inc/autosend.php',
  "    $id = as_add($kind, 'ob:' . $o['id'], (string)$o['phone'], (string)$o['name'], $body, $info);\n    if (!$id) return null;\n",
  "    $id = as_add($kind, 'ob:' . $o['id'], (string)$o['phone'], (string)$o['name'], $body, $info);\n    if (!$id) return null;\n"
  "    if ($kind === 'cancel' && str_starts_with((string)($o['ref'] ?? ''), 'selfcxl:')) { $sid = $id; after_reply(function () use ($sid) { $GLOBALS['as_via'] = 'customer cancelled'; as_flush(false, [$sid]); }, true); } // (2.99." + TAG + ") the CUSTOMER cancelled: their text goes NOW (the 2-min wait is for the salon's own cancels only)\n"),
 ('inc/sms-short.php',
  "        'selfcxl' => \"Su cita$who del $when esta CANCELADA. Quiere otra hora? Reserve aqui: $book Llame $ph\",",
  "        'selfcxl' => \"Su cita$who del $when esta cancelada. Puede reservar otra cita con este enlace: $book\", // (2.99." + TAG + ")"),
 ('inc/sms-short.php',
  "        'selfcxl' => \"Your appointment$who on $when is CANCELLED. Want a new time? Book here: $book Questions? Call $ph\",",
  "        'selfcxl' => \"Your appointment$who on $when is cancelled. You can book another appointment with this link: $book\", // (2.99." + TAG + ")"),
 ('inc/sms-short.php',
  "            'selfcxl' => [\"Su cita$who esta CANCELADA\", 'ERA: ' . $when, \"QUIERE OTRA HORA?\\n$book\"],",
  "            'selfcxl' => [\"Su cita$who del $when esta cancelada.\", \"Puede reservar otra cita con este enlace:\\n$book\"], // (2.99." + TAG + ")"),
 ('inc/sms-short.php',
  "            'selfcxl' => [\"Your appointment$who is CANCELLED.\", 'WAS: ' . $when, \"WANT A NEW TIME?\\n$book\"],",
  "            'selfcxl' => [\"Your appointment$who on $when is cancelled.\", \"You can book another appointment with this link:\\n$book\"], // (2.99." + TAG + ")"),
 ('inc/sms-short.php',
  "        if ($ask) $rows[] = sms_ask_line($es);",
  "        if ($ask && $kind !== 'selfcxl') $rows[] = sms_ask_line($es); // (2.99." + TAG + ") the customer's cancel text: exactly anh Logan's words (no Questions line)"),
 ('inc/outbox-2.php',
  "    $tpl = $es ? ($n > 1 ? \"Sus citas ({n} personas) del {when} est\u00e1n CANCELADAS.\" : \"Su cita del {when} est\u00e1 CANCELADA.\") . \"\\n\u2705 \u00bfQuiere otra hora? Reserve aqu\u00ed: {link}\\n\u00bfPreguntas? Llame al {salon_phone}\"\n"
  "               : ($n > 1 ? \"Your appointments ({n} people) on {when} are CANCELLED.\" : \"Your appointment on {when} is CANCELLED.\") . \"\\n\u2705 Want a new time? Book here: {link}\\nQuestions? Call {salon_phone}\";",
  "    $tpl = $es ? ($n > 1 ? \"Sus citas ({n} personas) del {when} est\u00e1n canceladas.\" : \"Su cita del {when} est\u00e1 cancelada.\") . \" Puede reservar otra cita con este enlace: {link}\" // (2.99." + TAG + ") anh Logan 31/10 00:48\n"
  "               : ($n > 1 ? \"Your appointments ({n} people) on {when} are cancelled.\" : \"Your appointment on {when} is cancelled.\") . \" You can book another appointment with this link: {link}\";"),
 ('assets/admin/messages.js',
  "function ibBubbles(rows, at, meta) { let last = -1e12, lastD = '';",
  "function ibBubbles(rows, at, meta) { rows = rows.filter(m => !(m.dir === 'sys' && /^" + X + " \u0110\u00e3 t\u1ef1 hu\u1ef7 h\u1eb9n/.test(String(m.body || '')))); /* (2.99." + TAG + ") the red line of a texted cancel: not shown (Undo stays on the appointment) */ let last = -1e12, lastD = '';"),
]
def sha(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
src = {f: open(f'{rel}/{f}', encoding='utf-8').read() for f, _, _ in P}
bad = False
for f, a, _ in P:
    n = src[f].count(a); print(f, 'sha', sha(src[f]), 'anchor x', n, 'already', ('2.99.' + TAG + ')') in src[f]); bad = bad or n != 1 or ('2.99.' + TAG + ')') in src[f]
if bad: sys.exit('STOP: an anchor is not found exactly once (or already patched) - nothing changed')
new = dict(src)
for f, a, b in P: new[f] = new[f].replace(a, b)
if not go:
    for f in src: print('NEW would be', f, sha(new[f]))
    sys.exit('check only - run again with: go')
bk = os.path.expanduser('~/app/old'); os.makedirs(bk, exist_ok=True); st = time.strftime('%m%d%H%M')
for f in src: shutil.copy2(f'{rel}/{f}', f'{bk}/{os.path.basename(f)}.pre-{TAG}-{st}')
for f in src:
    p = f'{rel}/{f}'; m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(new[f]); os.chmod(p, m)
for f in src:
    if not f.endswith('.php'): continue
    r = subprocess.run(['php', '-l', f'{rel}/{f}'], capture_output=True, text=True); print(r.stdout.strip() or r.stderr.strip())
    if 'No syntax errors' not in r.stdout:
        for g in src: shutil.copy2(f'{bk}/{os.path.basename(g)}.pre-{TAG}-{st}', f'{rel}/{g}')
        sys.exit('PHP ERROR - all files put back')
for f in src: print('NEW', f, sha(new[f]))
print('backup', bk, '*.pre-' + TAG + '-' + st)
