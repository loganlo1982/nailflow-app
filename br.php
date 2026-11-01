<?php
declare(strict_types=1);
if (PHP_SAPI !== 'cli') exit;
require '/home/uyurpyzubx0m/app/sites/an/current/inc/core.php';
$a = json_decode((string)setting('polish_colors'), true) ?: [];
$g = []; foreach ($a as $c) { $k = ($c['brand'] ?? '?') . ' | ' . ($c['kind'] ?? '?') . ' | on=' . (int)($c['on'] ?? 1); $g[$k] = ($g[$k] ?? 0) + 1; }
ksort($g); foreach ($g as $k => $n) echo "$k : $n\n"; echo 'total ', count($a), "\n";
