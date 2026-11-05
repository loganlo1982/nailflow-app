#!/bin/bash
# 2.99.647 (LENH 647, anh Logan 05/11 02:53 "kiem tra lai het cac code"): a NEW release folder = live 2.99.646 + r647.diff, then an, lovenails, showapp
# switch to it (+ php-fpm reload). The hair demo (own copy, nailflow account) gets the same 7 files patched in place (backup first).
# demo (Apple review) stays on 2.99.353. Usage: DIFF_MD5=<md5> bash deploy-647.sh <sha> [DRY=1]     Rollback: bash rollback-647.sh <backup dir>
set -euo pipefail
S="${1:?sha}"; B="https://raw.githubusercontent.com/loganlo1982/nailflow-app/$S/r646"
H=/home/uyurpyzubx0m; A=$H/app; OLD=$A/releases/2.99.646; NEW=$A/releases/2.99.647; T=/root/dep647; PHP=/usr/local/bin/php
HD=/home/nailflow/demo.hair.nailflowapp.com; SITES="an lovenails showapp"
die() { echo "STOP: $*"; exit 1; }
rm -rf "$T"; mkdir -p "$T"
curl -fsS -o "$T/r647.diff" "$B/r647.diff"; curl -fsS -o "$T/MD5S-647" "$B/MD5S-647"
[ "$(md5sum < "$T/r647.diff" | cut -c1-32)" = "${DIFF_MD5:?DIFF_MD5}" ] || die "diff md5"
for s in $SITES; do [ "$(readlink "$A/sites/$s/current")" = "../../releases/2.99.646" ] || die "$s is not on 2.99.646"; done
[ "$(readlink "$A/sites/demo/current")" = "../../releases/2.99.353" ] || die "demo moved"
FILES=$(awk '{print $2}' "$T/MD5S-647")
rm -rf "$T/rel"; cp -a "$OLD" "$T/rel"; rm -f "$T/rel/error_log"
patch -s -p1 -d "$T/rel" < "$T/r647.diff" || die "the diff does not apply to 2.99.646"
find "$T/rel" -name '*.orig' -o -name '*.rej' | grep -q . && die "patch left .orig/.rej"
(cd "$T/rel" && md5sum -c --quiet "$T/MD5S-647") || die "files differ from the tested copy"
for f in $FILES; do case "$f" in *.php) $PHP -l "$T/rel/$f" >/dev/null || die "php -l $f";; esac; done
# the hair copy: the 7 files must be the 2.99.646 ones before patching
mkdir -p "$T/hair"; for f in $FILES; do mkdir -p "$(dirname "$T/hair/$f")"; cp -p "$HD/$f" "$T/hair/$f"; cmp -s "$HD/$f" "$OLD/$f" || die "hair $f is not the 2.99.646 file"; done
patch -s -p1 -d "$T/hair" < "$T/r647.diff" || die "the diff does not apply to the hair copy"
(cd "$T/hair" && md5sum -c --quiet "$T/MD5S-647") || die "hair files differ from the tested copy"
echo "BUILD OK"
[ -z "${DRY:-}" ] || { echo "DRY RUN - nothing changed"; rm -rf "$T"; exit 0; }
[ ! -e "$NEW" ] || die "$NEW exists"
TS=$(date +%m%d%H%M); BK=/root/backup/pre-647-$TS; mkdir -p "$BK"; (cd "$HD" && tar czf "$BK/hair-files.tgz" $FILES); printf '%s\n' $FILES > "$BK/FILES.txt"
mv "$T/rel" "$NEW"; chown -R uyurpyzubx0m:uyurpyzubx0m "$NEW"
for s in $SITES; do ln -sfn ../../releases/2.99.647 "$A/sites/$s/current.new" && mv -T "$A/sites/$s/current.new" "$A/sites/$s/current"; chown -h uyurpyzubx0m:uyurpyzubx0m "$A/sites/$s/current"; done
for f in $FILES; do cat "$T/hair/$f" > "$HD/$f"; done
/scripts/restartsrv_apache_php_fpm --graceful >/dev/null 2>&1 || die "php-fpm reload"   # a release switch MUST reload PHP
for s in $SITES demo; do echo "$s -> $(readlink "$A/sites/$s/current")"; done; grep -h "define('APP_VERSION'" "$HD/inc/core.php"
rm -rf "$T"; echo "backup: $BK"; echo "DEPLOY647-OK"
