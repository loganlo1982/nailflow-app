<?php
// CHAT test 606w: call #69's saved text + the AI -> cl_weekday_fix from the sim tree; plus fixed cases. Nothing saved.
declare(strict_types=1);
if (PHP_SAPI !== 'cli') exit;
$A = $argv[1];
require '/home/uyurpyzubx0m/app/sites/an/current/inc/core.php'; require_once '/home/uyurpyzubx0m/app/sites/an/current/inc/calls.php';
$src = (string)file_get_contents($A . '/inc/calls-job.php'); $src = preg_replace('/^<\?php\s*/', '', $src); $src = preg_replace('/^declare\(strict_types=1\);/m', '', $src);
$src = str_replace("__DIR__ . '/", "'/home/uyurpyzubx0m/app/sites/an/current/inc/", $src); eval($src);
$c = q('SELECT * FROM calls WHERE id = 69')->fetch();
$j = cl_weekday_fix($c, cl_ai_after($c, cl_ai($c))); echo '#69 date ', $j['date'], ' ', $j['date_fix'] ?? '(no fix)', "\n";
$T = [['Tuesday, November 1st at 4', '2026-11-01'], ['tomorrow, Tuesday', '2026-11-02'], ['Friday the 6th', '2026-11-06'], ['Monday or Tuesday', '2026-11-03'], ['Sunday November 1', '2026-11-01'], ['el martes', '2026-11-01'], ['no day', '2026-11-04']];
foreach ($T as [$txt, $d]) { $r = cl_weekday_fix(['text_c' => $txt, 'text_s' => ''], ['date' => $d]); echo str_pad($txt, 28), " $d -> ", $r['date'], "\n"; }
