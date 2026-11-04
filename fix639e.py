#!/usr/bin/env python3
# fix639e.py - QA-0015 (P1): the AI phone offered and BOOKED a service with no price yet (hidden online since 636).
# Now one list cl_services() = active services minus svc_noprice_ids(), used by every AI phone service list (menu, words, guess, book). 4 files.
# Run:  python3 fix639e.py <release dir>   (kiem)   /   ... go
import sys, os, shutil, time, hashlib, json, subprocess
args = [a for a in sys.argv[1:]]
if not args: sys.exit('usage: python3 fix639e.py <release dir> [go]')
go = args[-1] == 'go'
if go: args = args[:-1]
R = args[0].rstrip('/'); XP = [os.path.abspath(a) for a in args[1:]]
def sha(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
F = json.loads(r"""{"inc/calls.php": {"base": "e22d99d1", "new": "8c9e3300", "A": [["function cl_on(): bool { return setting('call_on') === '1'; }\n", "function cl_on(): bool { return setting('call_on') === '1'; }\n/** (2.99.639e QA-0015) the services the AI phone may offer / book: the active ones WITHOUT the no-price ones (hidden online since 636 - svc_noprice_ids). */\nfunction cl_services(): array { if (!function_exists('svc_noprice_ids')) require_once __DIR__ . '/svc-tpl.php'; $no = svc_noprice_ids(); return array_values(array_filter(service_list(true), fn($s) => !in_array((int)$s['id'], $no, true))); }\n"]]}, "inc/calls-agent.php": {"base": "0847825d", "new": "cd72a2ed", "A": [["    foreach (service_list(true) as $s) { $who = array_values(array_map(fn($t) => (string)$t['name'], array_filter($staff, fn($t) => staff_can_do($t, [(int)$s['id']]))));", "    foreach (cl_services() as $s) { $who = array_values(array_map(fn($t) => (string)$t['name'], array_filter($staff, fn($t) => staff_can_do($t, [(int)$s['id']])))); /* 639e */"]]}, "inc/calls-ivr.php": {"base": "7994fd92", "new": "440c067b", "A": [["    try { foreach (service_list(true) as $sv) { $n = trim((string)preg_replace('/[^\\p{L}\\p{N} &\\'\\-]+/u', ' ', (string)$sv['name'])); $n = trim((string)preg_replace('/\\s+/', ' ', $n)); if ($n !== '') $h[] = mb_substr($n, 0, 100); } } catch (Throwable $e) {}", "    try { foreach (cl_services() as $sv) { $n = trim((string)preg_replace('/[^\\p{L}\\p{N} &\\'\\-]+/u', ' ', (string)$sv['name'])); $n = trim((string)preg_replace('/\\s+/', ' ', $n)); if ($n !== '') $h[] = mb_substr($n, 0, 100); } } catch (Throwable $e) {} /* 639e */"], ["    try { foreach (service_list(true) as $sv) { $k = trim(strtolower((string)preg_replace('/[^a-z0-9]+/i', ' ', (string)$sv['name']))); if (strlen($k) >= 3 && str_contains($n, ' ' . $k . ' ')) return true; } } catch (Throwable $e) {}", "    try { foreach (cl_services() as $sv) { $k = trim(strtolower((string)preg_replace('/[^a-z0-9]+/i', ' ', (string)$sv['name']))); if (strlen($k) >= 3 && str_contains($n, ' ' . $k . ' ')) return true; } } catch (Throwable $e) {} /* 639e */"], ["    $act = []; foreach (service_list(true) as $s) $act[(int)$s['id']] = $s; $info = svc_info();", "    $act = []; foreach (cl_services() as $s) $act[(int)$s['id']] = $s; $info = svc_info(); /* 639e */"]]}, "inc/calls-job.php": {"base": "687fa175", "new": "5383a20e", "A": [["    $sv = array_slice(array_map(fn($s) => (string)$s['name'], service_list(true)), 0, 60); $tn = array_map(fn($s) => (string)$s['name'], staff_list(true));", "    $sv = array_slice(array_map(fn($s) => (string)$s['name'], cl_services()), 0, 60); $tn = array_map(fn($s) => (string)$s['name'], staff_list(true)); /* 639e */"], ["    $svc = array_map(fn($s) => (int)$s['id'] . ': ' . $s['name'] . ' (' . (int)$s['duration'] . ' min)', service_list(true));", "    $svc = array_map(fn($s) => (int)$s['id'] . ': ' . $s['name'] . ' (' . (int)$s['duration'] . ' min)', cl_services()); /* 639e */"], ["    $info = svc_info(); $main = array_values(array_filter(service_list(true), fn($s) => !svc_is_addon($s, $info)));", "    $info = svc_info(); $main = array_values(array_filter(cl_services(), fn($s) => !svc_is_addon($s, $info))); /* 639e */"], ["    $act = []; foreach (service_list(true) as $s) $act[(int)$s['id']] = $s;\n    $sids = array_values(array_unique(array_filter(array_map('intval', (array)($j['service_ids'] ?? [])), fn($i) => isset($act[$i]))));", "    $act = []; foreach (cl_services() as $s) $act[(int)$s['id']] = $s; /* 639e */\n    $sids = array_values(array_unique(array_filter(array_map('intval', (array)($j['service_ids'] ?? [])), fn($i) => isset($act[$i]))));"], ["    $act = []; foreach (service_list(true) as $s) $act[(int)$s['id']] = $s;\n    $info = svc_info();", "    $act = []; foreach (cl_services() as $s) $act[(int)$s['id']] = $s; /* 639e */\n    $info = svc_info();"], ["    $act = []; foreach (service_list(true) as $s) $act[(int)$s['id']] = $s;\n    $pool = []; $names = [];", "    $act = []; foreach (cl_services() as $s) $act[(int)$s['id']] = $s; /* 639e */\n    $pool = []; $names = [];"], ["    $act = []; foreach (service_list(true) as $s) $act[(int)$s['id']] = $s; $info = svc_info();", "    $act = []; foreach (cl_services() as $s) $act[(int)$s['id']] = $s; $info = svc_info(); /* 639e */"]]}, "inc/calls-ask.php": {"base": "8ab96b73", "new": "42a1ff50", "A": [["    $main = array_values(array_filter(service_list(true), fn($s) => !cla_addon($s)));", "    $main = array_values(array_filter((function_exists('cl_services') ? cl_services() : service_list(true)), fn($s) => !cla_addon($s))); /* 639e */"]]}, "inc/calls-talk.php": {"base": "148b2a33", "new": "57fa38c9", "A": [["    foreach (service_list(true) as $s) { $who = array_values(array_map(fn($t) => (string)$t['name'], array_filter($staff, fn($t) => staff_can_do($t, [(int)$s['id']]))));", "    foreach ((function_exists('cl_services') ? cl_services() : service_list(true)) as $s) { $who = array_values(array_map(fn($t) => (string)$t['name'], array_filter($staff, fn($t) => staff_can_do($t, [(int)$s['id']])))); /* 639e */"]]}}""")
plan = []; bad = 0
for f, x in F.items():
    p = f'{R}/{f}'
    if not os.path.isfile(p): print(f, 'MISSING'); bad = 1; continue
    s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in x['A']]
    al = '639e' in s; print(f, 'sha', sha(s), '(LAMWEB base', x['base'] + ')', 'anchors', *n, 'already', al)
    if al or n != [1] * len(n): bad = 1; continue
    t = s
    for a, b in x['A']: t = t.replace(a, b)
    plan.append((f, p, t))
XA = json.loads(r"""[]""")
if XA and not XP: print('NOTE: this package also patches the web api.php copies (Love Nails ~/lovenails/api.php, ...) - give their paths after the release dir'); bad = 1
for p in XP:
    s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in XA]; al = '639e' in s; print(p, 'sha', sha(s), 'anchors', *n, 'already', al)
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
    b = f'{bk}/' + f.strip('/').replace('/', '__') + f'.pre-639e-{st}'; shutil.copy2(p, b); m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m); done.append((p, b)); chk(p)
    print('NEW', f, sha(t), 'backup', b)
for f, t in NEWF.items():
    p = f'{R}/{f}'; open(p, 'w', encoding='utf-8').write(t); made.append(p); os.chmod(p, 0o644); chk(p); print('MADE', f, sha(t))
print('OK 2.99.639e (QA-0015) - restart php-fpm.')
