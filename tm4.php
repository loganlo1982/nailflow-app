<?php
declare(strict_types=1);
if (PHP_SAPI !== 'cli') exit;
require '/home/uyurpyzubx0m/app/sites/an/current/inc/core.php';
foreach (q("SELECT c.id, c.started_at, c.dur_sec, c.status, c.appt_id, c.rec_url, (SELECT MIN(created_at) FROM appt_log l WHERE l.appt_id = c.appt_id AND c.appt_id > 0) booked FROM calls c WHERE c.kind = 'call' AND c.started_at >= '2026-10-31 00:00' ORDER BY c.id")->fetchAll() as $r) {
  $s = strtotime($r['started_at']); $b = $r['booked'] ? strtotime($r['booked']) : 0;
  printf("#%d %s rec %ds %s %s gap(start->booked - rec)=%s  %s\n", $r['id'], substr($r['started_at'], 5), $r['dur_sec'], $r['status'], $r['booked'] ? substr($r['booked'], 11) : '-', $b ? ($b - $s - (int)$r['dur_sec']) . 's' : '-', strpos((string)$r['rec_url'], '/api/laml/') !== false || strpos((string)$r['rec_url'], 'Recordings') !== false ? 'cXML' : 'SWML');
}
