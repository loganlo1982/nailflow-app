#!/usr/bin/env python3
# CHAT 01/11 16:30 - LENH 608 (anh Logan: "khi chu login thi vao trang Home"): the owner's app opens on Home page 1 after login / opening the app.
#  assets/admin/boot.js: the default start was setTab('appts') (Home only for a new salon, me.gs). Now: owner (not manager, not desk) -> Home page 1.
#  Unchanged: links / notifications (openFromUrl), reload keeps the page (nfBackTab), manager, desk, check-in iPad, tech.
# python3 fix608.py <release dir> [go] [sim]   (sim = do not touch public_html)
import sys, os, shutil, time, subprocess, hashlib
R = sys.argv[1].rstrip('/'); go = 'go' in sys.argv[2:]; sim = 'sim' in sys.argv[2:]
OLD = "else { setTab('appts'); if (me.gs) goHome(); } }"
NEW = "else { setTab('appts'); if (me.gs || (!IS_MGR && !IS_DESK)) { S.hmPage = 0; goHome(); } } } /* (CHAT 01/11 2.99.608 - LENH 608) the owner opens on Home page 1 */"
fs = [R + '/assets/admin/boot.js']
P = '/home/uyurpyzubx0m/public_html/assets/admin/boot.js'
if not sim and os.path.isfile(P) and os.path.realpath(P) != os.path.realpath(fs[0]): fs.append(P)
for f in fs:
    t = open(f, encoding='utf-8').read(); print(f, hashlib.sha256(t.encode()).hexdigest()[:8], 'anchor', t.count(OLD))
    if t.count(OLD) != 1: sys.exit('ANCHOR FAIL')
if not go: print('check only'); sys.exit()
od = os.path.expanduser('~/app/old'); os.makedirs(od, exist_ok=True); st = time.strftime('%m%d%H%M')
for i, f in enumerate(fs):
    b = od + '/assets__admin__boot.js.' + str(i) + '.pre-608-' + st; shutil.copy2(f, b)
    n = open(f, encoding='utf-8').read().replace(OLD, NEW); open(f, 'w', encoding='utf-8').write(n)
    if shutil.which('node'):
        r = subprocess.run(['node', '--check', f], capture_output=True, text=True)
        if r.returncode: shutil.copy2(b, f); sys.exit('JS FAIL - put back ' + f + r.stdout + r.stderr)
    print('OK', f, hashlib.sha256(n.encode()).hexdigest()[:8], 'backup', b)
