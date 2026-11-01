<?php
// CHAT 01/11 test: does the SignalWire recording file exist BEFORE the "finished" webhook? Read-only: polls the recordings list every 1 s for 6 min, logs changes.
declare(strict_types=1);
if (PHP_SAPI !== 'cli') exit;
require '/home/uyurpyzubx0m/app/sites/an/current/inc/core.php'; require_once '/home/uyurpyzubx0m/app/sites/an/current/inc/calls.php';
$base = cl_sw_base(); $proj = cl_project(); $tok = cl_sec('sw_token');
$get = function (string $u, bool $head = false) use ($proj, $tok) { $ch = curl_init($u); curl_setopt_array($ch, [CURLOPT_RETURNTRANSFER => true, CURLOPT_NOBODY => $head, CURLOPT_FOLLOWLOCATION => true, CURLOPT_TIMEOUT => 8, CURLOPT_HTTPAUTH => CURLAUTH_BASIC, CURLOPT_USERPWD => $proj . ':' . $tok]);
  $r = curl_exec($ch); $c = (int)curl_getinfo($ch, CURLINFO_HTTP_CODE); $len = (int)curl_getinfo($ch, CURLINFO_CONTENT_LENGTH_DOWNLOAD); curl_close($ch); return [$c, $r, $len]; };
$last = []; $seen = []; $end = time() + 360; $first = true;
while (time() < $end) {
  [$c, $r] = $get($base . '/api/relay/rest/recordings?page_size=3');
  $j = json_decode((string)$r, true); $list = $j['data'] ?? [];
  if ($first) { echo date('H:i:s'), " list http $c keys: ", implode(',', array_keys($list[0] ?? [])), "\n"; $first = false; }
  foreach ($list as $x) { $id = (string)($x['id'] ?? ''); $sig = json_encode([$x['state'] ?? null, $x['status'] ?? null, $x['duration'] ?? null, $x['url'] ?? null]);
    if (($last[$id] ?? '') !== $sig) { echo date('H:i:s'), " REC $id ", $sig, "\n"; $last[$id] = $sig; }
    if (!isset($seen[$id]) || $seen[$id] !== 200) { [$hc, , $hl] = $get($base . '/api/relay/rest/recordings/' . $id . '.wav', true); if (($seen[$id] ?? -1) !== $hc) { echo date('H:i:s'), " WAV $id http $hc len $hl\n"; $seen[$id] = $hc; } } }
  $cr = q('SELECT id, status, rec_sid, dur_sec FROM calls ORDER BY id DESC LIMIT 1')->fetch(); $s = json_encode($cr);
  if (($last['call'] ?? '') !== $s) { echo date('H:i:s'), " CALL $s\n"; $last['call'] = $s; }
  usleep(1000000);
}
echo "done\n";
