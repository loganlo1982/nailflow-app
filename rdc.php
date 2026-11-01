<?php
declare(strict_types=1);
if (PHP_SAPI !== 'cli') exit;
require '/home/uyurpyzubx0m/app/sites/an/current/inc/core.php';
foreach (q("SELECT * FROM calls ORDER BY id DESC LIMIT 2")->fetchAll() as $r) { echo "=====\n"; foreach ($r as $k => $v) if (!is_int($k)) echo $k, ': ', mb_substr((string)$v, 0, 1500), "\n"; }
