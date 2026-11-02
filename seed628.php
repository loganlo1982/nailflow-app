<?php
// LAMWEB 628 – demo.hair.nailflowapp.com: "Luxe Hair Studio" (TIEM GIA) – du lieu DEMO dep de anh Logan show cho chu tiem toc.
// CHI DU LIEU – KHONG doi code app. Chay lai bao nhieu lan cung duoc (= "Reset demo"): xoa du lieu demo cu, tao lai theo NGAY HOM NAY.
//   php seed628.php <thu muc app demo.hair>          -> chi KIEM (khong doi gi): DB nao, tiem nao, se xoa / tao gi
//   php seed628.php <thu muc app demo.hair> go       -> lam that (CHAT backup DB truoc)
// An toan: chi chay khi tiem la "HAIR SALON DEMO" / "Luxe Hair Studio" (hoac da seed628 truoc) VA co inc/hair.php (app toc). Khong dung tiem nails nao.
// Giu nguyen: dang nhap chu tiem (admin_hash, 2FA, thiet bi tin cay), push_subs, managers, dich vu (menu), cai dat khac. Khong tao mat khau.
// Tat het gui that: sms_enabled 0, Android 0, review 0, PayPal online 0, tin nhac hen / sinh nhat / win-back 0; outbox / autosend xoa sach sau khi seed.
// Khach 555-01xx / 555-02xx (so GIA). The / tien la GIA.
declare(strict_types=1);
if (PHP_SAPI !== 'cli') { http_response_code(404); exit; } // command line only
$R = rtrim((string)($argv[1] ?? ''), '/'); $GO = ($argv[2] ?? '') === 'go';
if ($R === '' || !is_file("$R/inc/core.php")) { fwrite(STDERR, "usage: php seed628.php <app dir> [go]\n"); exit(2); }
if (!is_file("$R/inc/hair.php")) { fwrite(STDERR, "DUNG: khong phai app toc (khong co inc/hair.php)\n"); exit(2); }
chdir($R);
require "$R/inc/core.php";
foreach (['backup', 'import', 'totp', 'rebook', 'gallery', 'birthday', 'paypal', 'review'] as $f) require_once "$R/inc/$f.php";
foreach (['giftcards', 'outbox', 'logo', 'reports', 'checkout', 'payroll', 'export', 'yearend', 'referral', 'promolinks', 'turnq', 'apptoffers', 'rewards', 'hair'] as $f) if (is_file("$R/inc/$f.php")) require_once "$R/inc/$f.php";
foreach (['_auth', '_menu', '_texts', '_kiosk', '_out'] as $f) if (is_file("$R/inc/api/$f.php")) require_once "$R/inc/api/$f.php"; // the app's helpers (get_appt …) – only functions
settings(); ensure_schema();
$name0 = (string)setting('salon_name');
if (!in_array(strtoupper($name0), ['HAIR SALON DEMO', 'LUXE HAIR STUDIO'], true) && setting('seed628') === '') { fwrite(STDERR, "DUNG: tiem '$name0' khong phai tiem demo toc – khong chay.\n"); exit(2); }
$DB = is_sqlite() ? (string)(cfg()['sqlite_path'] ?? '') : 'MySQL ' . (cfg()['db_name'] ?? '');
echo "seed628 · app $R · " . APP_VERSION . " · DB $DB · tiem '$name0' · demo " . (is_demo_site() ? 'ON' : 'OFF (de nghi bat config demo => true)') . " · hom nay " . date('Y-m-d') . "\n";
$WIPE = ['appointments', 'appt_log', 'autosend', 'bday_alerts', 'bday_log', 'bday_texts', 'customer_offers', 'customers', 'day_close', 'deleted_appts', 'deposits', 'events',
    'giftcard_log', 'giftcards', 'loyalty_log', 'messages', 'offer_locks', 'offer_uses', 'outbox', 'payroll_adj', 'payroll_checkno', 'payroll_log', 'payroll_pay', 'payroll_weeks',
    'phones_seen', 'promo_texts', 'rebook_log', 'receipt_queue', 'receipts', 'ref_links', 'refer_texts', 'referrals', 'review_asks', 'review_log', 'reward_log', 'rewards',
    'sms_log', 'staff_clock', 'staff_off', 'tip_payouts', 'turn_asks', 'turn_log', 'turn_offers', 'turn_snap', 'winback_texts'];
