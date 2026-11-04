#!/usr/bin/env python3
# LAMWEB 2.99.638d (LENH-638 A): Void / Refund hoa don tra bang may P5 -> may P5 TU tra tien ve the (khong tick "Done on DPS").
#   Void: P5 Void tung giao dich P5 (cung ngay, truoc settle); P5 tu choi vi batch da dong -> Return (khach cham the lai). Refund 1 phan = Return; refund het
#   cung batch = Void (khong can the). P5 khong duyet -> fail, hoa don KHONG doi. Lam lai sau khi do dang -> bo qua phan P5 da tra. Hoa don the thuong (DPS) nhu cu.
#   File moi inc/dejavoo-back.php; sua inc/api/checkout.php (receipt_void / receipt_refund) + assets/admin/checkout-receipt.js (o "tu tra ve P5", cho toi 2 phut).
#   Goc = sau 638c.
# Run:  python3 fix638d.py <release dir>   (kiem)   /   ... go
import sys, os, shutil, time, hashlib, json, subprocess
args = [a for a in sys.argv[1:]]
if not args: sys.exit('usage: python3 fix638d.py <release dir> [go]')
go = args[-1] == 'go'
if go: args = args[:-1]
R = args[0].rstrip('/'); XP = [os.path.abspath(a) for a in args[1:]]
def sha(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
F = json.loads(r"""{"inc/api/checkout.php": {"base": "153dc1ab", "new": "87e8753a", "A": [["    [$ctips, $ctipSum] = tips_parse($in['cash_tips'] ?? [], $staff, 'cash', $in['cash_tip_total'] ?? null);", "    [$ctips, $ctipSum] = tips_parse($in['cash_tips'] ?? [], $staff, 'cash', $in['cash_tip_total'] ?? null);\n    if (abs($tipSum - (float)$r['tip']) >= 0.005) { require_once APP_ROOT . '/inc/dejavoo-back.php'; if (dv_receipt_p5($r)) fail('This receipt was paid on the P5: its card tip cannot be changed here (the P5 would not match). Put the difference as a cash tip, or Void the receipt and pay again.'); } // (2.99.638d)"], ["    if ($cardBack > 0.004 && empty($in['dps_done'])) fail('Refund ' . usd($cardBack) . ' on the DPS machine first, then tick \"Done on DPS\".');", "    require_once APP_ROOT . '/inc/dejavoo-back.php'; $dvP5 = $cardBack > 0.004 ? dv_receipt_p5($r) : []; // (2.99.638d) paid on the P5: the P5 gives it back by itself (below)\n    if ($cardBack > 0.004 && empty($in['dps_done']) && !$dvP5) fail('Refund ' . usd($cardBack) . ' on the DPS machine first, then tick \"Done on DPS\".');"], ["    if ($cardBack > 0.004) $reason .= ' \u00b7 ' . usd($cardBack) . ' back on DPS \u2713';", "    if ($cardBack > 0.004 && !$dvP5) /* (2.99.638d) */ $reason .= ' \u00b7 ' . usd($cardBack) . ' back on DPS \u2713';"], ["    db()->beginTransaction(); // (2.99.92) all or nothing: a problem half-way changes nothing (the money, the techs' parts, the gift card, the rewards)", "    if ($dvP5) { dv_money_back($r, $action, $cardBack); $reason .= ' \u00b7 ' . usd($cardBack) . ' back on the P5 \u2713'; } // (2.99.638d) after every check above, before anything is saved: the P5 says no -> nothing changes\n    db()->beginTransaction(); // (2.99.92) all or nothing: a problem half-way changes nothing (the money, the techs' parts, the gift card, the rewards)"]]}, "assets/admin/checkout-receipt.js": {"base": "0420cc68", "new": "a1c1ea3b", "A": [["    const dpsBox = (amt) => amt > 0.004 ? `<div class=\"dps-back\"><b>Refund ${money(amt)} on the DPS machine now</b><label class=\"check\"><input type=\"checkbox\" id=\"dpsDone\"><span>Done on DPS</span></label></div>` : '';", "    const isP5 = (r.pays || []).some(p => p.m === 'Card' && p.dv); /* (2.99.638d) paid on the Dejavoo P5: it gives the money back by itself */\n    const dpsBox = (amt) => amt > 0.004 ? (isP5 ? `<div class=\"dps-back\"><b>${money(amt)} ${LV('goes back to the card on the P5 by itself (a refund: the customer taps the card on the P5)', 't\u1ef1 tr\u1ea3 v\u1ec1 th\u1ebb qua m\u00e1y P5 (ho\u00e0n 1 ph\u1ea7n: kh\u00e1ch ch\u1ea1m th\u1ebb l\u1ea1i tr\u00ean P5)')}</b><input type=\"checkbox\" id=\"dpsDone\" checked hidden></div>` : `<div class=\"dps-back\"><b>Refund ${money(amt)} on the DPS machine now</b><label class=\"check\"><input type=\"checkbox\" id=\"dpsDone\"><span>Done on DPS</span></label></div>`) : '';"], ["const y = await api('receipt_void', { id: r.id, reason: $('#rcWhy', box).value, ok_closed: okc, dps_done: !!$('#dpsDone', box)?.checked });", "const y = await api('receipt_void', { id: r.id, reason: $('#rcWhy', box).value, ok_closed: okc, dps_done: !!$('#dpsDone', box)?.checked }, null, isP5 /* (2.99.638d) the P5 may take up to 2 minutes */);"], ["techs: typed || (prev ? prev.techs.map(t => ({ staff: t.staff, amt: t.amt })) : null) });", "techs: typed || (prev ? prev.techs.map(t => ({ staff: t.staff, amt: t.amt })) : null) }, null, isP5 && how === 'Card' /* (2.99.638d) the customer taps the card on the P5 */);"]]}}""")
plan = []; bad = 0
for f, x in F.items():
    p = f'{R}/{f}'
    if not os.path.isfile(p): print(f, 'MISSING'); bad = 1; continue
    s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in x['A']]
    al = '2.99.638d' in s; print(f, 'sha', sha(s), '(LAMWEB base', x['base'] + ')', 'anchors', *n, 'already', al)
    if al or n != [1] * len(n): bad = 1; continue
    t = s
    for a, b in x['A']: t = t.replace(a, b)
    plan.append((f, p, t))
