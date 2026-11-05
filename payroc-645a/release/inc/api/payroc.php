<?php
/* (2.99.645a - LENH PAYROC) Settings -> Payments -> "Payroc (NailFlow)": the Payroc Cloud codes of this salon (Terminal ID, device serial number,
   API key), "Card on Payroc" on/off, "Check the connection" (a token only), and the SANDBOX TEST RUNNER for Payroc's certification
   (sale / decline / cancel on the device / void / refund on the device) – test orders only (NFT…), never a ticket, never a receipt.
   NailFlow only (like the Dejavoo box: nf_only refused). The API key is never sent back (only "…abcd"). */
declare(strict_types=1);
if (!defined('API_MAIN')) { http_response_code(404); exit; }
require_once APP_ROOT . '/inc/payroc.php';
need_admin();
if (function_exists('nf_only') && nf_only()) fail(nf_only_say(), 403);
$prLog = function (): array { $l = json_decode((string)setting('pr_log'), true); return array_slice(array_reverse(is_array($l) ? $l : []), 0, 15); };
$prTests = function (): array { $l = json_decode((string)setting('pr_tests'), true); return is_array($l) ? $l : []; };
$prTestPut = function (string $id, array $row) use ($prTests): void { $l = $prTests(); $l[$id] = $row + ($l[$id] ?? []); if (count($l) > 60) $l = array_slice($l, -60, null, true); set_setting('pr_tests', json_encode($l, JSON_UNESCAPED_UNICODE)); };
$out = fn(array $x = []) => json_out(['ok' => true, 'pr' => pr_shown() + ['ready' => pr_ready(), 'dev' => pr_dev_ready()], 'log' => $prLog(), 'tests' => array_values(array_reverse($prTests()))] + $x);
switch ($action) {
case 'pr_info': $out();
case 'pr_save':
    if ($method !== 'POST') fail('POST only', 405);
    $was = pr_shown();
    try { if (!empty($in['clear'])) pr_set_creds(null, null, null); else pr_set_creds((string)($in['tid'] ?? ''), (string)($in['sn'] ?? ''), (string)($in['key'] ?? ''), (string)($in['host'] ?? '')); }
    catch (InvalidArgumentException $e) { fail($e->getMessage()); }
    if (array_key_exists('on', $in)) { if (!empty($in['on']) && !pr_dev_ready()) fail('Type the Terminal ID, the device serial number and the API key first.'); set_setting('pr_on', !empty($in['on']) ? '1' : '0'); }
    $now = pr_shown(); $ch = []; foreach (['tid' => 'Terminal ID', 'sn' => 'device', 'key' => 'API key', 'host' => 'host', 'on' => 'on'] as $k => $lab) if ($was[$k] !== $now[$k]) $ch[] = $lab;
    if ($ch) audit('setting', 'Payroc', 'changed', implode(', ', $ch), 'Settings → Payments → Payroc'); /* never the key */
    $out();
case 'pr_check':
    if ($method !== 'POST') fail('POST only', 405);
    $r = pr_check(); $out(['check' => $r]);
case 'pr_test': /* the sandbox test runner – test orders only */
    if ($method !== 'POST') fail('POST only', 405);
    if (pr_host() !== 'uat' && pr_host() !== 'std') fail('Sandbox only.');
    app_lock('payroc'); if (session_status() === PHP_SESSION_ACTIVE) @session_write_close(); ignore_user_abort(true);
    $op = (string)($in['op'] ?? ''); $wait = max(1, min(PR_WAIT, (int)(cfg()['pr_wait'] ?? PR_WAIT))); @set_time_limit($wait + 120);
    $tc = mb_substr(trim((string)($in['tc'] ?? '')), 0, 40);
    if ($op === 'sale' || $op === 'refund') {
        $amt = round((float)($in['amt'] ?? 0), 2); if ($amt < 0.01 || $amt > 999) fail('Test amount: $0.01 – $999.');
        $ord = 'NFT' . date('ymdHis') . strtoupper(bin2hex(random_bytes(2))); $idem = pr_uuid();
        $prTestPut($ord, ['id' => $ord, 'tc' => $tc, 'op' => $op, 'amt' => $amt, 'at' => now_str(), 'idem' => $idem, 'st' => 'sending']);
        $x = $op === 'sale' ? pr_sale_send($amt, $ord, $idem, 'NailFlow test') : pr_refund_send($amt, $ord, $idem, 'NailFlow test refund');
        if ($x['status'] !== 'sent') { $prTestPut($ord, ['st' => $x['status'], 'msg' => $x['msg'], 'http' => $x['http'] ?? null]); $out(['test' => $prTests()[$ord]]); }
        $prTestPut($ord, ['instr' => $x['instr'], 'st' => 'inProgress']);
        $s = pr_instr_result($op === 'sale' ? 'payment' : 'refund', $x['instr'], $wait);
    } elseif ($op === 'poll' || $op === 'stop') {
        $ord = (string)($in['id'] ?? ''); $t = $prTests()[$ord] ?? null; if (!$t || ($t['instr'] ?? '') === '') fail('Unknown test.', 404);
        if ($op === 'stop') { $c = pr_instr_cancel($t['op'] === 'sale' ? 'payment' : 'refund', (string)$t['instr']); if ($c['ok']) { $prTestPut($ord, ['st' => 'cancelled', 'msg' => 'stopped from NailFlow (DELETE ' . $c['http'] . ')']); $out(['test' => $prTests()[$ord]]); } }
        $s = pr_instr_result($t['op'] === 'sale' ? 'payment' : 'refund', (string)$t['instr'], $op === 'stop' ? 5 : $wait);
    } elseif ($op === 'void') {
        $ord = (string)($in['id'] ?? ''); $t = $prTests()[$ord] ?? null; if (!$t || ($t['pay'] ?? '') === '' || ($t['op'] ?? '') !== 'sale') fail('Pick an approved test sale.', 404);
        $vi = (string)($t['videm'] ?? ''); if ($vi === '') { $vi = pr_uuid(); $prTestPut($ord, ['videm' => $vi]); }
        $v = pr_reverse((string)$t['pay'], null, $vi); $prTestPut($ord, ['void' => $v['ok'] ? 'reversed' : 'failed: ' . $v['msg'], 'void_at' => now_str()]); $out(['test' => $prTests()[$ord]]);
    } else fail('Unknown test.', 404);
    $prTestPut($ord, ['st' => $s['status'], 'msg' => (string)($s['msg'] ?? ''), 'pay' => (string)($s['payment_id'] ?? ''), 'code' => (string)($s['code'] ?? ''), 'approval' => (string)($s['approval'] ?? ''), 'last4' => (string)($s['last4'] ?? ''), 'card' => (string)($s['card'] ?? ''), 'done_at' => now_str()]);
    $out(['test' => $prTests()[$ord]]);
case 'pr_tests_csv': /* for the certification email: no key, no card number */
    $rows = [['order', 'test case', 'type', 'amount', 'time', 'instruction', 'result', 'responseCode', 'approval', 'paymentId', 'card', 'last4', 'void', 'message']];
    foreach ($prTests() as $t) $rows[] = [$t['id'] ?? '', $t['tc'] ?? '', $t['op'] ?? '', $t['amt'] ?? '', $t['at'] ?? '', $t['instr'] ?? '', $t['st'] ?? '', $t['code'] ?? '', $t['approval'] ?? '', $t['pay'] ?? '', $t['card'] ?? '', $t['last4'] ?? '', $t['void'] ?? '', $t['msg'] ?? ''];
    $csv = ''; foreach ($rows as $r) $csv .= implode(',', array_map(fn($v) => '"' . str_replace('"', '""', (string)$v) . '"', $r)) . "\r\n";
    json_out(['ok' => true, 'csv' => $csv]);
}
fail('Unknown action', 404);
