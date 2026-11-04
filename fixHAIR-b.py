#!/usr/bin/env python3
# CHAT 03/11 (anh Logan 21:10 "HAIR DEMO RECOVERY"): CHI demo.hair (thu muc hair). Goc = sau fixHAIR-ui + fixHAIR-chu.
#  1. Nguyen nhan that (tai hien): dang nhap app tho (hoac manager) trong CUNG trinh duyet voi trang chu tiem -> server doi CSRF -> moi lenh
#     LUU cua trang chu tiem tra 403 "Session expired" (book_check / luu hen...), xem lich van chay. Sua: staff_login / staff_setup / invite /
#     manager login GIU CSRF dang co (inc/api/staffpages.php x3, inc/api/auth.php x1).
#  2. Trang chu tiem: gap 403 "Session expired" -> tu lay CSRF moi (me) va gui lai 1 lan (server tu choi TRUOC khi lam gi -> khong trung, khong mat).
#     (assets/admin-core.js, 1 cho trong api()). Het phien that (401) -> man hinh dang nhap nhu cu.
#  3. Chu: YOUR TURN -> YOUR CLIENT (hair khong co luot) trong assets/hair-words.js.
# Run: python3 fixHAIR-b.py <thu muc hair> [go]
import sys, os, shutil, time, hashlib, subprocess
a = sys.argv[1:]; R = a[0].rstrip('/'); go = len(a) > 1 and a[1] == 'go'
sha = lambda t: hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
if not os.path.isfile(R + '/inc/hair.php') or not os.path.isfile(R + '/assets/hair-ui.js'): sys.exit('STOP: not the hair site after fixHAIR-ui')
K = "$_SESSION['csrf'] = bin2hex(random_bytes(16));"
KN = "$_SESSION['csrf'] = $_SESSION['csrf'] ?? bin2hex(random_bytes(16)); /* (hair-b CHAT 03/11) keep the owner page's token in the same browser */"
MG = "$_SESSION['mgr_seen'] = time(); " + K
API_A = "  if (!res.ok || data.error) throw new Error(data.error || ('Error ' + res.status));\n"
API_B = ("  if (res.status === 403 && body && !IS_DESK && !api.csrfRetry && /Session expired/.test(String(data.error || ''))) { /* (hair-b CHAT 03/11) the token changed in this browser (a stylist / manager logged in here): get it again, send once more – the server refused BEFORE doing anything */\n"
         "    api.csrfRetry = 1; try { const m = await api('me'); if (m && m.csrf) { S.csrf = m.csrf; return await api(action, body, params, keepalive); } } finally { api.csrfRetry = 0; } }\n" + API_A)
HW_A = "    [/with a hands service/g, 'with a hair service'], [/, the turn line,/g, ','],\n"
HW_B = HW_A + "    [/\\bYOUR TURN\\b/g, 'YOUR CLIENT'], [/\\bYour turn\\b/g, 'Your client'], [/\\byour turn\\b/g, 'your client'], /* (hair-b CHAT 03/11) no turns in a hair salon */\n"
HW_T_A = "|hands service|turn line|móng/"
HW_T_B = "|hands service|turn line|móng|[Yy]our turn|YOUR TURN/"
F = {
 'inc/api/staffpages.php': [(K, KN, 3)],
 'inc/api/auth.php': [(MG, "$_SESSION['mgr_seen'] = time(); " + KN, 1)],
 'assets/admin-core.js': [(API_A, API_B, 1)],
 'assets/hair-words.js': [(HW_A, HW_B, 1), (HW_T_A, HW_T_B, 1)],
}
plan = []; bad = 0
for f, reps in F.items():
    p = f'{R}/{f}'; s = open(p, encoding='utf-8').read(); al = 'hair-b CHAT 03/11' in s
    n = [s.count(x) for x, _, _ in reps]; print(f, 'sha', sha(s), 'anchors', n, 'already', al)
    if al or n != [c for _, _, c in reps]: bad = 1; continue
    t = s
    for x, y, _ in reps: t = t.replace(x, y)
    plan.append((f, p, t))
if bad: sys.exit('STOP: anchor not found / already done - nothing changed')
if not go:
    for f, p, t in plan: print('would be', f, sha(t))
    sys.exit('check only - run again with: go')
bk = f'{R}/inc/old-hairb-' + time.strftime('%m%d%H%M'); os.makedirs(bk, exist_ok=True); done = []
for f, p, t in plan:
    b = bk + '/' + f.replace('/', '__'); shutil.copy2(p, b); m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m); done.append((p, b))
    c = ['php', '-l', p] if p.endswith('.php') else (['node', '--check', p] if shutil.which('node') else None)
    if c:
        r = subprocess.run(c, capture_output=True, text=True)
        if r.returncode:
            for q, bb in done: shutil.copy2(bb, q)
            sys.exit('ERROR ' + p + ' ' + (r.stdout + r.stderr)[:300] + ' - every file put back')
    print('NEW', f, sha(t))
print('OK hair-b. Backups:', bk)
