#!/usr/bin/env python3
# fix639c.py - QA-0021 (P1): walk-in / booking form (book-form.js) tapped twice -> 2 appointments. Now one save at a time + the once key
# (the server already books a once key only once, inc/api/appts.php). 1 file, no screen change. Base: LIVE 637 + 638a..h + 639a + 639b.
# Run:  python3 fix639c.py <release dir>   (kiem)   /   ... go
import sys, os, shutil, time, hashlib, json, subprocess
args = [a for a in sys.argv[1:]]
if not args: sys.exit('usage: python3 fix639c.py <release dir> [go]')
go = args[-1] == 'go'
if go: args = args[:-1]
R = args[0].rstrip('/'); XP = [os.path.abspath(a) for a in args[1:]]
def sha(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
F = json.loads(r"""{"assets/admin/book-form.js": {"base": "95f2b86d", "new": "480778e1", "A": [["bday: '', walkin: !!o.walkin, cust: null, sendText: true, agree: null, step: 0,", "bday: '', walkin: !!o.walkin, cust: null, sendText: true, agree: null, step: 0, once: Math.random().toString(36).slice(2) + Date.now().toString(36) /* (2.99.639c QA-0021) one key per form: the server books it once */, busy: false,"], ["try {\nconst grp = W.people.length > 1 ? { svcs:", "if (W.busy) return; /* (2.99.639c QA-0021) tapped twice: the 2nd tap waits for the 1st */\nW.busy = true;\ntry {\nconst grp = W.people.length > 1 ? { svcs:"], ["send_confirm: !!(smsOk && !W.walkin), force: !!force, ref_phone:", "send_confirm: !!(smsOk && !W.walkin), force: !!force, once: W.once /* 639c */, ref_phone:"], ["catch (e) {\nmsg.innerHTML = `<p class=\"err\">${esc(e.message)}</p>`;\n}\n};\n$('#wSave', sh).addEventListener('click', () => save(false));", "catch (e) {\nmsg.innerHTML = `<p class=\"err\">${esc(e.message)}</p>`;\n}\nfinally {\nW.busy = false; /* 639c */\n}\n};\n$('#wSave', sh).addEventListener('click', () => save(false));"]]}}""")
plan = []; bad = 0
for f, x in F.items():
    p = f'{R}/{f}'
    if not os.path.isfile(p): print(f, 'MISSING'); bad = 1; continue
    s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in x['A']]
    al = '639c' in s; print(f, 'sha', sha(s), '(LAMWEB base', x['base'] + ')', 'anchors', *n, 'already', al)
    if al or n != [1] * len(n): bad = 1; continue
    t = s
    for a, b in x['A']: t = t.replace(a, b)
    plan.append((f, p, t))
XA = json.loads(r"""[]""")
if XA and not XP: print('NOTE: this package also patches the web api.php copies (Love Nails ~/lovenails/api.php, ...) - give their paths after the release dir'); bad = 1
for p in XP:
    s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in XA]; al = '639c' in s; print(p, 'sha', sha(s), 'anchors', *n, 'already', al)
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
    b = f'{bk}/' + f.strip('/').replace('/', '__') + f'.pre-639c-{st}'; shutil.copy2(p, b); m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m); done.append((p, b)); chk(p)
    print('NEW', f, sha(t), 'backup', b)
for f, t in NEWF.items():
    p = f'{R}/{f}'; open(p, 'w', encoding='utf-8').write(t); made.append(p); os.chmod(p, 0o644); chk(p); print('MADE', f, sha(t))
print('OK 2.99.639c (QA-0021) - no restart needed (JS); reload the pages.')
