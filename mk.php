<?php
declare(strict_types=1);
if (PHP_SAPI !== 'cli') exit;
require '/home/uyurpyzubx0m/app/sites/an/current/inc/core.php';
function dump($rows) { foreach ($rows as $r) { echo "--\n"; foreach ($r as $k => $v) if (!is_int($k) && (string)$v !== '' && (string)$v !== '0') echo $k, ': ', mb_substr((string)$v, 0, 900), "\n"; } }
echo "=== CALLS > 55\n"; dump(q("SELECT * FROM calls WHERE id > 55 ORDER BY id")->fetchAll());
echo "=== APPTS MARK\n"; $a = q("SELECT a.* FROM appointments a LEFT JOIN customers c ON c.id = a.customer_id WHERE a.date >= '2026-11-01' AND (UPPER(c.name) LIKE '%MARK%' OR UPPER(a.name) LIKE '%MARK%') ORDER BY a.id")->fetchAll(); dump($a);
$tabs = array_column(q(is_sqlite() ? "SELECT name FROM sqlite_master WHERE type='table'" : "SHOW TABLES")->fetchAll(PDO::FETCH_NUM), 0); echo "TABLES: ", implode(',', $tabs), "\n";
foreach ($tabs as $t) if (preg_match('/log|hist|audit|activ/i', $t)) { echo "=== $t (last 25)\n"; dump(q("SELECT * FROM `$t` ORDER BY 1 DESC LIMIT 25")->fetchAll()); }
