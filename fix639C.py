#!/usr/bin/env python3
# CHAT 2.99.639C (anh Logan 03/11 21:49 "cai nao em giup duoc thi lam"): QA-0022 + QA-0023. Goc = LIVE sau 639a + 638h + 639b.
#  QA-0022: lich admin / khoa PIN quay dung ngay theo mui gio CO DINH Chicago -> tiem o mui gio khac mo sai ngay. Nay: 'me' + 'desk_info' gui mui gio
#           cua tiem (setting timezone); localToday() dung mui gio do (chua co -> Chicago nhu cu). AN / Love Nails (Chicago): KHONG doi gi.
#  QA-0023a: Refund: nut Refund khoa trong luc xem truoc (refund_preview) dang chay -> khong gui phan chia tho cu.
#  QA-0023b: The qua tang "Save balance" / "Void this card": khoa nut khi dang gui (khong bao 2 lan).
#  QA-0023c: Settings -> Services: o "Counts as a main service" khong co data-i -> TypeError console. Chi gan cho input[data-i].
# Run: python3 fix639C.py <release> [go]
import sys, os, shutil, time, hashlib, subprocess
a = sys.argv[1:]; R = a[0].rstrip('/'); go = len(a) > 1 and a[1] == 'go'
sha = lambda t: hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
T = '(2.99.639C'
F = {
 'inc/api/auth.php': [("'salon' => setting('salon_name'), 'smsBrand' => sms_brand_name(),",
                       "'salon' => setting('salon_name'), 'smsBrand' => sms_brand_name(), 'tz' => (string)(setting('timezone') ?: 'America/Chicago') /* (2.99.639C QA-0022) the salon's own day on the screens */,")],
 'inc/api/desk.php': [("json_out(['salon' => setting('salon_name'), 'smsBrand' => sms_brand_name(),",
                       "json_out(['salon' => setting('salon_name'), 'smsBrand' => sms_brand_name(), 'tz' => (string)(setting('timezone') ?: 'America/Chicago') /* (2.99.639C QA-0022) */,")],
 'assets/admin-core.js': [("{ timeZone: 'America/Chicago' }).slice(0, 10)", "{ timeZone: window.SALON_TZ || 'America/Chicago' /* (2.99.639C QA-0022) the salon's time zone from the server */ }).slice(0, 10)")],
 'assets/admin/boot.js': [("  S.today = S.today || localToday(); S.date = S.date || S.today;",
                           "  try { if (me && me.tz) window.SALON_TZ = me.tz; } catch (e) {} /* (2.99.639C QA-0022) */\n  S.today = S.today || localToday(); S.date = S.date || S.today;")],
 'assets/admin/desk.js': [("  try { DK.info = await api('desk_info', null, dkK()); } catch (e) {",
                           "  try { DK.info = await api('desk_info', null, dkK()); if (DK.info && DK.info.tz) window.SALON_TZ = DK.info.tz; /* (2.99.639C QA-0022) */ } catch (e) {")],
 'assets/admin/checkout-receipt.js': [("      const preview = async () => {\n", "      const previewIn = async () => {\n"),
     ("      };\n      $('#rfAmt', box).addEventListener('input'",
      "      };\n      const preview = async () => { /* (2.99.639C QA-0023a) Refund waits for the newest preview */ const seq = (box._pv = (box._pv || 0) + 1); const yb = $('[data-yes]', box); if (yb) yb.disabled = true; try { await previewIn(); } finally { if (seq === box._pv && yb) yb.disabled = false; } };\n      $('#rfAmt', box).addEventListener('input'")],
 'assets/admin/settings-texts.js': [("      on('adjsave', async () => { try {", "      on('adjsave', async (ev) => { const bt = ev.currentTarget; if (bt.disabled) return; bt.disabled = true; /* (2.99.639C QA-0023b) */ try {"),
     ("      on('voidgo', async () => { try {", "      on('voidgo', async (ev) => { const bt = ev.currentTarget; if (bt.disabled) return; bt.disabled = true; /* (2.99.639C QA-0023b) */ try {"),
     ("show(box, r.card, true); saved(); } catch (e) { oops(e); } });", "show(box, r.card, true); saved(); } catch (e) { oops(e); } finally { bt.disabled = false; } });"),
     ("show(box, r.card, true); toast('Gift card voided'); } catch (e) { oops(e); } });", "show(box, r.card, true); toast('Gift card voided'); } catch (e) { oops(e); } finally { bt.disabled = false; } });")],
 'assets/admin/settings-salon.js': [("$$('#svList input', b).forEach(inp =>", "$$('#svList input[data-i]', b).forEach(inp => /* (2.99.639C QA-0023c) */")],
}
plan = []; bad = 0
for f, reps in F.items():
    p = f'{R}/{f}'
    if not os.path.isfile(p): print(f, 'MISSING'); bad = 1; continue
    s = open(p, encoding='utf-8').read(); al = T in s; n = [s.count(x) for x, _ in reps]; print(f, 'sha', sha(s), 'anchors', n, 'already', al)
    if al or n != [1] * len(reps): bad = 1; continue
    t = s
    for x, y in reps: t = t.replace(x, y)
    plan.append((f, p, t))
if bad: sys.exit('STOP: anchor not found / already done - nothing changed')
if not go:
    for f, p, t in plan: print('would be', f, sha(t))
    sys.exit('check only - run again with: go')
bk = os.path.expanduser('~/app/old'); os.makedirs(bk, exist_ok=True); st = time.strftime('%m%d%H%M'); done = []
for f, p, t in plan:
    b = f'{bk}/' + f.replace('/', '__') + f'.pre-639C-{st}'; shutil.copy2(p, b); m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m); done.append((p, b))
    c = ['php', '-l', p] if p.endswith('.php') else (['node', '--check', p] if shutil.which('node') else None)
    if c:
        r = subprocess.run(c, capture_output=True, text=True)
        if r.returncode:
            for q, bb in done: shutil.copy2(bb, q)
            sys.exit('ERROR ' + p + ' ' + (r.stdout + r.stderr)[:300] + ' - every file put back')
    print('NEW', f, sha(t), 'backup', b)
print('OK 2.99.639C (QA-0022 + QA-0023) - restart php-fpm.')
