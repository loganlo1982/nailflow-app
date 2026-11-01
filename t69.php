<?php
// CHAT test 606w: re-read call #69's saved text with the NEW rules (sim tree), print the AI's date/time - nothing saved.
declare(strict_types=1);
if (PHP_SAPI !== 'cli') exit;
$A = $argv[1];
require '/home/uyurpyzubx0m/app/sites/an/current/inc/core.php'; require_once '/home/uyurpyzubx0m/app/sites/an/current/inc/calls.php';
$src = (string)file_get_contents($A . '/inc/calls-job.php'); $src = preg_replace('/^<\?php\s*/', '', $src); $src = preg_replace('/^declare\(strict_types=1\);/m', '', $src);
eval($src);
$c = q('SELECT * FROM calls WHERE id = 69')->fetch();
$j = cl_ai($c); echo 'date ', $j['date'] ?? '', ' time ', $j['time'] ?? '', ' agreed ', json_encode($j['salon_agreed'] ?? null), ' quote ', $j['salon_quote'] ?? '', "\n";
