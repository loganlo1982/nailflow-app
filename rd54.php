<?php
declare(strict_types=1);
if (PHP_SAPI !== 'cli') exit;
require '/home/uyurpyzubx0m/app/sites/an/current/inc/core.php';
$r = q("SELECT id, status, file, text_c, text_s, ai_json, result, reason, err FROM calls WHERE id = ?", [(int)($argv[1] ?? 54)])->fetch();
foreach ($r as $k => $v) echo $k, ': ', mb_substr((string)$v, 0, 700), "\n";
