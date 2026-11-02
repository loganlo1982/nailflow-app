#!/usr/bin/env python3
# LAMWEB 2.99.620 = LENH-620 (anh Logan 01/11 23:13): step 5 "Book now" / "Reservar" button bigger: 29px (26px on short screens <= 700px), weight 800, min 64px, one line.
#  Only that button on step 5 (class go-book set by book-2.js); Next of steps 2-4, colours, Booking..., deposit / PayPal: unchanged.
#  CHANGED: assets/book-2.js (1 line), assets/book-2.css (appended). AN public_html: nothing (its index.php loads the same assets; ?v= = APP_VERSION).
# Run (in the app folder):  python3 fix620.py <app dir>  /  python3 fix620.py <app dir> go
import sys, os, shutil, time, hashlib, json, subprocess
R = sys.argv[1].rstrip('/'); go = len(sys.argv) > 2 and sys.argv[2] == 'go'
def sha(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
F = json.loads(r'''{"assets/book-2.js": {"base": "7b37cfc3", "new": "d1e17602", "A": [["link \u2013 Messages opens with no question)\n  act.hidden = !label; go.hidden = !label || combo; go.textContent = label; go.disabled = !enabled; go.classList.toggle('lit', s === 3 && enabled); go.classList.toggle('tech-dis', techDis); go.toggleAttribute('aria-disabled', techDis || go.classList.contains('soft-dis'));\n  let pk = $('#bPick'); if (!pk) { go.in", "link \u2013 Messages opens with no question)\n  act.hidden = !label; go.hidden = !label || combo; go.textContent = label; go.disabled = !enabled; go.classList.toggle('lit', s === 3 && enabled); go.classList.toggle('tech-dis', techDis); go.classList.toggle('go-book', s === 5 && !st.done && !depNeeded()); /* (2.99.620 - LENH 620) step 5 \"Book now\": big letters (CSS) */ go.toggleAttribute('aria-disabled', techDis || go.classList.contains('soft-dis'));\n  let pk = $('#bPick'); if (!pk) { go.in"]]}, "assets/book-2.css": {"base": "f48efd54", "new": "67098d0d", "A": [[".pc-yes2{min-height:56px;padding:12px}}\n", ".pc-yes2{min-height:56px;padding:12px}}\n/* (2.99.620 - LENH 620, anh Logan 01/11 23:13) step 5 \"\u2705 Book now\" / \"\u2705 Reservar\" only: bigger, bolder, one line (colors, shadow, disabled, Booking\u2026 unchanged) */\n.act button#bGo.go-book{font-size:29px;font-weight:800;min-height:64px;white-space:nowrap;letter-spacing:0}\n@media(max-height:700px){.act button#bGo.go-book{font-size:26px}}\n"]]}}''')
NEWF = json.loads(r'''{}''')
plan = []; bad = 0
for f, x in F.items():
    p = f'{R}/{f}'; s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in x['A']]
    al = '2.99.620' in s; print(f, 'sha', sha(s), '(LAMWEB base', x['base'] + ')', 'anchors', *n, 'already', al)
    if al or n != [1] * len(n): bad = 1; continue
    t = s
    for a, b in x['A']: t = t.replace(a, b)
    plan.append((f, p, t))
for f, t in NEWF.items():
    p = f'{R}/{f}'; ex = os.path.exists(p); print('NEW', f, 'exists' if ex else 'ok', sha(t))
    if ex: bad = 1
if bad: sys.exit('STOP: an anchor is not found exactly once, already patched, or a new file is already there - nothing changed')
if not go:
    for f, p, t in plan: print('NEW would be', f, sha(t))
    sys.exit('check only - run again with: go')
bk = os.path.expanduser('~/app/old'); os.makedirs(bk, exist_ok=True); st = time.strftime('%m%d%H%M'); done = []; made = []
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
    b = f'{bk}/' + f.replace('/', '__') + f'.pre-620-{st}'; shutil.copy2(p, b); m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m); done.append((p, b)); chk(p)
    print('NEW', f, sha(t), 'backup', b)
for f, t in NEWF.items():
    p = f'{R}/{f}'
    open(p, 'w', encoding='utf-8').write(t); made.append(p)
    os.chmod(p, 0o644)
    chk(p); print('MADE', f, sha(t))
print('OK 2.99.620 (Book now bigger) - set APP_VERSION 2.99.620 (core.php: the ?v= of the assets), restart php-fpm. Nothing in the AN public_html copies.')
