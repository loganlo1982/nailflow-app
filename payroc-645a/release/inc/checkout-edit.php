<?php
/* (2.99.206 – order 407) inc/checkout-edit.php – part of inc/checkout.php (was one 100 KB file): owner fixes on a receipt: $1 rule lines, ADD PAY, who did each service. Plain functions; inc/checkout.php loads it. */
declare(strict_types=1);
/** (2.99.194 – order 392) The owner splits ONE tech's money on a paid receipt into its service lines (e.g. $60 → $30 + $30) and the $1 rule is worked out
    again line by line. Only the techs' pay split changes (that tech, the $1 tech, admin_fee) – never the customer's total, tips, tax or how it was paid.
    Not on a void / refunded receipt, a closed day 🔒 or a closed payroll week. Kept in the Money & security log. */
function receipt_fee_lines(array $r, int $sid, array $in): array {
    if ($r['status'] !== 'paid') fail('This receipt is void.');
    if ((float)$r['refund'] > 0.004) fail('This receipt has a refund – the $1 lines cannot be changed.');
    day_open_or_fail((string)$r['day'], 'the $1 lines');
    if (payroll_week_closed((string)$r['day'])) fail('Payroll for that week is closed – reopen it first.', 409);
    $ps = json_decode((string)($r['pay_splits'] ?? ''), true); if (!is_array($ps) || !$ps) fail('This receipt has no money for each tech.');
    $fc = fee_cfg(); $feeTo = 0; foreach ($ps as $px) if ((float)($px['fee'] ?? 0) > 0 || !empty($px['feeOnly'])) $feeTo = (int)$px['staff']; if (!$feeTo) $feeTo = (int)$fc['staff'];
    $k = null; foreach ($ps as $i => $px) if ((int)$px['staff'] === $sid && empty($px['feeOnly'])) $k = $i;
    if ($k === null) fail('That tech is not on this receipt.');
    if ($sid === $feeTo) fail('The $1 rule is never taken from ' . staff_name($sid) . '.');
    $tiers = $ps[$k]['ft'] ?? null; if (!$tiers) foreach ($ps as $px) if (!empty($px['ft'])) $tiers = $px['ft']; if (!$tiers) $tiers = $fc['tiers'];
    $gross = round((float)($ps[$k]['gross'] ?? $ps[$k]['amt']), 2);
    $L = []; foreach ($in as $l) { if (!is_array($l)) continue; $g = round((float)($l['amt'] ?? 0), 2); if ($g <= 0) continue; if ($g > 10000) fail('Check the money.');
        $L[] = ['n' => mb_substr(trim((string)($l['name'] ?? '')), 0, 40), 'g' => $g]; }
    if (!$L) fail('Type the money of each service.');
    if (count($L) > 12) fail('At most 12 lines.');
    $sum = round(array_sum(array_column($L, 'g')), 2);
    if (abs($sum - $gross) > 0.005) fail('The lines add up to ' . usd($sum) . ' – must be ' . usd($gross) . ' (' . staff_name($sid) . '’s money on this receipt).');
    $old = round($gross - (float)$ps[$k]['amt'], 2); $new = 0.0; $fr = []; $cuts = 0;
    foreach ($L as $j => $l) { [$fa, $fm] = $tiers ? fee_tier($tiers, $l['g']) : [0.0, 0.0]; $L[$j]['a'] = $fa; if ($fa > 0) { $new = round($new + $fa, 2); $cuts++; $fr[] = ['g' => $l['g'], 'a' => $fa, 'm' => $fm]; } }
    $before = ['tech' => staff_name($sid), 'fee' => $old, 'lines' => $ps[$k]['lines'] ?? null];
    $ps[$k]['amt'] = round($gross - $new, 2); $ps[$k]['cuts'] = $cuts; $ps[$k]['lines'] = $L; $ps[$k]['ft'] = $tiers; unset($ps[$k]['tl']); // (582) split after Checkout → the turn by these lines
    if ($fr) $ps[$k]['feeRows'] = $fr; else unset($ps[$k]['feeRows']);
    $d = round($new - $old, 2); $fee = round((float)$r['admin_fee'] + $d, 2);
    if ($fee < -0.004) fail('The $1 money would go below $0.');
    $f = null; foreach ($ps as $i => $px) if ((int)$px['staff'] === $feeTo) $f = $i;
    if ($f === null && $d > 0) { $ps[] = ['staff' => $feeTo, 'tech' => staff_name($feeTo), 'amt' => 0.0, 'gross' => 0.0, 'cuts' => 0, 'feeOnly' => true]; $f = count($ps) - 1; }
    if ($f !== null) { $ps[$f]['amt'] = round((float)$ps[$f]['amt'] + $d, 2);
        if (!empty($ps[$f]['feeOnly']) && $ps[$f]['amt'] <= 0.004) { array_splice($ps, $f, 1); $f = null; } }
    foreach ($ps as $i => $px) $ps[$i]['fee'] = $f !== null && $i === $f ? max(0.0, $fee) : 0;
    $fee = max(0.0, $fee);
    q('UPDATE receipts SET pay_splits = ?, admin_fee = ? WHERE id = ?', [json_encode(array_values($ps), JSON_UNESCAPED_UNICODE), $fee, (int)$r['id']]);
    $txt = implode(' + ', array_map(fn($l) => ($l['n'] !== '' ? $l['n'] . ' ' : '') . usd($l['g']), $L));
    audit('fee_lines', 'Receipt #' . $r['rno'] . ' · ' . staff_name($sid), ['$1 rule' => usd($old)], ['$1 rule' => usd($new), 'lines' => $txt], '$1 lines fixed');
    if (function_exists('chg_bump')) chg_bump();
    return ['tech' => staff_name($sid), 'before' => $old, 'after' => $new, 'lines' => $L];
}

