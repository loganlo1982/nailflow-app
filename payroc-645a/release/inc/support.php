<?php
/* (2.99.336 – lệnh 567, sửa lệnh 543 – anh Logan 20/10 22:44) NAILFLOW SUPPORT IN A SALON'S ADMIN – WITH THE OWNER'S OK, VISIBLE, TIMED:
   - AN HQ (Logan's own login: password + Authenticator) finds the salon (salon phone / last 4 / owner email) → "🔧 Xin vào hỗ trợ" → a 6-digit code is texted
     to the OWNER'S CELL ("NailFlow support code: …", 10 min, one use, 5 wrong → 15 min locked) → the owner reads it to Logan → in. American Nails (Logan owns it)
     and the demo salon: no code. Love Nails + every other salon: the code.
   - HQ leaves a one-time pass (2 minutes) in the salon's database; the salon's admin (#sup=…) turns it into an owner session marked "support".
   - The session ends by itself after 2 hours (or "Thoát hỗ trợ"); a bar on top of the admin: "🔧 NailFlow support đang hỗ trợ – thoát lúc 11:45 PM".
   - The salon's own Money & security log: "NailFlow support vào lúc … (mã gửi tới cell …1234)", every change "NailFlow support", "thoát lúc …".
   - Never in a support session: the owner's password / Authenticator / email, void / refund, re-opening a closed payroll, exporting the customer list,
     the backup key, the QA account. Never shows a card number (the app never has one). */
declare(strict_types=1);

require_once __DIR__ . '/audit.php';
const SUP_SECONDS = 7200;
const SUP_DENY = ['change_password', 'admin_setup', 'admin_setup_totp', 'totp_setup', 'totp_enable', 'totp_disable', 'td_remove', 'admin_forgot', 'admin_reset',
    'receipt_void', 'receipt_refund', 'payroll_reopen', 'export', 'backup_key', 'qa_set', 'app_install'];

/** The support session of this request (null = none). Over 2 hours → ended now (logged) and gone. */
function sup_session(): ?array {
    $s = $_SESSION['support'] ?? null; if (!is_array($s) || empty($_SESSION['admin'])) return null;
    if ((int)($s['until'] ?? 0) <= time()) { sup_end('tự thoát sau 2 giờ'); return null; }
    return $s;
}
function sup_end(string $why): void {
    $s = $_SESSION['support'] ?? null; if (!is_array($s)) return;
    $prev = $GLOBALS['actor'] ?? null; actor_set('admin', 'NailFlow support');
    try { audit('support', 'NailFlow support', 'in support since ' . date('g:i A', (int)($s['at'] ?? time())), 'thoát lúc ' . date('n/j g:i A') . ' (' . $why . ')'); } catch (Throwable $e) {}
    $GLOBALS['actor'] = $prev;
    $_SESSION = []; if (session_status() === PHP_SESSION_ACTIVE) { @session_regenerate_id(true); }
}
/** The one-time pass HQ left (2 minutes) → an owner session marked support. */
function sup_open(string $t): array {
    if (!preg_match('/^[a-f0-9]{48}$/', $t)) throw new RuntimeException('Bad support link.');
    $p = json_decode((string)setting('sup_pass'), true);
    if (!is_array($p) || !hash_equals((string)($p['h'] ?? ''), hash('sha256', $t)) || (int)($p['until'] ?? 0) < time()) throw new RuntimeException('This support link is used or too old – ask again in AN HQ.');
    set_setting('sup_pass', ''); // one time
    session_regenerate_id(true);
    unset($_SESSION['mgr_id'], $_SESSION['mgr_ver'], $_SESSION['mgr_seen'], $_SESSION['admin_pending'], $_SESSION['qa'], $_SESSION['qmode']);
    $_SESSION['admin'] = true; $_SESSION['admin_pw'] = (int)setting('admin_pw_ver'); $_SESSION['admin_seen'] = time(); $_SESSION['csrf'] = bin2hex(random_bytes(16));
    $_SESSION['support'] = ['at' => time(), 'until' => time() + SUP_SECONDS, 'cell' => (string)($p['cell'] ?? ''), 'how' => (string)($p['how'] ?? 'code')];
    actor_set('admin', 'NailFlow support');
    audit('support', 'NailFlow support', '', 'vào lúc ' . date('n/j g:i A') . ($p['how'] === 'nocode' ? ' (tiệm của NailFlow – không cần mã)' : ' (mã gửi tới cell ' . ($p['cell'] ?: '?') . ')') . ' – tự thoát lúc ' . date('g:i A', time() + SUP_SECONDS));
    return ['ok' => true, 'csrf' => $_SESSION['csrf'], 'until' => (int)$_SESSION['support']['until']];
}
/** For "me": the bar on top of the admin. */
function sup_me(): ?array { $s = sup_session(); return $s ? ['until' => (int)$s['until'], 'untilTxt' => date('g:i A', (int)$s['until'])] : null; }
/** (543 22:41 kept by 567) the texting device / Auto send page: only NailFlow (HQ or a support session); the owner does not see or change it. */
function as_hq_only(): bool { $v = (string)setting('as_hq_only'); if ($v === '') return (cfg()['driver'] ?? 'mysql') !== 'sqlite'; return $v !== '0'; } // every real salon (MySQL): on; a test copy (sqlite): only when set
function as_can_edit(): bool { return (!as_hq_only() && !nf_only()) || sup_session() !== null || !empty($_SESSION['qa']); } // (2.99.636) + a salon that is not the main one: NailFlow sets up the texting phone (SQLite too)
/* (2.99.636 - LENH 636, LUAT CHUNG AN / MO, anh Logan 02/11 22:07 + DUYET-636 22:35) A salon owner sees and changes how THE SALON works; what can break the
   texting / phone AI / online money / the law, or is NailFlow's own tooling, is set up by NailFlow: the owner only sees its status. Refused on the SERVER
   (not only a hidden button), on MySQL and SQLite alike. American Nails (the main salon), the old single copy, a NailFlow support session and qa-bot: as before. */
