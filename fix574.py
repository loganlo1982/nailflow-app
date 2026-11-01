#!/usr/bin/env python3
# LAMWEB 2.99.574 (CHAT -> LAMWEB LENH 571, anh Logan 00:19 "Duyet"): the text to a customer with SEVERAL appointments who texts 'cancel'
# ("You have 4 appointments with us. Tap one ... Questions? Call") ended CUT - no salon phone.
# ROOT CAUSE: the salon's phone setting (Settings -> Salon info, setting 'salon_phone') is EMPTY at that salon; sms_fill() puts '' for {salon_phone}
# and keeps the line ("Questions? Call" has letters, so it is not dropped). The same for every automatic text with a Call phrase (EN/ES),
# the short texts (sms-short: "... Call "), the closed-day text, the tech-out text and the iPad calendar note.
# FIX: no salon phone -> the Call phrase goes (only the phrase: a line with a link or the salon name keeps them); a phone set -> exactly as before.
# Run: python3 fix574.py <release dir>        -> check only
#      python3 fix574.py <release dir> go     -> backup to ~/app/old + patch + php -l (all files put back by itself if one fails)
import sys, os, shutil, subprocess, time, hashlib
rel = sys.argv[1].rstrip('/'); go = len(sys.argv) > 2 and sys.argv[2] == 'go'
PH = "\U0001F4DE"  # telephone emoji
P = [
 ('inc/core/sms.php',
  "        $filled = strtr($line, $map);\n",
  "        if (trim((string)$map['{salon_phone}']) === '' && preg_match('/\\{(salon_phone|phone)\\}/', $line)) { // (2.99.574) no salon phone: the Call phrase goes (never 'Questions? Call' cut), the rest of the line stays\n"
  "            $line = (string)preg_replace('/\\s*(?:[\\x{00B7}\\x{2022}|]\\s*)?(?:\\x{1F4DE}\\s*)?(?:(?:Questions\\?|\\x{00BF}Preguntas\\?)\\s*)?(?:(?:or\\s+|o\\s+)?(?:please\\s+)?(?:call|ll\\x{00E1}menos|llame)(?:\\s+us)?(?:\\s+anytime)?(?:\\s+(?:at|al))?\\s*:?\\s*)?\\{(?:salon_phone|phone)\\}/iu', '', $line);\n"
  "            $line = trim((string)preg_replace('/^[\\s\\x{2013}\\x{2014}\\-\\x{00B7}]+/u', '', $line)); if ($line === '') continue; }\n"
  "        $filled = strtr($line, $map);\n"),
 ('inc/sms-short.php',
  "    $t = $L[$kind] ?? '';\n",
  "    $t = $L[$kind] ?? ''; if (trim($ph) === '') $t = rtrim((string)preg_replace('/\\s*(?:Questions\\? )?(?:Call|Llame)\\s*$/u', '', $t)); // (2.99.574) no salon phone: no cut 'Call' at the end\n"),
 ('inc/techout.php',
  "\"\\n\\n" + PH + " Questions? Call: \" . setting('salon_phone') . \"\\n\" . salon_title();",
  "(trim((string)setting('salon_phone')) !== '' ? \"\\n\\n" + PH + " Questions? Call: \" . setting('salon_phone') . \"\\n\" : \"\\n\\n\") . salon_title(); // (2.99.574) no salon phone: no Call line"),
 ('inc/api/settings.php',
  PH + " Questions? Call: \" . setting('salon_phone') . \"\n\" . salon_title();",
  "\" . (trim((string)setting('salon_phone')) !== '' ? '" + PH + " Questions? Call: ' . setting('salon_phone') . \"\n\" : '') . salon_title(); // (2.99.574) no salon phone: no Call line"),
 ('inc/api/_kiosk.php',
  ", 'Call: ' . setting('salon_phone')]));",
  "], trim((string)setting('salon_phone')) !== '' ? ['Call: ' . setting('salon_phone')] : [])); // (2.99.574) no salon phone: no 'Call:' line"),
]
def sha(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
src = {f: open(f'{rel}/{f}', encoding='utf-8').read() for f, _, _ in P}
bad = False
for f, a, _ in P:
    n = src[f].count(a); print(f, 'sha', sha(src[f]), 'anchor x', n, 'already', '2.99.574' in src[f]); bad = bad or n != 1 or '2.99.574' in src[f]
if bad: sys.exit('STOP: an anchor is not found exactly once (or already patched) - nothing changed')
new = dict(src)
for f, a, b in P: new[f] = new[f].replace(a, b)
if not go:
    for f in src: print('NEW would be', f, sha(new[f]))
    sys.exit('check only - run again with: go')
bk = os.path.expanduser('~/app/old'); os.makedirs(bk, exist_ok=True); st = time.strftime('%m%d%H%M')
for f in src: shutil.copy2(f'{rel}/{f}', f'{bk}/{os.path.basename(f)}.pre-574-{st}')
for f in src:
    p = f'{rel}/{f}'; m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(new[f]); os.chmod(p, m)
for f in src:
    r = subprocess.run(['php', '-l', f'{rel}/{f}'], capture_output=True, text=True); print(r.stdout.strip() or r.stderr.strip())
    if 'No syntax errors' not in r.stdout:
        for g in src: shutil.copy2(f'{bk}/{os.path.basename(g)}.pre-574-{st}', f'{rel}/{g}')
        sys.exit('PHP ERROR - all files put back')
for f in src: print('NEW', f, sha(new[f]))
print('backup', bk, '*.pre-574-' + st)
