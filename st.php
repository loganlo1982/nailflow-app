<?php
declare(strict_types=1);
if (PHP_SAPI !== 'cli') exit;
require '/home/uyurpyzubx0m/app/sites/an/current/inc/core.php';
function dump($rows) { foreach ($rows as $r) { echo "--\n"; foreach ($r as $k => $v) if (!is_int($k) && (string)$v !== '' && (string)$v !== '0') echo $k, ': ', mb_substr((string)$v, 0, 600), "\n"; } }
$a = q("SELECT * FROM appointments WHERE appt_date = '2026-11-01' AND UPPER(customer_name) LIKE 'STACY%'")->fetchAll(); echo "=== STACY\n"; dump($a);
foreach ($a as $x) { echo "=== LOG ", $x['id'], "\n"; dump(q("SELECT action, detail, source, who, created_at FROM appt_log WHERE appt_id = ? ORDER BY id", [$x['id']])->fetchAll()); }
echo "=== SERVICES\n"; foreach ($a as $x) dump(q("SELECT * FROM services WHERE id IN (" . implode(',', array_map('intval', explode(',', (string)$x['service_ids']))) . ")")->fetchAll());
echo "=== STAFF\n"; dump(q("SELECT * FROM staff WHERE active = 1")->fetchAll());
echo "=== CLOCK today\n"; try { dump(q("SELECT * FROM staff_clock WHERE work_date = '2026-11-01'")->fetchAll()); } catch (Throwable $e) { echo $e->getMessage(), "\n"; try { dump(q("SELECT * FROM staff_clock ORDER BY 1 DESC LIMIT 10")->fetchAll()); } catch (Throwable $e) { echo $e->getMessage(), "\n"; } }
echo "=== IN SERVICE NOW\n"; dump(q("SELECT id, customer_name, staff_id, status, start_min, started_at, done_at, arrived_at, service_ids FROM appointments WHERE appt_date = '2026-11-01' AND arrived_at <> '' ORDER BY id")->fetchAll());
echo "=== TURN OFFERS\n"; try { dump(q("SELECT * FROM turn_offers ORDER BY 1 DESC LIMIT 8")->fetchAll()); } catch (Throwable $e) { echo $e->getMessage(), "\n"; }
echo "=== LAST LOG\n"; dump(q("SELECT appt_id, action, detail, who, customer, created_at FROM appt_log WHERE id > 5339 ORDER BY id")->fetchAll());
