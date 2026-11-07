<?php
/* Read-only: why the 2.99.670 text assistant is on/off for a site. SALON_ID=<site> php taon.php   (prints no keys) */
$site = (string)getenv('SALON_ID'); if (!preg_match('/^[a-z0-9]+$/', $site)) { fwrite(STDERR, "SALON_ID?\n"); exit(1); }
require "/home/uyurpyzubx0m/app/sites/$site/current/inc/core.php";
require_once APP_ROOT . '/inc/textassist.php';
if (!function_exists('tb_on')) require_once APP_ROOT . '/inc/textbook.php';
if (!function_exists('cl_stt_get')) require_once APP_ROOT . '/inc/calls.php';
$key = trim((string)(cl_stt_get()['key'] ?? '')) !== '';
echo $site, ' ', APP_VERSION, ' ta_on=[', setting('ta_on'), '] main=', main_salon() ? 1 : 0, ' url=', pub_url(), ' tb_on=', tb_on() ? 1 : 0, ' ai_key=', $key ? 1 : 0, ' => txa_on=', txa_on() ? 1 : 0, "\n";
