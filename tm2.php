<?php
declare(strict_types=1);
if (PHP_SAPI !== 'cli') exit;
require '/home/uyurpyzubx0m/app/sites/an/current/inc/core.php';
foreach (q("SELECT action, who, created_at FROM appt_log WHERE appt_id = 1318 ORDER BY id")->fetchAll() as $l) echo $l['action'], ' ', $l['who'], ' ', $l['created_at'], "\n";
foreach (q("SELECT created_at, title, body FROM push_log WHERE kind = 'call' AND created_at >= '2026-11-01 16:38' ORDER BY id")->fetchAll() as $l) echo 'push ', $l['created_at'], ' ', $l['title'], "\n";
