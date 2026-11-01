<?php
// read-only: the last SignalWire calls (to see why the leg to the salon iPhone failed)
declare(strict_types=1);
if (PHP_SAPI !== 'cli') exit;
require '/home/uyurpyzubx0m/app/sites/an/current/inc/core.php'; require_once '/home/uyurpyzubx0m/app/sites/an/current/inc/calls.php';
$base = cl_sw_base(); $proj = cl_project(); $tok = cl_sec('sw_token');
$ch = curl_init($base . '/api/laml/2010-04-01/Accounts/' . $proj . '/Calls.json?PageSize=12');
curl_setopt_array($ch, [CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 15, CURLOPT_HTTPAUTH => CURLAUTH_BASIC, CURLOPT_USERPWD => $proj . ':' . $tok]);
$j = json_decode((string)curl_exec($ch), true); curl_close($ch);
foreach (($j['calls'] ?? []) as $c) printf("%s %-9s %-12s from %s to %s dur %s parent %s\n", substr((string)$c['start_time'], 17, 8), $c['direction'] ?? '', $c['status'] ?? '', $c['from'] ?? '', $c['to'] ?? '', $c['duration'] ?? '', substr((string)($c['parent_call_sid'] ?? ''), 0, 8));
if (!isset($j['calls'])) echo substr(json_encode($j), 0, 300), "\n";
