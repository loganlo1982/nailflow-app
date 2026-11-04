#!/usr/bin/env python3
# fix639d.py - QA-0009 (P1): a customer moving their booking (text link) was checked with the MENU minutes, not the booking length the owner
# set -> moved on top of the next customer. Now the longer of the two (reschedule + the times shown). 3 files, no screen / DB change.
# Base: LIVE + 639c. Also patches the web api.php copies? NO (no route change).
# Run:  python3 fix639d.py <release dir>   (kiem)   /   ... go
import sys, os, shutil, time, hashlib, json, subprocess
args = [a for a in sys.argv[1:]]
if not args: sys.exit('usage: python3 fix639d.py <release dir> [go]')
go = args[-1] == 'go'
if go: args = args[:-1]
R = args[0].rstrip('/'); XP = [os.path.abspath(a) for a in args[1:]]
def sha(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
F = json.loads(r"""{"inc/api/_out.php": {"base": "01e507b4", "new": "22bd1c6d", "A": [["    return [$per, $people];\n}\n/** (2.53) Chosen techs whose online hours", "    return [$per, $people];\n}\n/** (2.99.639d QA-0009) a booking the customer MOVES keeps its own length: the owner may have made it longer than the menu - the free time is checked\n    for the longer of the two (never shorter than the menu). $members in the same order as the people of booking_per. */\nfunction per_keep_dur(array $per, array $members): array {\n    foreach ($members as $i => $m) { if (!isset($per[$i])) continue; $own = (int)($m['duration'] ?? 0); $add = $own - (int)$per[$i]['dur']; if ($add <= 0) continue;\n        if (!empty($per[$i]['segs'])) { $l = array_key_last($per[$i]['segs']); $per[$i]['segs'][$l]['dur'] = (int)$per[$i]['segs'][$l]['dur'] + $add; }\n        $per[$i]['dur'] = $own; }\n    return $per;\n}\n/** (2.53) Chosen techs whose online hours"]]}, "inc/api/links.php": {"base": "965dbd8c", "new": "d6a25f70", "A": [["    [$per, $people2] = booking_per($people, $each, array_map(fn($m) => (int)($m['design'] ?? 0) === 1, $members), []);\n", "    [$per, $people2] = booking_per($people, $each, array_map(fn($m) => (int)($m['design'] ?? 0) === 1, $members), []);\n    $per = per_keep_dur($per, $members); /* (2.99.639d QA-0009) the booking's own length (made longer by the owner), not only the menu */\n"]]}, "inc/api/public.php": {"base": "807e4cc7", "new": "c0efa5ff", "A": [["    if (($rs = (string)($_GET['rs'] ?? '')) !== '' && ($ra = q('SELECT * FROM appointments WHERE token = ?', [$rs])->fetch())) $GLOBALS['slot_skip'] = array_map(fn($m) => (int)$m['id'], group_members($ra)); // (2.69) moving their own booking\n", "    if (($rs = (string)($_GET['rs'] ?? '')) !== '' && ($ra = q('SELECT * FROM appointments WHERE token = ?', [$rs])->fetch())) { $GLOBALS['slot_skip'] = array_map(fn($m) => (int)$m['id'], group_members($ra)); // (2.69) moving their own booking\n        $per = per_keep_dur($per, group_members($ra)); $dur = max(array_column($per, 'dur')); } /* (2.99.639d QA-0009) the times offered fit the booking's own length */\n"]]}}""")
plan = []; bad = 0
for f, x in F.items():
    p = f'{R}/{f}'
    if not os.path.isfile(p): print(f, 'MISSING'); bad = 1; continue
    s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in x['A']]
    al = '639d' in s; print(f, 'sha', sha(s), '(LAMWEB base', x['base'] + ')', 'anchors', *n, 'already', al)
    if al or n != [1] * len(n): bad = 1; continue
    t = s
    for a, b in x['A']: t = t.replace(a, b)
    plan.append((f, p, t))
XA = json.loads(r"""[]""")
if XA and not XP: print('NOTE: this package also patches the web api.php copies (Love Nails ~/lovenails/api.php, ...) - give their paths after the release dir'); bad = 1
for p in XP:
    s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in XA]; al = '639d' in s; print(p, 'sha', sha(s), 'anchors', *n, 'already', al)
    if al or n != [1] * len(n): bad = 1; continue
    t = s
    for a, b in XA: t = t.replace(a, b)
    plan.append((p, p, t))
NEWF = json.loads(r"""{}""")
for f, t in NEWF.items():
    p = f'{R}/{f}'; ex = os.path.exists(p); print('NEW FILE', f, 'exists' if ex else 'ok', sha(t))
    if ex: bad = 1
if bad: sys.exit('STOP: an anchor is not found exactly once, already patched, or a new file is already there - nothing changed')
if not go:
    for f, p, t in plan: print('NEW would be', f, sha(t))
    sys.exit('check only - run again with: go')
bk = os.path.expanduser('~/app/old'); os.makedirs(bk, exist_ok=True); st = time.strftime('%m%d%H%M'); done = []
made = []
def back(msg):
    for q, bb in done: shutil.copy2(bb, q)
    for q in made:
        try: os.remove(q)
        except OSError: pass
    sys.exit('ERROR ' + msg + ' - every file put back, new files removed')
def chk(p):
    c = ['php', '-l', p] if p.endswith('.php') else (['node', '--check', p] if p.endswith('.js') and shutil.which('node') else None)
    if not c: return
    r = subprocess.run(c, capture_output=True, text=True)
    if r.returncode: back('in ' + p + ': ' + (r.stdout + r.stderr)[:300])
for f, p, t in plan:
    b = f'{bk}/' + f.strip('/').replace('/', '__') + f'.pre-639d-{st}'; shutil.copy2(p, b); m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m); done.append((p, b)); chk(p)
    print('NEW', f, sha(t), 'backup', b)
for f, t in NEWF.items():
    p = f'{R}/{f}'; open(p, 'w', encoding='utf-8').write(t); made.append(p); os.chmod(p, 0o644); chk(p); print('MADE', f, sha(t))
print('OK 2.99.639d (QA-0009) - restart php-fpm.')
