<?php
/* CHAT 630 – demo.hair "Luxe Hair Studio": gan anh AI (nguoi GIA) cho 5 tho demo. CHI demo toc.
   Anh nguon: /home/nailflow/hair-data/demo-photos/<ten>.jpg (ashley, brianna, carlos, danielle, emily).
   Lam giong nut Staff -> Photo cua app: anh vuong 256 px -> uploads/staff/<20 hex>.jpg, staff.photo; ban nho cho khach app tu tao (staff_pub_url).
   seed628 khong dung cot photo -> reset demo moi dem van giu anh.
   php set630.php <app dir>        -> chi kiem
   php set630.php <app dir> go     -> lam that */
declare(strict_types=1);
if (PHP_SAPI !== 'cli') { http_response_code(404); exit; }
$R = rtrim((string)($argv[1] ?? ''), '/'); $GO = ($argv[2] ?? '') === 'go'; $SRC = '/home/nailflow/hair-data/demo-photos';
if ($R === '' || !is_file("$R/inc/core.php") || !is_file("$R/inc/hair.php")) { fwrite(STDERR, "usage: php set630.php <hair app dir> [go]\n"); exit(2); }
chdir($R); require "$R/inc/core.php"; settings();
$name0 = (string)setting('salon_name');
if (!in_array(strtoupper($name0), ['HAIR SALON DEMO', 'LUXE HAIR STUDIO'], true)) { fwrite(STDERR, "DUNG: tiem '$name0' khong phai demo toc\n"); exit(2); }
if (!function_exists('imagecreatefromjpeg')) { fwrite(STDERR, "DUNG: khong co GD\n"); exit(2); }
echo "set630 · $R · " . APP_VERSION . " · tiem '$name0' · " . ($GO ? 'GO' : 'chi kiem') . "\n";
foreach (['ASHLEY', 'BRIANNA', 'CARLOS', 'DANIELLE', 'EMILY'] as $n) {
    $s = q('SELECT id, photo FROM staff WHERE UPPER(name) = ? AND active = 1', [$n])->fetch();
    $f = $SRC . '/' . strtolower($n) . '.jpg';
    if (!$s) { echo "  $n: KHONG co tho\n"; continue; }
    if (!is_file($f) || !($im = @imagecreatefromjpeg($f))) { echo "  $n: KHONG doc duoc $f\n"; continue; }
    echo "  $n id {$s['id']} · anh cu '" . $s['photo'] . "' · nguon " . imagesx($im) . "px\n";
    if (!$GO) continue;
    $o = imagecreatetruecolor(256, 256); imagecopyresampled($o, $im, 0, 0, 0, 0, 256, 256, imagesx($im), imagesy($im));
    ob_start(); imagejpeg($o, null, 85); $bytes = (string)ob_get_clean();
    $dir = staff_dir(); $nm = bin2hex(random_bytes(10)); $new = "uploads/staff/$nm.jpg";
    if (@file_put_contents("$dir/$nm.jpg", $bytes) === false) { echo "  $n: LOI ghi file\n"; continue; }
    $old = staff_photo_url((string)$s['photo']);
    q('UPDATE staff SET photo = ? WHERE id = ?', [$new, (int)$s['id']]);
    if ($old !== '' && is_file(SITE_ROOT . '/' . $old)) @unlink(SITE_ROOT . '/' . $old);
    staff_pub_drop((int)$s['id']); staff_pub_save((int)$s['id'], ['on' => 1]);
    $pub = staff_pub_url(['id' => (int)$s['id'], 'photo' => $new]);
    echo "    -> $new (" . strlen($bytes) . " B) · khach: $pub\n";
}
echo "XONG\n";
