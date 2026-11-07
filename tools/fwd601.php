<?php
/* AN: the phone Telnyx rings first (call_fwd) + the owner phone for questions (call_owner): 672 (no longer in use) -> (601) 666-6677. Lists every setting still holding 672 (names only).
   SALON_ID=an php fwd601.php [go] */
declare(strict_types=1);
$site = (string)getenv('SALON_ID'); if ($site !== 'an') exit("an only\n");
require "/home/uyurpyzubx0m/app/sites/$site/current/inc/core.php"; settings(); require_once APP_ROOT . '/inc/calls.php';
$show = function () { foreach (['call_fwd', 'call_owner'] as $k) echo $k, ' = ', setting($k), "\n"; };
$show(); echo 'settings with 6727879: ', implode(', ', q("SELECT k FROM settings WHERE v LIKE '%672%7879%' OR v LIKE '%6727879%'")->fetchAll(PDO::FETCH_COLUMN)), "\n";
if (($argv[1] ?? '') !== 'go') exit("(list only)\n");
$in = ['fwd' => '(601) 666-6677']; if (in_array(norm_phone((string)setting('call_owner')), ['+15156727879', ''], true)) $in['owner'] = '(601) 666-6677';
cl_cfg_save($in); echo "saved\n"; $show();
