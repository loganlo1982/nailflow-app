<?php
declare(strict_types=1);
if (defined('NF_API_LIB')) return; // (2.99.586 - LENH 586) call_in.php: only the plain functions below (create_group, book_lock...), never the router
require __DIR__ . '/inc/core.php';
require __DIR__ . '/inc/backup.php';
require __DIR__ . '/inc/import.php';
require __DIR__ . '/inc/totp.php';
require __DIR__ . '/inc/rebook.php';
require __DIR__ . '/inc/gallery.php';
require __DIR__ . '/inc/birthday.php';
require __DIR__ . '/inc/paypal.php';
require __DIR__ . '/inc/review.php';
require_once __DIR__ . '/inc/giftcards.php';
require_once __DIR__ . '/inc/outbox.php';
require __DIR__ . '/inc/logo.php';
require_once __DIR__ . '/inc/reports.php';
require_once __DIR__ . '/inc/checkout.php';
require_once __DIR__ . '/inc/payroll.php';
require_once __DIR__ . '/inc/export.php';
require_once __DIR__ . '/inc/yearend.php';
require_once __DIR__ . '/inc/referral.php'; // (2.99.43) Refer a friend
require_once __DIR__ . '/inc/promolinks.php'; // (2.99.153) Win-back / Birthday links + the "texted" steps (also used by the cron: Auto send)
require_once __DIR__ . '/inc/turnq.php'; // (2.99.57) turn line, clock in on the iPad, end-of-day report
require_once __DIR__ . '/inc/apptoffers.php';
require_once __DIR__ . '/inc/rewards.php'; // (2.99.82) Rewards // (2.99.49) offers on an appointment: pills, ✅ Applied / Not used at payment
// (2.99.206 – order 407) api.php in parts: its plain functions live in these files (≤ ~60 KB each)
require_once __DIR__ . '/inc/api/_auth.php';
require_once __DIR__ . '/inc/api/_menu.php';
require_once __DIR__ . '/inc/api/_texts.php';
require_once __DIR__ . '/inc/api/_kiosk.php';
require_once __DIR__ . '/inc/api/_out.php';

// (2.99.69) anything unexpected: a short JSON message (the page shows it) – never a blank error page; the details go to error_log only
set_exception_handler(function (Throwable $e) {
    error_log('API ' . preg_replace('/[^a-z_0-9]/', '', (string)($_GET['action'] ?? '')) . ': ' . $e->getMessage() . ' @ ' . basename($e->getFile()) . ':' . $e->getLine());
    if (!headers_sent()) { http_response_code(500); header('Content-Type: application/json; charset=utf-8'); }
    echo json_encode(['error' => 'Something went wrong on the server. Please try again in a moment.']);
});
if (!is_installed()) fail('Not installed', 503);