/** (2.99.198 – order 397) Receipts → a ticket with the owner's number: TEST ↔ ADD PAY (owner only). ADD PAY = counted for the techs like any ticket; TEST = left out.
    Not on a closed day 🔒 or a closed payroll week. Money & security log. The visit stays TEST (never a turn). */
function receipt_addpay(array $r, bool $on): array {
    if ($on) fail('ADD PAY is no longer used – a test number’s ticket stays TEST.'); // (2.99.283 – order 497) (TEST back from an old ADD PAY still works)
    if (!is_test_phone((string)$r['phone']) && !in_array((int)$r['id'], array_map('intval', json_decode((string)setting('addpay_ids'), true) ?: []), true)) fail('Not an ADD PAY ticket.');
    day_open_or_fail((string)$r['day'], 'TEST ↔ ADD PAY');
    if (payroll_week_closed((string)$r['day'])) fail('Payroll for that week is closed – reopen it first.', 409);
    $was = (int)$r['test'] === 0;
    addpay_set((int)$r['id'], $on);
    if ($was !== $on) { q('UPDATE receipts SET test = ? WHERE id = ?', [$on ? 0 : 1, (int)$r['id']]);
        audit('desk_money', 'Receipt #' . $r['rno'] . ' · ' . pretty_phone((string)$r['phone']), $was ? 'ADD PAY' : 'TEST', $on ? 'ADD PAY – counted for the techs' : 'TEST – not counted', 'TEST ↔ ADD PAY');
        if (function_exists('chg_bump')) chg_bump(); }
    return ['addPay' => $on];
}
/** (2.99.198 – order 397) The ADD PAY receipts (ids) – kept so that changing Settings → Test numbers never turns them back into TEST (test_mark_all). */
function addpay_ids(): array { $l = json_decode((string)setting('addpay_ids'), true); return is_array($l) ? array_values(array_map('intval', $l)) : []; }
function addpay_set(int $id, bool $on): void { $l = addpay_ids(); $l = $on ? array_values(array_unique(array_merge($l, [$id]))) : array_values(array_diff($l, [$id])); set_setting('addpay_ids', json_encode($l)); }

