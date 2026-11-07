<?php
/* read-only: AN texting path - transport, SMS Server last ping, whether the gateway login is stored (yes/no only), the gateway's phones (name / last seen). No secret printed.
   SALON_ID=an php adinfo.php */
declare(strict_types=1);
$site = (string)getenv('SALON_ID'); if (!preg_match('/^[a-z0-9]+$/', $site)) exit("SALON_ID?\n");
require "/home/uyurpyzubx0m/app/sites/$site/current/inc/core.php"; settings(); require_once APP_ROOT . '/inc/autosend.php'; require_once APP_ROOT . '/inc/android.php';
echo 'as_device=', setting('as_device'), ' ad_transport=', setting('ad_transport'), ' login stored=', (ad_dec((string)setting('ad_user')) !== '' && ad_dec((string)setting('ad_pass')) !== '') ? 'yes' : 'no', "\n";
$p = json_decode((string)setting('ws_last_ping'), true); if (is_array($p)) { foreach (['token', 'key', 'secret', 'password'] as $k) unset($p[$k]); echo 'ws_last_ping=', mb_substr(json_encode($p), 0, 300), "\n"; }
if (ad_user() === '' || ad_pass() === '') exit("no gateway login\n");
$tok = ad_token(['devices:list']); if ($tok === '') exit('token failed: ' . ($GLOBALS['ad_err'] ?? '') . "\n");
[$code, $j] = ad_http('GET', '/devices', null, $tok); echo "devices ($code):\n";
foreach ((is_array($j) && array_is_list($j)) ? $j : [] as $d) echo '  ', substr((string)($d['id'] ?? ''), 0, 6), '… ', mb_substr((string)($d['name'] ?? ''), 0, 30), ' lastSeen=', (string)($d['lastSeen'] ?? ''), "\n";