$cnt = function (string $t): int { try { return (int)q("SELECT COUNT(*) FROM $t")->fetchColumn(); } catch (Throwable $e) { return -1; } };
echo 'se xoa: ' . implode(' ', array_map(fn($t) => "$t=" . $cnt($t), array_filter($WIPE, fn($t) => $cnt($t) > 0))) . "\n";
if (!$GO) { echo "chi kiem – chay lai voi: go\n"; exit(0); }

actor_set('admin', 'Owner');
mt_srand((int)crc32('luxe' . date('Y-m-d')));
$rnd = fn(int $a, int $b) => mt_rand($a, $b);
$pick = function (array $a) { return $a[mt_rand(0, count($a) - 1)]; };
foreach ($WIPE as $t) { try { db()->exec("DELETE FROM $t"); } catch (Throwable $e) {} }
try { if (is_sqlite()) db()->exec("DELETE FROM sqlite_sequence WHERE name IN ('receipts', 'appointments', 'giftcards', 'customers')"); } catch (Throwable $e) {}

// ---------- 1 the salon (FAKE) ----------
$H = []; for ($w = 0; $w < 7; $w++) $H[$w] = $w === 0 ? ['open' => '11:00', 'close' => '17:00'] : ['open' => '09:00', 'close' => '19:00'];
$S = ['salon_name' => 'Luxe Hair Studio', 'salon_short' => 'Luxe Hair', 'app_short' => 'LUXE', 'salon_phone' => '(515) 555-0100', 'salon_address' => '123 Main St, Des Moines, IA 50309',
    'hours' => json_encode($H), 'online_booking' => '1', 'gift_on' => '1', 'gift_online' => '0', 'checkout_start' => date('Y-m-d', strtotime('-90 days')),
    'sms_enabled' => '0', 'as_on' => '0', 'as_device' => '', 'review_on' => '0', 'sms_book_on' => '0', 'dep_on' => '0', 'payroll_split_on' => '0', 'admin_fee_on' => '0',
    'remind_on' => '0', 'bday_on' => '0', 'winback_on' => '0', 'rebook_on' => '0', 'refer_on' => '0', 'tax_pct' => '0', 'seed628' => date('Y-m-d H:i:s')];
foreach ($S as $k => $v) set_setting($k, $v);
if (function_exists('hair_cfg')) { $hc = hair_cfg(); $hc['android_on'] = false; $hc['comm_pct'] = 55; set_setting('hair_cfg', json_encode($hc, JSON_UNESCAPED_UNICODE)); }

// ---------- 3 menu: kept (20 hair services); the sample menu only when there is none ----------
if ((int)q('SELECT COUNT(*) FROM services WHERE active = 1')->fetchColumn() === 0 && function_exists('hair_menu_apply')) hair_menu_apply(false, 'hair');
$SV = []; foreach (q('SELECT * FROM services WHERE active = 1 ORDER BY sort')->fetchAll() as $s) $SV[(string)$s['name']] = $s;
$sid = function (string $n) use ($SV) { return isset($SV[$n]) ? (int)$SV[$n]['id'] : 0; };

// ---------- 2 five stylists (the 3 "Stylist n" rows are renamed, history kept) ----------
$ST = [['ASHLEY', 55, ["Women's Haircut", 'Bang Trim', 'Blowout', 'Wash & Style', 'Updo / Event Style', 'Deep Conditioning', 'Toner / Gloss']],
       ['BRIANNA', 60, ["Women's Haircut", 'Root Touch-Up', 'All-Over Color', 'Toner / Gloss', 'Partial Highlights', 'Full Highlights', 'Blowout', 'Deep Conditioning']],
       ['CARLOS', 50, ["Men's Haircut", 'Kids Haircut (12 & under)', 'Bang Trim', 'Wash & Style', 'Scalp Treatment', "Women's Haircut"]],
       ['DANIELLE', 60, ['Balayage', 'Full Highlights', 'Partial Highlights', 'All-Over Color', 'Color Correction (consult first)', 'Toner / Gloss', 'Keratin Smoothing', 'Perm']],
       ['EMILY', 50, ["Women's Haircut", 'Blowout', 'Updo / Event Style', 'Extensions Consultation', 'Tape-In Move-Up', 'Deep Conditioning', 'Scalp Treatment', 'Kids Haircut (12 & under)']]];
