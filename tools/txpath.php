<?php
/* AN texting path switch (reversible): direct = the app talks to the SMS Gateway cloud itself (no SMS Server; any online phone of the account = the Fold);
   back = the SMS Server (winsms) again. After "direct": the normal Settings "Check connection" (phones + this salon's webhooks). Prints no secret.
   SALON_ID=an php txpath.php direct|back */
declare(strict_types=1);
$site = (string)getenv('SALON_ID'); if ($site !== 'an') exit("an only\n");
require "/home/uyurpyzubx0m/app/sites/$site/current/inc/core.php"; settings(); require_once APP_ROOT . '/inc/autosend.php'; require_once APP_ROOT . '/inc/android.php';
$a = $argv[1] ?? ''; echo 'before: ad_transport=', setting('ad_transport'), "\n";
if ($a === 'back') { set_setting('ad_transport', 'winsms'); exit("now: winsms\n"); }
if ($a !== 'direct') exit("direct|back\n");
if (ad_dec((string)setting('ad_user')) === '' || ad_dec((string)setting('ad_pass')) === '') exit("no direct login stored - stop\n");
set_setting('ad_transport', ''); echo "now: direct\n";
$r = ad_check(); unset($r['token']); echo mb_substr(json_encode($r, JSON_UNESCAPED_UNICODE), 0, 600), "\n";
