<?php
// read-only: the last SignalWire calls (to see why the leg to the salon iPhone failed)
declare(strict_types=1);
if (PHP_SAPI !== 'cli') exit;
require '/home/uyurpyzubx0m/app/sites/an/current/inc/core.php'; require_once '/home/uyurpyzubx0m/app/sites/an/current/inc/calls.php';
$base = cl_sw_base(); $proj = cl_project(); $tok = cl_sec('sw_token');
$ch = curl_init($base . '/api/voice/logs?page_size=12');
curl_setopt_array($ch, [CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 15, CURLOPT_HTTPAUTH => CURLAUTH_BASIC, CURLOPT_USERPWD => $proj . ':' . $tok]);
$j = json_decode((string)curl_exec($ch), true); curl_close($ch);
foreach (($j["data"] ?? []) as $c) echo substr(json_encode(array_intersect_key($c, array_flip(["created_at","direction","status","from","to","duration","type","source","parent_id"]))), 0, 300), "\n";
if (!isset($j["data"])) echo substr(json_encode($j), 0, 300), "\n";