$old = q('SELECT id FROM staff ORDER BY sort, id')->fetchAll(PDO::FETCH_COLUMN); q('UPDATE staff SET active = 0');
$T = [];
foreach ($ST as $i => [$n, $pct, $sk]) {
    $ids = array_values(array_filter(array_map($sid, $sk)));
    if (isset($old[$i])) { q("UPDATE staff SET name = ?, sort = ?, active = 1, online = 1, commission_pct = ?, pct_hist = '', skills = ?, skill_all = 0, skill_cats = '', skill_pick = ?, off_days = ? WHERE id = ?",
        [$n, $i + 1, $pct, implode(',', $ids), implode(',', $ids), $n === 'CARLOS' ? '0' : ($n === 'EMILY' ? '1' : ''), (int)$old[$i]]); $T[$n] = (int)$old[$i]; }
    else { q("INSERT INTO staff (name, sort, active, online, commission_pct, skills, skill_all, skill_pick, off_days) VALUES (?, ?, 1, 1, ?, ?, 0, ?, ?)",
        [$n, $i + 1, $pct, implode(',', $ids), implode(',', $ids), $n === 'CARLOS' ? '0' : ($n === 'EMILY' ? '1' : '')]); $T[$n] = (int)db()->lastInsertId(); }
    $T[$n . '_svc'] = $ids;
}
$TECHS = ['ASHLEY', 'BRIANNA', 'CARLOS', 'DANIELLE', 'EMILY'];

// ---------- 4 36 customers (FAKE numbers 555-01xx / 555-02xx) ----------
$NM = ['EMMA JOHNSON', 'OLIVIA WILLIAMS', 'AVA BROWN', 'SOPHIA JONES', 'ISABELLA GARCIA', 'MIA MILLER', 'CHARLOTTE DAVIS', 'AMELIA RODRIGUEZ', 'HARPER MARTINEZ', 'EVELYN HERNANDEZ',
    'ABIGAIL LOPEZ', 'EMILY GONZALEZ', 'ELIZABETH WILSON', 'SOFIA ANDERSON', 'MADISON THOMAS', 'AVERY TAYLOR', 'ELLA MOORE', 'SCARLETT JACKSON', 'GRACE MARTIN', 'CHLOE LEE',
    'VICTORIA PEREZ', 'RILEY THOMPSON', 'ARIA WHITE', 'LILY HARRIS', 'ZOE SANCHEZ', 'NORA CLARK', 'HANNAH RAMIREZ', 'LAYLA LEWIS', 'JAMES ROBINSON', 'MICHAEL WALKER',
    'DANIEL YOUNG', 'MATTHEW ALLEN', 'DAVID KING', 'JOSE WRIGHT', 'LUCAS SCOTT', 'ETHAN TORRES'];
$NOTE = [0 => 'Prefers Brianna · color formula on file (6N + 20 vol)', 3 => 'Sensitive scalp – patch test before color', 7 => 'Likes a quiet appointment', 12 => 'Wedding on the 20th – trial updo booked',
    16 => 'Always books the 10 AM slot', 28 => 'Skin fade #1 on sides', 33 => 'Kid: Mateo (7) – likes the iPad'];
$C = [];
foreach ($NM as $i => $n) {
    $ph = $i < 30 ? sprintf('+151555501%02d', $i + 1) : sprintf('+151555502%02d', $i - 29);
    upsert_customer($ph, $n);
    $m = 1 + ($i * 5) % 12; $d = 1 + ($i * 7) % 28;
    q('UPDATE customers SET note = ?, birth_month = ?, birth_day = ?, birthday = ?, opted_out = 0, sms_consent_at = ?, created_at = ? WHERE phone = ?',
      [$NOTE[$i] ?? '', $i % 3 === 0 ? $m : 0, $i % 3 === 0 ? $d : 0, $i % 3 === 0 ? sprintf('%02d-%02d', $m, $d) : '', '', date('Y-m-d H:i:s', strtotime('-' . (70 + $i * 9) . ' days')), $ph]);
    $C[] = [$ph, $n, $i >= 28 ? 'm' : 'w', $i >= 22 && $i <= 27 ? 1 : 0];
    if ($i >= 22 && $i <= 27) q('UPDATE customers SET created_at = ? WHERE phone = ?', [date('Y-m-d H:i:s', strtotime('-' . (3 + ($i - 22) * 4) . ' days')), $ph]);
}

