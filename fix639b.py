#!/usr/bin/env python3
# LAMWEB 2.99.639b (QA-0011 P1 TIEN/LUONG): REFUND khi tuan luong HOM NAY da dong (dong som / force) -> phan tru cua tho MAT (khong vao tuan sau).
#   Sua: inc/api/checkout.php receipt_refund: tuan hom nay da dong -> hoi truoc (PAYROLL_CLOSED, nhu Void), dong y -> refund + payroll_carry(hom nay)
#   (phan cua tho vao dieu chinh tuan sau, nhu Void / Checkout / sua tip). "Fix service prices" giam gia (= refund) cung payroll_carry.
#   assets/admin/checkout-receipt.js: Refund bat PAYROLL_CLOSED -> hop hoi co san (payClosedAsk) -> gui ok_closed; bao "next week: ...". Tuan mo: nhu cu.
#   Goc = sau 639a.
# Run:  python3 fix639b.py <release dir>   (kiem)   /   ... go
import sys, os, shutil, time, hashlib, json, subprocess
args = [a for a in sys.argv[1:]]
if not args: sys.exit('usage: python3 fix639b.py <release dir> [go]')
go = args[-1] == 'go'
if go: args = args[:-1]
R = args[0].rstrip('/'); XP = [os.path.abspath(a) for a in args[1:]]
def sha(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
F = json.loads(r"""{"inc/api/checkout.php": {"base": "5e392ea9", "new": "52168dca", "A": [["    if ($action === 'receipt_void' && payroll_week_closed((string)$r['day']) && empty($in['ok_closed'])) fail('PAYROLL_CLOSED', 409);", "    if ($action === 'receipt_void' && payroll_week_closed((string)$r['day']) && empty($in['ok_closed'])) fail('PAYROLL_CLOSED', 409);\n    if ($action === 'receipt_refund' && payroll_week_closed(date('Y-m-d')) && empty($in['ok_closed'])) fail('PAYROLL_CLOSED', 409); // (2.99.639b QA-0011) a refund counts in TODAY's week: closed -> asked first, like Void"], ["        else $rf = receipt_refund($r, (float)($in['amount'] ?? 0), (string)($in['how'] ?? ''), $reason, $in['techs'] ?? null); // a refund counts in the week it is made", "        else $rf = receipt_refund($r, (float)($in['amount'] ?? 0), (string)($in['how'] ?? ''), $reason, $in['techs'] ?? null); // a refund counts in the week it is made\n        if ($action === 'receipt_refund') $carry = payroll_carry(date('Y-m-d'), 'Receipt #' . $r['rno'] . ' refund \u2013 ' . $reason); // (2.99.639b QA-0011) today's week closed early: the techs' part goes into next week (as Void / Checkout / tips)"], ["    try { $x = receipt_money_edit($r, $in); if (db()->inTransaction()) db()->commit(); }", "    try { $x = receipt_money_edit($r, $in); if ((float)(receipt_get((int)$r['id'])['refund'] ?? 0) > (float)$r['refund'] + 0.004) $x['carry'] = payroll_carry(date('Y-m-d'), 'Receipt #' . $r['rno'] . ' price lowered (refund)'); /* (2.99.639b QA-0011) */ if (db()->inTransaction()) db()->commit(); }"]]}, "assets/admin/checkout-receipt.js": {"base": "a1c1ea3b", "new": "0bbfbc1a", "A": [["        try { const y = await api('receipt_refund', { id: r.id, amount: +$('#rfAmt', box).value || 0, how, dps_done: !!$('#dpsDone', box)?.checked, reason: $('#rfWhy', box).value, techs: typed || (prev ? prev.techs.map(t => ({ staff: t.staff, amt: t.amt })) : null) }, null, isP5 && how === 'Card' /* (2.99.638d) the customer taps the card on the P5 */);\n          done(y, y.refund && y.refund.gift ? `Refund saved \u00b7 gift card ${y.refund.gift}` : 'Refund saved'); }\n        catch (x2) { e.target.disabled = false; const er = $('.err', box); er.textContent = x2.message; er.hidden = false; }\n", "        const goRf = async (okc) => { const y = await api('receipt_refund', { id: r.id, amount: +$('#rfAmt', box).value || 0, how, dps_done: !!$('#dpsDone', box)?.checked, reason: $('#rfWhy', box).value, ok_closed: okc, techs: typed || (prev ? prev.techs.map(t => ({ staff: t.staff, amt: t.amt })) : null) }, null, isP5 && how === 'Card' /* (2.99.638d) the customer taps the card on the P5 */); /* (2.99.639b QA-0011) */\n          done(y, (y.refund && y.refund.gift ? `Refund saved \u00b7 gift card ${y.refund.gift}` : 'Refund saved') + carryTxt(y.carry)); };\n        try { await goRf(false); }\n        catch (x2) { if (x2.message === 'PAYROLL_CLOSED') return payClosedAsk(box, () => goRf(true).catch(oops)); e.target.disabled = false; const er = $('.err', box); er.textContent = x2.message; er.hidden = false; }\n"]]}}""")
plan = []; bad = 0
for f, x in F.items():
    p = f'{R}/{f}'
    if not os.path.isfile(p): print(f, 'MISSING'); bad = 1; continue
    s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in x['A']]
    al = '2.99.639b' in s; print(f, 'sha', sha(s), '(LAMWEB base', x['base'] + ')', 'anchors', *n, 'already', al)
    if al or n != [1] * len(n): bad = 1; continue
    t = s
    for a, b in x['A']: t = t.replace(a, b)
    plan.append((f, p, t))
XA = json.loads(r"""[]""")
if XA and not XP: print('NOTE: this package also patches the web api.php copies (Love Nails ~/lovenails/api.php, ...) - give their paths after the release dir'); bad = 1
for p in XP:
    s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in XA]; al = '2.99.639b' in s; print(p, 'sha', sha(s), 'anchors', *n, 'already', al)
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
    b = f'{bk}/' + f.strip('/').replace('/', '__') + f'.pre-639b-{st}'; shutil.copy2(p, b); m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m); done.append((p, b)); chk(p)
    print('NEW', f, sha(t), 'backup', b)
for f, t in NEWF.items():
    p = f'{R}/{f}'; open(p, 'w', encoding='utf-8').write(t); made.append(p); os.chmod(p, 0o644); chk(p); print('MADE', f, sha(t))
print('OK 2.99.639b (QA-0011) - restart php-fpm.')
