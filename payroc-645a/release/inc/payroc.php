<?php
/* (2.99.645a - LENH PAYROC, anh Logan 04/11 21:03) PAYROC CLOUD – sandbox (UAT) only. The calls only; Checkout uses them through inc/payroc-pay.php.
   OFF by default (setting pr_on = '0'). Separate from Dejavoo: own settings (pr_*), own journal, own pending list – Dejavoo is not touched.
   Field names / paths from the public docs (docs.payroc.com, read 04/11 – /home/claude/payroc/RESEARCH.md):
   - token: POST {identity}/authorize, header x-api-key -> access_token (Bearer, expires_in 3600)
   - sale:  POST {api}/devices/{serialNumber}/payment-instructions  {processingTerminalId, order{orderId<=24, amount (cents), currency}, autoCapture}
            header Idempotency-Key (UUID v4, required) -> 202 {paymentInstructionId, status inProgress|completed|failure|canceled, link}
   - wait:  GET {api}/payment-instructions/{id} (the gateway waits up to 1 minute) -> completed + link rel=payment -> GET {api}/payments/{paymentId}
   - stop:  DELETE {api}/payment-instructions/{id} (only while inProgress; 409 = too late)
   - void:  POST {api}/payments/{paymentId}/reverse (open batch)   - refund on the device: POST {api}/devices/{sn}/refund-instructions
   - errors: problem+json {type, title, status, detail}
   UNCONFIRMED in the docs (so NOT used / NOT guessed): the referenced refund body (POST /payments/{id}/refund), tip adjust, the full list of
   transactionResult codes. "Approved" = instruction completed AND the payment's transactionResult.responseCode = "A" (the documented example).
   The two documented hosts conflict (api.uat.payroc.com vs api.payroc.com with a test key) – both are a setting (pr_host), nothing else.
   SAFETY: the API key is kept ENCRYPTED (ad_enc); the key and the token never go to a log, the audit, the screen or an error text.
   Live is refused in this build (only the UAT key / sandbox). */
declare(strict_types=1);
if (!function_exists('ad_enc')) require_once __DIR__ . '/android.php';

const PR_HOSTS = ['uat' => ['api' => 'https://api.uat.payroc.com/v1', 'id' => 'https://identity.uat.payroc.com/authorize'],
                  'std' => ['api' => 'https://api.payroc.com/v1', 'id' => 'https://identity.payroc.com/authorize']];
const PR_WAIT = 120; /* seconds the desk waits for the customer on the device (each status call itself waits up to 60 s) */