/** (2.99.199 – order 398, SO-LUAT 10/10) The owner fixes WHO did each line of a paid receipt (Receipt → tap a tech / a "↳ Service" line):
    every line = [staff, name, money]; lines can be moved to another tech, split in two, their money changed – the lines must still add up to the
    receipt's services. Then everything is worked out again: the $1 rule line by line, each tech's money, the $1 tech, Payroll / Tech report / AN Desk /
    Close day / AN Tech (they read the receipt), the turn (the receipt's money; a tech with money but no visit of their own: a turn by their money).
    Never changed: the customer's total, tax, discounts, tips (they stay with their tech – "Edit tips"), how it was paid.
    Not on a void / refunded receipt, a closed day 🔒 or a closed payroll week. Money & security log + "Techs edited … by …" on the receipt. */
function receipt_lines_edit(array $r, array $in, ?float $want = null, bool $quiet = false): array { // (2.99.345 – lệnh 580) $want: the new services total (Sửa tiền dịch vụ); $quiet: no turn change, no own log
    if ($r['status'] !== 'paid') fail('This receipt is void.');
    if ((float)$r['refund'] > 0.004) fail('This receipt has a refund – its techs cannot be changed.');
    day_open_or_fail((string)$r['day'], 'the techs of a receipt');
    if (payroll_week_closed((string)$r['day'])) fail('Payroll for that week is closed – reopen it first.', 409);
    $ps = json_decode((string)($r['pay_splits'] ?? ''), true); $old = is_array($ps) ? $ps : [];
    if (!$old) foreach (receipt_splits($r) as $x) $old[] = ['staff' => (int)$x['staff'], 'tech' => (string)$x['tech'], 'amt' => (float)$x['amt'], 'gross' => (float)$x['amt']];
    if (!$old) fail('This receipt has no money for each tech.');
    $total = 0.0; foreach ($old as $px) if (empty($px['feeOnly'])) $total += (float)($px['gross'] ?? $px['amt']); $total = round($total, 2); if ($want !== null) $total = round($want, 2);
    $fc = fee_cfg(); $feeTo = 0; foreach ($old as $px) if ((float)($px['fee'] ?? 0) > 0 || !empty($px['feeOnly'])) $feeTo = (int)$px['staff']; if (!$feeTo) $feeTo = (int)$fc['staff'];
    $tiers = null; foreach ($old as $px) if (!empty($px['ft'])) $tiers = $px['ft']; if (!$tiers) $tiers = $fc['on'] ? $fc['tiers'] : [];
    $names = []; foreach (staff_list(false) as $s) $names[(int)$s['id']] = (string)$s['name'];
    $L = []; foreach ($in as $l) { if (!is_array($l)) continue; $sid = (int)($l['staff'] ?? 0); $g = round((float)($l['amt'] ?? 0), 2);
        if ($g <= 0) continue; if ($g > 10000) fail('Check the money.'); if (!isset($names[$sid])) fail('Choose the tech for ' . usd($g) . '.');
        $L[] = ['staff' => $sid, 'n' => mb_substr(trim((string)($l['name'] ?? '')), 0, 40), 'g' => $g]; }
    if (!$L) fail('Type the money of each line.');
    if (count($L) > 20) fail('At most 20 lines.');
    $sum = round(array_sum(array_column($L, 'g')), 2);
    if (abs($sum - $total) > 0.005) fail('The lines add up to ' . usd($sum) . ' – must be ' . usd($total) . ' (the services on this receipt).');
    $pay = []; $splits = []; $fee = 0.0;
    foreach ($L as $l) { $sid = $l['staff'];
        if (!isset($pay[$sid])) $pay[$sid] = ['staff' => $sid, 'tech' => $names[$sid], 'amt' => 0.0, 'gross' => 0.0, 'cuts' => 0, 'lines' => []];
        $fa = 0.0; $fm = 0.0; if ($sid !== $feeTo && $tiers) [$fa, $fm] = fee_tier($tiers, $l['g']);
        $pay[$sid]['gross'] = round($pay[$sid]['gross'] + $l['g'], 2); $pay[$sid]['amt'] = round($pay[$sid]['amt'] + $l['g'] - $fa, 2);
        $pay[$sid]['lines'][] = ['n' => $l['n'], 'g' => $l['g'], 'a' => $fa];
        if ($fa > 0) { $pay[$sid]['cuts']++; $pay[$sid]['feeRows'][] = ['g' => $l['g'], 'a' => $fa, 'm' => $fm]; $fee = round($fee + $fa, 2); }
        if ($tiers) $pay[$sid]['ft'] = $tiers; }
    foreach ($pay as $sid => $px) $splits[] = ['staff' => $sid, 'tech' => $px['tech'], 'amt' => $px['gross']];
    if ($fee > 0) { if (isset($pay[$feeTo])) $pay[$feeTo]['amt'] = round($pay[$feeTo]['amt'] + $fee, 2);
        else $pay[$feeTo] = ['staff' => $feeTo, 'tech' => $names[$feeTo] ?? staff_name($feeTo), 'amt' => $fee, 'gross' => 0.0, 'cuts' => 0, 'feeOnly' => true]; }
    foreach ($pay as $sid => $px) $pay[$sid]['fee'] = $sid === $feeTo ? $fee : 0;
    $txt = fn(array $rows) => implode(' · ', array_map(fn($p) => $p['tech'] . ' ' . usd((float)$p['amt']), array_filter($rows, fn($p) => (float)$p['amt'] > 0)));
    $before = $txt($old); $after = $txt(array_values($pay));
    q('UPDATE receipts SET splits = ?, pay_splits = ?, admin_fee = ? WHERE id = ?', [json_encode($splits, JSON_UNESCAPED_UNICODE), json_encode(array_values($pay), JSON_UNESCAPED_UNICODE), $fee, (int)$r['id']]);
    // the turn: a tech with money on this receipt but no visit of their own gets a turn by their money (as ADD PAY – turnq.php)
    if (!$quiet) { $l2 = json_decode((string)setting('turn_split_ids'), true); $l2 = is_array($l2) ? array_map('intval', $l2) : []; if (!in_array((int)$r['id'], $l2, true)) { $l2[] = (int)$r['id']; set_setting('turn_split_ids', json_encode(array_values($l2))); }
    audit('receipt_techs', 'Receipt #' . $r['rno'], $before, $after, 'Techs of the receipt changed'); }
    if (function_exists('chg_bump')) chg_bump();
    $who = array_unique(array_merge(array_map(fn($p) => (int)$p['staff'], $old), array_keys($pay)));
    try { require_once APP_ROOT . '/inc/push.php'; foreach ($who as $sid) if ($sid && $sid !== $feeTo) push_notify('staff:' . $sid, 'pay', 'Receipt #' . $r['rno'] . ' changed', ['title' => '💵 Your money changed', 'body' => 'Receipt #' . $r['rno'] . ' was fixed by the owner – your part: ' . usd((float)($pay[$sid]['amt'] ?? 0)) . '. Open ' . app_names()['tech'] . ' to see it.', 'url' => '../tech/']); } catch (Throwable $e) { error_log('receipt_lines_edit push: ' . $e->getMessage()); }
    try { require_once __DIR__ . '/cal-sync.php'; cal_sync_receipt((int)$r['id'], 'techs on the receipt changed'); } catch (Throwable $e) { error_log('cal_sync: ' . $e->getMessage()); } // (2.99.296 – order 513)
    return ['before' => $before, 'after' => $after];
}
/** (2.99.345 – lệnh 580, anh Logan 21/10 15:17) ✎ SỬA TIỀN DỊCH VỤ on a PAID receipt (owner only): the price of each service line (the same lines as "Who did
    each service": [staff, name, money] – the techs cannot change here). The total changes by the difference; the difference MUST say how it was paid:
    + more: "collected" Card / Cash → a NEW payment line on the receipt (the old payment lines never change), subtotal / tax / total up;
      the $1 rule, each tech's money, Payroll / 1099 / Report / Close day of the RECEIPT's day worked out again (receipt_lines_edit) – tips untouched;
    − less: the Refund that exists (receipt_refund – the techs whose lines went down give it back; it counts on the day it is made).
    A reason is a must. Not on a void receipt / a closed day 🔒 / a closed payroll week ("reopen it first"). THE TURN NEVER CHANGES: the old money is kept
    on the lines for the turn (items 'tp', splits 'ta' – turnq.php). Money & security log + "✎ Money edited … by …" on the receipt. */
