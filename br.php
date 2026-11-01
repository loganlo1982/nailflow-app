<?php
declare(strict_types=1);
if (PHP_SAPI !== 'cli') exit;
require '/home/uyurpyzubx0m/app/sites/an/current/inc/core.php';
$t = array_column(q(is_sqlite() ? "SELECT name FROM sqlite_master WHERE type='table'" : "SHOW TABLES")->fetchAll(PDO::FETCH_NUM), 0);
foreach ($t as $x) if (stripos($x, 'color') !== false) { echo "TABLE $x\n"; $c = q("SELECT * FROM `$x` LIMIT 1")->fetch(PDO::FETCH_ASSOC); echo ' cols: ', implode(',', array_keys($c ?: [])), "\n"; }
try { foreach (q("SELECT brand, kind, active, COUNT(*) n FROM colors GROUP BY brand, kind, active ORDER BY brand")->fetchAll() as $r) echo json_encode($r, JSON_UNESCAPED_UNICODE), "\n"; } catch (Throwable $e) { echo $e->getMessage(), "\n"; }
foreach (q("SELECT k, v FROM settings WHERE k LIKE '%color%' OR k LIKE '%brand%'")->fetchAll() as $r) echo $r['k'], ' = ', mb_substr((string)$r['v'], 0, 200), "\n";
