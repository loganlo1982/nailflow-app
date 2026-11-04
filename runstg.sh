#!/bin/bash
# CHAT 03/11: staging UI preview (anh Logan 22:34/22:36) – https://nailflowapp.com/ui-preview/admin/  – FAKE data only, own code copy + own SQLite.
# Khong dung AN / Love Nails / demo / showapp / hair. Code = copy LIVE release 2.99.353 + fix640ui (CSS). Mat khau owner = hash cua showapp (khong ai go mat khau).
set -e
SRC=/home/uyurpyzubx0m/app/releases/2.99.353; DST=/home/nailflow/public_html/ui-preview; DATA=/home/nailflow/ui-preview-data; H=/tmp/h555s
[ -e "$DST" ] && { echo "DST EXISTS – STOP"; exit 1; }
[ -e "$DATA" ] && { echo "DATA EXISTS – STOP"; exit 1; }
SHOWDB=$(php -r '$c = require "/home/uyurpyzubx0m/app/sites/showapp/config.php"; echo $c["sqlite_path"] ?? "";')
[ -f "$SHOWDB" ] || { echo "no showapp db – STOP"; exit 1; }
mkdir -p "$DATA"; cp -a "$SRC" "$DST"; rm -f "$DST/inc/config.php"
python3 $H/fix640ui.py "$DST" go
cp $H/stg640.sqlite "$DATA/db.sqlite"
php -r '$s = new PDO("sqlite:" . $argv[1]); $h = $s->query("SELECT v FROM settings WHERE k = \"admin_hash\"")->fetchColumn(); if (!$h || strlen($h) < 50) { fwrite(STDERR, "no hash\n"); exit(1); }
 $d = new PDO("sqlite:" . $argv[2]); $u = $d->prepare("UPDATE settings SET v = ? WHERE k = \"admin_hash\""); $u->execute([$h]); echo "hash rows ", $u->rowCount(), "\n";' "$SHOWDB" "$DATA/db.sqlite"
cat > "$DST/inc/config.php" <<PHP
<?php
// staging UI preview (CHAT 03/11) – fake data, demo mode (nothing deleted, no messages sent)
return array('driver' => 'sqlite', 'sqlite_path' => '$DATA/db.sqlite', 'site_url' => 'https://nailflowapp.com/ui-preview', 'demo' => true, 'showapp' => true, 'noindex' => true);
PHP
chown -R nailflow:nailflow "$DST" "$DATA"; chmod 700 "$DATA"; chmod 600 "$DATA/db.sqlite" "$DST/inc/config.php"
find "$DST" -type l | head -3
for u in admin/ api.php?action=me assets/admin-popups.css inc/config.php; do curl -s -o /dev/null -w "$u %{http_code}\n" "https://nailflowapp.com/ui-preview/$u"; done
grep -c "2.99.640ui" "$DST/assets/admin-popups.css"
echo STG-DONE
