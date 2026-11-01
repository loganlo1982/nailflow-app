<?php
declare(strict_types=1);
if (PHP_SAPI !== 'cli') exit;
require '/home/uyurpyzubx0m/app/sites/an/current/inc/core.php';
$r = q('SELECT status, appt_id, result, reason FROM calls WHERE id = 69')->fetch(); echo json_encode($r, JSON_UNESCAPED_UNICODE), "\n";