// ---------- appointment helper (the same columns the app's own demo seed writes) ----------
$NUMA = 0;
$mkA = function (string $day, int $start, string $tech, int $svc, array $c, string $status = 'booked', array $x = []) use ($T, $SV, &$NUMA) {
    $s = q('SELECT * FROM services WHERE id = ?', [$svc])->fetch(); $NUMA++;
    if (!empty($x['clear'])) q("DELETE FROM appointments WHERE appt_date = ? AND staff_id = ? AND status = 'booked' AND start_min < CAST(? AS INTEGER) AND start_min + duration > CAST(? AS INTEGER)", [$day, $T[$tech], $start + (int)$s['duration'], $start]); /* the special demo visits get their time free */
    q('INSERT INTO appointments (appt_date, start_min, duration, staff_id, service_ids, customer_name, phone, color, kind, status, source, price, created_at, sms_ok, group_id, confirm_need, confirm_state, note, token, arrived_at, test)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, \'appt\', ?, ?, ?, ?, 0, ?, ?, ?, ?, ?, ?, 0)',
      [$day, $start, (int)$s['duration'], $T[$tech], (string)$svc, $c[1], $c[0], (string)$s['color'], $status, $x['source'] ?? 'admin', (float)$s['price'],
       $x['created'] ?? date('Y-m-d H:i:s', strtotime($day . ' -' . (2 + $NUMA % 9) . ' days')), $x['group'] ?? '', $x['need'] ?? 0, $x['cstate'] ?? (($x['source'] ?? '') === 'online' ? '' : 'yes'),
       $x['note'] ?? '', bin2hex(random_bytes(10)), $status === 'arrived' ? $day . ' ' . sprintf('%02d:%02d:00', intdiv($start, 60), $start % 60) : '']);
    return (int)db()->lastInsertId();
};
$svcFor = function (string $tech, string $sex) use ($T, $SV, $pick) {
    $ids = $T[$tech . '_svc']; if ($sex === 'm') { $m = array_values(array_filter($ids, fn($i) => in_array($i, [(int)($SV["Men's Haircut"]['id'] ?? 0), (int)($SV['Kids Haircut (12 & under)']['id'] ?? 0)], true))); if ($m) return $pick($m); }
    $ids = array_values(array_filter($ids, fn($i) => (float)q('SELECT price FROM services WHERE id = ?', [$i])->fetchColumn() > 0 && $i !== (int)($SV["Men's Haircut"]['id'] ?? 0))); return $pick($ids);
};
$hoursOf = function (string $day) use ($H) { $h = $H[(int)date('w', strtotime($day))]; return [(int)substr($h['open'], 0, 2) * 60, (int)substr($h['close'], 0, 2) * 60]; };
// a day of a tech: appointments one after the other (fill = how full)
$PLAN = []; /* one plan per day + stylist (today is used twice: what is over -> paid, the rest -> coming) */
$dayPlan = function (string $day, string $tech, float $fill) use ($hoursOf, $svcFor, $C, $T, $pick, $rnd, &$PLAN) {
    if (isset($PLAN[$day . $tech])) return $PLAN[$day . $tech];
    [$o, $cl] = $hoursOf($day); $t = $o + 15 * $rnd(0, 4); $out = [];
    $off = (string)q('SELECT off_days FROM staff WHERE id = ?', [$T[$tech]])->fetchColumn();
    if ($off !== '' && in_array((string)date('w', strtotime($day)), explode(',', $off), true)) return [];
    while ($t < $cl - 30) {
        $old = $day < date('Y-m-d', strtotime('-25 days')); /* 6 customers are NEW: their first visit is in the last 25 days (Reports: "New") */
        $men = array_values(array_filter($C, fn($x) => $x[2] === 'm')); $women = array_values(array_filter($C, fn($x) => $x[2] === 'w' && !($old && !empty($x[3]))));
        $c = $tech === 'CARLOS' && $rnd(1, 10) <= 7 ? $pick($men) : $pick($women); $svc = $svcFor($tech, $c[2]); /* men: Carlos (men's / kids cut); women: everyone */ $dur = (int)q('SELECT duration FROM services WHERE id = ?', [$svc])->fetchColumn();
        if ($t + $dur > $cl) break;
        if (mt_rand() / mt_getrandmax() < $fill) { $out[] = [$t, $svc, $c]; $t += $dur + 15 * $rnd(0, 2); } else $t += 30 * $rnd(1, 2); // a free gap
    }
    return $PLAN[$day . $tech] = $out;
};

