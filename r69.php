<?php
declare(strict_types=1);
if (PHP_SAPI !== 'cli') exit;
require '/home/uyurpyzubx0m/app/sites/an/current/inc/core.php';
foreach (q("SELECT id, kind, status, dur_sec, result, reason, text_c, text_s FROM calls WHERE id IN (67,68,69)")->fetchAll() as $r) { echo "--\n"; foreach ($r as $k => $v) if (!is_int($k)) echo $k, ': ', mb_substr((string)$v, 0, 400), "\n"; }
