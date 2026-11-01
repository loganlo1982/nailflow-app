<?php
declare(strict_types=1);
if (PHP_SAPI !== 'cli') exit;
require '/home/uyurpyzubx0m/app/sites/an/current/inc/core.php';
foreach (q("SELECT id, kind, status, started_at, dur_sec, next_at, lock_at, tries, appt_id, result, reason, LENGTH(text_c) lc, LENGTH(text_s) ls FROM calls WHERE id >= 56 ORDER BY id")->fetchAll() as $r) {
  $end = date('H:i:s', strtotime($r['started_at']) + (int)$r['dur_sec']);
  $log = q("SELECT action, created_at FROM appt_log WHERE source = 'call' AND created_at >= ? ORDER BY id LIMIT 3", [$r['started_at']])->fetchAll();
  echo "#{$r['id']} {$r['kind']} {$r['status']} start {$r['started_at']} dur {$r['dur_sec']} end~$end queued(next_at) {$r['next_at']} lock {$r['lock_at']} tries {$r['tries']} appt {$r['appt_id']} | ", mb_substr((string)$r['result'],0,80), " | ", $r['reason'], "\n";
  foreach ($log as $l) echo "    log ", $l['action'], ' ', $l['created_at'], "\n";
}