// ---------- 6 gift cards: 4 sold (in use) ----------
$G = [];
foreach ([[100, 'Card', 'OLIVIA WILLIAMS', '+15155550102', 25], [50, 'Cash', 'GRACE MARTIN', '+15155550119', 18], [150, 'Card', 'DAVID KING', '+15155550204', 12], [75, 'Card', 'ELLA MOORE', '+15155550117', 6]] as [$amt, $pb, $bn, $bp, $ago]) {
    $g = gift_create((float)$amt, ['buyer_name' => $bn, 'buyer_phone' => $bp, 'source' => 'salon', 'paid_by' => $pb, 'recipient' => '', 'to_phone' => ''], 'Owner');
    $when = date('Y-m-d', strtotime("-$ago days")) . ' 14:20:00'; q('UPDATE giftcards SET created_at = ? WHERE id = ?', [$when, $g['id']]); q('UPDATE giftcard_log SET created_at = ? WHERE card_id = ?', [$when, $g['id']]);
    $G[] = (string)$g['code'];
}

// ---------- 6 history: the last 30 days, every visit paid (cash / card / tip / gift card) ----------
$nRc = 0; $err = []; $GU = 0;
$payIt = function (int $aid, string $tech, int $svc, array $c) use (&$nRc, &$err, &$GU, $T, $G, $rnd) {
    $p = (float)q('SELECT price FROM services WHERE id = ?', [$svc])->fetchColumn(); $r = $rnd(1, 100);
    $tip = round($p * [0, 0.15, 0.18, 0.2][$rnd(0, 3)]); $in = ['ids' => [$aid], 'lines' => [['appt' => $aid, 'sid' => $svc, 'price' => $p, 'staff' => $T[$tech]]], 'splits' => [['staff' => $T[$tech], 'amt' => $p]]];
    if ($r <= 8) { $disc = 10; $in['disc_type'] = '%'; $in['disc_val'] = $disc; $p = round($p * 0.9, 2); }
    if ($r <= 55) $in['pays'] = [['m' => 'Card', 'amt' => $p, 'last4' => sprintf('%04d', $rnd(1000, 9999))]] + [];
    elseif ($r <= 85) { $in['pays'] = [['m' => 'Cash', 'amt' => $p, 'given' => ceil($p / 20) * 20]]; $tip = 0; if ($rnd(0, 1)) $in['cash_tips'] = [['staff' => $T[$tech], 'amt' => $rnd(5, 15)]]; }
    elseif ($r <= 93) { $a = round($p / 2); $in['pays'] = [['m' => 'Card', 'amt' => $p - $a], ['m' => 'Cash', 'amt' => $a]]; }
    else { $code = $G[$GU % count($G)]; $b = (float)q('SELECT balance FROM giftcards WHERE code = ?', [$code])->fetchColumn(); $ga = $GU < 5 ? min(round($b * 0.4), $p) : 0.0; if ($ga > 0) $GU++; // a few uses: every card keeps money
        if ($ga > 0) { $in['gift_code'] = $code; $in['gift_amount'] = $ga; } $rest = round($p - max(0, $ga), 2); $in['pays'] = $rest > 0 ? [['m' => 'Card', 'amt' => $rest]] : []; if ($rest <= 0) $tip = 0; }
    if ($tip > 0 && array_filter($in['pays'], fn($x) => $x['m'] === 'Card')) $in['tips'] = [['staff' => $T[$tech], 'amt' => $tip]];
    db()->beginTransaction(); // like the app's own Checkout: all or nothing
    try { checkout_save($in); db()->commit(); $nRc++; } catch (Throwable $e) { if (db()->inTransaction()) db()->rollBack(); $err[] = $e->getMessage(); }
};
$today = date('Y-m-d'); $nowMin = (int)date('G') * 60 + (int)date('i');
for ($d = 60; $d >= 0; $d--) { /* 60 days: Reports compare 30 days with the 30 before */
    $day = date('Y-m-d', strtotime("-$d days")); $wd = (int)date('w', strtotime($day)); $fill = $wd === 6 ? 0.85 : ($wd === 5 ? 0.7 : ($wd === 0 ? 0.6 : 0.45));
    $V = []; foreach ($TECHS as $tech) foreach ($dayPlan($day, $tech, $fill) as [$t, $svc, $c]) $V[] = [$t, $tech, $svc, $c];
    usort($V, fn($x, $y) => ($x[0] + (int)q('SELECT duration FROM services WHERE id = ?', [$x[2]])->fetchColumn()) <=> ($y[0] + (int)q('SELECT duration FROM services WHERE id = ?', [$y[2]])->fetchColumn())); /* paid in the order they finished: receipt numbers follow the time */
    foreach ($V as [$t, $tech, $svc, $c]) {
        if ($day === $today && $t + (int)q('SELECT duration FROM services WHERE id = ?', [$svc])->fetchColumn() > $nowMin) continue; /* today: only visits already over */
        if ($rnd(1, 100) <= 3) { $mkA($day, $t, $tech, $svc, $c, 'noshow'); continue; }
        $aid = $mkA($day, $t, $tech, $svc, $c, 'arrived'); $payIt($aid, $tech, $svc, $c);
    }
}
// the receipts' times: when the visit ended (not "now")
foreach (q("SELECT r.id, r.day, a.start_min, a.duration FROM receipts r JOIN appointments a ON a.receipt_id = r.id")->fetchAll() as $x) {
    $m = (int)$x['start_min'] + (int)$x['duration']; q('UPDATE receipts SET created_at = ? WHERE id = ?', [$x['day'] . sprintf(' %02d:%02d:00', intdiv($m, 60), $m % 60), $x['id']]);
    q('UPDATE appointments SET paid_at = ? WHERE receipt_id = ?', [$x['day'] . sprintf(' %02d:%02d:00', intdiv($m, 60), $m % 60), $x['id']]); }
