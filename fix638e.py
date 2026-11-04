#!/usr/bin/env python3
# LAMWEB 2.99.638e (LENH-638 A): Close day -> "Doi chieu may P5": batch dang mo cua P5 TUNG giao dich (POST /v2/Report/Daily: ReferenceId, loai, so tien,
#   last 4) so voi giao dich P5 cua app (hoa don / da duyet chua co hoa don / loi / void / return). Lech thi liet ke bang chu (P5 tru tien ma app khong co hoa don,
#   cho hoa don, void chua tren may, so tien khac, ca tay tren may). CHI DOC: khong tru tien, khong dong batch. Hien khi dv_on.
#   File moi inc/dejavoo-day.php; sua inc/api/dvpay.php (dv_day), inc/api/closeday.php (dvOn), assets/admin/giftcards.js (o P5 trong Close day), api.php x3.
#   Goc = sau 638d.
# Run:  python3 fix638e.py <release dir> <web api.php copies>   (kiem)   /   ... go
import sys, os, shutil, time, hashlib, json, subprocess
args = [a for a in sys.argv[1:]]
if not args: sys.exit('usage: python3 fix638e.py <release dir> [go]')
go = args[-1] == 'go'
if go: args = args[:-1]
R = args[0].rstrip('/'); XP = [os.path.abspath(a) for a in args[1:]]
def sha(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
F = json.loads(r"""{"api.php": {"base": "d9b3adeb", "new": "5e2499e1", "A": [["'tx_cfg' => 'callstx',", "/* (2.99.638e) */ 'dv_day' => 'dvpay', 'tx_cfg' => 'callstx',"], ["const DESK_ACTIONS = [", "const DESK_ACTIONS = [/* (2.99.638e) */ 'dv_day', "]]}, "pub/api.php": {"base": "14d38e44", "new": "304d529d", "A": [["'tx_cfg' => 'callstx',", "/* (2.99.638e) */ 'dv_day' => 'dvpay', 'tx_cfg' => 'callstx',"], ["const DESK_ACTIONS = [", "const DESK_ACTIONS = [/* (2.99.638e) */ 'dv_day', "]]}, "inc/api/dvpay.php": {"base": "400f8ef1", "new": "7c9068fd", "A": [["case 'dv_waiting':", "case 'dv_day': // (2.99.638e) Close day -> \"Check the P5\": its open batch payment by payment vs the app (reads only)\n    require_once APP_ROOT . '/inc/dejavoo-day.php'; desk_out(['on' => dv_pay_on()] + (dv_pay_on() ? dv_day_check() : ['ok' => false, 'msg' => 'Card on the P5 is off.', 'issues' => []]));\ncase 'dv_waiting':"]]}, "inc/api/closeday.php": {"base": "85cdc6d3", "new": "f45e0ceb", "A": [["    json_out($cd);", "    json_out($cd + ['dvOn' => setting('dv_on') === '1' /* (2.99.638e) the Close day screen asks the P5 (dv_day) */]);"]]}, "assets/admin/giftcards.js": {"base": "8f42591b", "new": "9b8dd19b", "A": [["<div class=\"cd-h\">Check against the DPS machine and the drawer</div>", "<div class=\"cd-h\">Check against the DPS machine and the drawer</div>\n${d.dvOn && form ? `<div id=\"cdP5\" class=\"cd-p5\"><p class=\"hint\">\ud83d\udcb3 ${LV('Checking the P5\u2026', '\u0110ang \u0111\u1ed1i chi\u1ebfu m\u00e1y P5\u2026')}</p></div>` : '' /* (2.99.638e) */}"], ["bindCount(sh, d, draw);", "bindCount(sh, d, draw);\nif (d.dvOn && $('#cdP5', sh)) dvDayFill($('#cdP5', sh)); /* (2.99.638e) */"], [": d.day }));\n}\ncatch (e) {\noops(e);\n} });\n});\n};\ndraw(d);\n}\n", ": d.day }));\n}\ncatch (e) {\noops(e);\n} });\n});\n};\ndraw(d);\n}\n\n/* (2.99.638e - LENH-638 A) Close day -> the Dejavoo P5's open batch vs the app's P5 payments (reads only; differences in plain words). */\nasync function dvDayFill(el) {\n  let x; try { x = await api('dv_day'); } catch (e) { el.innerHTML = `<p class=\"cd-short\">\ud83d\udcb3 P5: ${esc(e.message || String(e))}</p>`; return; }\n  if (!x.ok) { el.innerHTML = `<p class=\"cd-short\">\ud83d\udcb3 ${LV('P5 not checked', 'Ch\u01b0a \u0111\u1ed1i chi\u1ebfu \u0111\u01b0\u1ee3c m\u00e1y P5')}: ${esc(x.msg || '')}</p>`; return; }\n  const p = x.p5 || {}, iss = x.issues || [];\n  el.innerHTML = `<div class=\"rc-row\"><span>\ud83d\udcb3 ${LV('P5 batch now (sales \u2212 returns)', 'Batch m\u00e1y P5 hi\u1ec7n t\u1ea1i (b\u00e1n \u2212 ho\u00e0n)')}</span><b>${money(p.total || 0)}</b></div>`\n    + (iss.length ? `<p class=\"cd-short\" style=\"margin:4px 0\">\u26a0 ${LV('P5 and NailFlow differ:', 'M\u00e1y P5 v\u00e0 NailFlow l\u1ec7ch:')}</p><ul class=\"hint\" style=\"margin:0;padding-left:18px\">${iss.map(i => `<li>${esc(i.say)}</li>`).join('')}</ul>`\n      : `<p class=\"hint\" style=\"margin:4px 0\">\u2705 ${LV('The P5 matches the receipts paid on it.', 'M\u00e1y P5 kh\u1edbp v\u1edbi c\u00e1c ho\u00e1 \u0111\u01a1n c\u00e0 tr\u00ean P5.')}</p>`);\n}\n"]]}}""")
plan = []; bad = 0
for f, x in F.items():
    p = f'{R}/{f}'
    if not os.path.isfile(p):
        if f == 'pub/api.php': print(f, 'not on this server - skipped (CHAT 03/11)'); continue
        print(f, 'MISSING'); bad = 1; continue
    s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in x['A']]
    al = '2.99.638e' in s; print(f, 'sha', sha(s), '(LAMWEB base', x['base'] + ')', 'anchors', *n, 'already', al)
    if al or n != [1] * len(n): bad = 1; continue
    t = s
    for a, b in x['A']: t = t.replace(a, b)
    plan.append((f, p, t))
