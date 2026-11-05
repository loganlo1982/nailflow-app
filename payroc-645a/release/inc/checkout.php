<?php
// Checkout: the ticket (each service with its tech and price, a discount, one offer) and its receipt. No tips and no sales tax here:
// customers tip their tech in cash, and the DPS card machine adds the tax – the web total = services − discount.
// The page never talks to the card machine (DPS / PAX S300): the desk types the amount on the machine and taps "Card approved".
// Only the last 4 digits of a card may be kept – never a card number. Receipts are never deleted: Void and Refund keep them with a reason.
// Each appointment on the ticket still gets its price, discount, tip and "paid" like before, so History, Reports, Turns and loyalty keep working.
declare(strict_types=1);
require_once __DIR__ . '/audit.php';
// (2.99.206 – order 407) checkout in parts (≤ ~60 KB each)
require_once __DIR__ . '/checkout-receipts.php';
require_once __DIR__ . '/checkout-day.php';
require_once __DIR__ . '/checkout-edit.php';
require_once __DIR__ . '/rewards.php'; // (2.99.82)

const PAY_OTHER = ['Zelle', 'Venmo', 'Other'];

/** Close day: the card total plus this % (7) to compare with the DPS machine, which adds the sales tax. */
/** Top of a printed receipt / close-day report. */
function salon_info(): array { return ['name' => setting('salon_name'), 'address' => setting('salon_address'), 'phone' => setting('salon_phone'),
    'logo' => logo_sized(192, '../'), 'paper' => receipt_paper(), 'deskPrint' => setting('desk_autoprint') === '1']; } // (2.99.141) deskPrint: AN Desk prints the receipt by itself after paying // (2.99.34) a 192 px WebP (10 KB) instead of the 434 KB original
/** How receipts print (Settings → Salon info): 'letter' (the receipt in the middle of a Letter page, big enough to read) or '80mm' (receipt printer). */
/** The name of each tech's line on receipts (Settings → Receipt, "Custom service" by default): "Custom service · TONY $100.00". */
function receipt_line(): string { $v = trim((string)setting('receipt_line')); return $v !== '' ? $v : 'Custom service'; }
function receipt_paper(): string { return setting('receipt_paper') === '80mm' ? '80mm' : 'letter'; }
/** Who is doing it, for the receipt ("Owner", "Manager LINDA"). */
/** (2.99.53) Settings → Checkout, tax & payments: the sales tax % added at Checkout (0 = none), and the admin rule: each tech line of $min or more gives $amt to the
    admin tech (LOGAN unless chosen), taken from that tech's money – never from the customer's total, never on the customer's receipt. */
/** (2.99.56) The customer's tip screen: on/off and the 3 % buttons (Settings → Checkout, tax & payments). */
function tip_cfg(): array {
    $p = array_values(array_filter(array_map('intval', explode(',', (string)setting('tip_pcts'))), fn($x) => $x > 0 && $x <= 100));
    return ['on' => setting('tip_screen_on') !== '0', 'pcts' => count($p) === 3 ? $p : [15, 20, 25]];
}
function tax_pct(): float { return round(max(0.0, min(20.0, (float)setting('tax_pct'))), 3); }
function fee_cfg(): array {
    $sid = (int)setting('admin_fee_staff'); $name = '';
    foreach (staff_list(false) as $s) { if ($sid && (int)$s['id'] === $sid) { $name = (string)$s['name']; break; } } // (2.99.211 – order 411) only the tech chosen in Settings (no name guessed); American Nails: saved once by the upgrade (v94)
    if ($name === '') $sid = 0;
    $min = round(max(0.0, (float)setting('admin_fee_min')), 2); $amt = round(max(0.0, min(20.0, (float)setting('admin_fee_amt'))), 2);
    $tiers = $amt > 0 ? [['min' => $min, 'amt' => $amt]] : []; // (2.99.115) up to 3 levels (Settings): level 1 = the old one (39 → 1); 2 and 3 empty = not used
    foreach (['2', '3'] as $k) { $m = trim((string)setting('admin_fee_min' . $k)); $v = trim((string)setting('admin_fee_amt' . $k)); if ($m === '' || $v === '' || (float)$v <= 0) continue; $tiers[] = ['min' => round((float)$m, 2), 'amt' => round(min(20.0, (float)$v), 2)]; }
    usort($tiers, fn($x, $y) => $x['min'] <=> $y['min']);
    return ['on' => setting('admin_fee_on') === '1' && $sid > 0, 'min' => $min, 'amt' => $amt, 'tiers' => $tiers, 'staff' => $sid, 'name' => $name, 'showDesk' => setting('fee_show_desk') !== '0']; // (2.99.172) showDesk: the $1 line on AN Desk
}
/** (2.99.115) The $1 rule for ONE tech row: the HIGHEST level the row reaches (never added up) → [amount, from]. $tiers = the levels saved on a receipt (refunds) or today's. */
function fee_tier(array $tiers, float $row): array {
    $hit = [0.0, 0.0]; foreach ($tiers as $t) if ($row + 0.001 >= (float)$t['min'] && $row >= (float)$t['amt'] && (float)$t['amt'] > 0) $hit = [(float)$t['amt'], (float)$t['min']];
    return $hit;
}
function actor_name(): string { return (string)($GLOBALS['actor'][1] ?? 'Salon'); }

/** $amount split by the weights, to the cent; what rounding leaves goes to the biggest weight (all 0: equal parts). */
function alloc(float $amount, array $weights): array {
    $out = []; if (!$weights) return $out;
    $sum = array_sum($weights);
    if ($sum <= 0) $weights = array_fill_keys(array_keys($weights), 1.0);
    $sum = array_sum($weights); $done = 0.0; $big = null;
    foreach ($weights as $k => $w) { $out[$k] = round($amount * $w / $sum, 2); $done += $out[$k]; if ($big === null || $w > $weights[$big]) $big = $k; }
    $out[$big] = round($out[$big] + round($amount - $done, 2), 2);
    return $out;
}

/** The people paid together: this appointment, the rest of its group and other bookings of the same number that day – not paid yet. */
require_once __DIR__ . '/custkey.php'; // (2.99.269 – order 479)
function ticket_people(array $a): array {
    $open = fn(array $r): bool => $r['kind'] === 'appt' && in_array($r['status'], ['booked', 'arrived'], true);
    $by = [(int)$a['id'] => $a];
    if ($a['group_id'] !== '') foreach (q('SELECT * FROM appointments WHERE group_id = ?', [$a['group_id']])->fetchAll() as $r) if ($open($r)) $by[(int)$r['id']] = $r;
    if (strlen((string)$a['phone']) === 12) foreach (q('SELECT * FROM appointments WHERE phone = ? AND appt_date = ?', [$a['phone'], $a['appt_date']])->fetchAll() as $r) if ($open($r)) $by[(int)$r['id']] = $r;
    foreach (q('SELECT * FROM appointments WHERE appt_date = ? AND (split_of = ? OR id = ?)', [$a['appt_date'], (int)($a['split_of'] ?? 0) ?: (int)$a['id'], (int)($a['split_of'] ?? 0)])->fetchAll() as $r) if ($open($r)) $by[(int)$r['id']] = $r; // (2.99.269) merged on the desk
    $first = $by[(int)$a['id']]; unset($by[(int)$a['id']]);
    usort($by, fn($x, $y) => [(int)$x['start_min'], (int)$x['id']] <=> [(int)$y['start_min'], (int)$y['id']]);
    return array_merge([$first], array_values($by)); // the one tapped first
}

