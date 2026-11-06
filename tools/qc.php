<?php
/* read-only: the last calls at a salon + their live-booking files (no secrets) - php qc.php [site] [n] */
$site = $argv[1] ?? 'an'; $n = (int)($argv[2] ?? 3);
$c = require "/home/uyurpyzubx0m/app/sites/$site/config.php"; $p = new PDO("mysql:host=" . ($c["db_host"] ?? "localhost") . ";dbname=" . $c["db_name"] . ";charset=utf8mb4", $c["db_user"], $c["db_pass"]); $p->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
$set = []; foreach ($p->query("SELECT k, v FROM settings WHERE k IN ('tx_live','tx_on','call_ai_cap','call_cap_day')") as $r) $set[$r['k']] = $r['v']; echo json_encode($set), "\n";
$dir = null; foreach (["/home/uyurpyzubx0m/app/sites/$site/calls", "/home/uyurpyzubx0m/app/sites/$site/data/calls"] as $d) if (is_dir($d)) $dir = $d;
foreach ($p->query("SELECT id, call_sid, kind, screen, status, started_at, dur_sec, appt_id, LEFT(result,120) res, LEFT(reason,100) why, created_at FROM calls ORDER BY id DESC LIMIT $n") as $r) {
  $sid = $r['call_sid']; unset($r['call_sid']); echo "== ", json_encode($r, JSON_UNESCAPED_UNICODE), "\n";
  foreach (glob("/home/uyurpyzubx0m/app/sites/$site/*/txl-" . md5($sid) . ".*") ?: [] as $f) { echo "  ", basename($f), " ", filesize($f), " ", date('H:i:s', filemtime($f)), "\n"; if (str_ends_with($f, '.json')) echo "  ", substr((string)file_get_contents($f), 0, 600), "\n"; }
  foreach ($p->query("SELECT action, LEFT(detail,150) d, created_at FROM appt_log WHERE created_at >= '" . $r['started_at'] . "' AND created_at <= DATE_ADD('" . $r['started_at'] . "', INTERVAL 4 MINUTE) ORDER BY id") as $l) echo "  log ", implode(' | ', $l), "\n";
}
