#!/bin/bash
# 2.99.646 (LENH 646, anh Logan 05/11): a NEW release folder = live 2.99.353 + r646.diff, then an, lovenails, showapp switch to it.
# demo (Apple review) stays on 2.99.353. Rollback = bash rollback-646.sh (switches the 3 back).
# Usage: bash deploy-646.sh <sha> [DRY=1]
set -euo pipefail
S="${1:?sha}"; B="https://raw.githubusercontent.com/loganlo1982/nailflow-app/$S/r646"
H=/home/uyurpyzubx0m; A=$H/app; OLD=$A/releases/2.99.353; NEW=$A/releases/2.99.646; T=/root/dep646; PHP=/usr/local/bin/php
SITES="an lovenails showapp"; ANAPI=$H/public_html/api.php; LNAPI=$H/lovenails/api.php
HR="/* (2.99.646 - LENH 646 hair) hair salon only (404 for a nail salon) */ 'hair_get' => 'hair', 'hair_save' => 'hair', 'hair_menu' => 'hair', 'ios_in' => 'hair', "
die() { echo "STOP: $*"; exit 1; }
rm -rf "$T"; mkdir -p "$T"
curl -fsS -o "$T/r646.diff" "$B/r646.diff"; curl -fsS -o "$T/MD5S-646" "$B/MD5S-646"
[ "$(md5sum < "$T/r646.diff" | cut -c1-32)" = "${DIFF_MD5:?DIFF_MD5}" ] || die "diff md5"
for s in $SITES demo; do [ "$(readlink "$A/sites/$s/current")" = "../../releases/2.99.353" ] || die "$s is not on 2.99.353"; done
grep -q "define('APP_VERSION', '2.99.645');" "$OLD/inc/core.php" || die "live is not 2.99.645"
# build the new release in a temp folder, check it, then move it in place
rm -rf "$T/rel"; cp -a "$OLD" "$T/rel"; rm -f "$T/rel/error_log"
patch -s -p1 -d "$T/rel" < "$T/r646.diff" || die "the diff does not apply"
find "$T/rel" -name '*.orig' -o -name '*.rej' | grep -q . && die "patch left .orig/.rej"
(cd "$T/rel" && md5sum -c --quiet "$T/MD5S-646") || die "files differ from the tested copy"
for f in $(cd "$T/rel" && awk '{print $2}' "$T/MD5S-646"); do case "$f" in *.php) $PHP -l "$T/rel/$f" >/dev/null || die "php -l $f";; esac; done
for a in "$ANAPI" "$LNAPI"; do [ "$(grep -c "'pr_waiting' => 'prpay', " "$a")" = 1 ] || die "anchor in $a"; ! grep -q "'hair_get'" "$a" || die "$a has hair_get"; done
echo "BUILD OK"
[ -z "${DRY:-}" ] || { echo "DRY RUN - nothing changed"; rm -rf "$T"; exit 0; }
[ ! -e "$NEW" ] || die "$NEW exists"
mv "$T/rel" "$NEW"; chown -R uyurpyzubx0m:uyurpyzubx0m "$NEW"
TS=$(date +%m%d%H%M); BK=/root/backup/pre-646-$TS; mkdir -p "$BK"; cp -p "$ANAPI" "$BK/public_html-api.php"; cp -p "$LNAPI" "$BK/lovenails-api.php"
for a in "$ANAPI" "$LNAPI"; do A2="$a" RT="$HR" $PHP -r '$f=getenv("A2"); $s=file_get_contents($f); $k="'"'"'pr_waiting'"'"' => '"'"'prpay'"'"', "; if(substr_count($s,$k)!==1) exit(1); file_put_contents($f, str_replace($k, $k.getenv("RT"), $s));' || die "route insert $a"; $PHP -l "$a" >/dev/null || die "php -l $a"; done
for s in $SITES; do ln -sfn ../../releases/2.99.646 "$A/sites/$s/current.new" && mv -T "$A/sites/$s/current.new" "$A/sites/$s/current"; chown -h uyurpyzubx0m:uyurpyzubx0m "$A/sites/$s/current"; done
/scripts/restartsrv_apache_php_fpm --graceful >/dev/null 2>&1 || die "php-fpm reload";  # a release switch MUST reload PHP (05/11: its realpath cache mixed 2.99.353 and 2.99.646 files -> 500)
for s in $SITES demo; do echo "$s -> $(readlink "$A/sites/$s/current")"; done
rm -rf "$T"; echo "backup: $BK"; echo "DEPLOY646-OK"
