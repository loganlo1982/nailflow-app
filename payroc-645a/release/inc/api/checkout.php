<?php
// (2.99.139) api.php actions – this group only; api.php decides which file to load (API_ROUTES). Variables ($in, $method, $action…) are api.php's.
declare(strict_types=1);
if (!defined('API_MAIN')) { http_response_code(404); exit; }
switch ($action) {


case 'checkout': // the old checkout (no receipt) is gone: every payment goes through the Checkout ticket and makes a receipt (2.25)
    need_desk();
    fail('Please reload the page – checkout now makes a receipt.');

/* ---------- Checkout with receipts (owner or manager; Void / Refund: owner only) ---------- */
case 'ticket': // the Checkout screen for an appointment: everyone paid together, services with prices, techs, offers
    need_desk();
    require_once APP_ROOT . '/inc/person-edit.php'; if (empty($_GET['peek'])) co_hold_mark((int)($_GET['id'] ?? 0), true); // (2.99.295 – order 512) this customer is in Checkout: no popup edit
    // (2.99.434 – CHAT 27/10 17:42, ca AMBER) opening Checkout to LOOK is not "done" any more (was 2.99.312 – lệnh 532 mục 1: te_co_done here). Done = paid
    // (Card / Cash / Gift: checkout_save) or the tech / the desk taps Service done.
    desk_out(ticket_data(get_appt((int)($_GET['id'] ?? 0))) + ['salon' => salon_info(), 'dvOn' => setting('dv_on') === '1' /* (2.99.638c) Card on the P5 */, 'prOn' => setting('pr_on') === '1' /* (2.99.645a) Card on Payroc */]); // (2.99.93) no phone on the desk

case 'visit_merge': // (2.99.269 – order 479) the desk: two cards that are ONE customer (split by mistake) → one card / one Checkout (asked first on the page)
case 'visit_split': // … and back: this visit is a person of its own
    need_desk(); if ($method !== 'POST') fail('POST only', 405);
    require_once APP_ROOT . '/inc/custkey.php';
    $x = get_appt((int)($in['id'] ?? 0)); if ($x['status'] !== 'arrived') fail('Only a customer who is here (checked in, not paid).');
    $sep = cust_sep_ids();
    if ($action === 'visit_merge') {
        $y = get_appt((int)($in['into'] ?? 0)); if ((int)$y['id'] === (int)$x['id'] || $y['status'] !== 'arrived' || $y['appt_date'] !== $x['appt_date']) fail('Pick another customer of today who is here.');
        $root = (int)($y['split_of'] ?? 0) ?: (int)$y['id'];
        $ids = array_map(fn($r) => (int)$r['id'], array_filter(q("SELECT * FROM appointments WHERE appt_date = ? AND status = 'arrived' AND kind = 'appt'", [$x['appt_date']])->fetchAll(), fn($r) => cust_key($r) === cust_key($x)));
        foreach ($ids as $i) { if ($i !== $root) q('UPDATE appointments SET split_of = ? WHERE id = ?', [$root, $i]); appt_log(get_appt($i), 'cust_merge', 'Merged with ' . (string)$y['customer_name'] . ' (one customer)'); }
        $sep = array_values(array_diff($sep, $ids, [$root]));
    } else {
        require_once APP_ROOT . '/inc/visit-split.php'; visit_split_root($x); // (2.99.293) Split pressed on the root of a merge
        q('UPDATE appointments SET split_of = 0 WHERE id = ? AND split_of > 0', [(int)$x['id']]); if (!in_array((int)$x['id'], $sep, true)) $sep[] = (int)$x['id'];
        appt_log($x, 'cust_split', 'A person of their own (desk)');
    }
    set_setting('cust_sep', json_encode(array_slice(array_values(array_unique($sep)), -300)));
    json_out(['ok' => true]);

case 'checkout2': // a paid ticket: its receipt
    need_desk();
    // (2.99.88) all or nothing: a problem half-way (a gift card short, a closed day…) saves nothing at all
    app_lock('money'); /* (2.99.457 – rà soát) wait for the other device BEFORE the transaction: MySQL then reads the appointments as they are now (already paid → "already paid"), not as they were */
    db()->beginTransaction();
    try { $rc = checkout_save($in); require_once APP_ROOT . '/inc/payroll.php'; payroll_carry((string)$rc['day'], 'Receipt #' . $rc['rno'] . ' paid after the week was closed'); /* (2.99.447 – rà soát) Payroll closed early (force) + a checkout the same week: the tech's part goes into next week's adjustments (as Void does) – nothing when the week is open */ if (db()->inTransaction()) db()->commit(); }
    catch (Throwable $e) { if (db()->inTransaction()) db()->rollBack(); throw $e; }
    if (desk_req()) audit('desk_money', 'Receipt #' . $rc['rno'] . ' · ' . $rc['customer_name'], '', 'Checkout ' . usd((float)$rc['total']) . ' · by ' . actor_name() . ' · Front desk iPad'); // (2.99.89) who, when, which iPad (+ its address)
    desk_out(['ok' => true, 'receipt' => receipt_out($rc, true), 'salon' => salon_info()]);

case 'unpaid_earlier': // (2.99.133) SO-LUAT: checked in / in service / Service done on an EARLIER day and not paid → Checkout "Unpaid from …" until paid (owner + manager + Front desk)
    need_desk();
    $rows = [];
    foreach (unpaid_earlier_appts() as $a) {
        $rows[] = ['id' => (int)$a['id'], 'date' => (string)$a['appt_date'], 'start' => (int)$a['start_min'], 'name' => (string)$a['customer_name'],
            'tech' => (int)$a['staff_id'] ? staff_name((int)$a['staff_id']) : 'ANYONE', 'services' => appt_label($a), 'done' => (string)$a['done_at'] !== ''];
    }
    json_out(['rows' => $rows]);

case 'unpaid_visits': // (2.86) checked in but never checked out on the web (2+ hours after the end), the last 60 days – owner only; nothing is changed
    need_admin();
    /* (2.99.62) Checkout is always on */ // (2.99.25) "Use Checkout" off: the list is not shown
    $rows = [];
    foreach (q("SELECT * FROM appointments WHERE kind = 'appt' AND status = 'arrived' AND appt_date >= ? AND appt_date <= ? ORDER BY appt_date DESC, start_min", [date('Y-m-d', strtotime('-60 days')), date('Y-m-d')])->fetchAll() as $a) {
        if (appt_ts($a) + ((int)$a['duration'] + 120) * 60 > time() || before_checkout_day((string)$a['appt_date'])) continue; // (2.99.82) before Checkout started: not listed (2.99.133: not set = listed)
        $rows[] = ['id' => (int)$a['id'], 'date' => $a['appt_date'], 'start' => (int)$a['start_min'], 'name' => (string)$a['customer_name'],
            'tech' => (int)$a['staff_id'] ? staff_name((int)$a['staff_id']) : 'Any tech', 'services' => appt_label($a)];
    }
    json_out(['rows' => $rows]);

case 'receipts': // one day's receipts, or found by name / phone / receipt # / card last 4 (owner); a manager: today only
    $role = need_desk();
    $day = (string)($_GET['day'] ?? date('Y-m-d'));
    if (!valid_date($day)) fail('Bad date');
    $term = (string)($_GET['q'] ?? '');
    if ($role !== 'admin') { $day = date('Y-m-d'); $term = ''; }
    desk_out(['day' => $day, 'today' => date('Y-m-d'), 'rows' => array_map(fn($r) => receipt_out($r), receipts_find($day, $term)), 'salon' => salon_info()]); // (2.99.142) AN Desk: no phone numbers

case 'receipt':
    $role = need_desk();
    $r = receipt_get((int)($_GET['id'] ?? 0));
    if ($role !== 'admin' && $r['day'] !== date('Y-m-d')) fail("Only today's receipts.", 403);
    desk_out(['receipt' => receipt_out($r, true), 'salon' => salon_info()]);

case 'receipt_void':
case 'receipt_refund':
    need_admin();
    app_lock('money'); // (2.99.69) void / refund on 2 devices at once: one after the other
    $reason = trim(mb_substr((string)($in['reason'] ?? ''), 0, 160));
    if (mb_strlen($reason) < 3) fail('Write the reason.');
    $r = receipt_get((int)($in['id'] ?? 0));
    $carry = []; $rf = null;
    // (2.99.95) money that went on a card goes back on the DPS machine first: the desk ticks "Done on DPS" (Money & security log)
    $cardBack = $action === 'receipt_void' ? round((float)$r['card_amt'] + (float)$r['tip'] + (receipt_gift_sale_card($r) ? (float)((json_decode((string)$r['gift_sale'], true) ?: [])['by']['Card'] ?? 0) : 0), 2) : /* (2.99.627 L2) + the gift card sold on the bill (voided with it) */ (($in['how'] ?? '') === 'Card' ? round((float)($in['amount'] ?? 0), 2) : 0.0);
    require_once APP_ROOT . '/inc/dejavoo-back.php'; $dvP5 = $cardBack > 0.004 ? dv_receipt_p5($r) : []; // (2.99.638d) paid on the P5: the P5 gives it back by itself (below)
    require_once APP_ROOT . '/inc/payroc-pay.php'; $prPay = $cardBack > 0.004 ? pr_receipt_pay($r) : []; if ($prPay && $dvP5) fail('This receipt was paid on the P5 and on Payroc – give the card money back by hand. Nothing was changed.', 409); if ($prPay) $dvP5 = ['payroc']; /* (2.99.645a) paid on Payroc: Payroc gives it back by itself (below) */
    if ($cardBack > 0.004 && empty($in['dps_done']) && !$dvP5) fail('Refund ' . usd($cardBack) . ' on the DPS machine first, then tick "Done on DPS".');
    if ($cardBack > 0.004 && !$dvP5) /* (2.99.638d) */ $reason .= ' · ' . usd($cardBack) . ' back on DPS ✓';
    if ($action === 'receipt_void' && payroll_week_closed((string)$r['day']) && empty($in['ok_closed'])) fail('PAYROLL_CLOSED', 409);
    if ($action === 'receipt_refund' && payroll_week_closed(date('Y-m-d')) && empty($in['ok_closed'])) fail('PAYROLL_CLOSED', 409); // (2.99.639b QA-0011) a refund counts in TODAY's week: closed -> asked first, like Void // (2.99.59) a closed payroll week: asked first
    if ($dvP5) { if ($action === 'receipt_void') receipt_void_check($r); else receipt_refund_check($r, (float)($in['amount'] ?? 0), (string)($in['how'] ?? ''), $in['techs'] ?? null); } // (2.99.638d2 QA-0028) EVERY check of the receipt first: one that fails stops here, the P5 is never asked
    if ($prPay) { pr_money_back($r, $action, $cardBack); $reason .= ' · ' . usd($cardBack) . ' back on Payroc ✓'; } /* (2.99.645a) */
    elseif ($dvP5) { dv_money_back($r, $action, $cardBack); $reason .= ' · ' . usd($cardBack) . ' back on the P5 ✓'; } // (2.99.638d) after every check above, before anything is saved: the P5 says no -> nothing changes
    db()->beginTransaction(); // (2.99.92) all or nothing: a problem half-way changes nothing (the money, the techs' parts, the gift card, the rewards)
    try {
        if ($action === 'receipt_void') { receipt_void($r, $reason); $carry = payroll_carry((string)$r['day'], 'Receipt #' . $r['rno'] . ' voided – ' . $reason); }
        else $rf = receipt_refund($r, (float)($in['amount'] ?? 0), (string)($in['how'] ?? ''), $reason, $in['techs'] ?? null); // a refund counts in the week it is made
        if ($action === 'receipt_refund') $carry = payroll_carry(date('Y-m-d'), 'Receipt #' . $r['rno'] . ' refund – ' . $reason); // (2.99.639b QA-0011) today's week closed early: the techs' part goes into next week (as Void / Checkout / tips)
        if (db()->inTransaction()) db()->commit();
    } catch (Throwable $e) { if (db()->inTransaction()) db()->rollBack(); throw $e; }
    json_out(['ok' => true, 'receipt' => receipt_out(receipt_get((int)$r['id']), true), 'carry' => $carry, 'refund' => $rf, 'tipNote' => $action === 'receipt_void' ? tip_over_note((string)$r['day']) : '']);

case 'receipt_lines': // (2.99.199 – order 398) owner: Receipt → tap a tech / a line → who did each line (move, split, money); all worked out again
    need_admin();
    app_lock('money');
    if ($method !== 'POST') fail('POST only', 405);
    $r = receipt_get((int)($in['id'] ?? 0));
    db()->beginTransaction();
    try { $x = receipt_lines_edit($r, (array)($in['lines'] ?? [])); if (db()->inTransaction()) db()->commit(); }
    catch (Throwable $e) { if (db()->inTransaction()) db()->rollBack(); throw $e; }
    json_out(['ok' => true] + $x + ['receipt' => receipt_out(receipt_get((int)$r['id']), true)]);

case 'receipt_money': // (2.99.345 – lệnh 580) owner: ✎ Sửa tiền dịch vụ – the price of each line; + collected Card / Cash (a new payment line) · − the Refund
    need_admin();
    app_lock('money');
    if ($method !== 'POST') fail('POST only', 405);
    $r = receipt_get((int)($in['id'] ?? 0));
    db()->beginTransaction();
    try { $x = receipt_money_edit($r, $in); if ((float)(receipt_get((int)$r['id'])['refund'] ?? 0) > (float)$r['refund'] + 0.004) $x['carry'] = payroll_carry(date('Y-m-d'), 'Receipt #' . $r['rno'] . ' price lowered (refund)'); /* (2.99.639b QA-0011) */ if (db()->inTransaction()) db()->commit(); }
    catch (Throwable $e) { if (db()->inTransaction()) db()->rollBack(); throw $e; }
    json_out(['ok' => true] + $x + ['receipt' => receipt_out(receipt_get((int)$r['id']), true)]);

case 'receipt_addpay': // (2.99.198 – order 397) owner: a ticket with the owner's number → TEST ↔ ADD PAY
    need_admin();
    app_lock('money');
    if ($method !== 'POST') fail('POST only', 405);
    $r = receipt_get((int)($in['id'] ?? 0));
    $x = receipt_addpay($r, !empty($in['on']));
    json_out(['ok' => true] + $x + ['receipt' => receipt_out(receipt_get((int)$r['id']), true)]);

case 'receipt_fee_lines': // (2.99.194 – order 392) owner: one tech's money on a receipt → its service lines; the $1 rule again line by line (pay split only)
    need_admin();
    app_lock('money');
    if ($method !== 'POST') fail('POST only', 405);
    $r = receipt_get((int)($in['id'] ?? 0));
    db()->beginTransaction();
    try { $fx = receipt_fee_lines($r, (int)($in['staff'] ?? 0), (array)($in['lines'] ?? [])); if (db()->inTransaction()) db()->commit(); }
    catch (Throwable $e) { if (db()->inTransaction()) db()->rollBack(); throw $e; }
    json_out(['ok' => true, 'fix' => $fx, 'receipt' => receipt_out(receipt_get((int)$r['id']), true)]);

case 'refund_preview': // (2.99.59) the refund form: each tech's part (by their money) and the $1 that comes back
    need_admin();
    $r = receipt_get((int)($_GET['id'] ?? 0)); $amt = round((float)($_GET['amount'] ?? 0), 2);
    $typed = json_decode((string)($_GET['techs'] ?? ''), true);
    if ($amt <= 0) json_out(['techs' => [], 'fee' => []]);
    $taxPart = refund_tax_part($r, $amt, (string)($_GET['how'] ?? '')); // (2.99.88)
    [$parts, $fee] = refund_split($r, round($amt - $taxPart, 2), is_array($typed) && $typed ? $typed : null);
    json_out(['techs' => $parts, 'fee' => $fee, 'tax' => $taxPart, 'giftCode' => (string)$r['gift_code'] !== '' ? substr((string)$r['gift_code'], -4) : '']);

case 'tip_payout': // (2.99.59) Close day: pay a tech's card tips of that day in cash (Settings → Checkout, tax & payments → end of day); who / when kept
    need_admin();
    app_lock('money');
    if ($method !== 'POST') fail('POST only', 405);
    $day = (string)($in['day'] ?? '');
    if (!valid_date($day)) fail('Bad date');
    json_out(tip_payout_day($day, (int)($in['staff'] ?? 0)));

case 'money_report': // (2.99.54) Receipts → Report: each tech (services, $1 rows, after the $1 rule, tips) and the salon's totals; a manager: today only
    $role = need_desk();
    not_manager($role, "Only the owner can see each tech's money."); // (2.99.132) SO-LUAT: the manager never sees each tech's money
    $from = (string)($_GET['from'] ?? date('Y-m-d')); $to = (string)($_GET['to'] ?? $from);
    if (!valid_date($from) || !valid_date($to) || $from > $to) fail('Check the dates.');
    if ($role !== 'admin') $from = $to = date('Y-m-d');
    if ((strtotime($to) - strtotime($from)) / 86400 > 400) fail('At most about a year at a time.');
    json_out(money_report($from, $to));

case 'money_overview': // (2.99.191 – order 385) Tech report → Day / Week tabs, ONE load: the last weeks (salon's week = Payroll's) with each tech + the days of one week
    $role = need_desk();
    not_manager($role, "Only the owner can see each tech's money.");
    $day = (string)($_GET['day'] ?? date('Y-m-d')); if (!valid_date($day)) $day = date('Y-m-d');
    $n = max(2, min(12, (int)($_GET['weeks'] ?? 8))); $today = date('Y-m-d');
    $wk = function (string $f) { $t = payroll_week_end($f); $r = money_report($f, $t); $T = $r['totals'];
        return ['from' => $f, 'to' => $t, 'customers' => (int)$T['customers'], 'services' => round((float)$T['services'], 2), 'tips' => round((float)$T['tips'], 2), 'receipts' => (int)$T['receipts'],
            'techs' => array_map(fn($x) => ['staff' => (int)$x['staff'], 'name' => (string)$x['name'], 'customers' => (int)$x['customers'], 'services' => round((float)$x['services'], 2), 'tips' => round((float)$x['tips'], 2)], $r['techs'])]; };
    $cur = payroll_week_of($today); $weeks = []; // newest first; one more (the week before the oldest) for its ▲▼ %
    for ($i = 0; $i <= $n; $i++) $weeks[] = $wk(date('Y-m-d', strtotime($cur . ' -' . (7 * $i) . ' days')));
    $from = payroll_week_of($day); $days = [];
    for ($i = 0; $i < 7; $i++) { $d = date('Y-m-d', strtotime($from . ' +' . $i . ' days')); $T = $d > $today ? null : money_report($d, $d)['totals'];
        $days[] = ['day' => $d, 'services' => $T ? round((float)$T['services'], 2) : 0, 'receipts' => $T ? (int)$T['receipts'] : 0, 'closed' => hours_for($d) === null, 'future' => $d > $today]; }
    json_out(['today' => $today, 'week' => $from, 'weekTo' => payroll_week_end($from), 'days' => $days, 'weeks' => $weeks, 'feeName' => fee_cfg()['name']]);

case 'receipt_tips_edit': // (2.99.54) change the card / cash tips of a paid receipt (written in the Activity log and the Money & security log)
    need_admin();
    app_lock('money');
    if ($method !== 'POST') fail('POST only', 405);
    $r = receipt_get((int)($in['id'] ?? 0));
    if ($r['status'] !== 'paid') fail('This receipt is void.');
    day_open_or_fail((string)$r['day'], 'tips cannot be changed'); // (2.99.58)
    if (payroll_week_closed((string)$r['day']) && empty($in['ok_closed'])) fail('PAYROLL_CLOSED', 409); // (2.99.59)
    $staff = []; foreach (staff_list(false) as $x) $staff[(int)$x['id']] = $x['name'];
    [$tips, $tipSum] = tips_parse($in['tips'] ?? [], $staff, 'card', $in['tip_total'] ?? null);
    [$ctips, $ctipSum] = tips_parse($in['cash_tips'] ?? [], $staff, 'cash', $in['cash_tip_total'] ?? null);
    if (abs($tipSum - (float)$r['tip']) >= 0.005) { require_once APP_ROOT . '/inc/dejavoo-back.php'; if (dv_receipt_p5($r)) fail('This receipt was paid on the P5: its card tip cannot be changed here (the P5 would not match). Put the difference as a cash tip, or Void the receipt and pay again.'); require_once APP_ROOT . '/inc/payroc-pay.php'; if (pr_receipt_pay($r)) fail('This receipt was paid on Payroc: its card tip cannot be changed here (Payroc would not match). Put the difference as a cash tip, or Void the receipt and pay again.'); /* (2.99.645a) */ } // (2.99.638d)
    if ($tipSum > 0.004 && (float)$r['card_amt'] <= 0.004 && (float)$r['tip'] <= 0.004) fail('A card tip needs a card part – this receipt was not paid by card (put it as a cash tip).'); // (2.99.451 – rà soát) like Checkout: the DPS total never matches otherwise
    $before = 'card ' . usd((float)$r['tip']) . ', cash ' . usd((float)($r['cash_tip'] ?? 0));
    q('UPDATE receipts SET tip = ?, tips = ?, cash_tip = ?, cash_tips = ? WHERE id = ?', [$tipSum, json_encode($tips, JSON_UNESCAPED_UNICODE), $ctipSum, json_encode($ctips, JSON_UNESCAPED_UNICODE), $r['id']]);
    $ids = ids_list((string)$r['appt_ids']);
    if ($ids) { q('UPDATE appointments SET tip = 0, cash_tip = 0 WHERE receipt_id = ?', [$r['id']]); tips_to_appts($tips, $ids, 'tip'); tips_to_appts($ctips, $ids, 'cash_tip');
        $after = 'card ' . usd($tipSum) . ', cash ' . usd($ctipSum);
        foreach ($ids as $aid) { $a = q('SELECT * FROM appointments WHERE id = ?', [$aid])->fetch(); if ($a) appt_log($a, 'tip', 'Receipt #' . $r['rno'] . ' tips changed: ' . $before . ' → ' . $after); } }
    audit('tip_edit', 'Receipt #' . $r['rno'] . ' · ' . $r['customer_name'], $before, 'card ' . usd($tipSum) . ', cash ' . usd($ctipSum));
    $carry = payroll_carry((string)$r['day'], 'Receipt #' . $r['rno'] . ' tips changed'); // (2.99.59)
    json_out(['ok' => true, 'receipt' => receipt_out(receipt_get((int)$r['id']), true), 'carry' => $carry, 'tipNote' => tip_over_note((string)$r['day'])]); // (2.99.95)
}