/** Offers this customer can use now – one per checkout, never added together (the page picks the best one for the customer).
    kind, label, pct (percent of the services) or fixed (dollars), max (0 = no limit). */
function ticket_offers(string $phone): array {
    $out = [];
    if (strlen($phone) !== 12) return $out;
    $lc = loyalty_cfg(); $c = customer_by_phone($phone);
    if ($lc['on'] && $lc['reward'] > 0 && (int)($c['points'] ?? 0) >= $lc['need'])
        $out[] = ['kind' => 'reward', 'label' => '⭐ ' . usd($lc['reward']) . ' reward', 'pct' => 0, 'fixed' => $lc['reward'], 'max' => 0, 'why' => (int)$c['points'] . '/' . $lc['need'] . ' visits'];
    $seen = [];
    foreach (offers_active($phone) as $o) { // birthday / win-back offers from a text already sent (numbers kept from that day)
        if (isset($seen[$o['kind']])) continue;
        $seen[$o['kind']] = true;
        $pct = rtrim(rtrim(number_format((float)$o['pct'], 2, '.', ''), '0'), '.');
        $out[] = ['kind' => $o['kind'], 'id' => (int)$o['id'], 'label' => ($o['kind'] === 'birthday' ? '🎂 Birthday' : '👋 Welcome back') . ' −' . $pct . '%',
            'pct' => (float)$o['pct'], 'fixed' => 0, 'max' => (float)$o['max_amt'],
            'why' => ((float)$o['max_amt'] > 0 ? 'max ' . usd((float)$o['max_amt']) . ' · ' : '') . 'until ' . date('M j', strtotime($o['expires']))];
    }
    return $out;
}
/** What an offer takes off a service total. */
function offer_value(array $o, float $services): float {
    $v = $o['fixed'] > 0 ? (float)$o['fixed'] : $services * (float)$o['pct'] / 100;
    if ((float)$o['max'] > 0) $v = min($v, (float)$o['max']);
    return round(max(0, min($v, $services)), 2);
}
function offer_label(string $kind): string {
    return ['reward' => 'Loyalty reward', 'birthday' => 'Birthday offer', 'winback' => 'Welcome back offer'][$kind] ?? ($kind !== '' ? ucfirst($kind) : '');
}

/** Everything the checkout screen needs (owner or manager – managers see prices here only). */
/** (2.99.140) Settings → Checkout, tax & payments → Checkout look: auto (follows the device's light / dark) · light · dark. AN Desk is always dark. */
function co_theme(): string { $v = (string)setting('co_theme'); return in_array($v, ['light', 'dark'], true) ? $v : 'auto'; }
function ticket_data(array $a): array {
    if ($a['kind'] !== 'appt') fail('This is not an appointment.');
    if ((int)($a['redo_of'] ?? 0) > 0) fail('This is a Redo (free fix) – nothing to pay. Tap Service done when it is finished.'); // (2.99.102)
    if ($a['status'] === 'paid') fail('This appointment is already paid.');
    if (!in_array($a['status'], ['booked', 'arrived'], true)) fail('This appointment is ' . ($a['status'] === 'noshow' ? 'a no-show' : $a['status']) . '.');
    // 2.44: "Not decided" (online Skip / iPad Not sure) never blocks Checkout – the desk types the total; the service stays optional
    $svc = []; foreach (service_list(false) as $s) $svc[(int)$s['id']] = $s;
    $persons = [];
    foreach (ticket_people($a) as $p) {
        $lines = [];
        foreach (ids_list((string)$p['service_ids']) as $sid) if (isset($svc[$sid])) $lines[] = ['sid' => $sid, 'name' => $svc[$sid]['name'], 'price' => (float)$svc[$sid]['price'], 'staff' => (int)$p['staff_id']];
        if (count($lines) === 1 && (float)$p['price'] > 0) $lines[0]['price'] = (float)$p['price']; // a price changed on the appointment
        elseif (count($lines) > 1) { require_once APP_ROOT . '/inc/ticket-lines.php'; $lines = tl_spread($lines, (float)$p['price']); } // (2.99.301 – order 519) several services: one line each, a changed total → the last line
        if ((int)($p['design'] ?? 0)) $lines[] = ['sid' => 0, 'name' => 'Design', 'price' => 0.0, 'staff' => (int)$p['staff_id']];
        if (!function_exists('tq_cfg')) require_once APP_ROOT . '/inc/turnq.php'; // (2.99.271 – order 481) "y lượt" on each tech row: the same rules as the turn line
        static $tvs = null; if ($tvs === null) { $tvs = []; foreach (q('SELECT id, price, turn_value FROM services')->fetchAll() as $r) if (tq_svc_custom($r)) $tvs[(int)$r['id']] = (float)$r['turn_value']; }
        foreach ($lines as &$ln) if (isset($tvs[(int)$ln['sid']])) $ln['tv'] = $tvs[(int)$ln['sid']]; unset($ln);
        $ncP = (int)($p['turn_nc'] ?? -1); if ($ncP < 0) $ncP = ((string)($p['started_at'] ?? '') !== '' ? (int)($p['turn_req'] ?? 0) : appt_req($p)) === 1 ? tq_nc_val() : 0;
        $persons[] = ['id' => (int)$p['id'], 'who' => cust_key($p), 'tech' => (int)$p['staff_id'] ? staff_name((int)$p['staff_id']) : '', 'svc' => appt_label($p), 'name' => appt_disp_name($p), 'start' => (int)$p['start_min'], 'date' => $p['appt_date'], 'staff' => (int)$p['staff_id'],
            'deposit' => (float)$p['deposit'], 'lines' => $lines, 'nc' => $ncP, 'undecided' => appt_undecided($p), 'note' => appt_undecided($p) ? '' : (function_exists('appt_note_out') ? appt_note_out($p) : (string)$p['note'])];
    }
    $lc = loyalty_cfg(); $phone = (string)$a['phone']; $c = strlen($phone) === 12 ? customer_by_phone($phone) : null;
    $counted = strlen($phone) === 12 && (bool)q('SELECT 1 FROM appointments WHERE phone = ? AND appt_date = ? AND loyalty_given = 1', [$phone, $a['appt_date']])->fetchColumn();
    return ['persons' => $persons, 'phone' => $phone, 'pretty' => pretty_phone($phone), 'test' => (int)($a['test'] ?? 0) === 1 || is_test_phone($phone), 'testPhone' => is_test_phone($phone), /* (2.99.198 – order 397) */
        'services' => array_map(fn($s) => ['id' => (int)$s['id'], 'name' => $s['name'], 'price' => (float)$s['price'], 'color' => $s['color']], service_list()),
        'staff' => array_map(fn($s) => ['id' => (int)$s['id'], 'name' => $s['name'], 'photo' => staff_photo_url((string)$s['photo']), 'tone' => staff_tone((int)$s['id'])], staff_list()), // (2.99.170)
        'offers' => array_values(array_filter(ticket_offers($phone), fn($o) => $o['kind'] === 'reward')), 'aoffers' => ao_due(ticket_people($a)), 'refMax' => 1, 'oneOffer' => true, 'canDisc' => !co_desk_tech(), 'prefill' => setting('co_prefill') !== '0', 'ckTheme' => co_theme(), // (2.99.101) Settings → Checkout, tax & payments → "Prefill prices at checkout"
         // (2.99.95) 1 offer per visit; desk techs: no typed discount
        'taxPct' => tax_pct(), 'turnCfg' => (function () { if (!function_exists('tq_cfg')) require_once APP_ROOT . '/inc/turnq.php'; $c = tq_cfg(); return ['min' => $c['min'], 'under' => $c['under'], 'multi' => $c['multi'], 'per' => $c['per'], 'svcMin' => $c['svcMin'], 'half' => $c['half'], 'none' => $c['none']]; })(), 'tipCfg' => tip_cfg(), 'fee' => fee_cfg(), 'gift' => setting('gift_on') === '1', // (2.99.53) birthday / win-back: in aoffers
        'loyalty' => $lc['on'] && strlen($phone) === 12 ? ['points' => (int)($c['points'] ?? 0), 'need' => $lc['need'], 'reward' => $lc['reward'], 'min' => $lc['min'],
            'services' => $lc['services'], 'counted' => $counted] : null];
}

