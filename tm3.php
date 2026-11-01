<?php
declare(strict_types=1);
if (PHP_SAPI !== 'cli') exit;
require '/home/uyurpyzubx0m/app/sites/an/current/inc/core.php';
foreach (q("SELECT id, call_sid, kind, status, started_at, dur_sec, next_at, appt_id, result, ai_json FROM calls WHERE id >= 63 ORDER BY id")->fetchAll() as $r) {
  $j = json_decode((string)$r['ai_json'], true) ?: [];
  echo "#{$r['id']} {$r['kind']} {$r['status']} start {$r['started_at']} recdur {$r['dur_sec']} queued {$r['next_at']} appt {$r['appt_id']} | ", mb_substr((string)$r['result'], 0, 70), "\n";
  if ($r['appt_id']) foreach (q("SELECT action, created_at FROM appt_log WHERE appt_id = ? ORDER BY id LIMIT 2", [$r['appt_id']])->fetchAll() as $l) echo "   appt ", $l['action'], ' ', $l['created_at'], "\n";
}
foreach (q("SELECT created_at, title FROM push_log WHERE kind = 'call' AND created_at >= '2026-11-01 17:00' ORDER BY id")->fetchAll() as $l) echo 'push ', $l['created_at'], ' ', $l['title'], "\n";