foreach (q('SELECT id, created_at, appt_date FROM appointments')->fetchAll() as $a) if ((string)$a['created_at'] > date('Y-m-d H:i:s')) q('UPDATE appointments SET created_at = ? WHERE id = ?', [date('Y-m-d H:i:s', strtotime('-1 day')), $a['id']]);

// ---------- past days closed (cash counted = expected, DPS = expected, locked); past payroll weeks closed – like a salon that does it every night ----------
$nLock = 0; $nWk = 0;
for ($d = 60; $d >= 1; $d--) { $day = date('Y-m-d', strtotime("-$d days")); if (hours_for($day) === null) continue;
    try { $tt = close_day($day)['totals']; day_count_save($day, (float)$tt['cashExp'], 'Counted at closing', (float)$tt['dpsExp']); day_lock($day); $nLock++; } catch (Throwable $e) { $err[] = 'close ' . $day . ': ' . $e->getMessage(); } }
$wk = payroll_week_of(date('Y-m-d')); for ($i = 8; $i >= 1; $i--) { $w0 = date('Y-m-d', strtotime($wk . " -$i weeks")); try { payroll_close($w0, true); $nWk++; } catch (Throwable $e) { $err[] = 'payroll ' . $w0 . ': ' . $e->getMessage(); } }
// ---------- 5 coming: today (what is not over) + the next 14 days ----------
$nA = 0;
for ($d = 0; $d <= 14; $d++) {
    $day = date('Y-m-d', strtotime("+$d days")); $wd = (int)date('w', strtotime($day)); $fill = ($wd === 6 ? 0.85 : ($wd === 5 ? 0.7 : ($wd === 0 ? 0.6 : 0.4))) * ($d > 7 ? 0.65 : 1);
    foreach ($TECHS as $tech) foreach ($dayPlan($day, $tech, $fill) as [$t, $svc, $c]) {
        if ($day === $today && $t + (int)q('SELECT duration FROM services WHERE id = ?', [$svc])->fetchColumn() <= $nowMin) continue; /* already in the history above */
        $status = 'booked';
        if ($day === $today && $t < $nowMin + 10) $status = 'arrived';
        $mkA($day, $t, $tech, $svc, $c, $status, ['source' => $rnd(1, 100) <= 35 ? 'online' : 'admin', 'cstate' => 'yes']); $nA++;
    }
}
// a party of 2 (mother + daughter) on the coming Saturday, and 2 online bookings that still need "confirm"
$sat = date('Y-m-d', strtotime('next saturday')); $gid = 'g628' . substr(md5($sat), 0, 6);
$mkA($sat, 11 * 60, 'ASHLEY', $sid("Women's Haircut") ?: $T['ASHLEY_svc'][0], ['+15155550105', 'ISABELLA GARCIA', 'w'], 'booked', ['group' => $gid, 'source' => 'online', 'note' => 'Mom + daughter', 'clear' => 1]);
$mkA($sat, 11 * 60, 'EMILY', $sid('Kids Haircut (12 & under)') ?: $T['EMILY_svc'][0], ['+15155550105', 'ISABELLA GARCIA +1', 'w'], 'booked', ['group' => $gid, 'source' => 'online', 'clear' => 1]);
$d2 = date('Y-m-d', strtotime('+2 days')); $d3 = date('Y-m-d', strtotime('+3 days'));
$mkA($d2, 17 * 60, 'DANIELLE', $sid('Balayage') ?: $T['DANIELLE_svc'][0], ['+15155550123', 'ARIA WHITE', 'w'], 'booked', ['source' => 'online', 'need' => 1, 'cstate' => '', 'created' => date('Y-m-d H:i:s', strtotime('-2 hours')), 'clear' => 1]);
$mkA($d3, 10 * 60, 'BRIANNA', $sid('Full Highlights') ?: $T['BRIANNA_svc'][0], ['+15155550130', 'LAYLA LEWIS', 'w'], 'booked', ['source' => 'online', 'need' => 1, 'cstate' => '', 'created' => date('Y-m-d H:i:s', strtotime('-40 minutes')), 'clear' => 1]);

