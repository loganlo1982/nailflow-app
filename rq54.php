<?php
// CHAT 01/11 - 605B: requeue test call #54 (AN) so the new cl_fetch reads the SWML stereo recording
declare(strict_types=1);
if (PHP_SAPI !== 'cli') exit;
require '/home/uyurpyzubx0m/app/sites/an/current/inc/core.php';
$id = 54;
$r = q("SELECT id, status, file, rec_sid, rec_url, kind, dur_sec, reason FROM calls WHERE id = ?", [$id])->fetch();
echo json_encode($r, JSON_UNESCAPED_SLASHES|JSON_UNESCAPED_UNICODE), "\n";
if (($argv[1] ?? '') !== 'go') { echo "check only\n"; exit; }
q("UPDATE calls SET status = 'queued', next_at = '2026-11-01 00:00:00', lock_at = '', tries = 0, err = '', file = '', text_c = '', text_s = '' WHERE id = ?", [$id]);
echo "requeued\n";