function nf_only(): bool { return function_exists('site_is_main') && site_is_main() === false && sup_session() === null && empty($_SESSION['qa']); }
const NF_ONLY_ACTS = [
    'autosend_save', 'autosend_device', 'android_test', 'android_check', 'test_sms',                 // 1 the texting Android (+ Twilio)
    'tx_cfg', 'tx_setup', 'calls_cfg', 'dv_info', 'dv_save', 'dv_check' /* (2.99.638b) the card terminal (group 3) */, 'pr_info', 'pr_save', 'pr_check', 'pr_test', 'pr_tests_csv' /* (2.99.645a) Payroc */,                                                                // 2 the phone AI (Telnyx); the call list stays open
    'dep_test',                                                                                       // 3 online money (PayPal keys: save_settings below)
    'stop_del_all', 'stop_del_keep',                                                                  // 4 the STOP list (law)
    'backup_key', 'backup_now', 'backup_offsite_now',                                                 // 5 backups
    'qa_set', 'qa_desk_seed', 'qa_desk_clean', 'test_mode_start', 'test_mode_stop', 'test_mode_admin', 'test_clear', 'test_link_new', 'guest_set', 'oldok_set', 'oldok_undo', 'fcm_key']; // 6 NailFlow's tools
const NF_ONLY_KEYS = ['as_device', 'ad_transport', 'ws_key', 'ws_server_url', 'as_iphone', 'as_hq_only', 'sms_enabled', 'sms_webhook', 'twilio_sid', 'twilio_token', 'twilio_from',
    'paypal_client_id', 'paypal_secret', 'paypal_mode', 'paypal_clear', 'sms_footer', 'stop_hook_on', 'backup_on', 'backup_email', 'backup_offsite_on', 'test_phones', 'qa_off'];
const NF_ONLY_KEY_RE = '/^(sw_|tx_|call_|twilio_|paypal_|ad_|ws_)/';
function nf_only_say(): string { return 'NailFlow quản lý phần này – liên hệ NailFlow' . (function_exists('hq_support_phone_here') ? ' ' . hq_support_phone_here() : '') . '. · Set up by NailFlow.'; }
/** need_admin() / need_desk(): this request's action, and save_settings' keys (one sent with the SAME value as saved = ignored, so Save keeps working). */
function nf_only_guard(): void {
    static $done = false; if ($done || !nf_only()) return; $done = true;
    $a = (string)($GLOBALS['action'] ?? '');
    if (in_array($a, ['calls_cfg', 'tx_cfg'], true) && ($_SERVER['REQUEST_METHOD'] ?? 'GET') !== 'POST') return; // reading the phone AI's state: allowed (the page shows it, locked)
    if (in_array($a, NF_ONLY_ACTS, true)) { try { audit('nf_only', $a, '', 'refused – set up by NailFlow'); } catch (Throwable $e) {} fail(nf_only_say(), 403); }
    if (in_array($a, ['sms_tpl_save', 'sms_tpl_restore'], true) && in_array((string)($GLOBALS['in']['key'] ?? ''), NF_ONLY_KEYS, true)) { // (2.99.637a QA-0005) the STOP line (sms_footer) through Settings -> SMS templates; "Restore default" (has STOP) stays open
        try { audit('nf_only', $a, (string)$GLOBALS['in']['key'], 'refused – set up by NailFlow'); } catch (Throwable $e) {} fail(nf_only_say(), 403); }
    if ($a !== 'save_settings' || !is_array($GLOBALS['in'] ?? null)) return;
    foreach (array_keys($GLOBALS['in']) as $k) {
        if (!in_array($k, NF_ONLY_KEYS, true) && !preg_match(NF_ONLY_KEY_RE, (string)$k)) continue;
        $v = $GLOBALS['in'][$k]; $sv = is_bool($v) ? ($v ? '1' : '0') : (is_scalar($v) ? trim((string)$v) : json_encode($v));
        $secret = in_array($k, ['paypal_secret', 'twilio_token', 'ws_key'], true) || preg_match('/(token|secret|key)$/', (string)$k);
        if ($sv === trim(setting((string)$k)) || ($secret && $sv === '') || (is_numeric($sv) && is_numeric(setting((string)$k)) && (float)$sv == (float)setting((string)$k))) { unset($GLOBALS['in'][$k]); continue; }
        try { audit('nf_only', (string)$k, '', 'refused – set up by NailFlow'); } catch (Throwable $e) {}
        fail(nf_only_say(), 403);
    }
}

/** The main salon: the support code texts waiting (HQ put them on the list) go now. */
function sup_kick(): int {
    require_once __DIR__ . '/autosend.php'; require_once __DIR__ . '/android.php';
    $ids = q("SELECT id FROM autosend WHERE src LIKE 'sup:%' AND state = 'wait' AND created_at >= ?", [date('Y-m-d H:i:s', time() - 180)])->fetchAll(PDO::FETCH_COLUMN);
    return $ids ? ad_send_rows(array_map(fn($i) => ['id' => (int)$i], $ids)) : 0;
}
