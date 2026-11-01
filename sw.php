<?php
declare(strict_types=1);
if (PHP_SAPI !== 'cli') exit;
$A = $argv[1];
require '/home/uyurpyzubx0m/app/sites/an/current/inc/core.php'; require_once '/home/uyurpyzubx0m/app/sites/an/current/inc/calls.php';
$src = (string)file_get_contents($A . '/inc/calls-agent.php'); $i = strpos($src, 'function cl_agent_screen_swml('); $j = strpos($src, "\n/** The old free voicemail", $i); eval(substr($src, $i, $j - $i));
if (!function_exists('cl_agent_url')) { function cl_agent_url($a, $q = '') { return "U:$a$q"; } }
echo json_encode(cl_agent_screen_swml(), JSON_UNESCAPED_SLASHES), "\n";