XA = json.loads(r"""[["'tx_cfg' => 'callstx',", "/* (2.99.638e) */ 'dv_day' => 'dvpay', 'tx_cfg' => 'callstx',"], ["const DESK_ACTIONS = [", "const DESK_ACTIONS = [/* (2.99.638e) */ 'dv_day', "]]""")
if XA and not XP: print('NOTE: this package also patches the web api.php copies (Love Nails ~/lovenails/api.php, ...) - give their paths after the release dir'); bad = 1
for p in XP:
    s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in XA]; al = '2.99.638e' in s; print(p, 'sha', sha(s), 'anchors', *n, 'already', al)
    if al or n != [1] * len(n): bad = 1; continue
    t = s
    for a, b in XA: t = t.replace(a, b)
    plan.append((p, p, t))
NEWF = json.loads(r"""{"inc/dejavoo-day.php": "<?php\n/* (2.99.638e - LENH-638 A) Close day -> \"Check the P5\": the P5's OPEN batch, payment by payment (POST /v2/Report/Daily \u2013 ReferenceId, type, amount, last 4),\n   against the app's P5 payments (dv_pend: on a receipt / approved but not on a receipt / failed / void / return). Only reads \u2013 nothing is charged or closed.\n   A difference is listed in plain words; nothing is changed by itself. */\ndeclare(strict_types=1);\nrequire_once __DIR__ . '/dejavoo-pay.php';\n\nfunction dv_daily(int $wait = 30): array {\n    if (!dv_ready()) return ['ok' => false, 'msg' => 'The P5 is not set up.', 'rows' => []];\n    $h = dv_http('POST', '/v2/Report/Daily', ['SPInProxyTimeout' => $wait], $wait); $r = dv_norm($h); dv_log('daily', '', $r);\n    if ($r['status'] !== 'approved') return ['ok' => false, 'msg' => $r['msg'] !== '' ? $r['msg'] : $r['status'], 'rows' => []];\n    $rows = []; foreach ((array)($h['j']['DailyDetails'] ?? []) as $d) foreach ((array)($d['TransactionsDailyReports'] ?? []) as $t)\n        $rows[] = ['ref' => (string)($t['ReferenceId'] ?? ''), 'type' => (string)($t['TransactionType'] ?? ''), 'amt' => round((float)($t['Amount'] ?? 0), 2), 'last4' => (string)($t['Last4'] ?? ''), 'card' => (string)($t['CardType'] ?? '')];\n    return ['ok' => true, 'msg' => '', 'rows' => $rows];\n}\n/** The check. issues: [{what, ref, amt, say}] \u2013 empty = the P5 and the app agree. */\nfunction dv_day_check(): array {\n    $d = dv_daily(); if (!$d['ok']) return ['ok' => false, 'msg' => $d['msg'], 'p5' => null, 'issues' => []];\n    $pend = dv_pend(); $iss = []; $p5 = ['sale' => 0.0, 'ret' => 0.0, 'n' => 0]; $seen = [];\n    foreach ($d['rows'] as $t) {\n        $ty = strtolower($t['type']); $isVoid = str_contains($ty, 'void'); $isRet = str_contains($ty, 'return') || str_contains($ty, 'refund');\n        $seen[$t['ref']] = 1; $p = $pend[$t['ref']] ?? null; $st = (string)($p['st'] ?? '');\n        if ($isVoid) continue;\n        if ($isRet) { $p5['ret'] += $t['amt']; if (!$p) $iss[] = ['what' => 'p5_only', 'ref' => $t['ref'], 'amt' => $t['amt'], 'say' => 'A return of ' . usd($t['amt']) . ' on the P5 that NailFlow did not send (done on the P5 by hand?).']; continue; }\n        $p5['sale'] += $t['amt']; $p5['n']++;\n        if (!$p) { $iss[] = ['what' => 'p5_only', 'ref' => $t['ref'], 'amt' => $t['amt'], 'say' => usd($t['amt']) . ($t['last4'] !== '' ? ' \u00b7\u00b7' . $t['last4'] : '') . ' on the P5 that NailFlow did not send (charged on the P5 by hand?) \u2013 no receipt for it.']; continue; }\n        if (in_array($st, ['failed', 'unsure', 'wait'], true)) $iss[] = ['what' => 'charged_no_receipt', 'ref' => $t['ref'], 'amt' => $t['amt'], 'say' => 'The P5 TOOK ' . usd($t['amt']) . ' but NailFlow did not get the approval \u2013 no receipt. Check the customer, then make the receipt or cancel it on the P5.'];\n        elseif ($st === 'paid') $iss[] = ['what' => 'waiting', 'ref' => $t['ref'], 'amt' => $t['amt'], 'say' => usd($t['amt']) . ' approved on the P5, not on a receipt yet (' . ($p['key'] ?? '') . ').'];\n        elseif (in_array($st, ['voided', 'void', 'returned'], true)) $iss[] = ['what' => 'void_missing', 'ref' => $t['ref'], 'amt' => $t['amt'], 'say' => usd($t['amt']) . ' was cancelled in NailFlow but the P5 still has it as a sale \u2013 void it on the P5.'];\n        if ($p && in_array($st, ['used', 'paid'], true) && abs((float)$p['amt'] - $t['amt']) >= 0.005) $iss[] = ['what' => 'amount', 'ref' => $t['ref'], 'amt' => $t['amt'], 'say' => 'The P5 has ' . usd($t['amt']) . ', the receipt ' . usd((float)$p['amt']) . '.'];\n    }\n    $today = date('Y-m-d');\n    foreach ($pend as $ref => $p) if (($p['st'] ?? '') === 'used' && !isset($seen[$ref]) && substr((string)($p['paid_at'] ?? $p['at'] ?? ''), 0, 10) === $today)\n        $iss[] = ['what' => 'app_only', 'ref' => (string)$ref, 'amt' => (float)$p['amt'], 'say' => 'Receipt paid on the P5 today (' . usd((float)$p['amt']) . ') is not in the P5 batch (already settled?).'];\n    return ['ok' => true, 'msg' => '', 'p5' => ['sale' => round($p5['sale'], 2), 'ret' => round($p5['ret'], 2), 'total' => round($p5['sale'] - $p5['ret'], 2), 'n' => $p5['n']], 'issues' => $iss];\n}\n"}""")
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
    b = f'{bk}/' + f.strip('/').replace('/', '__') + f'.pre-638e-{st}'; shutil.copy2(p, b); m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m); done.append((p, b)); chk(p)
    print('NEW', f, sha(t), 'backup', b)
for f, t in NEWF.items():
    p = f'{R}/{f}'; open(p, 'w', encoding='utf-8').write(t); made.append(p); os.chmod(p, 0o644); chk(p); print('MADE', f, sha(t))
print('OK 2.99.638e (doi chieu P5 o Close day) - restart php-fpm.')
