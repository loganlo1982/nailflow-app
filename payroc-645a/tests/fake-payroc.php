<?php
/* Fake Payroc gateway for the local test kit only (no real Payroc). State in a JSON file. Behaviour by the amount's cents:
   ..01 declined (responseCode D) · ..99 cancelled on the device · ..77 stays inProgress · ..88 failure · ..55 first POST answers 500 (idempotency retry) · else approved (A). */
$S = __DIR__ . '/state.json'; $st = is_file($S) ? json_decode(file_get_contents($S), true) : []; $st += ['instr' => [], 'pay' => [], 'idem' => [], 'calls' => [], 'n' => 0];
$m = $_SERVER['REQUEST_METHOD']; $u = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH); $h = function_exists('getallheaders') ? array_change_key_case(getallheaders()) : [];
$in = json_decode(file_get_contents('php://input'), true) ?: [];
$st['calls'][] = $m . ' ' . $u; $save = function () use (&$st, $S) { file_put_contents($S, json_encode($st)); };
$out = function (int $c, $j = null) use ($save) { $save(); http_response_code($c); header('Content-Type: application/json'); if ($j !== null) echo json_encode($j); exit; };
$prob = fn($c, $t, $d = '') => $out($c, ['type' => 'https://docs.payroc.com/api/errors#x', 'title' => $t, 'status' => $c, 'detail' => $d]);
if ($u === '/authorize') { if (stripos($_SERVER['CONTENT_TYPE'] ?? '', 'application/json') === false) $prob(415, 'Unsupported Media Type'); if (($h['x-api-key'] ?? '') !== 'TESTKEY-1234567890abcd') $prob(401, 'Unauthorized'); $out(200, ['access_token' => 'tok' . (++$st['n']), 'expires_in' => 3600, 'token_type' => 'Bearer']); }
if (!preg_match('/^Bearer tok\d+$/', $h['authorization'] ?? '')) $prob(401, 'Unauthorized');
$base = 'http://127.0.0.1:18998/v1';
if ($m === 'POST' && preg_match('~^/v1/devices/([^/]+)/(payment|refund)-instructions$~', $u, $x)) {
    $k = $h['idempotency-key'] ?? ''; if (!preg_match('/^[0-9a-f-]{36}$/', $k)) $prob(400, 'Idempotency key missing');
    if (isset($st['idem'][$k])) { $id = $st['idem'][$k]; $out(202, ['paymentInstructionId' => $id, $x[2] . 'InstructionId' => $id, 'status' => $st['instr'][$id]['status']]); }
    $c = (int)($in['order']['amount'] ?? 0) % 100;
    if ($c === 55 && empty($st['fail55'][$k])) { $st['fail55'][$k] = 1; $id = 'I' . (++$st['n']); $st['idem'][$k] = $id; $st['instr'][$id] = ['kind' => $x[2], 'status' => 'completed', 'amt' => $in['order']['amount'], 'order' => $in['order']['orderId'], 'c' => 0]; $prob(500, 'Server error'); }
    $id = 'I' . (++$st['n']); $st['idem'][$k] = $id;
    $st['instr'][$id] = ['kind' => $x[2], 'status' => $c === 77 ? 'inProgress' : ($c === 99 ? 'canceled' : ($c === 88 ? 'failure' : 'completed')), 'amt' => $in['order']['amount'], 'order' => $in['order']['orderId'], 'c' => $c];
    $out(202, [$x[2] . 'InstructionId' => $id, 'status' => 'inProgress']);
}
if (preg_match('~^/v1/(payment|refund)-instructions/([^/]+)$~', $u, $x)) {
    $i = $st['instr'][$x[2]] ?? null; if (!$i) $prob(404, 'Resource not found');
    if ($m === 'DELETE') { if ($i['status'] !== 'inProgress') $prob(409, 'Cannot be canceled', 'Completed instruction cannot be canceled'); $st['instr'][$x[2]]['status'] = 'canceled'; $out(204); }
    if ($i['status'] === 'inProgress' && !empty($st['release'][$x[2]])) { $st['instr'][$x[2]]['status'] = 'completed'; $i['status'] = 'completed'; }
    if ($i['status'] === 'inProgress') { usleep(300000); $out(200, ['status' => 'inProgress', $x[1] . 'InstructionId' => $x[2]]); }
    $j = ['status' => $i['status'], $x[1] . 'InstructionId' => $x[2]];
    if ($i['status'] === 'failure') $j['errorMessage'] = 'Device offline';
    if ($i['status'] === 'completed') { $pid = 'P' . $x[2]; $st['pay'][$pid] = ['amt' => $i['amt'], 'order' => $i['order'], 'rc' => $i['c'] === 1 ? 'D' : 'A', 'st' => $i['c'] === 1 ? 'declined' : 'ready', 'kind' => $i['kind']];
        $j['link'] = ['rel' => $i['kind'] === 'payment' ? 'payment' : 'refund', 'method' => 'GET', 'href' => $base . '/' . ($i['kind'] === 'payment' ? 'payments' : 'refunds') . '/' . $pid]; }
    $out(200, $j);
}
$pay = function ($pid) use (&$st) { $p = $st['pay'][$pid]; return ['paymentId' => $pid, $p['kind'] === 'refund' ? 'refundId' : 'x' => $pid, 'order' => ['orderId' => $p['order'], 'amount' => $p['amt'], 'currency' => 'USD'], 'card' => ['type' => 'Visa', 'entryMethod' => 'contactless', 'cardNumber' => '476173******0011'],
    'transactionResult' => ['type' => $p['kind'] === 'refund' ? 'refund' : 'sale', 'status' => $p['st'], 'approvalCode' => $p['rc'] === 'A' ? 'OK' . substr($pid, -4) : '', 'authorizedAmount' => $p['rc'] === 'A' ? $p['amt'] : 0, 'currency' => 'USD', 'responseCode' => $p['rc'], 'responseMessage' => $p['rc'] === 'A' ? 'APPROVAL' : 'DECLINED']]; };
