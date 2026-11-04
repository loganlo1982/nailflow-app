#!/usr/bin/env python3
# LAMWEB 2.99.638g (LENH-638 B): TAP TO PAY tren iPhone - PHIA SERVER. Action ttp_result: NailFlowApp iOS (638h, CHUA lam) gui ket qua Dejavoo (Spin_Response)
#   -> DUYET (ResultCode/RespCode 0|00 + RefId) thanh 1 giao dich cua phieu (dv_pend st paid, src ttp) -> Checkout luu hoa don y nhu 638c (dv_take: dung phieu,
#   dung so tien, dung 1 lan). Cung RefId gui lai = cung giao dich (khong 2 hoa don). Khong duyet -> khong gi. Hoa don Tap to Pay: void/refund tren iPhone
#   (khong goi P5), dv_cancel tu choi, doi chieu P5 bo qua. File moi inc/dejavoo-ttp.php; sua dvpay.php, dejavoo-pay.php, dejavoo-back.php, dejavoo-day.php, api.php x3.
#   Goc = sau 638e.
# Run:  python3 fix638g.py <release dir> <web api.php copies>   (kiem)   /   ... go
import sys, os, shutil, time, hashlib, json, subprocess
args = [a for a in sys.argv[1:]]
if not args: sys.exit('usage: python3 fix638g.py <release dir> [go]')
go = args[-1] == 'go'
if go: args = args[:-1]
R = args[0].rstrip('/'); XP = [os.path.abspath(a) for a in args[1:]]
def sha(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
F = json.loads(r"""{"api.php": {"base": "5e2499e1", "new": "eb66eeb1", "A": [["'tx_cfg' => 'callstx',", "/* (2.99.638g) Tap to Pay result */ 'ttp_result' => 'dvpay', 'tx_cfg' => 'callstx',"], ["const DESK_ACTIONS = [", "const DESK_ACTIONS = [/* (2.99.638g) */ 'ttp_result', "]]}, "pub/api.php": {"base": "304d529d", "new": "10be8951", "A": [["'tx_cfg' => 'callstx',", "/* (2.99.638g) Tap to Pay result */ 'ttp_result' => 'dvpay', 'tx_cfg' => 'callstx',"], ["const DESK_ACTIONS = [", "const DESK_ACTIONS = [/* (2.99.638g) */ 'ttp_result', "]]}, "inc/api/dvpay.php": {"base": "7c9068fd", "new": "501f1173", "A": [["case 'dv_waiting':", "case 'ttp_result': // (2.99.638g) Tap to Pay on iPhone: the NailFlowApp sends the Dejavoo result (Spin_Response) -> a payment of the ticket\n    if ($method !== 'POST') fail('POST only', 405);\n    require_once APP_ROOT . '/inc/dejavoo-ttp.php'; desk_out(['ok' => true] + ttp_result((array)($in['ids'] ?? []), (float)($in['amt'] ?? 0), (array)($in['spin'] ?? [])));\ncase 'dv_waiting':"]]}, "inc/dejavoo-pay.php": {"base": "b9287da6", "new": "60a6c76b", "A": [["    $r = dv_pend()[$ref] ?? null; if (!$r || ($r['st'] ?? '') !== 'paid') fail('Nothing to cancel (no P5 payment waiting).', 404);", "    $r = dv_pend()[$ref] ?? null; if (!$r || ($r['st'] ?? '') !== 'paid') fail('Nothing to cancel (no P5 payment waiting).', 404);\n    if (($r['src'] ?? '') === 'ttp') fail('This one was paid with Tap to Pay on the iPhone \u2013 refund it on the iPhone (iPOSgo!).', 409); // (2.99.638g)"]]}, "inc/dejavoo-back.php": {"base": "a752a487", "new": "60831531", "A": [["function dv_receipt_p5(array $r): array { $o = []; foreach ((json_decode((string)$r['pays'], true) ?: []) as $p) if (($p['m'] ?? '') === 'Card' && !empty($p['dv']['ref'])) $o[] = $p['dv'] + ['pay' => (float)$p['amt']]; return $o; }", "function dv_receipt_p5(array $r): array { $o = []; foreach ((json_decode((string)$r['pays'], true) ?: []) as $p) if (($p['m'] ?? '') === 'Card' && !empty($p['dv']['ref']) && !str_starts_with((string)$p['dv']['ref'], 'TTP') /* (2.99.638g) Tap to Pay: not the P5 */) $o[] = $p['dv'] + ['pay' => (float)$p['amt']]; return $o; }"]]}, "inc/dejavoo-day.php": {"base": "c5e4ddf4", "new": "0848cd39", "A": [["    foreach ($pend as $ref => $p) if (($p['st'] ?? '') === 'used' && !isset($seen[$ref]) &&", "    foreach ($pend as $ref => $p) if (($p['st'] ?? '') === 'used' && ($p['src'] ?? '') !== 'ttp' /* (2.99.638g) */ && !isset($seen[$ref]) &&"]]}}""")
plan = []; bad = 0
for f, x in F.items():
    p = f'{R}/{f}'
    if not os.path.isfile(p):
        if f == 'pub/api.php': print(f, 'not on this server - skipped (CHAT 03/11)'); continue
        print(f, 'MISSING'); bad = 1; continue
    s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in x['A']]
    al = '2.99.638g' in s; print(f, 'sha', sha(s), '(LAMWEB base', x['base'] + ')', 'anchors', *n, 'already', al)
    if al or n != [1] * len(n): bad = 1; continue
    t = s
    for a, b in x['A']: t = t.replace(a, b)
    plan.append((f, p, t))
