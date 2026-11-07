<?php
/* the Settings "Test Android" button from a shell: ONE test text to the salon's test number (AN: 515-499-7409) through the Android gateway. Prints no secret.
   SALON_ID=<site> php adtest.php  (as the app user) ; php adtest.php <id> = the state of that test text */
declare(strict_types=1);
$site = (string)getenv('SALON_ID'); if (!preg_match('/^[a-z0-9]+$/', $site)) exit("SALON_ID?\n");
require "/home/uyurpyzubx0m/app/sites/$site/current/inc/core.php"; settings(); require_once APP_ROOT . '/inc/autosend.php'; require_once APP_ROOT . '/inc/android.php';
if (!empty($argv[1])) { $x = q('SELECT id, phone, state, via, note, taken_at FROM autosend WHERE id = ?', [(int)$argv[1]])->fetch(); echo json_encode($x, JSON_UNESCAPED_UNICODE), "\n"; exit; }
if (as_dev() !== 'android' || !ad_ready()) exit("Android not ready\n");
$tp = ad_test_phone(); if ($tp !== '+15154997409') exit("test number is not 499 - stop\n");
$id = as_add('test', 'test:' . date('YmdHis') . ':' . bin2hex(random_bytes(2)), $tp, 'TEST', 'TEST from ' . salon_title() . ' – Fold works ✓ ' . date('g:i A'), 'Test (Android)');
if (!$id) exit("not added\n");
$n = ad_send_rows([['id' => $id]]);
$x = q('SELECT id, state, via, note FROM autosend WHERE id = ?', [$id])->fetch(); echo json_encode($x, JSON_UNESCAPED_UNICODE), "\n";
