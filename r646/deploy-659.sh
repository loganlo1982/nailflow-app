#!/bin/bash
# 2.99.659 = 2.99.658 (live booking fixes #195) + phones on Telnyx only, set up only in HQ (SignalWire dropped) + iPhone voicemail sent to the AI (#198).
# A NEW release = live 2.99.657 + r659.diff. New top-level file tx_hq.php goes next to call_tx.php in every salon web folder (same kind: link or own copy).
# switch to it (+ php-fpm reload). The hair demo (own copy, nailflow account) gets the same files patched in place (backup first).
# demo (Apple review) stays on 2.99.353. Usage: DIFF_MD5=<md5> bash deploy-659.sh <sha> [DRY=1]     Rollback: bash rollback-659.sh <backup dir>
set -euo pipefail
S="${1:?sha}"; B="https://raw.githubusercontent.com/loganlo1982/nailflow-app/$S/r646"
H=/home/uyurpyzubx0m; A=$H/app; OLD=$A/releases/2.99.657; NEW=$A/releases/2.99.659; T=/root/dep659; PHP=/usr/local/bin/php
HD=/home/nailflow/demo.hair.nailflowapp.com; SITES="an lovenails showapp"
die() { echo "STOP: $*"; exit 1; }
rm -rf "$T"; mkdir -p "$T"
curl -fsS -o "$T/r659.diff" "$B/r659.diff"; curl -fsS -o "$T/MD5S-659" "$B/MD5S-659"
[ "$(md5sum < "$T/r659.diff" | cut -c1-32)" = "${DIFF_MD5:?DIFF_MD5}" ] || die "diff md5"
for s in $SITES; do [ "$(readlink "$A/sites/$s/current")" = "../../releases/2.99.657" ] || die "$s is not on 2.99.657"; done
[ "$(readlink "$A/sites/demo/current")" = "../../releases/2.99.353" ] || die "demo moved"
FILES=$(awk '{print $2}' "$T/MD5S-659")
rm -rf "$T/rel"; cp -a "$OLD" "$T/rel"; rm -f "$T/rel/error_log"
patch -s -p1 -d "$T/rel" < "$T/r659.diff" || die "the diff does not apply to 2.99.657"
find "$T/rel" -name '*.orig' -o -name '*.rej' | grep -q . && die "patch left .orig/.rej"
(cd "$T/rel" && md5sum -c --quiet "$T/MD5S-659") || die "files differ from the tested copy"
for f in $FILES; do case "$f" in *.php) $PHP -l "$T/rel/$f" >/dev/null || die "php -l $f";; esac; done
# the hair copy: the files must be the 2.99.657 ones before patching
mkdir -p "$T/hair"; for f in $FILES; do mkdir -p "$(dirname "$T/hair/$f")"; if [ ! -e "$OLD/$f" ]; then [ ! -e "$HD/$f" ] || die "hair $f exists already"; continue; fi; cp -p "$HD/$f" "$T/hair/$f"; cmp -s "$HD/$f" "$OLD/$f" || die "hair $f is not the 2.99.657 file"; done  # (654) a NEW file (inc/calls-live.php) is made by the patch
patch -s -p1 -d "$T/hair" < "$T/r659.diff" || die "the diff does not apply to the hair copy"
(cd "$T/hair" && md5sum -c --quiet "$T/MD5S-659") || die "hair files differ from the tested copy"
# the salon web folders: where call_tx.php is, tx_hq.php goes the same way (a link -> a link to the same place; an own copy -> a copy)
WEBS=$($PHP -r 'foreach ((require "'"$A"'/sites.php") as $id => $s) echo $id, " ", rtrim((string)($s["web"] ?? ""), "/"), "\n";') || die "sites.php"
[ -n "$WEBS" ] || die "no salon web folders"
echo "$WEBS"
echo "$WEBS" | while read -r id w; do [ -n "$w" ] || continue; c="$w/call_tx.php"; if [ -L "$c" ]; then echo "$id link $(readlink "$c")"; elif [ -f "$c" ]; then echo "$id copy $(md5sum < "$c" | cut -c1-8) (657 $(md5sum < "$OLD/call_tx.php" | cut -c1-8))"; else echo "$id none"; fi; done
# American Nails keeps its Telnyx number (2.99.659 has no built-in number any more)
for s in an lovenails; do $PHP -r '$c = require "'"$A"'/sites/'"$s"'/config.php"; $p = new PDO("mysql:host=" . ($c["db_host"] ?? "localhost") . ";dbname=" . $c["db_name"] . ";charset=utf8mb4", $c["db_user"], $c["db_pass"]); foreach ($p->query("SELECT k, LENGTH(v) l, IF(k IN (\"tx_number\",\"tx_on\",\"call_fwd\"), v, \"\") v FROM settings WHERE k IN (\"tx_number\",\"tx_on\",\"tx_key\",\"tx_pub\",\"call_fwd\")") as $r) echo "'"$s"' ", $r["k"], "=", $r["v"] !== "" ? $r["v"] : "(" . $r["l"] . " chars)", "\n";' || die "settings $s"; done
echo "BUILD OK"
[ -z "${DRY:-}" ] || { for f in $FILES; do if [ -e "$HD/$f" ]; then echo "$f"; fi; done >/dev/null; echo "DRY RUN - nothing changed"; rm -rf "$T"; exit 0; }
[ ! -e "$NEW" ] || die "$NEW exists"
TS=$(date +%m%d%H%M); BK=/root/backup/pre-659-$TS; mkdir -p "$BK"; OLDF=$(for f in $FILES; do if [ -e "$HD/$f" ]; then echo "$f"; fi; done); (cd "$HD" && tar czf "$BK/hair-files.tgz" $OLDF); printf '%s\n' $OLDF > "$BK/FILES.txt"  # (654) only the files that were there (the new one stays, unused by 2.99.657)
mv "$T/rel" "$NEW"; chown -R uyurpyzubx0m:uyurpyzubx0m "$NEW"
AN_N=$($PHP -r '$c = require "'"$A"'/sites/an/config.php"; $p = new PDO("mysql:host=" . ($c["db_host"] ?? "localhost") . ";dbname=" . $c["db_name"] . ";charset=utf8mb4", $c["db_user"], $c["db_pass"]); echo (string)$p->query("SELECT v FROM settings WHERE k = \"tx_number\"")->fetchColumn();')
[ -n "$AN_N" ] || $PHP -r '$c = require "'"$A"'/sites/an/config.php"; $p = new PDO("mysql:host=" . ($c["db_host"] ?? "localhost") . ";dbname=" . $c["db_name"] . ";charset=utf8mb4", $c["db_user"], $c["db_pass"]); $p->prepare("INSERT INTO settings (k, v) VALUES (\"tx_number\", ?) ON DUPLICATE KEY UPDATE v = VALUES(v)")->execute(["+15155136667"]); echo "AN tx_number saved\n";'
echo "$WEBS" | while read -r id w; do [ -n "$w" ] || continue; c="$w/call_tx.php"; [ ! -e "$w/tx_hq.php" ] || continue
  if [ -L "$c" ]; then ln -s "$(dirname "$(readlink "$c")")/tx_hq.php" "$w/tx_hq.php"; chown -h --reference="$c" "$w/tx_hq.php"
  elif [ -f "$c" ]; then cp "$NEW/tx_hq.php" "$w/tx_hq.php"; chown --reference="$c" "$w/tx_hq.php"; chmod 644 "$w/tx_hq.php"; echo "$w/tx_hq.php" >> "$BK/NEWFILES.txt"; fi; done
for s in $SITES; do ln -sfn ../../releases/2.99.659 "$A/sites/$s/current.new" && mv -T "$A/sites/$s/current.new" "$A/sites/$s/current"; chown -h uyurpyzubx0m:uyurpyzubx0m "$A/sites/$s/current"; done
for f in $FILES; do cat "$T/hair/$f" > "$HD/$f"; done
/scripts/restartsrv_apache_php_fpm --graceful >/dev/null 2>&1 || die "php-fpm reload"   # a release switch MUST reload PHP
for s in $SITES demo; do echo "$s -> $(readlink "$A/sites/$s/current")"; done; grep -h "define('APP_VERSION'" "$HD/inc/core.php"
rm -rf "$T"; echo "backup: $BK"; echo "DEPLOY659-OK"