function pr_on(): bool { return setting('pr_on') === '1'; }
function pr_host(): string { return setting('pr_host') === 'std' ? 'std' : 'uat'; }
function pr_api(): string { $b = trim((string)(cfg()['pr_base'] ?? '')); return $b !== '' ? rtrim($b, '/') : PR_HOSTS[pr_host()]['api']; }
function pr_idurl(): string { $b = trim((string)(cfg()['pr_idurl'] ?? '')); return $b !== '' ? $b : PR_HOSTS[pr_host()]['id']; }
/** Terminal ID + device serial number (not secret) + the API key (encrypted). */
function pr_creds(): array { return ['tid' => trim((string)setting('pr_tid')), 'sn' => trim((string)setting('pr_sn')), 'key' => ad_dec((string)setting('pr_key'))]; }
function pr_ready(): bool { $c = pr_creds(); return $c['tid'] !== '' && $c['key'] !== ''; }
function pr_dev_ready(): bool { return pr_ready() && pr_creds()['sn'] !== ''; }
/** HQ: save. '' = keep the one saved; null = remove. Everything checked BEFORE anything is saved. */
function pr_set_creds(?string $tid, ?string $sn, ?string $key, ?string $host = null): array {
    $tid = $tid === null ? null : trim($tid); $sn = $sn === null ? null : trim($sn); $key = $key === null ? null : trim($key);
    if ($tid !== null && $tid !== '' && !preg_match('/^[A-Za-z0-9]{4,50}$/', $tid)) throw new InvalidArgumentException('Terminal ID: 4–50 letters / digits.');
    if ($sn !== null && $sn !== '' && !preg_match('/^[A-Za-z0-9_.\-]{1,64}$/', $sn)) throw new InvalidArgumentException('Device serial number: letters / digits only.');
    if ($key !== null && $key !== '' && (strlen($key) < 16 || strlen($key) > 512 || preg_match('/\s/', $key))) throw new InvalidArgumentException('API key: check it (no spaces).');
    if ($host !== null && $host !== '' && !isset(PR_HOSTS[$host])) throw new InvalidArgumentException('Host: uat or std.');
    if ($tid === null) set_setting('pr_tid', ''); elseif ($tid !== '') set_setting('pr_tid', $tid);
    if ($sn === null) set_setting('pr_sn', ''); elseif ($sn !== '') set_setting('pr_sn', $sn);
    if ($key === null) set_setting('pr_key', ''); elseif ($key !== '') { set_setting('pr_key', ad_enc($key)); set_setting('pr_tok', ''); }
    if ($host !== null && $host !== '') { set_setting('pr_host', $host); set_setting('pr_tok', ''); }
    return pr_shown();
}
function pr_shown(): array { $c = pr_creds(); return ['tid' => $c['tid'], 'sn' => $c['sn'], 'key' => $c['key'] === '' ? '' : '…' . substr($c['key'], -4), 'host' => pr_host(), 'api' => pr_api(), 'on' => pr_on()]; }
/** UUID v4 – one per request; the SAME key is sent again when the answer was lost (the gateway then gives back the first one). */
function pr_uuid(): string { $b = random_bytes(16); $b[6] = chr((ord($b[6]) & 0x0f) | 0x40); $b[8] = chr((ord($b[8]) & 0x3f) | 0x80); return vsprintf('%s%s-%s-%s-%s-%s%s%s', str_split(bin2hex($b), 4)); }
/** orderId: 1–24 characters, ours. */
function pr_new_order(): string { return 'NF' . date('ymdHis') . strtoupper(bin2hex(random_bytes(3))); }
function pr_cents(float $a): int { return (int)round(max(0.0, $a) * 100); }

