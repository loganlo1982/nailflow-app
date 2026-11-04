#!/usr/bin/env python3
# LAMWEB 2.99.638d2 (QA-0028 P1 TIEN, LENH-638d2, anh Logan 03/11 14:33): 638d - P5 tra tien TRUOC khi kiem hoa don -> tra du / tra 2 lan.
#   Sua: (1) tach phan KIEM cua receipt_void / receipt_refund thanh receipt_void_check / receipt_refund_check (KHONG ghi gi; receipt_void/refund goi
#   chinh no - cung 1 code); receipt_void / receipt_refund cua hoa don P5 chay check XONG roi moi goi P5. (2) dv_money_back: tien tra ve the <= P5 da thu tren
#   hoa don - tien the da tra truoc; vuot -> fail, khong goi P5. (3) bam lai / 2 may: app_lock money + check -> lan 2 bi tu choi truoc P5.
#   Hoa don the thuong + Tap to Pay: y nhu cu. Goc = sau 638g.
# Run:  python3 fix638d2.py <release dir>   (kiem)   /   ... go
import sys, os, shutil, time, hashlib, json, subprocess
args = [a for a in sys.argv[1:]]
if not args: sys.exit('usage: python3 fix638d2.py <release dir> [go]')
go = args[-1] == 'go'
if go: args = args[:-1]
R = args[0].rstrip('/'); XP = [os.path.abspath(a) for a in args[1:]]
def sha(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
F = json.loads(r"""{"inc/checkout-receipts.php": {"base": "33e7bf7f", "new": "24ad657e", "A": [["function receipt_refund(array $r, float $amt, string $how, string $reason, $techs = null): array {\n    if ($r['status'] !== 'paid') fail('This receipt is void.');\n    $amt = round($amt, 2);\n    $how = in_array($how, ['Card', 'Cash', 'Gift card', 'Other'], true) ? $how : 'Other';\n    $all = round((float)$r['total'] - (float)$r['deposit'] - (float)$r['refund'], 2); // (2.99.627 L1) what is left of the whole receipt\n    $real = 0.0; foreach (json_decode((string)$r['refunds'], true) ?: [] as $f) if (($f['how'] ?? '') !== 'Gift card') $real += (float)$f['amt']; // money really given back (not onto a gift card)\n    $left = $how === 'Gift card' ? $all : min($all, round(receipt_collect($r) - $real, 2)); // (2.99.59) gift card money can go back on the card; (2.99.627 L1) a refund onto the gift card no longer blocks the cash / card part\n    day_open_or_fail(date('Y-m-d'), 'a refund goes on today'); // (2.99.58)\n    if ($left <= 0) fail($how === 'Gift card' || $all <= 0 ? 'Everything on this receipt was already refunded.' : ((float)$r['gift'] > 0 ? 'Paid with a gift card \u2013 refund it to \ud83c\udf81 Gift card.' : 'Everything on this receipt was already refunded.'));\n    if ($amt <= 0 || $amt > $left + 0.001) fail('Refund from $0.01 to ' . usd($left) . '.');\n    $taxPart = refund_tax_part($r, $amt, $how); // (2.99.88) the tax goes back to the customer, not from the techs\n    [$parts, $fee] = refund_split($r, round($amt - $taxPart, 2), $techs);\n", "/** (2.99.638d2 QA-0028) Every check of a refund, NOTHING written \u2013 run BEFORE the card money moves on the P5, and again by receipt_refund() (same code). */\nfunction receipt_refund_check(array $r, float $amt, string $how, $techs = null): array {\n    if ($r['status'] !== 'paid') fail('This receipt is void.');\n    $amt = round($amt, 2);\n    $how = in_array($how, ['Card', 'Cash', 'Gift card', 'Other'], true) ? $how : 'Other';\n    $all = round((float)$r['total'] - (float)$r['deposit'] - (float)$r['refund'], 2); // (2.99.627 L1) what is left of the whole receipt\n    $real = 0.0; foreach (json_decode((string)$r['refunds'], true) ?: [] as $f) if (($f['how'] ?? '') !== 'Gift card') $real += (float)$f['amt']; // money really given back (not onto a gift card)\n    $left = $how === 'Gift card' ? $all : min($all, round(receipt_collect($r) - $real, 2)); // (2.99.59) gift card money can go back on the card; (2.99.627 L1) a refund onto the gift card no longer blocks the cash / card part\n    day_open_or_fail(date('Y-m-d'), 'a refund goes on today'); // (2.99.58)\n    if ($left <= 0) fail($how === 'Gift card' || $all <= 0 ? 'Everything on this receipt was already refunded.' : ((float)$r['gift'] > 0 ? 'Paid with a gift card \u2013 refund it to \ud83c\udf81 Gift card.' : 'Everything on this receipt was already refunded.'));\n    if ($amt <= 0 || $amt > $left + 0.001) fail('Refund from $0.01 to ' . usd($left) . '.');\n    $taxPart = refund_tax_part($r, $amt, $how); // (2.99.88) the tax goes back to the customer, not from the techs\n    [$parts, $fee] = refund_split($r, round($amt - $taxPart, 2), $techs);\n    return ['amt' => $amt, 'how' => $how, 'taxPart' => $taxPart, 'parts' => $parts, 'fee' => $fee];\n}\nfunction receipt_refund(array $r, float $amt, string $how, string $reason, $techs = null): array {\n    ['amt' => $amt, 'how' => $how, 'taxPart' => $taxPart, 'parts' => $parts, 'fee' => $fee] = receipt_refund_check($r, $amt, $how, $techs); // (2.99.638d2)\n"], ["function receipt_void(array $r, string $reason): void {\n    if ($r['status'] !== 'paid') fail('This receipt is already void.');\n    if ((float)$r['refund'] > 0) fail('Money was already refunded on this receipt, so it cannot be voided.');\n    day_open_or_fail((string)$r['day'], 'receipts of that day cannot be voided'); // (2.99.58)\n    $gsc = receipt_gift_sale_card($r); // (2.99.627 L2, anh Logan 02/11: VOID HET) the gift card sold on this bill is voided with it \u2013 not when some of it was used\n    if ($gsc && ((float)$gsc['balance'] < (float)$gsc['amount'] - 0.001 || gift_used_ever((int)$gsc['id']))) fail('Gift card ' . gift_mask((string)$gsc['code']) . ' was already used (' . usd((float)$gsc['balance']) . ' left) \u2013 refund instead.');\n", "/** (2.99.638d2 QA-0028) Every check of a void, NOTHING written \u2013 run BEFORE the card money moves on the P5, and again by receipt_void() (same code). Returns the gift card sold on the bill (or null). */\nfunction receipt_void_check(array $r): ?array {\n    if ($r['status'] !== 'paid') fail('This receipt is already void.');\n    if ((float)$r['refund'] > 0) fail('Money was already refunded on this receipt, so it cannot be voided.');\n    day_open_or_fail((string)$r['day'], 'receipts of that day cannot be voided'); // (2.99.58)\n    $gsc = receipt_gift_sale_card($r); // (2.99.627 L2, anh Logan 02/11: VOID HET) the gift card sold on this bill is voided with it \u2013 not when some of it was used\n    if ($gsc && ((float)$gsc['balance'] < (float)$gsc['amount'] - 0.001 || gift_used_ever((int)$gsc['id']))) fail('Gift card ' . gift_mask((string)$gsc['code']) . ' was already used (' . usd((float)$gsc['balance']) . ' left) \u2013 refund instead.');\n    return $gsc;\n}\nfunction receipt_void(array $r, string $reason): void {\n    $gsc = receipt_void_check($r); // (2.99.638d2)\n"]]}, "inc/api/checkout.php": {"base": "87e8753a", "new": "5e392ea9", "A": [["    if ($dvP5) { dv_money_back($r, $action, $cardBack);", "    if ($dvP5) { if ($action === 'receipt_void') receipt_void_check($r); else receipt_refund_check($r, (float)($in['amount'] ?? 0), (string)($in['how'] ?? ''), $in['techs'] ?? null); } // (2.99.638d2 QA-0028) EVERY check of the receipt first: one that fails stops here, the P5 is never asked\n    if ($dvP5) { dv_money_back($r, $action, $cardBack);"]]}, "inc/dejavoo-back.php": {"base": "60831531", "new": "5eadddce", "A": [["    if (count($p5) === 1 && abs(round((float)($p5[0]['amt'] ?? $p5[0]['pay']), 2) - round($cardBack, 2)) < 0.005 &&", "    $backCard = 0.0; foreach ((json_decode((string)$r['refunds'], true) ?: []) as $f) if (($f['how'] ?? '') === 'Card') $backCard += (float)$f['amt']; // (2.99.638d2 QA-0028) card money already given back on this receipt\n    if (round($cardBack, 2) > round($sum - $backCard, 2) + 0.004) fail('The P5 took ' . usd($sum) . ' on this receipt' . ($backCard > 0 ? ' and ' . usd($backCard) . ' already went back' : '') . ' \u2013 at most ' . usd(max(0, round($sum - $backCard, 2))) . ' can go back on the card. Nothing was changed.', 400);\n    if (count($p5) === 1 && abs(round((float)($p5[0]['amt'] ?? $p5[0]['pay']), 2) - round($cardBack, 2)) < 0.005 &&"]]}}""")
plan = []; bad = 0
for f, x in F.items():
    p = f'{R}/{f}'
    if not os.path.isfile(p): print(f, 'MISSING'); bad = 1; continue
    s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in x['A']]
    al = '2.99.638d2' in s; print(f, 'sha', sha(s), '(LAMWEB base', x['base'] + ')', 'anchors', *n, 'already', al)
    if al or n != [1] * len(n): bad = 1; continue
    t = s
    for a, b in x['A']: t = t.replace(a, b)
    plan.append((f, p, t))
XA = json.loads(r"""[]""")
if XA and not XP: print('NOTE: this package also patches the web api.php copies (Love Nails ~/lovenails/api.php, ...) - give their paths after the release dir'); bad = 1
for p in XP:
    s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in XA]; al = '2.99.638d2' in s; print(p, 'sha', sha(s), 'anchors', *n, 'already', al)
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
    b = f'{bk}/' + f.strip('/').replace('/', '__') + f'.pre-638d2-{st}'; shutil.copy2(p, b); m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m); done.append((p, b)); chk(p)
    print('NEW', f, sha(t), 'backup', b)
for f, t in NEWF.items():
    p = f'{R}/{f}'; open(p, 'w', encoding='utf-8').write(t); made.append(p); os.chmod(p, 0o644); chk(p); print('MADE', f, sha(t))
print('OK 2.99.638d2 (QA-0028) - restart php-fpm.')
