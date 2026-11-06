<?php
/* test bookings only: phone 515-499-7409, booked TODAY, still 'booked' -> list; with "go" they are cancelled silently (no text). php tc.php [site] [go] */
$site = $argv[1] ?? 'an'; $go = ($argv[2] ?? '') === 'go';
$c = require "/home/uyurpyzubx0m/app/sites/$site/config.php"; $p = new PDO("mysql:host=" . ($c["db_host"] ?? "localhost") . ";dbname=" . $c["db_name"] . ";charset=utf8mb4", $c["db_user"], $c["db_pass"]); $p->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
$rows = $p->query("SELECT id, appt_date, customer_name, phone, status, created_at FROM appointments WHERE phone LIKE '%4997409' AND status = 'booked' AND DATE(created_at) = CURDATE() ORDER BY id")->fetchAll();
foreach ($rows as $r) echo json_encode($r), "\n";
if ($go) { $u = $p->prepare("UPDATE appointments SET status = 'cancelled', confirm_state = 'no' WHERE id = ? AND status = 'booked' AND phone LIKE '%4997409'"); foreach ($rows as $r) { $u->execute([$r['id']]); echo "cancelled ", $r['id'], "\n"; } }
echo count($rows), " row(s)", $go ? " cancelled" : " (list only)", "\n";
