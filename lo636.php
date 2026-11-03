<?php
/* CHAT 03/11 – anh Logan: "Log out cac thiet bi login Love Nails". CHI tiem lovenails. Khong doi mat khau / PIN / link iPad.
   php lo636.php          -> chi dem   |   php lo636.php go -> dang xuat het: chu tiem, quan ly, tho (phien + key app + thiet bi tin cay) */
declare(strict_types=1);
if (PHP_SAPI !== 'cli') exit;
putenv('SALON_ID=lovenails'); $_SERVER['SALON_ID'] = 'lovenails';
require '/home/uyurpyzubx0m/app/sites/an/current/inc/core.php'; settings(); require_once APP_ROOT . '/inc/totp.php';
if (SITE_ID !== 'lovenails') { fwrite(STDERR, "DUNG: SITE_ID " . SITE_ID . "\n"); exit(2); }
$GO = ($argv[1] ?? '') === 'go'; $dir = site_sessions();
$c = []; foreach (app_toks() as $x) { $w = (string)($x['who'] ?? '?'); $c[$w] = ($c[$w] ?? 0) + 1; }
$files = glob(rtrim($dir, '/') . '/sess_*') ?: []; $adm = 0; foreach ($files as $f) if (str_contains((string)@file_get_contents($f), 'admin|')) $adm++;
echo 'tiem ', setting('salon_name'), ' · ', SITE_ID, ' · ', APP_VERSION, "\n";
echo 'key app: ', json_encode($c), ' · thiet bi tin cay: ', count(td_list()), ' · phien: ', count($files), ' (chu tiem ', $adm, ') · quan ly: ', q('SELECT COUNT(*) FROM managers WHERE active = 1')->fetchColumn(), ' · tho co PIN: ', q("SELECT COUNT(*) FROM staff WHERE active = 1 AND pin_hash <> ''")->fetchColumn(), "\n";
if (!$GO) { echo "chi dem - chay lai voi: go\n"; exit; }
set_setting('admin_pw_ver', (string)((int)setting('admin_pw_ver') + 1)); td_save([]); app_toks_save([]);
q('UPDATE managers SET pin_ver = pin_ver + 1'); q('UPDATE staff SET pin_ver = pin_ver + 1');
$n = 0; foreach ($files as $f) if (@unlink($f)) $n++;
audit('pw_change', 'All devices', '', 'Logged out everywhere by NailFlow (owner, managers, techs) - passwords / PINs unchanged');
echo "XONG: xoa $n phien, key app 0, thiet bi tin cay 0, quan ly + tho phai dang nhap lai (PIN cu)\n";