/** 2.39 Checkout: the desk types only the total (services are not shown). The services booked stay on the receipt, their prices scaled so
    they add up to the total (by the list prices; people on one ticket get their part the same way). An appointment's tech stays when that tech
    is in the split, otherwise (ANYONE, or someone else did it) the tech with the most money in the split. */
function checkout_amount_lines(array $appts, array $svc, float $amount, array $splits, bool $zeroOk = false): array {
    if ($amount <= 0 && !($zeroOk && $amount == 0.0)) fail('Type the total (what the customer had done).'); // (2.99.279) $0 services + a gift card sold on the bill: allowed
    if ($amount > 20000) fail('Check the total.');
    $in = []; $main = 0; $best = -1.0;
    foreach ($splits as $sp) if (is_array($sp) && ($st = (int)($sp['staff'] ?? 0))) { $in[$st] = 1; if ((float)($sp['amt'] ?? 0) > $best) { $best = (float)$sp['amt']; $main = $st; } }
    $per = []; $w = [];
    foreach ($appts as $aid => $a) {
        $ls = [];
        foreach (ids_list((string)$a['service_ids']) as $sid) if (isset($svc[$sid])) $ls[] = ['sid' => $sid, 'name' => (string)$svc[$sid]['name'], 'list' => (float)$svc[$sid]['price']];
        if (!$ls) $ls[] = ['sid' => 0, 'name' => 'Services', 'list' => max(0.0, (float)($a['price'] ?? 0))]; // (2.99.338 – lệnh 570) no service but a price on the visit (⚡ Checkout nhanh: the money typed for that tech) → its share of the total (was: equal shares)
        $per[$aid] = $ls; $w[$aid] = array_sum(array_column($ls, 'list'));
    }
    $part = alloc($amount, $w); $lines = [];
    foreach ($per as $aid => $ls) {
        $pp = alloc($part[$aid], array_column($ls, 'list'));
        $st = (int)$appts[$aid]['staff_id']; if (!isset($in[$st])) $st = $main;
        foreach ($ls as $i => $l) $lines[] = ['appt' => $aid, 'sid' => $l['sid'], 'name' => $l['name'], 'price' => $pp[$i], 'staff' => $st];
    }
    return $lines;
}

/** (2.99.95) A tech who opened the Front desk iPad with their own PIN (not the owner's tech, not a manager): no typed discount. */
function co_desk_tech(): bool {
    if (!function_exists('desk_req') || !desk_req()) return false;
    $d = desk_session(); if (!$d || ($d['kind'] ?? '') !== 'staff' || (int)$d['id'] === (int)fee_cfg()['staff']) return false; // a manager PIN: not a "desk tech"
    $s = q('SELECT * FROM staff WHERE id = ?', [(int)$d['id']])->fetch(); return !($s && function_exists('clock_any_time') && clock_any_time($s)); // (2.99.100) a tech who is also a manager: like a manager
}
/** (2.99.95) The day a ticket is paid on: today, or the day of the visit when it is from an earlier day (the customer forgot / no internet) –
    owner or manager only, and only while that day is not closed 🔒. */