/* ---------- HTTP ---------- */
/** Raw call. Never throws; never puts the key / token in the result. */
function pr_raw(string $method, string $url, array $headers, ?string $data, int $timeout): array {
    $ch = curl_init($url);
    curl_setopt_array($ch, [CURLOPT_RETURNTRANSFER => true, CURLOPT_CONNECTTIMEOUT => 10, CURLOPT_TIMEOUT => $timeout, CURLOPT_CUSTOMREQUEST => $method, CURLOPT_HTTPHEADER => $headers] + ($data !== null ? [CURLOPT_POSTFIELDS => $data] : []));
    $raw = curl_exec($ch); $code = (int)curl_getinfo($ch, CURLINFO_RESPONSE_CODE); $errno = curl_errno($ch); curl_close($ch);
    if ($raw === false || $errno) return ['net' => true, 'http' => $code, 'j' => null, 'err' => $errno === CURLE_OPERATION_TIMEDOUT ? 'timeout' : 'no answer'];
    $j = $raw === '' ? [] : json_decode((string)$raw, true);
    return ['net' => false, 'http' => $code, 'j' => is_array($j) ? $j : null, 'err' => ''];
}
/** Bearer token (kept encrypted until 2 minutes before it ends). '' = could not get one (why in $why). */
function pr_token(bool $fresh = false, string &$why = ''): string {
    if (!$fresh) { $t = json_decode(ad_dec((string)setting('pr_tok')), true); if (is_array($t) && ($t['exp'] ?? 0) > time() + 120 && ($t['tok'] ?? '') !== '') return (string)$t['tok']; }
    $c = pr_creds(); if ($c['key'] === '') { $why = 'not set up'; return ''; }
    $h = pr_raw('POST', pr_idurl(), ['x-api-key: ' . $c['key'], 'Accept: application/json', 'Content-Type: application/json'], '', 20);
    $tok = (string)($h['j']['access_token'] ?? '');
    if ($h['net'] || $h['http'] !== 200 || $tok === '') { $why = $h['net'] ? $h['err'] : 'identity HTTP ' . $h['http'] . (($h['j']['title'] ?? '') !== '' ? ' ' . mb_substr((string)$h['j']['title'], 0, 80) : ''); set_setting('pr_tok', ''); return ''; }
    set_setting('pr_tok', ad_enc(json_encode(['tok' => $tok, 'exp' => time() + max(60, (int)($h['j']['expires_in'] ?? 3600))])));
    return $tok;
}
/** API call with the token (a 401 gets a new token once; a POST keeps its Idempotency-Key, so it is safe to send again). */
function pr_http(string $method, string $path, ?array $body, string $idem = '', int $timeout = 30): array {
    $why = ''; $tok = pr_token(false, $why); if ($tok === '') return ['net' => false, 'http' => 401, 'j' => null, 'err' => 'auth: ' . $why];
    for ($n = 0; $n < 2; $n++) {
        $hd = ['Authorization: Bearer ' . $tok, 'Accept: application/json'];
        if ($body !== null) $hd[] = 'Content-Type: application/json';
        if ($idem !== '') $hd[] = 'Idempotency-Key: ' . $idem;
        $h = pr_raw($method, pr_api() . $path, $hd, $body !== null ? json_encode($body) : ($method === 'POST' ? '' : null), $timeout);
        if ($h['http'] !== 401 || $n === 1) return $h;
        $tok = pr_token(true, $why); if ($tok === '') return ['net' => false, 'http' => 401, 'j' => null, 'err' => 'auth: ' . $why];
    }
    return ['net' => true, 'http' => 0, 'j' => null, 'err' => 'no answer'];
}
function pr_problem(array $h): string { $j = (array)($h['j'] ?? []); return trim(mb_substr(trim((string)($j['title'] ?? '') . ' ' . (string)($j['detail'] ?? '')), 0, 160)) ?: ($h['err'] ?: 'HTTP ' . $h['http']); }

/* ---------- journal (no key, no token, no card number) ---------- */
function pr_log(string $op, array $r, array $x = []): void {
    $l = json_decode((string)setting('pr_log'), true); $l = is_array($l) ? $l : [];
    $l[] = array_filter(['at' => now_str(), 'op' => $op, 'host' => pr_host(), 'order' => $x['order'] ?? '', 'instr' => $r['instr'] ?? ($x['instr'] ?? ''), 'pay' => $r['payment_id'] ?? ($x['pay'] ?? ''),
        'status' => $r['status'] ?? '', 'code' => $r['code'] ?? '', 'msg' => mb_substr((string)($r['msg'] ?? ''), 0, 120), 'amount' => $x['amount'] ?? null,
        'last4' => $r['last4'] ?? '', 'card' => $r['card'] ?? '', 'approval' => $r['approval'] ?? '', 'http' => $r['http'] ?? null, 'by' => $x['by'] ?? '', 'test' => $x['test'] ?? ''], fn($v) => $v !== '' && $v !== null);
    set_setting('pr_log', json_encode(array_slice($l, -300), JSON_UNESCAPED_UNICODE));
}

