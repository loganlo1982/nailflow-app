<?php
/* (2.99.645a - LENH PAYROC) Checkout (owner / manager / front desk iPad): the card part on Payroc Cloud – inc/payroc-pay.php. Off = these say so. */
declare(strict_types=1);
if (!defined('API_MAIN')) { http_response_code(404); exit; }
require_once APP_ROOT . '/inc/payroc-pay.php';
need_desk();
switch ($action) {
case 'pr_charge':
    if ($method !== 'POST') fail('POST only', 405);
    desk_out(['ok' => true] + pr_charge((array)($in['ids'] ?? []), (float)($in['amt'] ?? 0)));
case 'pr_stop':
    if ($method !== 'POST') fail('POST only', 405);
    desk_out(pr_stop((array)($in['ids'] ?? [])));
case 'pr_cancel':
    if ($method !== 'POST') fail('POST only', 405);
    desk_out(pr_cancel((string)($in['ref'] ?? '')));
case 'pr_waiting':
    desk_out(['on' => pr_pay_on(), 'waiting' => pr_waiting()]);
}
fail('Unknown action', 404);