XA = json.loads(r"""[["'tx_cfg' => 'callstx',", "/* (2.99.638g) Tap to Pay result */ 'ttp_result' => 'dvpay', 'tx_cfg' => 'callstx',"], ["const DESK_ACTIONS = [", "const DESK_ACTIONS = [/* (2.99.638g) */ 'ttp_result', "]]""")
if XA and not XP: print('NOTE: this package also patches the web api.php copies (Love Nails ~/lovenails/api.php, ...) - give their paths after the release dir'); bad = 1
for p in XP:
    s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in XA]; al = '2.99.638g' in s; print(p, 'sha', sha(s), 'anchors', *n, 'already', al)
    if al or n != [1] * len(n): bad = 1; continue
    t = s
    for a, b in XA: t = t.replace(a, b)
    plan.append((p, p, t))
NEWF = json.loads(r"""{"inc/dejavoo-ttp.php": "<?php\n/* (2.99.638g - LENH-638 B) TAP TO PAY on iPhone (Dejavoo iPOSgo!): the NailFlowApp (iOS, 638h \u2013 not yet) charges with the Dejavoo library and sends the\n   result here (Spin_Response: RefId, AuthCode, PNRef, ResultCode / RespCode \"0\" | \"00\", AcntLast4, CardType, Amount, Tip, TotalAmt ...).\n   An APPROVED result becomes a P5-like payment of the ticket (dv_pend, st 'paid', src 'ttp') -> Checkout saves the receipt with it exactly like 638c\n   (dv_take: right ticket, right amount, used once). The same RefId twice = the same payment (never 2 receipts). Not approved -> nothing. Off unless dv_on. */\ndeclare(strict_types=1);\nrequire_once __DIR__ . '/dejavoo-pay.php';\n\nfunction ttp_ok(array $s): bool { foreach (['ResultCode', 'RespCode'] as $k) { $v = trim((string)($s[$k] ?? '')); if ($v !== '' && $v !== '0' && $v !== '00') return false; }\n    return trim((string)($s['ResultCode'] ?? ($s['RespCode'] ?? ''))) !== ''; }\nfunction ttp_result(array $ids, float $amt, array $spin): array {\n    if (!dv_on()) fail('Card payments on the iPhone are off (Settings \u2192 Payments).', 400);\n    $s = isset($spin['Spin_Response']) && is_array($spin['Spin_Response']) ? $spin['Spin_Response'] : $spin;\n    $rid = preg_replace('/[^A-Za-z0-9\\-_.]/', '', (string)($s['RefId'] ?? '')); if ($rid === '' || strlen($rid) > 60) fail('Tap to Pay: no RefId in the answer.');\n    $key = dv_key($ids); $amt = round($amt, 2); if ($key === '' || $amt < 0.01) fail('Check the amount.');\n    $ref = 'TTP' . $rid; app_lock('dejavoo');\n    $old = dv_pend()[$ref] ?? null;\n    if ($old) { // the same answer sent again (the app retried): the same payment\n        if (($old['key'] ?? '') !== $key) fail('That Tap to Pay payment is for another ticket.', 409);\n        return dv_card_out($ref, $old) + ['again' => true, 'st' => (string)$old['st']];\n    }\n    if (!ttp_ok($s)) { dv_log('ttp', $ref, ['status' => 'declined', 'code' => (string)($s['ResultCode'] ?? $s['RespCode'] ?? ''), 'msg' => mb_substr((string)($s['Message'] ?? $s['RespMsg'] ?? ''), 0, 80)], ['amount' => $amt]);\n        fail('Tap to Pay: not approved (' . mb_substr((string)($s['Message'] ?? $s['RespMsg'] ?? 'declined'), 0, 80) . ').', 402); }\n    $ex = (array)($s['ExtData'] ?? []); $tot = $s['TotalAmt'] ?? $ex['Amount'] ?? $s['Amount'] ?? null; $tot = $tot === null || $tot === '' ? $amt : round((float)$tot, 2);\n    $l4 = (string)($s['AcntLast4'] ?? $ex['AcntLast4'] ?? ''); $l4 = preg_match('/^\\d{4}$/', $l4) ? $l4 : '';\n    $row = ['key' => $key, 'amt' => $tot, 'st' => 'paid', 'src' => 'ttp', 'at' => now_str(), 'paid_at' => now_str(), 'by' => actor_name(), 'last4' => $l4,\n        'card' => mb_substr((string)($s['CardType'] ?? $s['PaymentType'] ?? ''), 0, 20), 'auth_code' => mb_substr((string)($s['AuthCode'] ?? ''), 0, 20), 'pnref' => mb_substr((string)($s['PNRef'] ?? ''), 0, 40)];\n    dv_pend_put($ref, $row);\n    dv_log('ttp', $ref, ['status' => 'approved', 'last4' => $l4, 'card' => $row['card'], 'auth_code' => $row['auth_code'], 'pnref' => $row['pnref']], ['amount' => $tot]);\n    audit('dejavoo', 'Tap to Pay ' . usd($tot), '', 'approved \u00b7 ' . ($row['card'] ?: 'card') . ($l4 !== '' ? ' \u00b7\u00b7' . $l4 : '') . ' \u00b7 auth ' . $row['auth_code'] . ' \u00b7 ref ' . $ref . ' \u00b7 ' . $key);\n    if (abs($tot - $amt) >= 0.005) json_out(['error' => 'The iPhone took ' . usd($tot) . ', the ticket says ' . usd($amt) . '. Check it (refund on the iPhone if it is wrong).', 'dvPaid' => dv_card_out($ref, $row)], 409);\n    return dv_card_out($ref, $row);\n}\n"}""")
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
    b = f'{bk}/' + f.strip('/').replace('/', '__') + f'.pre-638g-{st}'; shutil.copy2(p, b); m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m); done.append((p, b)); chk(p)
    print('NEW', f, sha(t), 'backup', b)
for f, t in NEWF.items():
    p = f'{R}/{f}'; open(p, 'w', encoding='utf-8').write(t); made.append(p); os.chmod(p, 0o644); chk(p); print('MADE', f, sha(t))
print('OK 2.99.638g (Tap to Pay - server) - restart php-fpm. Chua ai goi (app iOS chua co).')