/* ---------- the payment / its result ---------- */
/** A payment object -> plain result. approved only with responseCode "A". */
function pr_pay_norm(array $p): array {
    $tr = (array)($p['transactionResult'] ?? []); $card = (array)($p['card'] ?? []);
    $num = (string)($card['cardNumber'] ?? ''); $l4 = preg_match('/(\d{4})\D*$/', $num, $m) ? $m[1] : '';
    $rc = (string)($tr['responseCode'] ?? ''); $st = (string)($tr['status'] ?? '');
    return ['payment_id' => (string)($p['paymentId'] ?? ''), 'code' => $rc, 'tr_status' => $st, 'msg' => mb_substr((string)($tr['responseMessage'] ?? ''), 0, 120),
        'approval' => (string)($tr['approvalCode'] ?? ''), 'authorized' => isset($tr['authorizedAmount']) ? round(((int)$tr['authorizedAmount']) / 100, 2) : null,
        'amount' => isset($p['order']['amount']) ? round(((int)$p['order']['amount']) / 100, 2) : null, 'order' => (string)($p['order']['orderId'] ?? ''),
        'last4' => $l4, 'card' => (string)($card['type'] ?? ''), 'entry' => (string)($card['entryMethod'] ?? ''),
        'approved' => $rc === 'A', 'reversed' => strcasecmp($st, 'reversal') === 0];
}
function pr_payment(string $paymentId): array {
    $h = pr_http('GET', '/payments/' . rawurlencode($paymentId), null, '', 30);
    if ($h['net'] || $h['http'] !== 200 || !is_array($h['j'])) return ['ok' => false, 'http' => $h['http'], 'msg' => pr_problem($h), 'net' => $h['net']];
    return ['ok' => true, 'http' => 200] + pr_pay_norm($h['j']);
}
function pr_link_id(array $j, string $rel): string { $l = $j['link'] ?? null; $ls = isset($l['rel']) ? [$l] : (is_array($l) ? $l : []); if (isset($j['links']) && is_array($j['links'])) $ls = array_merge($ls, $j['links']);
    foreach ($ls as $x) if (is_array($x) && ($x['rel'] ?? '') === $rel && preg_match('~/([A-Za-z0-9_\-]+)/?$~', (string)($x['href'] ?? ''), $m)) return $m[1]; return ''; }
/** Wait for an instruction (payment- or refund-) until it is not inProgress or $wait seconds passed. kind: payment | refund */
function pr_instr_wait(string $kind, string $id, int $wait): array {
    $end = time() + max(1, $wait); $last = ['status' => 'inProgress'];
    do {
        $h = pr_http('GET', '/' . $kind . '-instructions/' . rawurlencode($id), null, '', min(75, max(5, $end - time() + 5)));
        if ($h['net'] || $h['http'] !== 200 || !is_array($h['j'])) { $last = ['status' => 'unknown', 'http' => $h['http'], 'msg' => pr_problem($h), 'net' => $h['net']]; if ($h['http'] === 404) { $last['status'] = 'not_found'; break; } if (!$h['net'] && $h['http'] >= 400 && $h['http'] < 500) break; continue; }
        $st = (string)($h['j']['status'] ?? ''); $last = ['status' => $st, 'msg' => mb_substr((string)($h['j']['errorMessage'] ?? ''), 0, 120), 'link_id' => pr_link_id($h['j'], $kind)];
        if ($st !== 'inProgress') break;
    } while (time() < $end);
    return $last;
}
/** The result of an instruction -> one plain answer.
    status: approved | declined | cancelled | failure | waiting | unknown | not_found | auth | error ; paid = true ONLY when approved. */
function pr_instr_result(string $kind, string $id, int $wait): array {
    $w = pr_instr_wait($kind, $id, $wait); $o = ['instr' => $id, 'status' => 'unknown', 'msg' => (string)($w['msg'] ?? ''), 'paid' => false];
    if ($w['status'] === 'inProgress') return ['status' => 'waiting'] + $o;
    if ($w['status'] === 'canceled') return ['status' => 'cancelled'] + $o;
    if ($w['status'] === 'failure') return ['status' => 'failure'] + $o;
    if ($w['status'] === 'not_found') return ['status' => 'not_found'] + $o;
    if ($w['status'] !== 'completed') return ['status' => (($w['http'] ?? 0) === 401 ? 'auth' : 'unknown'), 'http' => $w['http'] ?? null] + $o;
    if (($w['link_id'] ?? '') === '') return ['status' => 'unknown', 'msg' => 'completed without a ' . $kind . ' link'] + $o;
    $p = $kind === 'payment' ? pr_payment($w['link_id']) : pr_refund_get($w['link_id']);
    if (empty($p['ok'])) return ['status' => 'unknown', 'payment_id' => $w['link_id'], 'msg' => (string)($p['msg'] ?? '')] + $o;
    return array_merge($o, $p, ['status' => $p['approved'] ? 'approved' : 'declined', 'paid' => $p['approved']]);
}
function pr_refund_get(string $refundId): array {
    $h = pr_http('GET', '/refunds/' . rawurlencode($refundId), null, '', 30);
    if ($h['net'] || $h['http'] !== 200 || !is_array($h['j'])) return ['ok' => false, 'http' => $h['http'], 'msg' => pr_problem($h)];
    $n = pr_pay_norm($h['j']); $n['payment_id'] = (string)($h['j']['refundId'] ?? $refundId); return ['ok' => true] + $n;
}

