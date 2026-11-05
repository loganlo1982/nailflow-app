#!/bin/bash
# 2.99.646 hair: demo.hair.nailflowapp.com runs the SAME code as nails (release 2.99.646), as a hair salon (config 'salon_type' => 'hair').
# Kept: its config, its database (/home/nailflow/hair-data), uploads, .htaccess, error_log. TEST=1: a full copy on 127.0.0.1:18646 first (real data copy, nothing live).
set -euo pipefail
HD=/home/nailflow/demo.hair.nailflowapp.com; REL=/home/uyurpyzubx0m/app/releases/2.99.646; PHP=/usr/local/bin/php; TS=$(date +%m%d%H%M)
die() { echo "STOP: $*"; exit 1; }
[ -f "$REL/inc/core.php" ] && grep -q "2.99.646" "$REL/inc/core.php" || die "release 2.99.646 missing"
DB=$($PHP -r '$c = require "/home/nailflow/demo.hair.nailflowapp.com/inc/config.php"; echo $c["sqlite_path"] ?? "";'); [ -f "$DB" ] || die "hair db"
EX=(--exclude=/inc/config.php --exclude=/uploads --exclude=/data --exclude=/.htaccess --exclude=error_log --exclude=/tests646 --exclude=/cgi-bin)
addtype() { grep -q "'salon_type'" "$1" || sed -i "0,/return array(/s//return array('salon_type' => 'hair', /" "$1"; grep -q "'salon_type' => 'hair'" "$1" || die "salon_type not set in $1"; $PHP -l "$1" >/dev/null; }
if [ -n "${TEST:-}" ]; then
  T=/root/hairtest; rm -rf $T; mkdir -p $T/data; cp -a "$HD" $T/web; cp "$DB" $T/data/hair.sqlite
  rsync -a "${EX[@]}" "$REL/" $T/web/
  sed -i "s#$DB#$T/data/hair.sqlite#" $T/web/inc/config.php; addtype $T/web/inc/config.php
  cd $T/web && (timeout 60 $PHP -S 127.0.0.1:18646 >/dev/null 2>$T/srv.log &) ; sleep 1.5
  for u in "/" "/admin/" "/api.php?action=info" "/checkin/" "/tech/" "/manage.php" "/gift.php"; do echo "$(curl -s -o $T/out.txt -w '%{http_code}' "http://127.0.0.1:18646$u") $u $(head -c 80 $T/out.txt | tr -d '\n')"; done
  $PHP -r 'chdir("/root/hairtest/web"); require "inc/core.php"; settings(); echo "is_hair=", is_hair() ? "yes" : "no", " show_price=", setting("book_show_price"), " turn_auto=", (function_exists("ta_on") ? (ta_on() ? "on" : "off") : "?"), "\n";' 2>&1 | head -3 || true
  grep -ci "fatal\|warning" $T/srv.log || true; tail -3 $T/srv.log
  pkill -f "127.0.0.1:18646" || true; rm -rf $T; echo "HAIR TEST DONE"; exit 0
fi
BK=/root/backup/hair-pre-646-$TS.tgz; tar czf "$BK" -C /home/nailflow demo.hair.nailflowapp.com hair-data; echo "backup: $BK"
rsync -a --chown=nailflow:nailflow "${EX[@]}" "$REL/" "$HD/"
addtype "$HD/inc/config.php"
echo "HAIR646-OK (rollback: rm then tar xzf $BK -C /home/nailflow)"
