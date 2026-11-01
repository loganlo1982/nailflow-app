<?php
declare(strict_types=1);
if (PHP_SAPI !== 'cli') exit;
require '/home/uyurpyzubx0m/app/sites/an/current/inc/core.php';
function dump($rows) { foreach ($rows as $r) { echo "--\n"; foreach ($r as $k => $v) if (!is_int($k) && (string)$v !== '' && (string)$v !== '0') echo $k, ': ', mb_substr((string)$v, 0, 900), "\n"; } }

echo "=== APPTS MARK\n"; try { dump(q("SELECT * FROM appointments WHERE id >= 1300 ORDER BY id")->fetchAll()); } catch (Throwable $e) { echo $e->getMessage(), "\n"; }
$tabs = array_column(q(is_sqlite() ? "SELECT name FROM sqlite_master WHERE type='table'" : "SHOW TABLES")->fetchAll(PDO::FETCH_NUM), 0); echo "TABLES: ", implode(',', $tabs), "\n";
foreach ($tabs as $t) try { if (preg_match('/log|hist|audit|activ/i', $t)) { echo "=== $t (last 25)\n"; dump(q("SELECT * FROM `$t` ORDER BY 1 DESC LIMIT 25")->fetchAll()); } } catch (Throwable $e) { echo $e->getMessage(), "\n"; }
