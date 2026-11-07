<?php
/* AN gateway account: remove the OLD phone (Galaxy A17, "a17") so new texts can only go to the Fold. Only a device whose name has "a17" AND is offline 10+ min. Prints no secret.
   SALON_ID=an php addev.php [go] */
declare(strict_types=1);
$site = (string)getenv('SALON_ID'); if ($site !== 'an') exit("an only\n");
require "/home/uyurpyzubx0m/app/sites/$site/current/inc/core.php"; settings(); require_once APP_ROOT . '/inc/autosend.php'; require_once APP_ROOT . '/inc/android.php';
$tok = ad_token(['devices:list', 'devices:delete']); if ($tok === '') exit('token failed: ' . ($GLOBALS['ad_err'] ?? '') . "\n");
[$code, $j] = ad_http('GET', '/devices', null, $tok); echo "devices ($code)\n";
foreach ((is_array($j) && array_is_list($j)) ? $j : [] as $d) {
    $name = (string)($d['name'] ?? ''); $ls = strtotime((string)($d['lastSeen'] ?? '')) ?: 0; $old = stripos($name, 'a17') !== false && $ls < time() - 600;
    echo '  ', $name, ' lastSeen=', $ls ? date('H:i:s', $ls) : '?', $old ? '  <- old A17' : '', "\n";
    if ($old && ($argv[1] ?? '') === 'go') { [$c2, , $e2] = ad_http('DELETE', '/devices/' . rawurlencode((string)$d['id']), null, $tok); echo "  removed: $c2 $e2\n"; }
}