if ($m === 'GET' && preg_match('~^/v1/(payments|refunds)/([^/]+)$~', $u, $x)) { if (!isset($st['pay'][$x[2]])) $prob(404, 'Resource not found'); $out(200, $pay($x[2])); }
if ($m === 'POST' && preg_match('~^/v1/payments/([^/]+)/(reverse|refund)$~', $u) && ($raw = trim(file_get_contents('php://input'))) !== '' && $raw[0] !== '{') $prob(400, 'Bad request', 'One or more validation errors occurred, see error section for more info'); /* the real UAT answer to a body that is not a JSON object (seen 04/11 22:31) */
if ($m === 'POST' && preg_match('~^/v1/payments/([^/]+)/reverse$~', $u, $x)) { if (!isset($st['pay'][$x[1]])) $prob(404, 'Resource not found'); if (!empty($st['closed'][$x[1]])) $prob(400, 'Batch closed', 'Payment is not in an open batch'); $st['pay'][$x[1]]['st'] = 'reversal'; $out(200, $pay($x[1])); }
if ($m === 'POST' && preg_match('~^/v1/payments/([^/]+)/refund$~', $u, $x)) { if (!isset($st['pay'][$x[1]])) $prob(404, 'Resource not found'); if (!isset($in['amount'], $in['processingTerminalId'])) $prob(400, 'Bad request'); $rid = 'R' . (++$st['n']); $st['pay'][$rid] = ['amt' => $in['amount'], 'order' => 'ref', 'rc' => ((int)$in['amount'] % 100) === 1 ? 'D' : 'A', 'st' => 'ready', 'kind' => 'refund']; $j = $pay($rid); $j['refundId'] = $rid; $out(200, $j); }
$prob(404, 'Resource not found');
