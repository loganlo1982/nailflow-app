<?php
/* (2.99.645a - LENH PAYROC) Checkout -> Card -> "Card on Payroc": the card part goes to the Payroc device FIRST (Payroc Cloud); the receipt is saved only
   after Payroc says APPROVED (instruction completed + payment responseCode "A"). One Payroc payment per ticket (key = its appointment ids):
   tapping twice, a lost answer, a closed tab NEVER charges twice – an open try is asked first (same instruction / same Idempotency-Key);
   an approved payment waits (setting pr_pend) until checkout_save uses it (same DB transaction as the receipt). Only when pr_on = 1 and Payroc is set up.
   Separate from Dejavoo (dv_*): its own list, lock and journal. */
declare(strict_types=1);
require_once __DIR__ . '/payroc.php';

const PR_PEND_KEEP = 200;
function pr_pend(): array { $p = json_decode((string)setting('pr_pend'), true); return is_array($p) ? $p : []; }
function pr_pend_put(string $ref, array $row): void {
    $p = pr_pend(); $p[$ref] = $row + ($p[$ref] ?? []);
    if (count($p) > PR_PEND_KEEP) { uasort($p, fn($a, $b) => strcmp((string)($a['at'] ?? ''), (string)($b['at'] ?? ''))); while (count($p) > PR_PEND_KEEP) { $k = array_key_first($p); if (in_array($p[$k]['st'] ?? '', ['paid', 'wait', 'unsure'], true)) break; unset($p[$k]); } }
    set_setting('pr_pend', json_encode($p, JSON_UNESCAPED_UNICODE));
}
function pr_key(array $ids): string { $i = array_values(array_unique(array_filter(array_map('intval', $ids)))); sort($i); return $i ? 'T' . implode('-', $i) : ''; }
function pr_pay_on(): bool { return pr_on() && pr_dev_ready(); }
function pr_card_out(string $ref, array $r): array { return ['ref' => $ref, 'amt' => (float)$r['amt'], 'last4' => (string)($r['last4'] ?? ''), 'card' => (string)($r['card'] ?? ''), 'approval' => (string)($r['approval'] ?? '')]; }
function pr_wait_s(): int { return max(1, min(PR_WAIT, (int)(cfg()['pr_wait'] ?? PR_WAIT))); }
/** The answer of an instruction -> the pending row (paid / failed / still waiting / unsure). */
function pr_apply_result(string $ref, array $row, array $s): array {
    if ($s['status'] === 'approved') {
        $row = ['st' => 'paid', 'amt' => $s['authorized'] !== null ? (float)$s['authorized'] : (float)$row['amt'], 'want' => (float)$row['amt'], 'pay' => (string)$s['payment_id'], 'last4' => (string)$s['last4'], 'card' => (string)$s['card'], 'approval' => (string)$s['approval'], 'paid_at' => now_str()] + $row;
        pr_pend_put($ref, $row);
        audit('payroc', 'Payroc card ' . usd((float)$row['amt']), '', 'approved · ' . ($row['card'] ?: 'card') . ($row['last4'] !== '' ? ' ··' . $row['last4'] : '') . ' · approval ' . $row['approval'] . ' · payment ' . $row['pay'] . ' · order ' . $ref . ' · ' . ($row['key'] ?? ''));
        return $row;
    }
    $st = in_array($s['status'], ['declined', 'cancelled', 'failure', 'not_found'], true) ? 'failed' : ($s['status'] === 'waiting' ? 'wait' : 'unsure');
    $row = ['st' => $st, 'why' => $s['status'], 'msg' => (string)($s['msg'] ?? '')] + $row; pr_pend_put($ref, $row); return $row;
}
/** Ask again about an open try of this ticket (never a 2nd sale while one may be on the device). */
function pr_recheck(string $ref, array $r, int $wait): array {
    $instr = (string)($r['instr'] ?? '');
    if ($instr === '' && ($r['idem'] ?? '') !== '') { $x = pr_sale_send((float)$r['amt'], $ref, (string)$r['idem'], (string)($r['by'] ?? '')); /* the SAME Idempotency-Key: the gateway gives back the first instruction, never a 2nd */
        if ($x['status'] !== 'sent') return pr_apply_result($ref, $r, ['status' => $x['status'] === 'error' && ($x['http'] ?? 0) >= 400 && ($x['http'] ?? 0) < 500 && ($x['http'] ?? 0) !== 409 ? 'failure' : 'unknown', 'msg' => $x['msg']]);
        $instr = $x['instr']; $r['instr'] = $instr; pr_pend_put($ref, ['instr' => $instr]); }
    return pr_apply_result($ref, $r, pr_instr_result('payment', $instr, $wait));
}
function pr_fail_for(array $row): void {
    if (($row['st'] ?? '') === 'wait') fail('The customer is still on the Payroc device. When it is done, tap Pay again – it is checked first, never charged twice. (Or Stop it on the device.)', 409);
    if (($row['st'] ?? '') === 'unsure') fail('Not sure the card was charged (' . ($row['msg'] ?: 'no answer') . '). Tap Pay again to check – it asks Payroc first, never charges twice.', 409);
    $why = ['declined' => 'Card declined.', 'cancelled' => 'Cancelled on the device.', 'failure' => 'Payroc could not run it' . (($row['msg'] ?? '') !== '' ? ' (' . $row['msg'] . ')' : '') . '.', 'not_found' => 'Payroc did not find the payment.'][$row['why'] ?? ''] ?? 'Not approved.';
    fail($why, 402);
}
/** The desk taps Pay with "Card on Payroc": charge $amt for this ticket (or give back the payment already approved for it). */
function pr_charge(array $ids, float $amt): array {
    if (!pr_pay_on()) fail('Card on Payroc is off (Settings → Payments).', 400);
    $key = pr_key($ids); $amt = round($amt, 2); if ($key === '' || $amt < 0.01 || $amt > 20000) fail('Check the amount.');
    app_lock('payroc'); /* a 2nd tap waits here, then finds the 1st payment */
    if (session_status() === PHP_SESSION_ACTIVE) @session_write_close();
    $wait = pr_wait_s(); ignore_user_abort(true); @set_time_limit($wait + 120);
    foreach (pr_pend() as $ref => $r) {
        if (($r['key'] ?? '') !== $key) continue;
        if (in_array($r['st'] ?? '', ['wait', 'unsure'], true)) { $r = pr_recheck((string)$ref, $r, min($wait, 60)); if (in_array($r['st'], ['wait', 'unsure'], true)) pr_fail_for($r); }
        if (($r['st'] ?? '') === 'paid') {
            if (abs((float)$r['amt'] - $amt) < 0.005) return pr_card_out((string)$ref, $r) + ['again' => true];
            json_out(['error' => 'Payroc already took ' . usd((float)$r['amt']) . ' for this ticket (not ' . usd($amt) . '). Cancel it first, or pay ' . usd((float)$r['amt']) . '.', 'prPaid' => pr_card_out((string)$ref, $r)], 409);
        }
    }
    $ref = pr_new_order(); $row = ['key' => $key, 'amt' => $amt, 'st' => 'unsure', 'at' => now_str(), 'by' => actor_name(), 'idem' => pr_uuid()];
    pr_pend_put($ref, $row); /* saved BEFORE the call: a lost answer is asked again with the same key */
    $x = pr_sale_send($amt, $ref, $row['idem'], (string)$row['by']);
    if ($x['status'] !== 'sent') { $row = pr_apply_result($ref, $row, ['status' => $x['status'] === 'unknown' ? 'unknown' : 'failure', 'msg' => $x['msg']]); pr_fail_for($row); }
    $row['instr'] = $x['instr']; pr_pend_put($ref, ['instr' => $x['instr'], 'st' => 'wait']);
    $row = pr_apply_result($ref, $row, pr_instr_result('payment', $x['instr'], $wait));
    if ($row['st'] !== 'paid') pr_fail_for($row);
    if (abs((float)$row['amt'] - $amt) >= 0.005) json_out(['error' => 'Payroc took ' . usd((float)$row['amt']) . ', the ticket says ' . usd($amt) . '. Check it (cancel it if it is wrong).', 'prPaid' => pr_card_out($ref, $row)], 409);
    return pr_card_out($ref, $row);
}
/** Stop the try still waiting on the device for this ticket. */
function pr_stop(array $ids): array {
    app_lock('payroc'); $key = pr_key($ids);
    foreach (pr_pend() as $ref => $r) {
        if (($r['key'] ?? '') !== $key || !in_array($r['st'] ?? '', ['wait', 'unsure'], true) || ($r['instr'] ?? '') === '') continue;
        $c = pr_instr_cancel('payment', (string)$r['instr']);
        if ($c['ok']) { pr_pend_put((string)$ref, ['st' => 'failed', 'why' => 'cancelled']); return ['ok' => true, 'stopped' => true]; }
        $r = pr_recheck((string)$ref, $r, 5); /* too late: it finished – its result */
        return ['ok' => true, 'stopped' => false, 'st' => $r['st']] + ($r['st'] === 'paid' ? ['prPaid' => pr_card_out((string)$ref, $r)] : []);
    }
    return ['ok' => true, 'stopped' => false, 'st' => 'none'];
}
/** checkout_save: the approved Payroc payment of THIS ticket and THIS amount, not used yet. */
function pr_take(string $ref, array $ids, float $amt): array {
    $r = pr_pend()[$ref] ?? null;
    if (!$r || ($r['st'] ?? '') !== 'paid') fail('The Payroc payment was not approved (or was used already) – tap Pay again.', 409);
    if (($r['key'] ?? '') !== pr_key($ids)) fail('That Payroc payment is for another ticket.', 409);
    if (abs((float)$r['amt'] - round($amt, 2)) >= 0.005) fail('The card part (' . usd($amt) . ') is not what Payroc took (' . usd((float)$r['amt']) . ').', 409);
    return $r;
}
function pr_used(string $ref, int $rno): void { pr_pend_put($ref, ['st' => 'used', 'rno' => $rno, 'used_at' => now_str()]); }
/** "Cancel on Payroc" for a payment approved but not on a receipt (Void = reverse, open batch). */
function pr_cancel(string $ref): array {
    app_lock('payroc');
    $r = pr_pend()[$ref] ?? null; if (!$r || ($r['st'] ?? '') !== 'paid') fail('Nothing to cancel (no Payroc payment waiting).', 404);
    $idem = (string)($r['videm'] ?? ''); if ($idem === '') { $idem = pr_uuid(); pr_pend_put($ref, ['videm' => $idem]); }
    $v = pr_reverse((string)$r['pay'], null, $idem);
    if (!$v['ok']) fail('Payroc did not cancel it (' . $v['msg'] . '). Nothing was changed.', 409);
    pr_pend_put($ref, ['st' => 'void', 'void_at' => now_str()]);
    audit('payroc', 'Payroc card ' . usd((float)$r['amt']), 'approved', 'cancelled (reverse) · payment ' . $r['pay'] . ' · order ' . $ref . ' · ' . ($r['key'] ?? ''));
    return ['ok' => true];
}
function pr_waiting(): array { $o = []; foreach (pr_pend() as $ref => $r) if (($r['st'] ?? '') === 'paid') $o[] = pr_card_out((string)$ref, $r) + ['key' => (string)($r['key'] ?? ''), 'at' => (string)($r['paid_at'] ?? $r['at'] ?? '')]; return $o; }

