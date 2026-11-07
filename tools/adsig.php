<?php
/* read-only: AN Android signing key - only its LENGTH and kind of characters (never the key) + when the HQ last changed texting keys. SALON_ID=an php adsig.php */
declare(strict_types=1);
$site = (string)getenv('SALON_ID'); if (!preg_match('/^[a-z0-9]+$/', $site)) exit("SALON_ID?\n");
require "/home/uyurpyzubx0m/app/sites/$site/current/inc/core.php"; settings(); require_once APP_ROOT . '/inc/autosend.php'; require_once APP_ROOT . '/inc/android.php';
$k = ad_sign(); echo 'sign length=', strlen($k), ' alnum=', preg_match('/^[A-Za-z0-9]+$/', $k) ? 'yes' : 'no', ' shared=', (sd_cred('ad_sign') !== null ? 'yes' : 'no'), "\n";
foreach (q("SELECT created_at, LEFT(action,40) a, LEFT(detail,80) d FROM audit_log WHERE action LIKE '%exting%' OR detail LIKE '%signing%' ORDER BY id DESC LIMIT 3") as $r) echo implode(' | ', $r), "\n";
