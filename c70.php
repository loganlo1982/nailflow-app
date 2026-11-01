<?php
declare(strict_types=1);
if (PHP_SAPI !== 'cli') exit;
require '/home/uyurpyzubx0m/app/sites/an/current/inc/core.php';
foreach (q("SELECT * FROM calls WHERE id >= 71 ORDER BY id")->fetchAll() as $r) { echo "--\n"; foreach ($r as $k => $v) if (!is_int($k) && (string)$v !== '' && !in_array($k, ['rec_url'], true)) echo $k, ': ', mb_substr((string)$v, 0, 500), "\n"; }
