<?php
declare(strict_types=1);
if (PHP_SAPI !== 'cli') exit;
require '/home/uyurpyzubx0m/app/sites/an/current/inc/core.php';
$r = q('SELECT status, appt_id FROM calls WHERE id = 69')->fetch(); echo json_encode($r), "\n";
if ($r && $r['status'] === 'review' && (int)$r['appt_id'] === 0) { q("UPDATE calls SET status = 'queued', next_at = '2026-11-01 00:00:00', lock_at = '', tries = 0, err = '', ai_json = '', reason = '', result = '' WHERE id = 69"); echo "requeued\n"; }