function receipt_money_lines(array $r): array {
    $ps = json_decode((string)($r['pay_splits'] ?? ''), true); $L = [];
    $nm = []; $sn = receipt_split_names($r); foreach (receipt_splits($r) as $i => $x) $nm[(int)$x['staff']] = (string)($sn[$i] ?? 'Service'); // "Deluxe Pedicure" – not just "Service"
    if (is_array($ps) && $ps) { foreach ($ps as $x) { if (!empty($x['feeOnly'])) continue; $ls = !empty($x['lines']) ? $x['lines'] : [['n' => $nm[(int)$x['staff']] ?? 'Service', 'g' => (float)($x['gross'] ?? $x['amt'])]];
        foreach ($ls as $l) $L[] = ['staff' => (int)$x['staff'], 'n' => (string)($l['n'] ?? 'Service') ?: 'Service', 'g' => round((float)($l['g'] ?? 0), 2)]; } }
    else foreach (receipt_splits($r) as $x) $L[] = ['staff' => (int)$x['staff'], 'n' => $nm[(int)$x['staff']] ?? 'Service', 'g' => round((float)$x['amt'], 2)];
    return $L;
}
function receipt_money_edit(array $r, array $in): array {
    if ($r['status'] !== 'paid') fail('This receipt is void.');
    $reason = trim(mb_substr((string)($in['reason'] ?? ''), 0, 160)); if (mb_strlen($reason) < 3) fail(TV('Type the reason (e.g. "Wrong price – card was $155").', 'Ghi lý do (vd "Nhập sai giá – thẻ quẹt $155").'));
    $how = (string)($in['how'] ?? ''); if (!in_array($how, ['Card', 'Cash'], true)) fail(TV('Choose how the difference was paid: Card or Cash.', 'Chọn cách trả phần chênh lệch: Card hoặc Cash.'));
    $old = receipt_money_lines($r); if (!$old) fail('This receipt has no money for each tech.');
    $new = array_values(array_filter((array)($in['lines'] ?? []), 'is_array'));
    if (count($new) !== count($old)) fail(TV('The lines changed – open the receipt again.', 'Các dòng đã đổi – mở lại hoá đơn.'), 409);
    $L = []; $D = []; $chg = [];
    foreach ($old as $i => $o) { $n = $new[$i]; if ((int)($n['staff'] ?? 0) !== $o['staff']) fail(TV('The lines changed – open the receipt again.', 'Các dòng đã đổi – mở lại hoá đơn.'), 409);
        $g = round((float)($n['amt'] ?? 0), 2); if ($g < 0 || $g > 10000) fail('Check the money.');
        $L[] = ['staff' => $o['staff'], 'name' => $o['n'], 'amt' => $g];
        if (abs($g - $o['g']) > 0.004) { $D[$o['staff']] = round(($D[$o['staff']] ?? 0) + $g - $o['g'], 2); $chg[] = staff_name($o['staff']) . ' ' . $o['n'] . ' ' . usd($o['g']) . ' → ' . usd($g); } }
    $d = round(array_sum(array_column($L, 'amt')) - array_sum(array_column($old, 'g')), 2);
    if (!$chg || abs($d) < 0.005) fail(TV('Nothing changed – the total must change (to move money between techs: tap a tech).', 'Không có thay đổi – tổng phải khác (chuyển tiền giữa thợ: bấm vào thợ).'));
    foreach ($D as $sid => $v) if (($d > 0 && $v < -0.004) || ($d < 0 && $v > 0.004)) fail(TV('Raise OR lower prices in one edit, not both.', 'Mỗi lần sửa: chỉ tăng HOẶC chỉ giảm giá.'));
    $pct = (float)($r['tax_pct'] ?? 0); $dTax = (float)($r['tax'] ?? 0) > 0 && $pct > 0 ? round(abs($d) * $pct / 100, 2) : 0.0; $pay = round(abs($d) + $dTax, 2);
    $oldTotal = (float)$r['total'];
    if ($d < 0) { // − less: the Refund that exists, on the techs whose lines went down
        if ((float)$r['refund'] > 0.004) fail(TV('This receipt already has a refund – refund the difference instead (Refund).', 'Hoá đơn đã có refund – hoàn phần chênh lệch bằng Refund.')); // (2.99.639a QA-0012) the line prices never change on a refund: lowering again refunded twice
        require_once __DIR__ . '/payroc-pay.php'; if (pr_receipt_pay($r)) fail(TV('This receipt was paid on Payroc – give the difference back with Refund (Payroc gives it back on the card).', 'Hoá đơn trả qua Payroc – hoàn phần chênh lệch bằng Refund (Payroc tự trả về thẻ).'), 409); /* (2.99.645a) */
        require_once __DIR__ . '/dejavoo-back.php'; if (dv_receipt_p5($r)) fail(TV('This receipt was paid on the P5 – give the difference back with Refund (the P5 gives it back on the card).', 'Hoá đơn trả bằng máy P5 – hoàn phần chênh lệch bằng Refund (máy P5 tự trả về thẻ).'), 409); /* (2.99.638h e) a lower price here never reached the P5 */
        $amt = $pay; $taxPart = refund_tax_part($r, $amt, $how);
        $techs = []; foreach (alloc(round($amt - $taxPart, 2), array_map(fn($v) => abs($v), $D)) as $sid => $v) if ($v > 0) $techs[] = ['staff' => (int)$sid, 'amt' => $v];
        $rf = receipt_refund($r, $amt, $how, 'Sửa tiền dịch vụ: ' . $reason, $techs);
        $newTotal = round($oldTotal - $amt, 2); $txt = '−' . usd($amt) . ' ' . $how . ' (refund)';
    } else { // + more: worked out again on the receipt's day; a NEW payment line
        if ((float)$r['refund'] > 0.004) fail(TV('This receipt has a refund – the prices cannot go up.', 'Hoá đơn đã có refund – không tăng giá được.'));
        day_open_or_fail((string)$r['day'], 'Sửa tiền dịch vụ');
        if (payroll_week_closed((string)$r['day'])) fail(TV('Payroll for that week is closed – reopen it first.', 'Tuần lương đó đã chốt – mở lại trước.'), 409);
        $sp0 = []; foreach (receipt_splits($r) as $x) $sp0[(int)$x['staff']] = round((float)($x['ta'] ?? $x['amt']), 2);
        $tl0 = []; foreach ($old as $o) $tl0[$o['staff']][] = $o['g']; foreach (json_decode((string)($r['pay_splits'] ?? ''), true) ?: [] as $px) if (!empty($px['tl'])) $tl0[(int)$px['staff']] = array_map('floatval', (array)$px['tl']); // (582) the turn's lines as at Checkout
        receipt_lines_edit($r, array_map(fn($l) => ['staff' => $l['staff'], 'name' => $l['name'], 'amt' => $l['amt']], $L), round(array_sum(array_column($L, 'amt')), 2), true);
        $r2 = receipt_get((int)$r['id']);
        $sp = receipt_splits($r2); foreach ($sp as $i => $x) if (isset($sp0[(int)$x['staff']])) $sp[$i]['ta'] = $sp0[(int)$x['staff']]; // the turn keeps the old money
        $items = json_decode((string)$r2['items'], true) ?: [];
        foreach ($D as $sid => $v) { $idx = array_keys(array_filter($items, fn($l) => (int)($l['staff'] ?? 0) === (int)$sid && (float)($l['price'] ?? 0) > 0.004)); if (!$idx) continue;
            $k = $idx[0]; foreach ($old as $j => $o) if ($o['staff'] === (int)$sid && abs($L[$j]['amt'] - $o['g']) > 0.004) { foreach ($idx as $c) if ((string)($items[$c]['name'] ?? '') === $o['n'] && abs((float)$items[$c]['price'] - $o['g']) < 0.006) { $k = $c; break; } break; }
            if (!isset($items[$k]['tp'])) $items[$k]['tp'] = round((float)$items[$k]['price'], 2); $items[$k]['price'] = round((float)$items[$k]['price'] + $v, 2); }
        $ps2 = json_decode((string)$r2['pay_splits'], true) ?: []; foreach ($ps2 as $i => $px) if (empty($px['feeOnly']) && isset($tl0[(int)$px['staff']])) $ps2[$i]['tl'] = $tl0[(int)$px['staff']];
        q('UPDATE receipts SET pay_splits = ? WHERE id = ?', [json_encode($ps2, JSON_UNESCAPED_UNICODE), (int)$r['id']]);
        $pays = json_decode((string)$r2['pays'], true) ?: [];
        $pays[] = ['m' => $how, 'amt' => $pay, 'add' => 1, 'at' => now_str(), 'by' => actor_name(), 'note' => mb_substr($reason, 0, 80)] + ($how === 'Cash' ? ['given' => $pay, 'change' => 0] : ['last4' => '']);
        $col = $how === 'Card' ? 'card_amt' : 'cash_amt';
        q("UPDATE receipts SET items = ?, splits = ?, pays = ?, subtotal = subtotal + ?, tax = tax + ?, total = total + ?, $col = $col + ? WHERE id = ?",
            [json_encode($items, JSON_UNESCAPED_UNICODE), json_encode($sp, JSON_UNESCAPED_UNICODE), json_encode($pays, JSON_UNESCAPED_UNICODE), $d, $dTax, $pay, $pay, (int)$r['id']]);
        $newTotal = round($oldTotal + $pay, 2); $txt = '+' . usd($pay) . ' ' . $how; $rf = null;
    }
    audit('receipt_money', 'Receipt #' . $r['rno'] . ' · ' . $r['customer_name'], 'Tổng ' . usd($oldTotal), 'Tổng ' . usd($newTotal),
        'Sửa tiền hoá đơn #' . $r['rno'] . ': ' . implode('; ', $chg) . '; tổng ' . usd($oldTotal) . ' → ' . usd($newTotal) . '; ' . $txt . '; lý do ' . $reason . '; turn không đổi');
    if (function_exists('chg_bump')) chg_bump();
    return ['before' => $oldTotal, 'after' => $newTotal, 'diff' => $d > 0 ? $pay : -$pay, 'how' => $how, 'changes' => $chg, 'refund' => $rf];
}
/** (2.99.345 – lệnh 580) "✎ Money edited Oct 21 3:05 PM by Owner" on the receipt (the last one). */
function receipt_money_edited(array $r): string {
    try { $a = q("SELECT at, who FROM audit_log WHERE kind = 'receipt_money' AND target LIKE ? ORDER BY id DESC LIMIT 1", ['Receipt #' . $r['rno'] . ' ·%'])->fetch(); } catch (Throwable $e) { return ''; }
    return $a ? '✎ Money edited ' . date('M j g:i A', strtotime((string)$a['at'])) . ' by ' . $a['who'] : '';
}
/** (2.99.199 – order 398) "Techs edited 5:02 PM by LOGAN" on the receipt (the last change). */
function receipt_techs_edited(array $r): string {
    try { $a = q("SELECT at, who FROM audit_log WHERE kind = 'receipt_techs' AND target = ? ORDER BY id DESC LIMIT 1", ['Receipt #' . $r['rno']])->fetch(); } catch (Throwable $e) { return ''; }
    return $a ? 'Techs edited ' . date('M j g:i A', strtotime((string)$a['at'])) . ' by ' . $a['who'] : '';
}
