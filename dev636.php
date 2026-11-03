<?php
/* CHAT – CHI DOC: may nao da dang nhap Love Nails, IP co trung voi may dang nhap American Nails khong. */
if (PHP_SAPI !== 'cli') exit;
$R = '/home/uyurpyzubx0m/app/sites/an/current';
function rows(string $sid, string $R): array {
    $c = 'require "' . $R . '/inc/core.php"; settings(); echo json_encode(q("SELECT at, who, kind, target, after_v, ip FROM audit_log WHERE (kind IN (\'login\',\'twofa\',\'pw_change\',\'support\') OR target LIKE \'%login%\' OR after_v LIKE \'%log%in%\') AND at >= ? ORDER BY id", [date("Y-m-d", strtotime("-45 days"))])->fetchAll());';
    return json_decode((string)shell_exec('SALON_ID=' . $sid . ' php -d error_log=/dev/null -r ' . escapeshellarg($c)), true) ?: [];
}
$an = rows('an', $R); $ln = rows('lovenails', $R);
$anIp = []; foreach ($an as $r) if ($r['ip'] !== '') $anIp[$r['ip']] = ($anIp[$r['ip']] ?? 0) + 1;
$by = []; foreach ($ln as $r) { $k = $r['ip'] ?: '-'; $by[$k][] = $r; }
echo 'AN: ', count($an), ' dong dang nhap, ', count($anIp), " IP · Love Nails: ", count($ln), " dong\n";
foreach ($by as $ip => $l) {
    $last = end($l); $kinds = []; foreach ($l as $r) { $t = $r['who'] . ':' . mb_substr($r['after_v'], 0, 40); $kinds[$t] = 1; }
    printf("%-16s %3d lan · cuoi %s · %s · %s\n", $ip, count($l), substr($last['at'], 5, 11), isset($anIp[$ip]) ? 'CUNG IP VOI AN (' . $anIp[$ip] . ')' : 'khong thay o AN', mb_substr(implode(' | ', array_keys($kinds)), 0, 110));
}