/* ---------- the calls ---------- */
/** Send a sale to the device. $idem: the SAME key again after a lost answer. Returns instr + status (does not wait). */
function pr_sale_send(float $amount, string $order, string $idem, string $operator = ''): array {
    $c = pr_creds();
    if (!pr_dev_ready()) { $r = ['status' => 'auth', 'msg' => 'Payroc is not set up (NailFlow sets it up).', 'instr' => '']; pr_log('sale', $r, ['order' => $order, 'amount' => round($amount, 2)]); return $r; }
    $body = ['processingTerminalId' => $c['tid'], 'order' => ['orderId' => substr($order, 0, 24), 'amount' => pr_cents($amount), 'currency' => 'USD'], 'autoCapture' => true, 'customizationOptions' => ['entryMethod' => 'deviceRead']]
        + ($operator !== '' ? ['operator' => mb_substr($operator, 0, 50)] : []);
    $h = pr_http('POST', '/devices/' . rawurlencode($c['sn']) . '/payment-instructions', $body, $idem, 30);
    if ($h['net'] || $h['http'] >= 500) { $h2 = pr_http('POST', '/devices/' . rawurlencode($c['sn']) . '/payment-instructions', $body, $idem, 30); if (!$h2['net']) $h = $h2; } /* the docs: a 500 / no answer -> the same request with the same key */
    $id = (string)($h['j']['paymentInstructionId'] ?? '');
    $r = $id !== '' && in_array($h['http'], [200, 201, 202], true) ? ['status' => 'sent', 'instr' => $id, 'msg' => ''] : ['status' => $h['net'] ? 'unknown' : ($h['http'] === 401 ? 'auth' : 'error'), 'instr' => $id, 'http' => $h['http'], 'msg' => pr_problem($h), 'net' => $h['net']];
    pr_log('sale', $r, ['order' => $order, 'amount' => round($amount, 2)]); return $r;
}
/** Stop a sale still waiting on the device. ok = stopped; too_late = it finished (look at its result). */
function pr_instr_cancel(string $kind, string $id): array {
    $h = pr_http('DELETE', '/' . $kind . '-instructions/' . rawurlencode($id), null, '', 30);
    $r = ['ok' => $h['http'] === 204 || $h['http'] === 200, 'too_late' => $h['http'] === 409, 'http' => $h['http'], 'msg' => pr_problem($h), 'status' => $h['http'] === 204 || $h['http'] === 200 ? 'cancelled' : ($h['http'] === 409 ? 'too_late' : 'error')];
    pr_log('cancel', $r, ['instr' => $id]); return $r;
}
/** Void (reverse) a payment of the open batch. $amount null = all of it. ok only when the answer is the payment with status "reversal". */
function pr_reverse(string $paymentId, ?float $amount, string $idem): array {
    $h = pr_http('POST', '/payments/' . rawurlencode($paymentId) . '/reverse', $amount !== null ? ['amount' => pr_cents($amount)] : [], $idem, 30);
    if ($h['net'] || $h['http'] >= 500) { $h2 = pr_http('POST', '/payments/' . rawurlencode($paymentId) . '/reverse', $amount !== null ? ['amount' => pr_cents($amount)] : [], $idem, 30); if (!$h2['net']) $h = $h2; }
    $n = is_array($h['j']) && $h['http'] === 200 ? pr_pay_norm($h['j']) : [];
    $r = ['ok' => !empty($n['reversed']), 'http' => $h['http'], 'msg' => $n ? ($n['msg'] ?: ($n['tr_status'] ?? '')) : pr_problem($h), 'status' => !empty($n['reversed']) ? 'reversed' : ($h['net'] ? 'unknown' : 'error'), 'payment_id' => $paymentId, 'code' => $n['code'] ?? ''];
    pr_log('void', $r, ['pay' => $paymentId, 'amount' => $amount]); return $r;
}
/** Money back on the device (the customer presents the card again). Returns instr + status (does not wait). */
function pr_refund_send(float $amount, string $order, string $idem, string $why = 'Refund'): array {
    $c = pr_creds();
    if (!pr_dev_ready()) { $r = ['status' => 'auth', 'msg' => 'Payroc is not set up (NailFlow sets it up).', 'instr' => '']; pr_log('refund', $r, ['order' => $order, 'amount' => round($amount, 2)]); return $r; }
    $body = ['processingTerminalId' => $c['tid'], 'order' => ['orderId' => substr($order, 0, 24), 'amount' => pr_cents($amount), 'currency' => 'USD', 'description' => mb_substr($why, 0, 200)], 'customizationOptions' => ['entryMethod' => 'deviceRead']];
    $h = pr_http('POST', '/devices/' . rawurlencode($c['sn']) . '/refund-instructions', $body, $idem, 30);
    if ($h['net'] || $h['http'] >= 500) { $h2 = pr_http('POST', '/devices/' . rawurlencode($c['sn']) . '/refund-instructions', $body, $idem, 30); if (!$h2['net']) $h = $h2; }
    $id = (string)($h['j']['refundInstructionId'] ?? '');
    $r = $id !== '' && in_array($h['http'], [200, 201, 202], true) ? ['status' => 'sent', 'instr' => $id, 'msg' => ''] : ['status' => $h['net'] ? 'unknown' : 'error', 'instr' => $id, 'http' => $h['http'], 'msg' => pr_problem($h)];
    pr_log('refund', $r, ['order' => $order, 'amount' => round($amount, 2)]); return $r;
}
/** Refund a payment by its paymentId – no card needed. Request from Payroc's own "Card Present Certification" Postman collection (read 04/11 21:55):
    POST {api}/payments/{paymentId}/refund {processingTerminalId, operator, amount (cents), description} + Idempotency-Key.
    ok ONLY when the answer carries transactionResult.responseCode "A"; anything else is shown as it came (never guessed as refunded). */
