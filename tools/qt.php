<?php
/* read-only: today's walk-ins, the turn line state and logs at American Nails (no secrets printed) */
$c = require "/home/uyurpyzubx0m/app/sites/an/config.php"; $p = new PDO("mysql:host=" . ($c["db_host"] ?? "localhost") . ";dbname=" . $c["db_name"] . ";charset=utf8mb4", $c["db_user"], $c["db_pass"]); $p->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
$d = date('Y-m-d'); $from = $argv[1] ?? '10:20'; echo "now ", date('H:i:s'), "\n";
$st = []; foreach ($p->query("SELECT id, name FROM staff") as $r) $st[$r['id']] = $r['name'];
echo "-- appts\n"; foreach ($p->query("SELECT id, staff_id, start_min, duration, status, customer_name, auto_tech, arrived_at, started_at, done_at, source FROM appointments WHERE appt_date = '$d' AND status <> 'cancelled' ORDER BY start_min") as $r) { $r['tech'] = $st[$r['staff_id']] ?? '-'; $r['t'] = sprintf('%d:%02d', intdiv((int)$r['start_min'], 60), $r['start_min'] % 60); unset($r['start_min']); echo implode(' | ', $r), "\n"; }
echo "-- log\n"; foreach ($p->query("SELECT appt_id, action, LEFT(detail,140) d, created_at FROM appt_log WHERE created_at >= '$d $from' ORDER BY id") as $r) echo implode(' | ', $r), "\n";
echo "-- offers\n"; try { foreach ($p->query("SELECT id, appt_id, staff_id, kind, state, at FROM turn_offers WHERE work_date = '$d' ORDER BY id") as $r) { $r['tech'] = $st[$r['staff_id']] ?? '-'; echo implode(' | ', $r), "\n"; } } catch (Throwable $e) { echo $e->getMessage(), "\n"; }
echo "-- asks\n"; try { foreach ($p->query("SELECT * FROM turn_asks WHERE work_date = '$d' ORDER BY id") as $r) echo json_encode($r), "\n"; } catch (Throwable $e) { echo $e->getMessage(), "\n"; }
echo "-- clock\n"; try { foreach ($p->query("SELECT * FROM clock WHERE work_date = '$d' ORDER BY id") as $r) echo json_encode($r), "\n"; } catch (Throwable $e) { echo $e->getMessage(), "\n"; }
echo "-- settings\n"; foreach ($p->query("SELECT k, LEFT(v,80) v FROM settings WHERE k LIKE 'ta\\_%' OR k LIKE 'turn%' OR k LIKE 'tr\\_%'") as $r) echo $r['k'], '=', $r['v'], "\n";
