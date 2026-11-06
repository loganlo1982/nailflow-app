<?php
/* read-only: one customer's day - texts in/out, outbox, appointments (+ group), their log. php qm.php <site> <last 7+ digits of the phone> */
$site = $argv[1] ?? 'an'; $ph = preg_replace('/\D/', '', $argv[2] ?? ''); if (strlen($ph) < 7) exit("phone?\n");
$c = require "/home/uyurpyzubx0m/app/sites/$site/config.php"; $p = new PDO("mysql:host=" . ($c["db_host"] ?? "localhost") . ";dbname=" . $c["db_name"] . ";charset=utf8mb4", $c["db_user"], $c["db_pass"]); $p->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
$cut = fn($s, $n = 90) => mb_substr(preg_replace('/\s+/', ' ', (string)$s), 0, $n);
echo "-- messages\n"; foreach ($p->query("SELECT id, dir, body, created_at FROM messages WHERE phone LIKE '%$ph' AND created_at >= CURDATE() ORDER BY id") as $r) echo $r['id'], ' ', $r['created_at'], ' ', $r['dir'], ' ', $cut($r['body']), "\n";
echo "-- outbox\n"; foreach ($p->query("SELECT id, kind, ref, appt_id, status, created_at, sent_at, body FROM outbox WHERE phone LIKE '%$ph' AND created_at >= CURDATE() ORDER BY id") as $r) echo $r['id'], ' ', $r['created_at'], ' ', $r['kind'], ' ', $r['ref'], ' a', $r['appt_id'], ' ', $r['status'], ' ', $r['sent_at'], ' ', $cut($r['body'], 50), "\n";
$ids = []; $gs = [];
foreach ($p->query("SELECT id, group_id FROM appointments WHERE phone LIKE '%$ph' AND appt_date >= CURDATE() - INTERVAL 1 DAY") as $r) { $ids[] = (int)$r['id']; if ($r['group_id'] !== '') $gs[] = $p->quote($r['group_id']); }
if ($gs) foreach ($p->query("SELECT id FROM appointments WHERE group_id IN (" . implode(',', array_unique($gs)) . ")") as $r) $ids[] = (int)$r['id'];
$ids = array_values(array_unique($ids)); if (!$ids) exit("no appointments\n");
echo "-- appointments\n"; foreach ($p->query("SELECT id, appt_date, start_min, staff_id, customer_name, status, group_id, LEFT(note,60) note FROM appointments WHERE id IN (" . implode(',', $ids) . ")") as $r) echo json_encode($r, JSON_UNESCAPED_UNICODE), "\n";
echo "-- log\n"; foreach ($p->query("SELECT appt_id, action, source, who, LEFT(detail,110) d, created_at FROM appt_log WHERE appt_id IN (" . implode(',', $ids) . ") AND created_at >= CURDATE() ORDER BY id") as $r) echo implode(' | ', $r), "\n";