function checkout_day(array $appts): string {
    $today = date('Y-m-d'); $d = $today;
    foreach ($appts as $a) if ((string)$a['appt_date'] < $d) $d = (string)$a['appt_date'];
    if ($d === $today) { day_open_or_fail($today, 'no new checkouts'); return $today; } // (2.99.58)
    foreach ($appts as $a) if ((string)$a['appt_date'] !== $d) fail('Check out each day separately.', 409); // (2.99.100) today + an earlier day on one ticket
    if (co_desk_tech()) fail('A visit of an earlier day: the owner or a manager checks it out.', 403);
    if (before_checkout_day($d)) fail('That day is before "Start using Checkout on" (Settings → Checkout, tax & payments) – it stays as it was.', 409); // (2.99.100)
    if (day_locked($d)) fail('Day closed – reopen first (' . date('M j', strtotime($d)) . ': Receipts → Close day → Unlock).', 409);
    // (2.99.132) counted, then reopened by the owner (Unlock, with a reason): a forgotten visit of that day can be checked out – Close day 🔒 asks to Save the count again
    require_once __DIR__ . '/payroll.php'; if (payroll_week_closed($d)) fail('Payroll for that week is closed.', 409); // (2.99.100)
    return $d;
}
/** Save a paid ticket: the receipt, then every appointment on it (paid, its share of the discount and tip), visits, gift card. */
function checkout_save(array $in): array {
    $ids = array_values(array_unique(array_filter(array_map('intval', (array)($in['ids'] ?? [])))));
    if (!$ids || count($ids) > 30) fail('Nothing to pay.');
    if (!array_filter($ids, fn($i) => (string)q('SELECT appt_date FROM appointments WHERE id = ?', [$i])->fetchColumn() < date('Y-m-d'))) day_open_or_fail(date('Y-m-d'), 'no new checkouts'); // (2.99.58)
    app_lock('money'); // (2.99.69) the same visit on 2 devices at once: the second one is told "already paid" (one receipt)
    $appts = [];
    foreach ($ids as $id) {
        $a = q('SELECT * FROM appointments WHERE id = ?', [$id])->fetch();
        if (!$a || $a['kind'] !== 'appt') fail('Appointment not found.', 404);
        if (!in_array($a['status'], ['booked', 'arrived'], true)) fail($a['customer_name'] . ' is already ' . ($a['status'] === 'paid' ? 'paid' : $a['status']) . '.');
        $appts[$id] = $a;
    }
    $first = $appts[$ids[0]]; $phone = (string)$first['phone'];
    $rday = checkout_day($appts); // (2.99.95) a visit of an earlier day: the receipt goes on THAT day (if it is not closed)
    $svc = []; foreach (service_list(false) as $s) $svc[(int)$s['id']] = $s;
    $staff = []; foreach (staff_list(false) as $s) $staff[(int)$s['id']] = $s['name'];
    if (array_key_exists('amount', $in)) $in['lines'] = checkout_amount_lines($appts, $svc, round((float)$in['amount'], 2), (array)($in['splits'] ?? []), is_array($in['gift_sale'] ?? null)); // 2.39: only the total typed
    $lines = [];
    foreach ((array)($in['lines'] ?? []) as $l) {
        if (!is_array($l)) continue;
        $aid = (int)($l['appt'] ?? 0);
        if (!isset($appts[$aid])) fail('A service is not on this ticket.');
        $sid = (int)($l['sid'] ?? 0); if (!isset($svc[$sid])) $sid = 0;
        $name = $sid ? (string)$svc[$sid]['name'] : trim(mb_substr((string)($l['name'] ?? ''), 0, 60));
        if ($name === '') fail('Every service needs a name.');
        $price = round((float)($l['price'] ?? 0), 2);
        if ($price < 0 || $price > 10000) fail('Check the price of ' . $name . '.');
        $st = (int)($l['staff'] ?? 0);
        if (!isset($staff[$st])) fail('Choose the tech for ' . $name . '.');
        $lines[] = ['appt' => $aid, 'sid' => $sid, 'name' => $name, 'price' => $price, 'staff' => $st, 'tech' => $staff[$st]];
    }
    if (!$lines) fail('Add at least one service.');
    if (count($lines) > 80) fail('Too many services on one ticket.');
    foreach ($appts as $aid => $a) if (!array_filter($lines, fn($l) => $l['appt'] === $aid)) fail('Add a service for ' . $a['customer_name'] . ' (or take them off this ticket).');
    $sub = round(array_sum(array_column($lines, 'price')), 2);

    // Money for each tech (2.37): the services total (before discount, offer and gift card – the salon pays those) split between techs.
    // Every dollar goes to one tech, no tech twice. An older page that sends no split: each tech gets the prices of their lines.
    $splits = []; $rows = [];
    if (is_array($in['splits'] ?? null)) {
        foreach ($in['splits'] as $sp) {
            if (!is_array($sp)) continue;
            $st = (int)($sp['staff'] ?? 0); $amt = round((float)($sp['amt'] ?? 0), 2);
            if ($amt < 0 || $amt > 10000) fail('Check the money for each tech.');
            if ($amt == 0.0 && !$st) continue;
            if (!isset($staff[$st])) fail('Choose the tech for ' . usd($amt) . ' (Split between techs).');
            $rows[] = ['staff' => $st, 'amt' => $amt, 'name' => mb_substr(trim(preg_replace('/\s+/u', ' ', (string)($sp['name'] ?? ''))), 0, 40)]; // (2.99.53) one line per tech row (the $1 rule looks at each row); (2.99.194 – order 392) "+ Service" = its own row (name + money)
            if (isset($splits[$st])) $splits[$st]['amt'] = round($splits[$st]['amt'] + $amt, 2); // the same tech on two rows (a party): one split
            else $splits[$st] = ['staff' => $st, 'tech' => $staff[$st], 'amt' => $amt];
        }
    } else foreach ($lines as $l) {
        if (!isset($splits[$l['staff']])) $splits[$l['staff']] = ['staff' => $l['staff'], 'tech' => $l['tech'], 'amt' => 0.0];
        $splits[$l['staff']]['amt'] = round($splits[$l['staff']]['amt'] + $l['price'], 2);
    }
    $splits = array_values(array_filter($splits, fn($x) => $x['amt'] > 0 || $sub == 0.0));
    // (2.99.53) The admin rule: a row of $39 or more → that tech gets $1 less, the admin tech $1 more (the admin's own rows: nothing). Only the pay split.
    $fc = fee_cfg(); $fee = 0.0; $pay = []; foreach ($splits as $x) $pay[(int)$x['staff']] = $x + ['gross' => $x['amt'], 'cuts' => 0];
    /* (2.99.194 – order 392) a tech with 2+ rows ("+ Service" lines): every line kept on the receipt (name · money · $1) → Receipt, AN Tech, Tech report show each line */
    $nRows = []; foreach ($rows as $rw) if ($rw['amt'] > 0) $nRows[$rw['staff']] = ($nRows[$rw['staff']] ?? 0) + 1;
    foreach ($rows as $rw) if ($rw['amt'] > 0 && isset($pay[$rw['staff']]) && ($nRows[$rw['staff']] > 1 || $rw['name'] !== '')) {
        $fa0 = $fc['on'] && $fc['tiers'] && $rw['staff'] !== $fc['staff'] ? fee_tier($fc['tiers'], (float)$rw['amt'])[0] : 0.0;
        $pay[$rw['staff']]['lines'][] = ['n' => $rw['name'], 'g' => round((float)$rw['amt'], 2), 'a' => $fa0]; }
    if ($fc['on'] && $fc['tiers']) foreach ($rows as $rw) if ($rw['staff'] !== $fc['staff']) { // each row on its own – (2.99.115) the highest level it reaches
        [$fa, $fm] = fee_tier($fc['tiers'], (float)$rw['amt']); if ($fa <= 0) continue;
        $pay[$rw['staff']]['amt'] = round($pay[$rw['staff']]['amt'] - $fa, 2); $pay[$rw['staff']]['cuts']++; $fee = round($fee + $fa, 2);
        $pay[$rw['staff']]['feeRows'][] = ['g' => round((float)$rw['amt'], 2), 'a' => $fa, 'm' => $fm]; $pay[$rw['staff']]['ft'] = $fc['tiers']; // kept on the receipt: a refund uses the levels of THAT day
    }
    if ($fee > 0) { if (isset($pay[$fc['staff']])) $pay[$fc['staff']]['amt'] = round($pay[$fc['staff']]['amt'] + $fee, 2); else $pay[$fc['staff']] = ['staff' => $fc['staff'], 'tech' => $fc['name'], 'amt' => $fee, 'gross' => 0.0, 'cuts' => 0, 'feeOnly' => true];
        foreach ($pay as &$px) $px['fee'] = (int)$px['staff'] === $fc['staff'] ? $fee : 0; unset($px); }
    $pay = array_values($pay);
    // (2.52) Card tip / (2.99.54) cash tip for each tech (optional): 100% the tech's – no $1 rule, no tax, not in the services' TOTAL.
    [$tips, $tipSum] = tips_parse($in['tips'] ?? [], $staff, 'card', $in['tip_total'] ?? null);
    [$ctips, $ctipSum] = tips_parse($in['cash_tips'] ?? [], $staff, 'cash', $in['cash_tip_total'] ?? null);
    $left = round($sub - array_sum(array_column($splits, 'amt')), 2);
    if ($sub > 0 && abs($left) > 0.005) fail($left > 0 ? 'Split between techs: ' . usd($left) . ' is not given to a tech yet.' : 'Split between techs is ' . usd(-$left) . ' more than the services.');

    // Discount typed by the desk ($ or %), then at most one offer (loyalty reward, birthday, welcome back).
    $dv = max(0, (float)($in['disc_val'] ?? 0)); $dnote = '';
    if (($in['disc_type'] ?? '$') === '%') {
        if ($dv > 100) fail('The discount is more than 100%.');
        $disc = round($sub * $dv / 100, 2); if ($dv > 0) $dnote = rtrim(rtrim(number_format($dv, 2, '.', ''), '0'), '.') . '%';
    } else $disc = round($dv, 2);
    if ($disc > $sub + 0.001) fail('The discount is more than the services.');
    if ($disc > 0 && co_desk_tech()) fail('A typed discount: the owner or a manager only.'); // (2.99.95) techs at the Front desk iPad: offers only
    $promo = 0.0; $pk = (string)($in['offer'] ?? ''); $o = null;
    if ($pk !== 'reward') $pk = ''; // (2.99.53) birthday / win-back are taken off with the other offers below
    if ($pk !== '') {
        foreach (ticket_offers($phone) as $x) if ($x['kind'] === $pk) $o = $x;
        if (!$o) fail('This offer cannot be used now.');
        $promo = min(offer_value($o, $sub), max(0, round($sub - $disc, 2)));
    }
    $base = max(0, round($sub - $disc - $promo, 2));
    // (2.99.53) the customer's offers left ON are taken off (never below $0); the ones turned off stay for next time
    $on = is_array($in['ao_on'] ?? null) ? array_map('strval', $in['ao_on']) : array_keys(array_filter((array)($in['offers'] ?? []), fn($v) => $v === 'applied'));
    if ($promo > 0 && $on) fail('Only 1 offer per visit.'); // (2.99.95)
    [$aoPairs, $offAmt, $offLines] = ao_checkout($on, array_values($appts), $base);
    $base = max(0, round($base - $offAmt, 2));
    $tp = tax_pct(); $tax = round($base * $tp / 100, 2); // (2.99.53) Settings → Checkout, tax & payments → Tax % (0 = the card machine adds it, as before)
    $total = round($base + $tax, 2);
    $dep = round(array_sum(array_map(fn($a) => (float)$a['deposit'], $appts)), 2); // paid online before
    if ($dep > $total + 0.005) fail('Deposit is more than the total – refund ' . usd(round($dep - $total, 2)) . ' or change the ticket.'); // (2.99.95) never kept quietly

    // Gift card paying part or all of it (one card per ticket).
    $giftAmt = round(max(0, (float)($in['gift_amount'] ?? 0)), 2); $gift = null;
    if ($giftAmt > 0) {
        $gift = gift_find((string)($in['gift_code'] ?? ''));
        if (($p = gift_problem($gift)) !== '') fail($p);
        if ($giftAmt > (float)$gift['balance'] + 0.001) fail('The gift card only has ' . usd((float)$gift['balance']) . ' left.');
        if ($giftAmt > $total - $dep + 0.001) fail('The gift card amount is more than the total.');
    }
    $collect = round($total - $dep - $giftAmt, 2);
    /* (2.99.279 – order 491) "🎁 Bán gift card" ON the bill: paid together with the services (one payment), made only when the bill is paid (this same save).
       Not services: no tax, no $1 rule, no turn, not a tech's money, no offer on it, no tip on it. Its money is split by how the bill was paid (anh chọn C:
       by the share of each way, the cents to the card part) and counted as "gift card sold" in Close day – never in the services' money. */
    $gsIn = is_array($in['gift_sale'] ?? null) ? $in['gift_sale'] : null; $gsAmt = 0.0; $gsPhone = ''; $gsCode = '';
    if ($gsIn) {
        if (setting('gift_on') !== '1') fail('Gift cards are turned off (Settings → Gift cards).');
        $gsAmt = round((float)($gsIn['amount'] ?? 0), 2); if ($gsAmt < 5 || $gsAmt > 500) fail('Gift card: choose an amount from $5 to $500.');
        $gsPhone = trim((string)($gsIn['phone'] ?? '')) !== '' ? norm_phone((string)$gsIn['phone']) : ''; if ($gsPhone !== '' && strlen($gsPhone) !== 12) fail('Gift card: the phone number must have 10 digits.');
        $gsCode = trim((string)($gsIn['code'] ?? ''));
        if ($gsCode !== '') { $gn = gift_norm($gsCode); // (2.99.281 – order 494) checked BEFORE anything is saved: a number that cannot be read / a card already in the system
            if ($gn === '') fail('Gift card: số thẻ không đọc được – scan lại hoặc gõ lại.');
            if (($ox = q('SELECT * FROM giftcards WHERE code = ?', [$gn])->fetch()) && !gift_reusable($ox)) fail(/* (2.99.627 L2) a card voided with its bill: sold again */ 'Gift card: Thẻ này đã có (' . gift_mask($gn) . ') – dùng thẻ khác.'); }
    }
    $collectAll = round($collect + $gsAmt, 2);

    // How it was paid. Card: the amount was typed on the card machine; only the last 4 digits (optional). Cash: the change.
    $pays = []; $card = $cash = $other = 0.0;
    foreach ((array)($in['pays'] ?? []) as $p) {
        if (!is_array($p)) continue;
        $m = (string)($p['m'] ?? ''); $amt = round((float)($p['amt'] ?? 0), 2);
        if ($amt <= 0) continue;
        if ($amt > 20000) fail('Check the amounts.');
        if ($m === 'Card') {
            $l4 = preg_replace('/\D+/', '', (string)($p['last4'] ?? ''));
            if ($l4 !== '' && strlen($l4) !== 4) fail('Card: type only the last 4 digits (or leave it empty).');
            $dvx = []; if (($dvr = trim((string)($p['dv_ref'] ?? ''))) !== '') { // (2.99.638c) paid on the P5: only the approved payment of THIS ticket and amount, used once (same transaction as the receipt)
                require_once APP_ROOT . '/inc/dejavoo-pay.php'; $dv = dv_take($dvr, (array)($in['ids'] ?? []), $amt); if ((string)($dv['last4'] ?? '') !== '') $l4 = (string)$dv['last4'];
                $dvx = ['dv' => ['ref' => $dvr, 'amt' => round((float)$dv['amt'], 2), 'auth' => (string)($dv['auth_code'] ?? ''), 'pnref' => (string)($dv['pnref'] ?? ''), 'card' => (string)($dv['card'] ?? '')]]; dv_used($dvr, 0); }
            elseif (($prr = trim((string)($p['pr_ref'] ?? ''))) !== '') { /* (2.99.645a) paid on Payroc: only the approved payment of THIS ticket and amount, used once (same transaction as the receipt) */
                require_once APP_ROOT . '/inc/payroc-pay.php'; $pr = pr_take($prr, (array)($in['ids'] ?? []), $amt); if ((string)($pr['last4'] ?? '') !== '') $l4 = (string)$pr['last4'];
                $dvx = ['pr' => ['ref' => $prr, 'amt' => round((float)$pr['amt'], 2), 'pay' => (string)($pr['pay'] ?? ''), 'approval' => (string)($pr['approval'] ?? ''), 'card' => (string)($pr['card'] ?? '')]]; pr_used($prr, 0); }
            $pays[] = ['m' => 'Card', 'amt' => $amt, 'last4' => $l4] + $dvx; $card += $amt;
        } elseif ($m === 'Cash') {
            $got = round(max(0, (float)($p['given'] ?? 0)), 2);
            if ($got > 0 && $got + 0.001 < $amt) fail('The cash received is less than the amount.');
            $got = max($got, $amt);
            $pays[] = ['m' => 'Cash', 'amt' => $amt, 'given' => $got, 'change' => round($got - $amt, 2)]; $cash += $amt;
        } elseif ($m === 'Other') {
            $pays[] = ['m' => 'Other', 'amt' => $amt, 'how' => in_array($p['how'] ?? '', PAY_OTHER, true) ? $p['how'] : 'Other']; $other += $amt;
        } else fail('Choose how the customer paid.');
    }
    if ((int)round(($card + $cash + $other) * 100) !== (int)round($collectAll * 100)) fail(/* (2.99.450 – rà soát) to the cent: $53.49 for $53.50 was taken */ 'The payments (' . usd(round($card + $cash + $other, 2)) . ') are not the amount due (' . usd($collectAll) . ').');
    if ($tipSum > 0.004 && $card <= 0.004 && $collectAll > 0.004) fail('A card tip needs a card part – take the tip off or pay part by card.'); // (2.99.92) every way of paying
    $gsSplit = [];
    if ($gsAmt > 0) { // (2.99.279) the gift card's part of each way of paying: by its share, the cents to the card part (no card part: to the biggest one)
        $tot = round($card + $cash + $other, 2); $by0 = ['Card' => $card, 'Cash' => $cash, 'Other' => $other];
        foreach (['Cash', 'Other'] as $k) $gsSplit[$k] = $tot > 0 ? floor($gsAmt * $by0[$k] / $tot * 100 + 1e-7) / 100 : 0.0;
        $gsSplit['Card'] = round($gsAmt - $gsSplit['Cash'] - $gsSplit['Other'], 2);
        if ($gsSplit['Card'] > $card + 0.001) { $over = round($gsSplit['Card'] - $card, 2); $gsSplit['Card'] = round($card, 2); $big = $cash >= $other ? 'Cash' : 'Other'; $gsSplit[$big] = round($gsSplit[$big] + $over, 2); }
        $gsSplit = array_filter(array_map(fn($v) => round($v, 2), $gsSplit), fn($v) => $v > 0.004);
        // the bill's own payments = the services only (what is left after the gift card's part); cash: the change stays the same
        $left = $gsSplit;
        foreach ($pays as &$p0) { $k = $p0['m']; $take = min((float)($left[$k] ?? 0), (float)$p0['amt']); if ($take <= 0) continue; $left[$k] = round(($left[$k] ?? 0) - $take, 2);
            $p0['amt'] = round($p0['amt'] - $take, 2); if ($k === 'Cash') $p0['given'] = round(max($p0['amt'], (float)$p0['given'] - $take), 2); $p0['gsale'] = $take; } unset($p0);
        $card = round($card - ($gsSplit['Card'] ?? 0), 2); $cash = round($cash - ($gsSplit['Cash'] ?? 0), 2); $other = round($other - ($gsSplit['Other'] ?? 0), 2);
        $pays = array_values(array_map(function ($p0) { unset($p0['gsale']); return $p0; }, array_filter($pays, fn($p0) => $p0['amt'] > 0.004)));
    }
    $method = count($pays) > 1 ? 'Split' : ($pays ? ($pays[0]['m'] === 'Other' ? $pays[0]['how'] : $pays[0]['m']) : ($giftAmt > 0 ? 'Gift card' : ($gsAmt > 0 ? (count($gsSplit) === 1 ? (string)array_key_first($gsSplit) : 'Split') : 'Deposit')));

    $aoLocks = ao_lock($aoPairs); // (2.99.64) the offers used here are taken now – a second device gets "just used"
    // The receipt (numbered from 1001).
    $names = array_values(array_unique(array_map(fn($a) => (string)$a['customer_name'], $appts)));
    $names = array_values(array_filter($names, fn($n) => !preg_match('/^(.+) \+\d+$/', $n, $m) || !in_array($m[1], $names, true))); // (2.49) "TERI ROSS", not "TERI ROSS, TERI ROSS +1"
    $rid = 0; $rno = 0;
    for ($try = 0; $try < 5 && !$rid; $try++) {
        $rno = (int)q('SELECT COALESCE(MAX(rno), 1000) FROM receipts')->fetchColumn() + 1;
        try {
            q('INSERT INTO receipts (rno, day, created_at, by_name, customer_name, phone, appt_ids, people, items, subtotal, discount, disc_note, promo, promo_kind, deposit, gift, gift_code,
                tip, tips, total, pays, method, card_amt, cash_amt, other_amt, status, refunds, token, splits, offers, offer_amt, tax, tax_pct, pay_splits, admin_fee, cash_tip, cash_tips) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
              [$rno, $rday, now_str(), mb_substr(actor_name(), 0, 60), mb_substr(implode(', ', $names), 0, 80), $phone, implode(',', $ids), count($appts),
               json_encode($lines, JSON_UNESCAPED_UNICODE), $sub, $disc, $dnote, $promo, $promo > 0 ? $pk : '', $dep, $giftAmt, $gift ? (string)$gift['code'] : '',
               $tipSum, json_encode($tips, JSON_UNESCAPED_UNICODE), $total, json_encode($pays), $method, round($card, 2), round($cash, 2), round($other, 2), 'paid', '[]', bin2hex(random_bytes(10)),
               json_encode($splits, JSON_UNESCAPED_UNICODE), json_encode($offLines, JSON_UNESCAPED_UNICODE), $offAmt, $tax, $tp, json_encode($pay, JSON_UNESCAPED_UNICODE), $fee, $ctipSum, json_encode($ctips, JSON_UNESCAPED_UNICODE)]);
            $rid = (int)db()->lastInsertId();
        } catch (PDOException $e) { if ($try === 4) { ao_unlock($aoLocks); throw $e; } } // two checkouts at the same moment: the next number
    }
    if ($aoLocks) q('UPDATE offer_locks SET receipt_id = ? WHERE k IN (' . implode(',', array_fill(0, count($aoLocks), '?')) . ')', array_merge([$rid], $aoLocks));
    if ($rid && $gift) q('UPDATE receipts SET gift_left = ? WHERE id = ?', [round(max(0, (float)$gift['balance'] - $giftAmt), 2), $rid]); // (2.99.55) "balance $y" on the receipt
    if ($rid && $gsAmt > 0) { // (2.99.279 – order 491) the gift card is made now – the bill is paid (a ✕ or leaving Checkout made nothing)
        $bn = mb_strtoupper(trim(implode(', ', $names))); if ($gsPhone !== '' && function_exists('gift_name_for')) { $nn = gift_name_for($gsPhone); if ($nn !== '') $bn = $nn; }
        $pb = count($gsSplit) === 1 ? (string)array_key_first($gsSplit) : 'Split';
        $g2 = gift_create($gsAmt, ['buyer_name' => $bn, 'buyer_phone' => $gsPhone !== '' ? $gsPhone : $phone, 'source' => 'salon', 'paid_by' => $pb, 'code' => $gsCode], actor_name());
        q('UPDATE giftcards SET paid_split = ?, receipt_id = ? WHERE id = ?', [count($gsSplit) > 1 ? json_encode($gsSplit) : '', $rid, (int)$g2['id']]);
        q('UPDATE receipts SET gift_sale = ? WHERE id = ?', [json_encode(['amount' => $gsAmt, 'code' => (string)$g2['code'], 'id' => (int)$g2['id'], 'by' => $gsSplit]), $rid]);
        audit('gift_sale', 'Gift card ' . gift_mask((string)$g2['code']), '', 'Sold ' . usd($gsAmt) . ' on receipt #' . $rno . ' (' . implode(' + ', array_map(fn($k, $v) => $k . ' ' . usd($v), array_keys($gsSplit), $gsSplit)) . ')');
    }
    /* (2.99.198 – order 397, SO-LUAT 10/10) the owner's own number (a test number): at Checkout "💵 Add pay for the techs" → ADD PAY – counted like any ticket
       (techs' pay, $1 rule, Payroll, Tech report, Close day, sales); no turn (the visit stays TEST), no rewards / texts (the number is a test number). ADD PAY = test 0 + a test number. */
    $addPay = false; // (2.99.283 – order 497) no ADD PAY any more: a test number's ticket is always TEST (old ADD PAY tickets stay)
    if ($rid && !$addPay && (is_test_phone($phone) || array_filter($appts, fn($a) => (int)($a['test'] ?? 0) === 1))) q('UPDATE receipts SET test = 1 WHERE id = ?', [$rid]); // TEST receipt: left out of every total
    if ($rid && $addPay) addpay_set($rid, true);
    if ($rid && $addPay) audit('desk_money', 'Receipt #' . $rno . ' · ' . pretty_phone($phone), 'TEST', 'ADD PAY – counted for the techs (Checkout)', 'Owner number used to add pay');

    // Every appointment on it: its services, its share of the discount / offer, paid.
    $apSum = []; foreach ($lines as $l) $apSum[$l['appt']] = ($apSum[$l['appt']] ?? 0) + $l['price'];
    $discShare = alloc(round($disc + $promo + $offAmt, 2), $apSum);
    foreach ($appts as $aid => $a) {
        $mine = array_values(array_filter($lines, fn($l) => $l['appt'] === $aid));
        $sids = array_values(array_unique(array_filter(array_map(fn($l) => $l['sid'], $mine))));
        $by = []; foreach ($mine as $l) $by[$l['staff']] = ($by[$l['staff']] ?? 0) + $l['price'];
        arsort($by); $main = (int)array_key_first($by);
        $newStaff = (int)$a['staff_id'] ?: $main; // ANYONE: the tech who did it
        $newSvc = $sids ? implode(',', $sids) : (string)$a['service_ids'];
        if ($newStaff !== (int)$a['staff_id'] || $newSvc !== (string)$a['service_ids']) {
            q('UPDATE appointments SET staff_id = ?, service_ids = ? WHERE id = ?', [$newStaff, $newSvc, $aid]);
            if (function_exists('undecided_clean')) undecided_clean((int)$aid); // (2.99.110)
            $a = get_appt($aid);
        }
        // (2.59) checkout = done now (checkout early: the tech is free right away); start from the plan (or typed at the desk)
        if ($a['done_at'] === '' && ((int)$a['staff_id'] || $a['started_at'] !== '') && $a['appt_date'] === date('Y-m-d')) {
            // (2.99.288 – order 504) Checkout = done now; how it was before (in service since …) is written, so a VOID of this receipt puts it back exactly
            appt_log($a, 'done_co', 'Service done by Checkout – before: ' . ($a['started_at'] !== '' ? 'in service since ' . date('g:i A', strtotime((string)$a['started_at'])) : 'not started') . ' [co:' . (int)$rid . '|' . (string)$a['started_at'] . '|' . (int)$a['start_src'] . '|' . (int)$a['done_src'] . '|' . (int)$a['turn_nc'] . '|' . (float)$a['turn_value'] . '|' . (int)$a['turn_req'] . ']');
            plan_finish($a, time(), 0);
        }
        q("UPDATE appointments SET status = 'paid', price = ?, tip = 0, discount = ?, pay_method = ?, paid_at = ?, is_new = 0, receipt_id = ?,
           arrived_at = CASE WHEN arrived_at = '' THEN ? ELSE arrived_at END WHERE id = ?",
          [round($apSum[$aid], 2), $discShare[$aid], mb_substr($method, 0, 12), now_str(), $rid, now_str(), $aid]);
    }
    tips_to_appts($tips, $ids, 'tip'); tips_to_appts($ctips, $ids, 'cash_tip'); // each tech's tips on their appointment (Reports)
    // Money log: a price changed from the service list, or a discount given
    $edits = [];
    if (array_key_exists('amount', $in)) { $list = round(array_sum(array_map(fn($l) => $l['sid'] && isset($svc[$l['sid']]) ? (float)$svc[$l['sid']]['price'] : 0, $lines)), 2);
        if (abs($list - $sub) >= 0.005) $edits[] = 'list prices ' . usd($list) . ' → typed ' . usd($sub); }
    else foreach ($lines as $l) if ($l['sid'] && isset($svc[$l['sid']]) && abs((float)$svc[$l['sid']]['price'] - $l['price']) >= 0.005) $edits[] = $l['name'] . ' ' . usd((float)$svc[$l['sid']]['price']) . ' → ' . usd($l['price']);
    if ($edits || $disc > 0) audit('checkout_edit', 'Receipt #' . $rno . ' · ' . implode(', ', $names), 'services ' . usd($sub), ($edits ? implode(', ', $edits) . '; ' : '') . ($disc > 0 ? 'discount ' . usd($disc) . ($dnote !== '' ? ' (' . $dnote . ')' : '') . '; ' : '') . 'total ' . usd($total), (string)($in['disc_reason'] ?? ''));
    if (!empty($o['id']) && $promo > 0) // a birthday / win-back offer is used once
        q("UPDATE customer_offers SET status = 'used', used_at = ?, receipt_id = ?, amount = ? WHERE id = ?", [now_str(), $rid, $promo, $o['id']]);
    if ($pk === 'reward' && $promo > 0) { // the reward takes its visits off
        $lc = loyalty_cfg();
        loyalty_add($phone, -$lc['need'], 'reward', usd($promo) . ' reward used · Receipt #' . $rno, (int)$first['id'], actor_name());
        q('UPDATE appointments SET loyalty_used = ? WHERE id = ?', [$lc['need'], $first['id']]);
    }
    foreach ($ids as $aid) loyalty_visit(get_appt($aid));
    if ($gift) {
        if (q('UPDATE giftcards SET balance = balance - ? WHERE id = ? AND balance >= ? - 0.001', [$giftAmt, $gift['id'], $giftAmt])->rowCount() !== 1) /* (2.99.627 L3) 2nd guard: never below $0 (the whole checkout rolls back) */
            fail('The gift card only has ' . usd((float)q('SELECT balance FROM giftcards WHERE id = ?', [$gift['id']])->fetchColumn()) . ' left – check it and try again.');
        q('UPDATE appointments SET gift_used = ?, gift_id = ? WHERE id = ?', [$giftAmt, $gift['id'], $first['id']]);
        gift_log((int)$gift['id'], -$giftAmt, 'used', $first['customer_name'] . ' · Receipt #' . $rno, (int)$first['id'], actor_name());
    }
    foreach ($ids as $aid) appt_log(get_appt($aid), 'paid', 'Receipt #' . $rno . ' · ' . usd($total) . ' · ' . $method . ($giftAmt > 0 ? ' · gift card ' . usd($giftAmt) : '') . ($tipSum > 0 ? ' · card tip ' . usd($tipSum) : '') . ($ctipSum > 0 ? ' · cash tip ' . usd($ctipSum) : ''));
    ao_record($aoPairs, get_appt((int)$first['id']), (int)$rid); // (2.99.49) on the receipt and the customer's history
    try { rw_receipt_paid(receipt_get($rid)); } catch (Throwable $e) { error_log('rewards: ' . $e->getMessage()); } // (2.99.82) Rewards: what this visit adds
    co_left_rest($ids, (string)$rno); // (2.99.585 - LENH 585) the parts of this visit not paid and not started: cancelled (no turn, no text)
    out_validate(); // a reminder not sent yet is not needed any more
    flow_tick(); // (2.58) the tech's next waiting customer starts now
    try { require_once __DIR__ . '/cal-sync.php'; cal_sync_receipt((int)$rid, 'Checkout'); } catch (Throwable $e) { error_log('cal_sync: ' . $e->getMessage()); } // (2.99.296 – order 513) the calendar follows the receipt
    return receipt_get($rid);
}
/** (2.99.585 - LENH 585, anh Logan 31/10 14:21 + 14:26 - ca SHELBIE / TAMMY: paid the Pedicure only, the Gel Manicure stayed on the calendar)
    Checkout = the customer is leaving. A part of THE SAME VISIT that is NOT on the paid ticket and NOT started is cancelled like "Khach bo ve":
    - the same customer (cust_key: same phone + same name, or merged) checked in today, or a part split from a paid one (split_of);
    - no turn / no bonus (it never started), the tech is free at once, NO cancel text to the customer, one Activity log line.
    The paid services keep their turn. Another person of a party (another name) is never touched. Only a checkout of today. */
