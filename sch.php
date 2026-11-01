<?php
declare(strict_types=1);
if (PHP_SAPI !== 'cli') exit;
require '/home/uyurpyzubx0m/app/sites/an/current/inc/core.php';
require_once '/home/uyurpyzubx0m/app/sites/an/current/inc/calls-job.php';
$k = array_keys(cl_ai_schema()['schema']['properties']); echo count($k), ' keys: ', implode(',', $k), "\n";
foreach (['salon_side','salon_agreed','customer_name','customer_phone','service_ids','service_text','new_date','new_time'] as $x) echo $x, in_array($x, $k, true) ? ' OK' : ' MISSING', "\n";
if (($argv[1] ?? '') === 'rq') { $id = (int)$argv[2]; $r = q('SELECT status, appt_id FROM calls WHERE id = ?', [$id])->fetch(); echo json_encode($r), "\n";
 if ($r && $r['status'] === 'review' && (int)$r['appt_id'] === 0) { q("UPDATE calls SET status = 'queued', next_at = '2026-11-01 00:00:00', lock_at = '', tries = 0, err = '', ai_json = '', reason = '', result = '' WHERE id = ?", [$id]); echo "requeued $id\n"; } }