// Keep people logged in for 30 days (own session folder so shared-host cleanup doesn't log them out).
$sessDir = site_sessions(); // (2.99.222 – order 421 A) each salon its own
if (!is_dir($sessDir)) @mkdir($sessDir, 0700);
if (is_dir($sessDir) && is_writable($sessDir)) session_save_path($sessDir);
ini_set('session.gc_maxlifetime', (string)(60 * 60 * 24 * 30));
ini_set('session.use_strict_mode', '1'); // (2.61) never accept a session id the server did not make
$testSite = is_test_site(); // the test copy (/banthu/) keeps its own login cookie, so the real admin login is never touched
// (2.99.222 – order 421 A) a salon of the shared code living in a folder of another salon's address (a test copy): its own cookie (name + path) – never the other salon's login
$subPath = SITE_ID !== '' ? rtrim((string)parse_url((string)(cfg()['site_url'] ?? ''), PHP_URL_PATH), '/') : ''; $sub = $subPath !== '';
session_set_cookie_params(['lifetime' => 60 * 60 * 24 * 30, 'httponly' => true, 'samesite' => 'Lax', 'path' => $testSite ? '/banthu/' : ($sub ? $subPath . '/' : '/'),
    'secure' => (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') || (($_SERVER['HTTP_X_FORWARDED_PROTO'] ?? '') === 'https') || !preg_match('/^(localhost|127\.0\.0\.1)(:\d+)?$/', (string)($_SERVER['HTTP_HOST'] ?? 'localhost'))]); // (2.61) always Secure on the real site
session_name($testSite ? 'salontest' : ($sub ? 'salonsess_' . preg_replace('/\W/', '', SITE_ID) : 'salonsess'));
if ($testSite) header('X-Robots-Tag: noindex, nofollow');
$GLOBALS['sess_had'] = isset($_COOKIE[session_name()]);
session_start();
// (2.99.246 – order 446) a visitor who is not logged in and never got anything in the session (booking page, iPad, bots): no session file, no cookie.
// The reply is held (ob_start) so the cookie can still be taken back at the end; the early replies (after_reply_run, Pushover) tidy first.
$GLOBALS['sess_file'] = rtrim((string)session_save_path(), '/') . '/sess_' . session_id();
function sess_tidy(): void {
    static $done = false; if ($done) return; $done = true;
    if (!empty($GLOBALS['sess_had']) || !empty($_SESSION)) return;
    $sn = session_name();
    if (session_status() === PHP_SESSION_ACTIVE) @session_destroy();
    else { $f = (string)($GLOBALS['sess_file'] ?? ''); clearstatcache(true, $f); if ($f !== '' && is_file($f) && filesize($f) === 0) @unlink($f); } // let go early: only an EMPTY file goes
    if (!headers_sent()) { $keep = array_filter(headers_list(), fn($h) => stripos($h, 'Set-Cookie:') === 0 && stripos($h, 'Set-Cookie: ' . $sn . '=') !== 0); header_remove('Set-Cookie'); foreach ($keep as $h) header($h, false); }
}
ob_start();
register_shutdown_function('sess_tidy');

$action = $_GET['action'] ?? '';
if ($action === 'nf_ver') { header('Cache-Control: no-store'); json_out(['v' => APP_VERSION]); } // (2.99.282 – order 495) the running version only (no login needed, nothing else)
$method = $_SERVER['REQUEST_METHOD'];
$in = [];
if ($method === 'POST') $in = json_decode(file_get_contents('php://input') ?: '[]', true) ?: [];
if (!is_array($in)) $in = [];
settings(); // sets timezone
try { require_once APP_ROOT . '/inc/nb-hold.php'; nb_tick(); } catch (Throwable $e) { error_log('nb tick: ' . $e->getMessage()); } // (2.99.314 – lệnh 536) a "New booking" held > 30 s goes with ANY request (admin, AN Desk, iPad, AN Tech, the customer pages) – never only when the cron runs
try { ensure_schema(); } catch (PDOException $e) { error_log('Schema update: ' . $e->getMessage()); fail('Database error. Please try again.', 500); }
// (2.99.100) 🧪 Test mode: the customers' online booking keeps the real hours; the time ran out → stopped and cleaned by itself
$GLOBALS['tm_public'] = in_array($action, ['info', 'slots', 'book', 'dep_order', 'dep_capture', 'reschedule'], true);
test_mode_tick();
// (2.99.215 – order 412) a salon PAUSED in AN HQ (Logan): customers cannot book or move a booking online – the booking page says "Online booking is paused – please call". Data kept.
if (setting('hq_paused') === '1' && in_array($action, ['slots', 'book', 'dep_order', 'reschedule'], true)) fail('Online booking is paused – please call the salon.', 403);
/** 🧪 Test mode: the check-in iPad takes only the test numbers. */
function tm_kiosk_phone(string $phone): void { if (test_mode_on() && !is_test_phone($phone)) fail('Test mode – thêm số test trong Settings → Test numbers.', 403); /* (2.99.284 – order 500 mục 4) */ }

/* ---------- auth ---------- */
const MGR_IDLE = 12 * 3600; // a manager not using the app for 12 hours is logged out
const ADMIN_IDLE = 12 * 3600; // the owner too (the page's own background refreshes do not count)
/** (2.99.311) a request from the NailFlow app: its cookie OR its header (the header stays when the phone's web view lost the cookie). */
function nf_app_req(): bool { return ($_COOKIE['nfapp'] ?? '') === '1' || ($_SERVER['HTTP_X_NF_APP'] ?? '') === '1'; }
const ADMIN_IDLE_APP = 30 * 86400; // (2.99.253 – order 458) the owner in the NailFlow app: 30 days on that phone – the app asks Face ID / fingerprint every time it opens (assets/native.js)
const UNDECIDED_NOTE = '❓ Not decided – ask tech'; // walk-in at the iPad who tapped "Not sure yet – Skip" (shown on the schedule instead of a service)
const UNDECIDED_COLOR = '#F2B705'; // yellow on the schedule until the service is chosen
/**
 * Logged-in manager [id, name], or null. Turned off, removed or a new PIN = logged out everywhere; so is 12 hours without using the app
 * (the page's own background refreshes send X-Auto and do not count).
 */
function manager_session(): ?array {
    static $m = false;
    if ($m !== false) return $m;
    $id = (int)($_SESSION['mgr_id'] ?? 0);
    if (!$id) return $m = null;
    $r = q('SELECT * FROM managers WHERE id = ?', [$id])->fetch();
    if (!$r || !(int)$r['active'] || $r['pin_hash'] === '' || (int)$r['pin_ver'] !== (int)($_SESSION['mgr_ver'] ?? -1)
        || time() - (int)($_SESSION['mgr_seen'] ?? 0) > MGR_IDLE) { unset($_SESSION['mgr_id'], $_SESSION['mgr_ver'], $_SESSION['mgr_seen']); return $m = null; }
    if (($_SERVER['HTTP_X_AUTO'] ?? '') !== '1') $_SESSION['mgr_seen'] = time();
    return $m = ['id' => $id, 'name' => (string)$r['name'], 'display' => (string)($r['display_name'] ?? '')];
}
/**
 * 'admin' (the owner), 'manager' (Appointments only) or ''. The owner can open /manager/ to see exactly what a manager sees:
 * that page sends X-Role: manager, which only ever takes rights away.
 */
function role(): string {
    if (desk_req()) return desk_session() && in_array($_GET['action'] ?? '', DESK_ACTIONS, true) ? 'desk' : ''; // (2.99.89) the Front desk iPad: only its person, only its actions
    if (!empty($_SESSION['qmode'])) return ''; // (2.99.322 – lệnh 539) checkout mode: this login has AN Desk rights only (X-Desk + PIN, above) until the owner password is typed (qd_exit)
    if (!empty($_SESSION['admin']) && (int)($_SESSION['admin_pw'] ?? 0) !== (int)setting('admin_pw_ver')) { unset($_SESSION['admin'], $_SESSION['admin_seen']); } // (2.99.88) the password changed: older sessions log in again
    if (!empty($_SESSION['admin'])) {
        if (time() - (int)($_SESSION['admin_seen'] ?? time()) > (nf_app_req() ? ADMIN_IDLE_APP : ADMIN_IDLE)) { unset($_SESSION['admin'], $_SESSION['admin_seen']); return manager_session() ? 'manager' : ''; }
        if (($_SERVER['HTTP_X_AUTO'] ?? '') !== '1') { $_SESSION['admin_seen'] = time(); owner_seen(); }
        return ($_SERVER['HTTP_X_ROLE'] ?? '') === 'manager' ? 'manager' : 'admin';
    }
    return manager_session() ? 'manager' : '';
}
function is_admin(): bool { return role() === 'admin'; }
/** (2.99.215 – order 412) "Owner last in" on the AN HQ card: the owner (never qa-bot) used the admin – saved at most every 10 minutes. */
function owner_seen(): void { static $done = false; if ($done || !empty($_SESSION['qa']) || !empty($_SESSION['support'])) return; $done = true; // (567) NailFlow support is not the owner
    if (time() - (int)strtotime(setting('admin_last_login') ?: '2000-01-01') >= 600) { try { set_setting('admin_last_login', now_str()); } catch (Throwable $e) {} } }
/* ---------- (2.99.89) Front desk iPad (/desk/?k=…) ----------
   The page sends its link code in X-Desk on every call. Nothing opens with the code alone: the person at the desk types their PIN (the owner's
   own tech, a manager, or a tech with "Front desk: can check out / sell gift cards"), once – until "🔒 Lock" or the end of the day (2.99.134).
   With X-Desk the owner / manager login of this browser is never used – only the person who typed the PIN, and only the actions below. */
const DESK_IDLE = 330; // (2.99.101) not used any more: (2.99.134) the desk stays open until "🔒 Lock" or the end of the day
const DESK_ACTIONS = [/* (2.99.638g) */ 'ttp_result', /* (2.99.638e) */ 'dv_day', /* (2.99.638c) the desk iPad pays on the P5 too */ 'dv_charge', 'dv_cancel', 'dv_waiting', /* (2.99.362 – lệnh 604) Lịch theo turn */ 'turn_view', /* (2.99.344 – lệnh 578) */ 'quick_co_pin', /* (2.99.338 – lệnh 570) */ 'quick_co_info', 'quick_checkout', /* (2.99.312 – lệnh 532) */ 'turn_over_answer', 'desk_tech', /* (2.99.295 – order 512) Checkout closed */ 'ticket_close', /* (2.99.288 – order 504) ↩ Chưa xong */ 'appt_not_done', /* (2.99.282 – order 495) Bán gift card on AN Desk: is the card number free */ 'gift_code_check', 'turn_eta', 'pass_keep', /* (2.99.272) */ 'visit_merge', 'visit_split', /* (2.99.269) */ 'turn_accept_for', 'turn_offer_next', /* (2.99.256) */ 'ticket', 'appt_services', 'checkout2', 'receipt', 'gift_lookup', 'gift_by_phone', 'gift_create', 'gift_text', 'text_sent', 'before_undo', 'desk_list', 'desk_lock', 'rq_add', 'receipts', 'desk_threads', 'desk_thread', 'desk_reply', 'desk_push']; // (2.99.142) + Receipts today (look / print again)
/** (2.99.93) The Front desk iPad never gets a customer's phone number: every phone field taken out of its answers (no "Text receipt" there). */
function desk_clean($x) {
    if (!is_array($x)) return $x;
    $o = [];
    foreach ($x as $k => $v) {
        if ($k === 'salon') { $o[$k] = $v; continue; } // the salon's own name / address / phone stay (printed on the receipt)
        if (is_string($k) && (preg_match('/phone|^pretty$|^ph$|^ph[A-Z]|^tel$/i', $k))) continue;
        if ($k === 'canText') { $o[$k] = false; continue; }
        if ($k === 'textBody' || $k === 'smsBody') continue;
        $o[$k] = desk_clean($v);
    }
    return $o;
}
// (2.99.206 – order 407) the functions that were here: inc/api/_auth.php


// Who is doing things, for the activity log (customer pages and the check-in iPad say it themselves).
$DESK = desk_req(); // (2.99.89) the Front desk iPad: the name of the person who typed the PIN ("TAMMY (front desk)") – on the receipt as "Checked out by"
if ($DESK) actor_set('desk', ($d0 = desk_session()) ? $d0['name'] . ' (front desk)' : 'Front desk iPad');
elseif (!empty($_SESSION['admin'])) actor_set('admin', 'Owner');
// (2.99.336 – lệnh 567) NailFlow support (from AN HQ, with the owner's code): its own name in every log, 2 hours, some things never
require_once APP_ROOT . '/inc/support.php';
if (!$DESK && !empty($_SESSION['support'])) {
    if (sup_session()) { actor_set('admin', 'NailFlow support');
        if (in_array($action, SUP_DENY, true)) fail('NailFlow support không làm việc này – chủ tiệm tự làm. · Not allowed in a support session.', 403);
        if ($action === 'save_settings') unset($in['owner_email'], $in['admin_reset_phone']); }
    elseif ($action !== 'me' && $action !== 'sup_exit') fail('Phiên hỗ trợ đã hết (2 giờ). · The support session ended.', 401);
}
/* (2.99.622 #8 = pub/api.php 2.99.428) 👀 Guest owner (a try-out login): the owner's pages, minus the GUEST_DENY list; "Guest owner" in every log */
require_once APP_ROOT . '/inc/guest.php';
if (!$DESK && !empty($_SESSION['guest']) && !empty($_SESSION['admin'])) { actor_set('admin', 'Guest owner'); guest_guard($action, $in); }
/* (2.99) qa-bot: the test account – the admin pages like the owner, but it may only change TEST bookings / test numbers (qa_guard). */
if ($DESK) {}
elseif (!empty($_SESSION['qa'])) {
    if (setting('qa_off') === '1') { $_SESSION = []; fail('The QA account is turned off.', 401); }
    actor_set('admin', 'qa-bot'); qa_guard($action, $method, $in);
}
elseif ($mgr0 = manager_session()) actor_set('manager', 'Manager ' . $mgr0['name']);
elseif (staff_session()) actor_set('staff', 'Tech ' . staff_name(staff_session()));
// (2.99.206 – order 407) the functions that were here: inc/api/_menu.php

// (2.99.206 – order 407) the functions that were here: inc/api/_texts.php

// (2.99.206 – order 407) the functions that were here: inc/api/_kiosk.php

// (2.99.206 – order 407) the functions that were here: inc/api/_out.php

/** A booking the customer page cannot make; the message is shown to the customer. */
final class BookingError extends RuntimeException {}

/** Checks an online booking from the customer page (also again when a deposit is paid). Throws BookingError. */
function online_booking_check(array $in): array {
    $tm = test_link_ok((string)($in['tm'] ?? '')); // (2.55.2) TEST MODE page
    if (setting('online_booking') !== '1' && !$tm) throw new BookingError('Online booking is turned off. Please call the salon.');
    if (!empty($in['website'])) throw new BookingError('Blocked'); // honeypot
    $date = (string)($in['date'] ?? ''); $start = (int)($in['start'] ?? -1);
    $people = array_map('intval', is_array($in['people'] ?? null) ? $in['people'] : [0]);
    $people = array_slice($people, 0, max_group()) ?: [0];
    $name = strtoupper(trim(mb_substr((string)($in['name'] ?? ''), 0, 60)));
    $phone = norm_phone((string)($in['phone'] ?? ''));
    $each = person_services($in['svcs'] ?? null, count($people)); // (2.51) each person their own services
    $svc = $each ? services_by_ids(array_values(array_unique(array_merge(...array_map(fn($l) => array_map('intval', array_column($l, 'id')), $each))))) : services_by_ids(ints($in['services'] ?? []));
    if ($each && in_array([], $each, true)) throw new BookingError('Please choose a service for each person.');
    if (!$each) $each = array_fill(0, count($people), $svc);
    if (!valid_date($date) || !$svc) throw new BookingError('Please choose a service and time.');
    if (strlen($phone) !== 12) throw new BookingError('Please enter a 10-digit US phone number.');
    if (fake_phone($phone)) throw new BookingError('Please enter your real mobile number.'); // (2.55.24)
    if ($tm && !is_test_phone($phone)) throw new BookingError('TEST MODE: only test numbers can book here (Settings → Test numbers).');
    $c = customer_by_phone($phone);
    // Returning customers are greeted as "Linh N." and send no name: use the full name on file.
    if ($name === '' && $c) $name = strtoupper(trim((string)$c['name']));
    if ($name === '') throw new BookingError('Please enter your name.');
    $tp = $tm && is_test_phone($phone); // (2.61) test numbers skip the limits only on the TEST MODE page (a known test number on the normal page is a normal customer)
    if (!$tp && $c && (int)($c['suspect'] ?? 0) === 1) // released twice for not confirming (the owner can clear it in Customers)
        throw new BookingError('Please call the salon to book your appointment: ' . setting('salon_phone') . '. Thank you!', 403);
    $test = $tp; // test numbers (TEST MODE page): no limits, no minimum notice, never "call the salon"
    $upcoming = (int)q("SELECT COUNT(*) FROM appointments WHERE phone = ? AND appt_date >= ? AND status = 'booked'", [$phone, date('Y-m-d')])->fetchColumn();
    if (!$test && $upcoming + count($people) > max(10, max_group())) throw new BookingError('You already have several upcoming appointments. Please call the salon to book more.');
    // nail design, asked for each person: their design service takes 1 h 30; the open times fit the longest person
    $designs = array_map(fn($k) => has_design_service($each[$k]) && !empty($in['design'][$k]) ? 1 : 0, array_keys($people));
    $durs = array_map(fn($k) => services_minutes($each[$k], (bool)$designs[$k]), array_keys($people));
    $dur = max($durs);
    $sids = array_map('intval', array_column($svc, 'id'));
    [$per, $people] = booking_per($people, $each, $designs, is_array($in['plan'] ?? null) ? $in['plan'] : []); // (2.53) a tech for each service
    foreach ($per as $k => $x) if (!empty($x['segs'])) $durs[$k] = (int)$x['dur'];
    $dur = max($durs);
    if (!$test && $start < online_earliest($date)) // e.g. the page was left open: that time is now too close to book online
        throw new BookingError((int)setting('min_notice_min') > 0 ? 'Online bookings need at least ' . notice_label() . ' notice. Please pick a later time.' : 'That time has passed. Please pick a later time.', 409);
    if (!in_array($start, public_slots($date, $people, $sids, $dur, $test, $per), true)) throw new BookingError('Sorry, that time was just taken. Please pick another time.', 409);
    $mode = $GLOBALS['slot_modes'][$start] ?? 'seq';
    return ['date' => $date, 'start' => $start, 'people' => $people, 'name' => $name, 'phone' => $phone, 'svc' => $svc, 'sids' => $sids, 'dur' => $dur, 'durs' => $durs, 'designs' => $designs, 'c' => $c, 'each' => $each, 'per' => $per, 'mode' => $mode,
        'note' => trim(mb_substr((string)($in['note'] ?? ''), 0, 300)), 'sms_ok' => !empty($in['sms_ok']), 'birthday' => (string)($in['birthday'] ?? ''), 'bchange' => !empty($in['bchange'])];
}
/** Makes a checked online booking: customer, appointments, confirmation text, alerts. $depositEach = paid online for each person. */
function online_book_create(array $b, float $depositEach = 0): array {
    actor_set('online', 'Customer (online)');
    $isNew = nc_on() && nc_is_new($b['phone']) ; // (2.99.283 – order 497) test numbers too (was: no fake-booking rule for them) // new customer: must tap Confirm in the text (inc/noconfirm.php)
    $big = count($b['people']) > count(online_staff($b['date'], $b['sids'])); // more people than techs taking online bookings that day: the salon arranges them
    if (!$b['c'] || trim((string)$b['c']['name']) === '') upsert_customer($b['phone'], $b['name']); // keep the name the salon already has on file
    if (setting('bday_on') === '1' && preg_match('/^(\d{2})-(\d{2})$/', $b['birthday'], $bm)) bday_store($b['phone'], (int)$bm[1], (int)$bm[2], $b['bchange']); // (2.64) month + day ("03-00" = the month only); fills in what is missing, changes it only after "Change"
    $each = $b['each'] ?? [];
    $rows = create_group(['people' => $b['people'], 'date' => $b['date'], 'start' => $b['start'], 'duration' => $b['dur'], 'durations' => $b['durs'] ?? [], 'designs' => $b['designs'] ?? [], 'service_ids' => implode(',', $b['sids']),
        'service_ids_each' => array_map(fn($l) => implode(',', array_column($l, 'id')), $each), 'price_each' => array_map(fn($l) => array_sum(array_column($l, 'price')), $each),
        'color_each' => array_map(fn($l) => $l[0]['color'] ?? '', $each), 'segs_each' => segs_placed($b['per'] ?? [], (int)$b['start'], (string)($b['mode'] ?? 'seq')),
        'name' => $b['name'], 'phone' => $b['phone'], 'note' => $b['note'], 'color' => $b['svc'][0]['color'],
        'walkin' => false, 'source' => 'online', 'price' => array_sum(array_column($b['svc'], 'price')), 'sms_ok' => $b['sms_ok']]);
    if ($depositEach > 0) foreach ($rows as $r) q('UPDATE appointments SET deposit = ? WHERE id = ?', [$depositEach, $r['id']]);
    if ($isNew && $depositEach <= 0) { // (a paid deposit is proof enough)
        foreach ($rows as $r) q('UPDATE appointments SET confirm_need = 1 WHERE id = ?', [$r['id']]);
        $rows = array_map(fn($r) => get_appt((int)$r['id']), $rows);
    }
    $conf = out_booked($rows); // the confirmation text goes on Messages → To send (sent by itself only with Twilio on)
    $texted = $conf && $conf['status'] === 'sent';
    $n = count($rows);
    $dep = $depositEach > 0 ? ' · deposit ' . usd($depositEach * $n) . ' paid' : '';
    $calls = [['admin', 'online', ($big ? "Big group ($n people) – please arrange the techs: " : '') . $b['name'] . ($n > 1 && !$big ? " · $n people" : '')
        . ' · ' . appt_label($rows[0]) . ' · ' . short_when($rows[0]) . $dep, (int)$rows[0]['id'],
        !empty($GLOBALS['ref_push']) ? ['title' => '', 'body' => (string)$GLOBALS['ref_push'] . ' · ' . short_when($rows[0])] // (2.99.43) booked through a friend's link
        : ['body' => ($big ? "Big group ($n people): " : '') . push_line($rows[0]) . ($n > 1 && !$big ? " · $n people" : '') . $dep]],
        ['chime', (int)$rows[0]['id'], '📅 New booking: ' . push_line($rows[0]) . ($n > 1 ? " · $n people" : ''), 'online_new']]; // the chime on the open pages
    foreach ($rows as $r) $calls[] = ['staff', (int)$r['staff_id'], 'new', 'New: ' . appt_line($r), (int)$r['id']];
    // (2.99.306 – lệnh 21:42) the customer's YOU'RE BOOKED goes to the Android first: these notifications wait for its "Sent" (at most 30 s – inc/nb-hold.php);
    // not going by the Android (by hand / Auto send off / failed) → at once as before. The calendar shows the booking at once either way.
    require_once APP_ROOT . '/inc/nb-hold.php';
    $hold = 0; try { $hold = nb_hold_as_id($conf); } catch (Throwable $e) { $hold = 0; }
    if ($hold) nb_hold_add($hold, $calls); else nb_run($calls);
    return ['rows' => $rows, 'texted' => $texted];
}

/** One booking at a time (checking the free times and saving it), so two people can't take the same time together.
    Released when the request ends. */
function book_lock(): bool {
    if (is_sqlite()) { // (2.99.69) the local test copy: a file lock, so a test with many requests at once works like the real site (MySQL GET_LOCK)
        static $fh = null; if ($fh) return true;
        $fh = @fopen(sys_get_temp_dir() . '/salon_booking_' . md5((string)(cfg()['sqlite_path'] ?? '') . (SITE_ID !== '' ? '|' . SITE_ID : '')) . '.lock', 'c');
        $ok = $fh && flock($fh, LOCK_EX); $GLOBALS['book_lock_fh'] = $fh; $GLOBALS['book_locked'] = $ok; return $ok; } // let go when the request ends (or book_unlock)
    try { $ok = (bool)q('SELECT GET_LOCK(?, 8)', [lock_name('booking')])->fetchColumn(); $GLOBALS['book_locked'] = $ok; return $ok; } catch (Throwable $e) { return false; }
}
/** (2.99.163) "📲 Book & text to confirm": the code the customer's phone made (6 letters / digits, the first a letter) is kept on the booking
    (the first row of a group). Taken by another booking → a new one (the customer's text then matches nothing and is skipped). Returns "AN-…". */
function an_code_take(string $want, array $row): string {
    $abc = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'; $c = strtoupper(trim($want));
    $pre = preg_match('/^[A-Z]{2}$/', strtoupper((string)setting('code_prefix'))) ? strtoupper((string)setting('code_prefix')) : 'AN'; // (2.99.261) LN-… on the shared Android
    if (!preg_match('/^[A-HJ-NP-Z][A-HJ-NP-Z2-9]{5}$/', $c)) return $pre . '-' . (int)$row['id'];
    for ($i = 0; $i < 5 && q("SELECT 1 FROM appointments WHERE an_code = ? AND id <> ?", [$c, (int)$row['id']])->fetchColumn(); $i++) {
        $c = $abc[random_int(0, 23)]; for ($j = 0; $j < 5; $j++) $c .= $abc[random_int(0, 31)]; }
    q('UPDATE appointments SET an_code = ? WHERE id = ?', [$c, (int)$row['id']]);
    return $pre . '-' . $c;
}
function an_of(array $row): string { $p = preg_match('/^[A-Z]{2}$/', strtoupper((string)setting('code_prefix'))) ? strtoupper((string)setting('code_prefix')) : 'AN'; return (string)($row['an_code'] ?? '') !== '' ? $p . '-' . $row['an_code'] : $p . '-' . (int)$row['id']; }
/** (2.99.162) Let go of the booking lock early (before the email / notifications sent after the answer). */
function book_unlock(): void {
    if (empty($GLOBALS['book_locked'])) return; $GLOBALS['book_locked'] = false;
    if (is_sqlite()) { if (!empty($GLOBALS['book_lock_fh'])) { flock($GLOBALS['book_lock_fh'], LOCK_UN); } return; }
    q('SELECT RELEASE_LOCK(?)', [lock_name('booking')]);
}
/** Create appointments for 1+ people. Returns created rows. */
function create_group(array $o): array {
    $people = $o['people']; $segsE = (array)($o['segs_each'] ?? []);
    $gid = count($people) > 1 || $segsE ? bin2hex(random_bytes(6)) : ''; // (2.53) parts of one person are linked through the group too
    $rows = []; $n = count($people);
    $ins = function (array $v) use ($o, $gid) {
        q('INSERT INTO appointments (appt_date, start_min, duration, staff_id, service_ids, customer_name, phone, note, color, kind, status, source, is_new, walkin, group_id, price, arrived_at, token, created_at, sms_ok, design, split_of)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
          [$o['date'], $v['start'], $v['dur'], $v['staff'], $v['sids'], $v['name'], $o['phone'], $v['note'], $v['color'] ?: $o['color'], 'appt',
           $o['walkin'] ? 'arrived' : 'booked', $o['source'], $o['source'] === 'online' ? 1 : 0, $o['walkin'] ? 1 : 0, $gid, $v['price'],
           $o['walkin'] ? now_str() : '', bin2hex(random_bytes(12)), now_str(), ($o['sms_ok'] ?? true) ? 1 : 0, $v['design'], $v['split_of']]);
        $nid = (int)db()->lastInsertId(); test_sync_appt($nid); // a test phone number: TEST booking
        return get_appt($nid);
    };
    foreach ($people as $k => $pid) { // per person: their own services, length and nail design (online groups answer for each person)
        $name = $k ? (trim((string)($o['names'][$k] ?? '')) !== '' ? (string)$o['names'][$k] : mb_substr($o['name'], 0, 55) . ' +' . $k) : $o['name']; $note = (string)($o['notes'][$k] ?? $o['note']);
        $segs = $segsE[$k] ?? null;
        if ($segs) { // (2.53) a tech for each service: the first part, then the others linked to it (split_of)
            $main = null;
            foreach ($segs as $i => $g) {
                $r = $ins(['start' => (int)$g['start'], 'dur' => (int)$g['dur'], 'staff' => (int)$g['staff'], 'sids' => implode(',', $g['sids']), 'name' => $name, 'note' => $i ? '' : $note,
                    'color' => (string)$g['color'], 'price' => (float)$g['price'], 'design' => (int)$g['design'], 'split_of' => $main ? (int)$main['id'] : 0]);
                if (!$main) $main = $r;
                $rows[] = $r;
            }
            continue;
        }
        $rows[] = $ins(['start' => (int)$o['start'], 'dur' => (int)($o['durations'][$k] ?? $o['duration']), 'staff' => (int)$pid, 'sids' => (string)($o['service_ids_each'][$k] ?? $o['service_ids']),
            'name' => $name, 'note' => $note, 'color' => (string)($o['color_each'][$k] ?? ''), 'price' => (float)($o['price_each'][$k] ?? $o['price']),
            'design' => (int)($o['designs'][$k] ?? $o['design'] ?? 0), 'split_of' => 0]);
    }
    foreach ($rows as $r) appt_log($r, 'booked', implode(' · ', array_filter([appt_label($r) ?: ($r['note'] !== '' ? '' : 'No service'),
        (int)$r['staff_id'] ? staff_name((int)$r['staff_id']) : 'ANYONE', $r['duration'] . ' min', $o['walkin'] ? 'walk-in' : '', $n > 1 ? "group of $n" : '',
        (int)$r['split_of'] ? '🔗 with the block at ' . min_to_label((int)get_appt((int)$r['split_of'])['start_min']) : ''])));
    return $rows;
}
/** "Time: Mon Sep 29 2:00 PM → Tue Sep 30 3:00 PM · Tech: TONY → LOGAN …" – what an edit changed, for the activity log. */
function appt_changes(array $old, array $new): string {
    $when = fn($a) => date('D M j', strtotime((string)$a['appt_date'])) . ' ' . min_to_label((int)$a['start_min']);
    $tech = fn($a) => (int)$a['staff_id'] ? staff_name((int)$a['staff_id']) : 'ANYONE';
    $p = [];
    if ($when($old) !== $when($new)) $p[] = 'Time: ' . $when($old) . ' → ' . $when($new);
    if ((int)$old['staff_id'] !== (int)$new['staff_id']) $p[] = 'Tech: ' . $tech($old) . ' → ' . $tech($new);
    if (($s0 = appt_label($old)) !== ($s1 = appt_label($new))) $p[] = 'Services: ' . ($s0 ?: '—') . ' → ' . ($s1 ?: '—');
    if ((int)$old['duration'] !== (int)$new['duration']) $p[] = 'Length: ' . $old['duration'] . ' → ' . $new['duration'] . ' min';
    if ($old['customer_name'] !== $new['customer_name']) $p[] = 'Name: ' . $old['customer_name'] . ' → ' . $new['customer_name'];
    if ($old['phone'] !== $new['phone']) $p[] = 'Phone changed';
    if ($old['note'] !== $new['note']) $p[] = 'Note changed';
    return implode(' · ', $p);
}

define('API_MAIN', 1);
/* (2.99.139) which file has each action (inc/api/<file>.php) – one file per group of screens; only that file is loaded */
const API_ROUTES = [/* (2.99.632 - LENH 632) the salon setup link */ /* (2.99.635B - LENH 635B) the same actions as AN / Love Nails' own api.php */ 'ck_app_exit' => 'qdesk', 'colorlib_brands' => 'colors', 'colorlib_get' => 'colors', 'colors_admin' => 'colors', 'colors_ai_on' => 'colors', 'colors_ai_read' => 'colors', 'colors_auto_save' => 'colors', 'colors_delete' => 'colors', 'colors_import' => 'colors', 'colors_list' => 'colors', 'colors_photo' => 'colors', 'colors_save' => 'colors', 'colors_undo' => 'colors', 'guest_info' => 'guestapi', 'guest_set' => 'guestapi', 'login_sms' => 'auth', 'oldok_info' => 'oldok', 'oldok_set' => 'oldok', 'oldok_undo' => 'oldok', 'tfa_info' => 'tfa', 'turn_view' => 'turnview', 'setup_new' => 'setuplink', 'setup_prev' => 'setuplink', 'setup_prev_clear' => 'setuplink', 'setup_info' => 'setuplink', 'setup_turn' => 'setuplink', 'setup_shop' => 'setuplink', 'setup_staff_one' => 'setuplink', 'setup_staff_off' => 'setuplink', 'setup_staff_end' => 'setuplink', /* (2.99.612 - LENH 612) */ /* (2.99.638b - LENH 638) Dejavoo P5 box, NailFlow only */ 'dv_info' => 'dejavoo', 'dv_save' => 'dejavoo', 'dv_check' => 'dejavoo', /* (2.99.638c - LENH 638) Checkout card on the P5 */ 'dv_charge' => 'dvpay', 'dv_cancel' => 'dvpay', 'dv_waiting' => 'dvpay', /* (2.99.638e) */ 'dv_day' => 'dvpay', /* (2.99.638g) Tap to Pay result */ 'ttp_result' => 'dvpay', /* (2.99.645a - LENH PAYROC) Payroc Cloud: HQ box + sandbox tests (NailFlow only), Checkout card */ 'pr_info' => 'payroc', 'pr_save' => 'payroc', 'pr_check' => 'payroc', 'pr_test' => 'payroc', 'pr_tests_csv' => 'payroc', 'pr_charge' => 'prpay', 'pr_stop' => 'prpay', 'pr_cancel' => 'prpay', 'pr_waiting' => 'prpay', 'tx_cfg' => 'callstx', 'tx_setup' => 'callstx', 'tx_ids' => 'callstx', /* (2.99.586 - LENH 586) */ 'calls_state' => 'calls', 'calls_list' => 'calls', 'call_get' => 'calls', 'call_audio' => 'calls', 'call_undo' => 'calls', 'call_seen' => 'calls', 'call_booked' => 'calls', 'calls_cfg' => 'calls', /* (2.99.341 – lệnh 575) */ 'qd_lockinfo' => 'qdesk', 'qd_unlock' => 'qdesk', /* (2.99.338 – lệnh 570) */ 'quick_co_info' => 'quickco', 'quick_checkout' => 'quickco', 'quick_co_pin' => 'quickco' /* (2.99.344 – lệnh 578) */, /* (2.99.336 – lệnh 567) */ 'sup_open' => 'support', 'sup_exit' => 'support', 'sup_kick' => 'support', /* (2.99.332 – lệnh 561) */ 'cxl_undo' => 'notify', /* (2.99.329 – lệnh 556) */ 'snd_get' => 'sounds', 'snd_set' => 'sounds', /* (2.99.339 – lệnh 569) */ 'voice_list' => 'sounds', 'voice_have' => 'sounds', 'voice_lang' => 'sounds', /* (2.99.325 – lệnh 550) */ 'rg_get' => 'ring', 'rg_save' => 'ring', 'rg_me' => 'ring', /* (2.99.322 – lệnh 539) */ 'qd_on' => 'qdesk', 'qd_exit' => 'qdesk', 'qd_state' => 'qdesk', 'qd_dev_add' => 'qdesk', 'qd_dev_exit' => 'qdesk', 'qd_dev_list' => 'qdesk', 'qd_dev_del' => 'qdesk', 'pt_cfg' => 'pushtech', 'pt_file' => 'pushtech', 'pt_test' => 'pushtech', /* (2.99.315 – lệnh 534) */ 'tech_svc_undo' => 'techapp', 'turn_over_answer' => 'techeasy', 'desk_tech' => 'techeasy', /* (2.99.312 – lệnh 532) */ 'cal_move' => 'calmove', /* (2.99.296 – order 513) */ 'person_edit' => 'pedit', 'ticket_close' => 'pedit', /* (2.99.295 – order 512) */ 'receipt_swap_list' => 'rcswap', 'receipt_swap' => 'rcswap', /* (2.99.294 – order 511) */ 'admin_setup_totp' => 'ownersetup', /* (2.99.291 – order 508) */ 'appt_not_done' => 'appts', /* (2.99.288 – order 504) */ 'getstarted' => 'start', 'gs_mark' => 'start', /* (2.99.218 – order 419) */ 'talk_start' => 'talk', 'talk_poll' => 'talk', 'talk_end' => 'talk', 'talk_state' => 'talk', 'talk_answer' => 'talk', /* (2.99.165) */ 'info' => 'public', 'slots' => 'public', 'book' => 'public', 'dep_order' => 'public', 'dep_capture' => 'public', 'lookup_name' => 'public', 'quick_rebook' => 'public', 'bstat' => 'public', 'an_check' => 'public', 'an_code_send' => 'public', 'an_code_check' => 'public', /* (2.99.243) */ 'review_list' => 'marketing', 'bday_list' => 'marketing', 'bday_sent' => 'marketing', 'refer_list' => 'marketing', 'refer_credit_told' => 'marketing', 'refer_sent' => 'marketing', 'refer_lookup' => 'marketing', 'ref_intro' => 'marketing', 'referral' => 'marketing', 'review_today' => 'marketing', 'review_asked' => 'marketing', 'winback_list' => 'marketing', 'promo_list' => 'marketing', 'promo_sent' => 'marketing', 'winback_sent' => 'marketing', 'winback_stop' => 'marketing', 'autosend_kick' => 'autosend', 'autosend_reply_done' => 'autosend', 'autosend_page' => 'autosend', 'autosend_save' => 'autosend', 'as_send_now' => 'autosend' /* (2.99.251) */, 'autosend_fail' => 'autosend', 'autosend_device' => 'autosend', 'android_check' => 'autosend', 'android_test' => 'autosend', 'sms_hook' => 'autosend', 'link_stop' => 'stop', 'stop_check' => 'stop', 'stop_feed' => 'stop', 'stop_del_keep' => 'stop', 'stop_del_all' => 'stop', 'cust_restore' => 'stop', 'cust_by_id' => 'stop', 'bstats' => 'stop', 'my_appt' => 'links', 'ics' => 'links', 'reschedule' => 'links', 'answer' => 'links', 'gift_info' => 'links', 'gift_order' => 'links', 'gift_capture' => 'links', 'gallery' => 'links', 'test_link_new' => 'links', 'desk_info' => 'desk', 'desk_unlock' => 'desk', 'desk_lock' => 'desk', 'desk_list' => 'desk', 'desk_threads' => 'desk', 'desk_thread' => 'desk', 'desk_reply' => 'desk', 'desk_push' => 'desk', 'ck_info' => 'checkin', 'ck_staff' => 'checkin', 'ck_clock' => 'checkin', 'ck_staffpin' => 'checkin', 'ck_busy' => 'checkin', 'ck_diag' => 'checkin', 'ck_tick' => 'checkin', 'ck_lookup' => 'checkin', 'ck_checkin' => 'checkin', 'ck_birthday' => 'checkin', 'ck_optin' => 'checkin', 'ck_undo' => 'checkin', 'ck_refcheck' => 'checkin', 'ck_walkin' => 'checkin', 'me' => 'auth', 'hq_open' => 'auth', 'app_login' => 'auth', /* (2.99.224 – order 421 B) */ 'set_lang' => 'auth', 'login' => 'auth', 'qa_login' => 'auth', 'admin_setup' => 'auth', 'qa_set' => 'auth', 'login_2fa' => 'auth', 'app_resume' => 'auth', 'mgr_names' => 'auth', 'mgr_login' => 'auth', 'mgr_logout' => 'auth', 'managers' => 'auth', 'mgr_save' => 'auth', 'mgr_remove' => 'auth', 'activity' => 'auth', 'appt_log' => 'auth', 'logout' => 'auth', 'day' => 'appts', 'save_appt' => 'appts', 'book_check' => 'appts', 'appt_split' => 'appts', 'appt_rename' => 'appts', 'set_status' => 'appts', 'seen' => 'appts', 'delete_appt' => 'appts', 'appt_restore' => 'appts', 'redo_create' => 'appts', 'checkout' => 'checkout', 'ticket' => 'checkout', 'checkout2' => 'checkout', 'visit_merge' => 'checkout', 'visit_split' => 'checkout' /* (2.99.269 – order 479) */, 'unpaid_earlier' => 'checkout', 'unpaid_visits' => 'checkout', 'receipts' => 'checkout', 'receipt' => 'checkout', 'receipt_void' => 'checkout', 'receipt_refund' => 'checkout', 'refund_preview' => 'checkout', 'receipt_fee_lines' => 'checkout', 'receipt_addpay' => 'checkout', 'receipt_lines' => 'checkout', 'receipt_money' => 'checkout' /* (2.99.345 – lệnh 580) */, 'tip_payout' => 'checkout', 'money_report' => 'checkout', 'money_overview' => 'checkout', 'receipt_tips_edit' => 'checkout', 'tech_turn' => 'techapp', 'tech_ask_answer' => 'techapp', 'turn_ask_give' => 'techapp', 'turn_accept_for' => 'techapp', 'tech_pass_ok' => 'techapp', 'pass_keep' => 'techapp' /* (2.99.272) */, 'tech_eta' => 'techapp', 'turn_eta' => 'techapp' /* (2.99.273) */, 'turn_offer_next' => 'techapp' /* (2.99.256) */, 'turn_asks' => 'techapp', 'tech_break' => 'techapp', 'tech_svc_done' => 'techapp', 'tech_pay_weeks' => 'techapp', 'tech_year' => 'techapp', 'tech_push_test' => 'techapp', 'tech_turn_accept' => 'techapp', 'tech_turn_skip' => 'techapp', 'tech_money' => 'techapp', 'tech_range' => 'techapp', 'tech_payweek' => 'techapp', 'close_day' => 'closeday', 'close_day_count' => 'closeday', 'close_day_lock' => 'closeday', 'report_day' => 'closeday', 'drawer_check' => 'closeday', 'close_day_unlock' => 'closeday', 'offer_undo' => 'closeday', 'paid_outside' => 'closeday', 'clear_day' => 'closeday', 'before_since_start' => 'closeday', 'before_move_back' => 'closeday', 'before_list' => 'closeday', 'before_clear' => 'closeday', 'before_undo' => 'closeday', 'undo_checkout' => 'closeday', 'gift_lookup' => 'gift', 'gift_by_phone' => 'gift', 'gift_search' => 'gift', 'gift_create' => 'gift', 'gift_code_check' => 'gift', 'gift_text' => 'gift', 'gift_adjust' => 'gift', 'gift_void' => 'gift', 'gift_balance' => 'gift', 'loyalty_set' => 'gift', 'tech_out' => 'techout', 'out_plan' => 'techout', 'out_move' => 'techout', 'out_texts' => 'techout', 'tech_off_list' => 'techout', 'tech_off_range' => 'techout', 'tech_back' => 'techout', 'outbox' => 'texts', 'outbox_mark' => 'texts', 'outbox_android' => 'texts' /* (2.99.251) */, 'outbox_sent_ok' => 'texts', 'text_prep' => 'texts', 'text_sent' => 'texts', 'rq_add' => 'sendrc', 'rq_list' => 'sendrc', 'rq_done' => 'sendrc', 'sms_preview' => 'texts', 'sms_samples' => 'texts', 'sms_tpl_save' => 'texts', 'sms_tpl_restore' => 'texts', 'sms_tpl_default' => 'texts', 'sms_preview_all' => 'texts', 'confirm_set' => 'texts', 'opt_out' => 'texts', 'turns' => 'turn', 'clock_in' => 'turn', 'clock_list' => 'turn', 'clock_for' => 'turn', 'clock_out' => 'turn', 'clock_edit' => 'turn', 'turn_order' => 'turn', 'turn_reset' => 'turn', 'day_report_test' => 'turn', 'clock_remove' => 'turn', 'turn_start' => 'turn', 'appt_services' => 'turn', 'turn_done' => 'turn', 'turn_undo' => 'turn', 'turn_adjust' => 'turn', 'history' => 'reports', 'yearend' => 'reports', 'ye_start' => 'reports', 'yearend_xlsx' => 'reports', 'yearend_pdf' => 'reports', 'yearend_csv' => 'reports', 'payroll_week' => 'reports', 'payroll_adj' => 'reports', 'payroll_adj_del' => 'reports', 'payroll_check_no' => 'reports', 'payroll_pay' => 'reports', 'pay_texted' => 'reports', 'payroll_close' => 'reports', 'payroll_reopen' => 'reports', 'payroll_csv' => 'reports', 'audit' => 'reports', 'reports' => 'reports', 'customer' => 'customers', 'customers' => 'customers', 'cust_find' => 'customers', 'cust_dups' => 'customers', 'cust_merge' => 'customers', 'cust_not_dup' => 'customers', 'customer_remove' => 'customers', 'customers_import' => 'customers', 'customer_save' => 'customers', 'customer_suspect' => 'customers', 'customer_wrong' => 'customers', 'customer_phone_fix' => 'customers' /* (2.99.251) */, 'test_mode' => 'customers', 'test_mode_admin' => 'customers', 'test_mode_start' => 'customers', 'test_mode_stop' => 'customers', 'test_clear' => 'customers', 'customer_note' => 'customers', 'set_birthday' => 'customers', 'export' => 'customers', 'threads' => 'notify', 'thread' => 'notify', 'own_reply_mark' => 'notify', 'own_reply_save' => 'notify' /* (2.99.351 – lệnh 584) */, 'own_reply_get' => 'notify' /* (2.99.352 – lệnh 590) */, 'send_message' => 'notify', 'sd_pick' => 'notify' /* (2.99.261) */, 'events' => 'notify', 'push_key' => 'notify', 'push_sub' => 'notify', 'push_unsub' => 'notify', 'fcm_key' => 'notify', 'push_off' => 'notify', 'push_keep_only' => 'notify', 'push_test' => 'notify', 'push_log' => 'notify', 'staff_names' => 'staffpages', 'staff_me' => 'staffpages', 'staff_login' => 'staffpages', 'staff_setup' => 'staffpages', 'invite_check' => 'staffpages', 'invite_pin' => 'staffpages', 'staff_logout' => 'staffpages', 'staff_day' => 'staffpages', 'staff_services' => 'staffpages', 'tech_add_service' => 'staffpages', 'tech_board' => 'staffpages', 'appt_times' => 'staffpages', 'svc_times' => 'staffpages', 'today_board' => 'staffpages', 'today_move' => 'staffpages', 'today_time' => 'staffpages', 'today_done' => 'staffpages', 'today_undo_done' => 'staffpages', 'flow_settings' => 'staffpages', 'settings' => 'settings', 'dep_refund' => 'settings', 'dep_test' => 'settings', 'logo_save' => 'settings', 'tv_file_save' => 'settings', 'tv_file_del' => 'settings' /* (2.99.256) */, 'logo_revert' => 'settings', 'gallery_add' => 'settings', 'gallery_save' => 'settings', 'gallery_delete' => 'settings', 'backup_key' => 'settings', 'backup_offsite_now' => 'settings', 'backup_now' => 'settings', 'mgr_newkey' => 'settings', 'checkin_newkey' => 'settings', 'badges' => 'settings', 'app_install' => 'settings', 'qa_desk_seed' => 'settings', 'qa_desk_clean' => 'settings', 'desk_newkey' => 'settings', 'closed_add' => 'settings', 'closed_texts' => 'settings', 'closed_remove' => 'settings', 'save_settings' => 'settings', 'save_staff_one' => 'staffadmin', 'staff_setup_code' => 'staffadmin', 'staff_photo' => 'staffadmin', 'staff_photo_pub' => 'staffadmin', 'staff_set_pin' => 'staffadmin', 'staff_invite' => 'staffadmin', 'staff_setup_link' => 'staffadmin', 'menu_2026b' => 'staffadmin', 'menu_2026' => 'staffadmin', 'save_svc_groups' => 'staffadmin', 'staff_hours_all' => 'staffadmin', 'staff_order' => 'staffadmin', 'remove_staff' => 'staffadmin', 'save_services' => 'staffadmin', 'test_sms' => 'staffadmin', 'totp_setup' => 'staffadmin', 'totp_enable' => 'staffadmin', 'totp_disable' => 'staffadmin', 'td_remove' => 'staffadmin' /* (2.99.257) */, 'admin_forgot' => 'staffadmin', 'admin_reset' => 'staffadmin', 'change_password' => 'staffadmin'];
$apiFile = API_ROUTES[$action] ?? '';
try {
if ($apiFile === '') fail('Unknown action', 404);
if (is_demo_site()) { require_once __DIR__ . '/inc/demo.php'; demo_refuse($action); } // (2.99.276) the demo salon: no deleting, no account changes
require __DIR__ . '/inc/api/' . $apiFile . '.php';
} catch (PDOException $e) {
    error_log('DB error: ' . $e->getMessage());
    fail('Database error. Please try again.', 500);
}