function co_left_rest(array $paidIds, string $rno): array {
    $done = [];
    try { require_once APP_ROOT . '/inc/custkey.php';
        $paid = []; foreach ($paidIds as $i) { $p = q('SELECT * FROM appointments WHERE id = ?', [(int)$i])->fetch(); if ($p) $paid[] = $p; }
        if (!$paid || (string)$paid[0]['appt_date'] !== date('Y-m-d')) return [];
        $keys = []; $roots = []; foreach ($paid as $p) { $keys[cust_key($p)] = 1; $roots[(int)($p['split_of'] ?? 0) ?: (int)$p['id']] = 1; }
        foreach (q("SELECT * FROM appointments WHERE appt_date = ? AND kind = 'appt' AND status IN ('arrived', 'booked') AND started_at = '' AND done_at = '' ORDER BY start_min, id", [date('Y-m-d')])->fetchAll() as $a) {
            if (in_array((int)$a['id'], array_map('intval', $paidIds), true)) continue;
            $same = isset($keys[cust_key($a)]); $part = isset($roots[(int)($a['split_of'] ?? 0)]) || ((int)($a['split_of'] ?? 0) === 0 && isset($roots[(int)$a['id']]));
            if (!(($a['status'] === 'arrived' && $same) || ($part && $same))) continue;
            if (!q("UPDATE appointments SET status = 'cancelled', is_new = 0 WHERE id = ? AND status IN ('arrived', 'booked') AND started_at = ''", [$a['id']])->rowCount()) continue;
            $who = mb_strtoupper(strtok(trim((string)$a['customer_name']), ' ') ?: 'Customer'); $sn = appt_label($a) ?: 'the service';
            appt_log($a, 'cancelled', $who . ' checked out – ' . $sn . ' not done, cancelled (Receipt #' . $rno . ') – no turn, no text');
            if ((int)$a['staff_id']) notify_staff((int)$a['staff_id'], 'cancel', '🚶 ' . $who . ' checked out – ' . $sn . ' not done · you are free', (int)$a['id']);
            $done[] = (int)$a['id'];
        }
    } catch (Throwable $e) { error_log('585 co_left_rest: ' . $e->getMessage()); }
    return $done;
}
// (2.99.206 – order 407) the functions that were here: inc/checkout-receipts.php

// (2.99.206 – order 407) the functions that were here: inc/checkout-day.php

// (2.99.206 – order 407) the functions that were here: inc/checkout-edit.php