/* ---------- a receipt paid on Payroc: Void / Refund give the money back on Payroc by themselves; anything not approved -> the receipt is NOT changed ---------- */
function pr_receipt_pay(array $r): array { $o = []; foreach ((json_decode((string)$r['pays'], true) ?: []) as $p) if (($p['m'] ?? '') === 'Card' && !empty($p['pr']['ref'])) $o[] = $p['pr'] + ['pay_amt' => (float)$p['amt']]; return $o; }
function pr_money_back(array $r, string $action, float $cardBack): string {
    $pp = pr_receipt_pay($r); if (!$pp) return '';
    if (!pr_ready()) fail('This receipt was paid on Payroc, but Payroc is not set up now – NailFlow must set it up first. Nothing was changed.', 409);
    if (session_status() === PHP_SESSION_ACTIVE) @session_write_close(); ignore_user_abort(true); @set_time_limit(pr_wait_s() + 150);
    app_lock('payroc'); $pend = pr_pend(); $done = [];
    $sum = round(array_sum(array_map(fn($x) => (float)($x['amt'] ?? $x['pay_amt']), $pp)), 2);
    $refund = function (float $amt, string $why) use ($r): string {
        $ord = pr_new_order(); $idem = pr_uuid(); $x = pr_refund_send($amt, $ord, $idem, 'Receipt #' . (int)$r['rno'] . ' ' . $why);
        if ($x['status'] !== 'sent') fail('Payroc did not start the refund (' . $x['msg'] . '). The receipt was NOT changed.', 402);
        $s = pr_instr_result('refund', $x['instr'], pr_wait_s());
        if ($s['status'] !== 'approved') fail('Payroc did not give ' . usd($amt) . ' back (' . ($s['status'] === 'waiting' ? 'the customer is still on the device' : ($s['msg'] ?: $s['status'])) . '). The receipt was NOT changed.', 402);
        pr_pend_put($ord, ['key' => 'R' . (int)$r['rno'], 'amt' => $amt, 'st' => 'refund', 'at' => now_str(), 'rno' => (int)$r['rno'], 'instr' => $x['instr'], 'pay' => (string)$s['payment_id'], 'approval' => (string)$s['approval']]);
        audit('payroc', 'Payroc refund ' . usd($amt), '', 'approved · receipt #' . $r['rno'] . ' · ' . $why . ' · order ' . $ord); return 'refund ' . $ord; };
    $void = function (array $x) use ($r, &$pend): bool {
        $ref = (string)$x['ref']; if (($pend[$ref]['st'] ?? '') === 'voided') return true;
        $idem = (string)($pend[$ref]['videm'] ?? ''); if ($idem === '') { $idem = pr_uuid(); pr_pend_put($ref, ['videm' => $idem]); }
        $v = pr_reverse((string)$x['pay'], null, $idem); if (!$v['ok']) return false;
        pr_pend_put($ref, ['st' => 'voided', 'void_at' => now_str(), 'rno' => (int)$r['rno']]); audit('payroc', 'Payroc void ' . usd((float)($x['amt'] ?? $x['pay_amt'])), 'approved', 'reversed · receipt #' . $r['rno'] . ' · payment ' . $x['pay']); return true; };
    if ($action === 'receipt_void') {
        if (abs($sum - $cardBack) >= 0.005) fail('This receipt has a Payroc payment of ' . usd($sum) . ' but ' . usd($cardBack) . ' on card – give the card money back by hand on the right machine. Nothing was changed.', 409);
        foreach ($pp as $x) { if ($void($x)) { $done[] = 'void ' . $x['ref']; continue; } $done[] = $refund(round((float)($x['amt'] ?? $x['pay_amt']), 2), 'void after the batch closed'); pr_pend_put((string)$x['ref'], ['st' => 'returned', 'rno' => (int)$r['rno']]); }
        return implode(', ', $done);
    }
    $back = 0.0; foreach ((json_decode((string)$r['refunds'], true) ?: []) as $f) if (($f['how'] ?? '') === 'Card') $back += (float)$f['amt'];
    if (round($cardBack, 2) > round($sum - $back, 2) + 0.004) fail('Payroc took ' . usd($sum) . ' on this receipt' . ($back > 0 ? ' and ' . usd($back) . ' already went back' : '') . ' – at most ' . usd(max(0, round($sum - $back, 2))) . ' can go back on the card. Nothing was changed.', 400);
    if (count($pp) === 1 && abs(round((float)($pp[0]['amt'] ?? $pp[0]['pay_amt']), 2) - round($cardBack, 2)) < 0.005 && $void($pp[0])) return 'void ' . $pp[0]['ref'];
    return $refund(round($cardBack, 2), 'refund');
}
