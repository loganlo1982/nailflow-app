<?php
/* re-send ONE salon's Telnyx AI assistant (its instructions from the live code) - only when that salon already has one (never creates). Prints no key.
   SALON_ID=<site> php txai.php   (run as the app user) */
declare(strict_types=1);
$site = (string)getenv('SALON_ID'); if (!preg_match('/^[a-z0-9]+$/', $site)) { echo "SALON_ID?\n"; exit(1); }
require "/home/uyurpyzubx0m/app/sites/$site/current/inc/core.php";
settings(); require_once APP_ROOT . '/inc/calls-tx.php';
if ((string)setting('tx_assistant_id') === '' || tx_key() === '') { echo "$site: no Telnyx assistant - skipped\n"; exit(0); }
echo $site, ' ', APP_VERSION, ' asks tech: ', (str_contains(tx_instructions(), 'any tech, or someone special') ? 'yes' : 'NO'), "\n";
$r = tx_setup_step('ai'); echo $site, ': ', json_encode($r, JSON_UNESCAPED_UNICODE), "\n";