function pr_refund_ref(string $paymentId, float $amount, string $idem, string $why = 'Refund'): array {
    $c = pr_creds(); $body = ['processingTerminalId' => $c['tid'], 'operator' => 'NailFlow', 'amount' => pr_cents($amount), 'description' => mb_substr($why, 0, 200)];
    $h = pr_http('POST', '/payments/' . rawurlencode($paymentId) . '/refund', $body, $idem, 30);
    if ($h['net'] || $h['http'] >= 500) { $h2 = pr_http('POST', '/payments/' . rawurlencode($paymentId) . '/refund', $body, $idem, 30); if (!$h2['net']) $h = $h2; }
    $n = is_array($h['j']) && in_array($h['http'], [200, 201], true) ? pr_pay_norm($h['j']) : [];
    $ok = ($n['code'] ?? '') === 'A';
    $r = ['ok' => $ok, 'http' => $h['http'], 'status' => $ok ? 'refunded' : ($h['net'] ? 'unknown' : ($n ? 'not approved' : 'error')), 'code' => $n['code'] ?? '', 'approval' => $n['approval'] ?? '',
        'refund_id' => (string)($h['j']['refundId'] ?? ($n['payment_id'] ?? '')), 'msg' => $n ? ($n['msg'] ?: (string)($n['tr_status'] ?? '')) : pr_problem($h)];
    pr_log('refund_ref', $r, ['pay' => $paymentId, 'amount' => round($amount, 2)]); return $r;
}
/** "Check the connection": only a token (nothing is charged). */
function pr_check(): array { $why = ''; $t = pr_token(true, $why); $r = ['ok' => $t !== '', 'status' => $t !== '' ? 'token ok' : 'no token', 'msg' => $t !== '' ? '' : $why]; pr_log('check', $r); return $r; }
