<?php
// read-only: print the LIVE call SWML + screening SWML exactly as SignalWire gets them (no DB write)
declare(strict_types=1);
if (PHP_SAPI !== 'cli') exit;
$A = $argv[1] ?? '/home/uyurpyzubx0m/app/sites/an/current'; $L = '/home/uyurpyzubx0m/app/sites/an/current';
require $L . '/inc/core.php'; require_once $L . '/inc/calls.php'; foreach (['calls-job', 'calls-ivr'] as $x) require_once $L . '/inc/' . $x . '.php';
$src = (string)file_get_contents($A . '/inc/calls-agent.php'); $src = preg_replace('/^<\?php\s*/', '', $src); $src = preg_replace('/^declare\(strict_types=1\);/m', '', $src);
$src = str_replace("__DIR__ . '/", "'" . $L . "/inc/", $src); $src = str_replace("q(\"INSERT INTO calls", "(fn() => null)(\"INSERT INTO calls", $src);
if (!function_exists('group_members')) { function group_members($a) { return [$a]; } } if (!function_exists('rp_upcoming')) { function rp_upcoming($p) { return []; } }
eval($src);
$d = cl_agent_swml(['call' => ['call_id' => 'TEST-X', 'from' => '+15154997409', 'to' => '+15156061616']]);
foreach ($d['sections']['main'] as $x) echo json_encode($x, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE), "\n";
echo "== after: ", substr(json_encode($d['sections']['after'] ?? null, JSON_UNESCAPED_SLASHES), 0, 300), "\n== screen: ", json_encode(cl_agent_screen_swml(), JSON_UNESCAPED_SLASHES), "\n";