XA = json.loads(r"""[]""")
if XA and not XP: print('NOTE: this package also patches the web api.php copies (Love Nails ~/lovenails/api.php, ...) - give their paths after the release dir'); bad = 1
for p in XP:
    s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in XA]; al = '2.99.638d' in s; print(p, 'sha', sha(s), 'anchors', *n, 'already', al)
    if al or n != [1] * len(n): bad = 1; continue
    t = s
    for a, b in XA: t = t.replace(a, b)
    plan.append((p, p, t))
NEWF = json.loads(r"""{"inc/dejavoo-back.php": "<?php\n/* (2.99.638d - LENH-638 A) Void / Refund of a receipt paid on the P5: the money goes back on the P5 BY ITSELF (no \"Done on DPS\" tick). Void = the P5 Void\n   of each P5 payment (same day, before the batch closes); the P5 says no (closed batch) -> Return (the customer taps the card again). A partial refund =\n   Return. Anything the P5 does not approve -> fail: the receipt is NOT changed. A retry after a half-done void skips what the P5 already gave back. */\ndeclare(strict_types=1);\nrequire_once __DIR__ . '/dejavoo-pay.php';\n\nfunction dv_receipt_p5(array $r): array { $o = []; foreach ((json_decode((string)$r['pays'], true) ?: []) as $p) if (($p['m'] ?? '') === 'Card' && !empty($p['dv']['ref'])) $o[] = $p['dv'] + ['pay' => (float)$p['amt']]; return $o; }\nfunction dv_money_back(array $r, string $action, float $cardBack): string {\n    $p5 = dv_receipt_p5($r); if (!$p5) return '';\n    if (!dv_ready()) fail('This receipt was paid on the P5, but the P5 is not set up now \u2013 NailFlow must set it up first. Nothing was changed.', 409);\n    $sum = round(array_sum(array_map(fn($x) => (float)($x['amt'] ?? $x['pay']), $p5)), 2);\n    if (session_status() === PHP_SESSION_ACTIVE) @session_write_close(); ignore_user_abort(true); @set_time_limit(DV_WAIT + 90);\n    $wait = max(1, min(DV_WAIT, (int)(cfg()['dv_wait'] ?? DV_WAIT))); $pend = dv_pend(); $done = [];\n    $ret = function (float $amt, string $why) use ($r, $wait): string {\n        $ref = dv_new_ref(); $s = dv_return($amt, $ref, $wait);\n        if (empty($s['paid'])) fail('The P5 did not give ' . usd($amt) . ' back (' . (['declined' => 'declined', 'cancelled' => 'cancelled on the P5', 'not_connected' => 'P5 not connected'][$s['status']] ?? ($s['msg'] ?: $s['status'])) . ')' . (!empty($s['unsure']) ? ' \u2013 not sure: look at the P5 before trying again' : '') . '. The receipt was NOT changed.', 402);\n        dv_pend_put($ref, ['key' => 'R' . (int)$r['rno'], 'amt' => $amt, 'st' => 'return', 'at' => now_str(), 'rno' => (int)$r['rno'], 'auth_code' => (string)($s['auth_code'] ?? '')]); // (close day: the P5's returns)\n        audit('dejavoo', 'P5 return ' . usd($amt), '', 'approved \u00b7 receipt #' . $r['rno'] . ' \u00b7 ' . $why . ' \u00b7 ref ' . $ref . ' \u00b7 auth ' . ($s['auth_code'] ?? '')); return 'return ' . $ref; };\n    if ($action === 'receipt_void') {\n        if (abs($sum - $cardBack) >= 0.005) fail('This receipt has a P5 payment of ' . usd($sum) . ' but ' . usd($cardBack) . ' on card \u2013 give the card money back by hand on the right machine. Nothing was changed.', 409);\n        foreach ($p5 as $x) {\n            $ref = (string)$x['ref']; $amt = round((float)($x['amt'] ?? $x['pay']), 2);\n            if (in_array($pend[$ref]['st'] ?? '', ['voided', 'returned'], true)) { $done[] = ($pend[$ref]['st'] ?? '') . ' ' . $ref; continue; } // a retry: already back\n            $v = dv_void($amt, $ref);\n            if (!empty($v['ok'])) { dv_pend_put($ref, ['st' => 'voided', 'void_at' => now_str(), 'rno' => (int)$r['rno']]); audit('dejavoo', 'P5 void ' . usd($amt), 'approved', 'voided on the P5 \u00b7 receipt #' . $r['rno'] . ' \u00b7 ref ' . $ref); $done[] = 'void ' . $ref; continue; }\n            if (!in_array($v['status'], ['error', 'not_found'], true)) fail('The P5 did not void ' . usd($amt) . ' (' . ($v['msg'] ?: $v['status']) . '). The receipt was NOT changed.', 402);\n            $done[] = $ret($amt, 'void after the batch closed'); dv_pend_put($ref, ['st' => 'returned', 'ret_at' => now_str(), 'rno' => (int)$r['rno']]);\n        }\n        return implode(', ', $done);\n    }\n    if (count($p5) === 1 && abs(round((float)($p5[0]['amt'] ?? $p5[0]['pay']), 2) - round($cardBack, 2)) < 0.005 && !in_array($pend[(string)$p5[0]['ref']]['st'] ?? '', ['voided', 'returned'], true)) { // all of it back, same batch: Void (no card needed)\n        $ref = (string)$p5[0]['ref']; $v = dv_void(round($cardBack, 2), $ref);\n        if (!empty($v['ok'])) { dv_pend_put($ref, ['st' => 'voided', 'void_at' => now_str(), 'rno' => (int)$r['rno']]); audit('dejavoo', 'P5 void ' . usd($cardBack), 'approved', 'refund \u2013 voided on the P5 \u00b7 receipt #' . $r['rno'] . ' \u00b7 ref ' . $ref); return 'void ' . $ref; }\n        if (!in_array($v['status'], ['error', 'not_found'], true)) fail('The P5 did not void ' . usd($cardBack) . ' (' . ($v['msg'] ?: $v['status']) . '). The receipt was NOT changed.', 402);\n    }\n    return $ret(round($cardBack, 2), 'refund'); // part of it, or the batch is closed: Return (the customer taps the card)\n}\n"}""")
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
    b = f'{bk}/' + f.strip('/').replace('/', '__') + f'.pre-638d-{st}'; shutil.copy2(p, b); m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m); done.append((p, b)); chk(p)
    print('NEW', f, sha(t), 'backup', b)
for f, t in NEWF.items():
    p = f'{R}/{f}'; open(p, 'w', encoding='utf-8').write(t); made.append(p); os.chmod(p, 0o644); chk(p); print('MADE', f, sha(t))
print('OK 2.99.638d (void / refund qua P5) - restart php-fpm.')
