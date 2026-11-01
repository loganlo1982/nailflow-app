<?php
declare(strict_types=1);
if (PHP_SAPI !== 'cli') exit;
$A = $argv[1];
require '/home/uyurpyzubx0m/app/sites/an/current/inc/core.php'; require_once '/home/uyurpyzubx0m/app/sites/an/current/inc/calls.php';
$src = (string)file_get_contents($A . '/inc/calls-agent.php'); $src = preg_replace('/^<\?php\s*/', '', $src); $src = preg_replace('/^declare\(strict_types=1\);/m', '', $src);
$src = str_replace("__DIR__ . '/", "'/home/uyurpyzubx0m/app/sites/an/current/inc/", $src);
$src = str_replace("q(\"INSERT INTO calls", "(fn() => null)(\"INSERT INTO calls", $src); // never write a test row
eval($src);
$d = cl_agent_swml(['call' => ['call_id' => 'TEST-606r', 'from' => '+15154997409', 'to' => '+15156061616']]);
$m = $d['sections']['main']; foreach ($m as $x) echo json_encode(array_map(fn($v) => is_array($v) ? array_intersect_key($v, array_flip(['to', 'timeout', 'ringback', 'url', 'stereo'])) : $v, $x), JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE), "\n";
