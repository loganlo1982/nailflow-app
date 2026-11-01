<?php
declare(strict_types=1);
if (PHP_SAPI !== 'cli') exit;
require '/home/uyurpyzubx0m/app/sites/an/current/inc/core.php';
foreach (q("SELECT id, from_phone, kind, status, started_at, dur_sec, result, reason, text_c, text_s, ai_json FROM calls WHERE id >= 71 ORDER BY id")->fetchAll() as $r) {
  $j = json_decode((string)$r['ai_json'], true); $log = $j['agent']['log'] ?? [];
  echo "#{$r['id']} from {$r['from_phone']} {$r['kind']} {$r['status']} {$r['started_at']} dur {$r['dur_sec']} | ", mb_substr((string)$r['result'], 0, 80), ' | ', $r['reason'], "\n  C: ", mb_substr((string)$r['text_c'], 0, 200), "\n  S: ", mb_substr((string)$r['text_s'], 0, 200), "\n";
  foreach (array_slice($log, 1, 8) as $l) echo '   ', is_array($l) ? ($l[0] . ': ' . mb_substr((string)($l[1] ?? ''), 0, 150)) : '', "\n";
}