// ---------- loyalty points for a few regulars ----------
if (function_exists('loyalty_add')) foreach ([['+15155550101', 6], ['+15155550104', 4], ['+15155550117', 9], ['+15155550202', 3]] as [$ph, $n]) { try { loyalty_add($ph, $n, 'hand', 'Demo visits', 0, 'Owner'); } catch (Throwable $e) {} }

// ---------- 7 nothing is ever sent: every queued text / auto send is removed ----------
$nQ = count($GLOBALS['after_reply_q'] ?? []); $GLOBALS['after_reply_q'] = []; /* the phone notifications the app queued while seeding are dropped – NOTHING goes to Apple / Google */
foreach (['outbox', 'autosend', 'sms_log', 'receipt_queue', 'review_asks', 'push_log', 'events'] as $t) { try { db()->exec("DELETE FROM $t"); } catch (Throwable $e) {} }
set_setting('sms_enabled', '0'); set_setting('as_on', '0');

$gb = q("SELECT COUNT(*) n, COALESCE(SUM(balance), 0) b FROM giftcards WHERE status = 'active'")->fetch();
echo 'XONG: ' . count($TECHS) . ' tho · ' . count($C) . ' khach · ' . (int)q('SELECT COUNT(*) FROM services WHERE active = 1')->fetchColumn() . ' dich vu · '
    . $nA . ' hen sap toi (+ nhom 2 + 2 can confirm) · ' . $nRc . ' hoa don 60 ngay (' . usd((float)q("SELECT COALESCE(SUM(total), 0) FROM receipts WHERE status = 'paid'")->fetchColumn()) . ') · '
    . $nLock . ' ngay da dong · ' . $nQ . ' thong bao bo (khong gui) · ' . $nWk . ' tuan luong da chot · ' . (int)$gb['n'] . ' gift card dang dung (con ' . usd((float)$gb['b']) . ')' . ($err ? ' · LOI checkout: ' . count($err) . ' – ' . implode(' | ', array_slice(array_unique($err), 0, 3)) : '') . "\n";
