<?php
declare(strict_types=1);
if (PHP_SAPI !== 'cli') exit;
require '/home/uyurpyzubx0m/app/sites/an/current/inc/core.php';
foreach (q("SELECT appt_id, action, detail, who, customer, appt_when, created_at FROM appt_log WHERE created_at >= '2026-11-01 12:55:00' ORDER BY id")->fetchAll() as $r) { echo "--\n"; foreach ($r as $k => $v) if (!is_int($k)) echo $k, ': ', $v, "\n"; }
foreach (q("SELECT id, customer_name, staff_id, status, start_min, duration, service_ids, group_id, started_at, done_at FROM appointments WHERE appt_date = '2026-11-01' AND start_min >= 720 ORDER BY start_min")->fetchAll() as $r) echo json_encode($r, JSON_UNESCAPED_UNICODE), "\n";
