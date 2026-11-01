<?php
// CHAT test 606p: read call #63's file with the OLD way (one after the other) and the NEW way (cl_stt2), compare text + time. argv[1] = app dir to load
declare(strict_types=1);
if (PHP_SAPI !== 'cli') exit;
$A = $argv[1];
require '/home/uyurpyzubx0m/app/sites/an/current/inc/core.php'; require_once '/home/uyurpyzubx0m/app/sites/an/current/inc/calls.php'; echo 'core ok', PHP_EOL; require_once $A . '/inc/calls-job.php'; echo 'job ok ', function_exists('cl_stt2') ? 'stt2' : 'NO', PHP_EOL;
$c = q('SELECT * FROM calls WHERE id = 63')->fetch();
$parts = cl_split((string)file_get_contents(cl_path((string)$c['file']))); $hint = cl_stt_hint();
echo 'parts ', count($parts), "\n";
$t0 = microtime(true); $a = cl_stt($parts[0], $hint); $b = cl_stt($parts[1], $hint); $t1 = microtime(true);
[$x, $y] = cl_stt2([$parts[0], $parts[1]], $hint); $t2 = microtime(true);
printf("OLD %.2fs  NEW %.2fs\n", $t1 - $t0, $t2 - $t1);
echo 'OLD c: ', $a, "\nNEW c: ", $x, "\nOLD s: ", $b, "\nNEW s: ", $y, "\n";
