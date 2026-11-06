#!/bin/bash
# 2.99.656 = live booking: everything in ONE call = one booking ("add another person" on the same call; real call #190). A NEW release = live 2.99.655 + r656.diff.
# switch to it (+ php-fpm reload). The hair demo (own copy, nailflow account) gets the same files patched in place (backup first).
# demo (Apple review) stays on 2.99.353. Usage: DIFF_MD5=<md5> bash deploy-656.sh <sha> [DRY=1]     Rollback: bash rollback-656.sh <backup dir>
set -euo pipefail
S="${1:?sha}"; B="https://raw.githubusercontent.com/loganlo1982/nailflow-app/$S/r646"
H=/home/uyurpyzubx0m; A=$H/app; OLD=$A/releases/2.99.655; NEW=$A/releases/2.99.656; T=/root/dep656; PHP=/usr/local/bin/php
HD=/home/nailflow/demo.hair.nailflowapp.com; SITES="an lovenails showapp"
die() { echo "STOP: $*"; exit 1; }
rm -rf "$T"; mkdir -p "$T"
curl -fsS -o "$T/r656.diff" "$B/r656.diff"; curl -fsS -o "$T/MD5S-656" "$B/MD5S-656"
[ "$(md5sum < "$T/r656.diff" | cut -c1-32)" = "${DIFF_MD5:?DIFF_MD5}" ] || die "diff md5"
for s in $SITES; do [ "$(readlink "$A/sites/$s/current")" = "../../releases/2.99.655" ] || die "$s is not on 2.99.655"; done
[ "$(readlink "$A/sites/demo/current")" = "../../releases/2.99.353" ] || die "demo moved"
FILES=$(awk '{print $2}' "$T/MD5S-656")
rm -rf "$T/rel"; cp -a "$OLD" "$T/rel"; rm -f "$T/rel/error_log"
patch -s -p1 -d "$T/rel" < "$T/r656.diff" || die "the diff does not apply to 2.99.655"
find "$T/rel" -name '*.orig' -o -name '*.rej' | grep -q . && die "patch left .orig/.rej"
(cd "$T/rel" && md5sum -c --quiet "$T/MD5S-656") || die "files differ from the tested copy"
for f in $FILES; do case "$f" in *.php) $PHP -l "$T/rel/$f" >/dev/null || die "php -l $f";; esac; done
# the hair copy: the files must be the 2.99.655 ones before patching
mkdir -p "$T/hair"; for f in $FILES; do mkdir -p "$(dirname "$T/hair/$f")"; if [ ! -e "$OLD/$f" ]; then [ ! -e "$HD/$f" ] || die "hair $f exists already"; continue; fi; cp -p "$HD/$f" "$T/hair/$f"; cmp -s "$HD/$f" "$OLD/$f" || die "hair $f is not the 2.99.655 file"; done  # (654) a NEW file (inc/calls-live.php) is made by the patch
patch -s -p1 -d "$T/hair" < "$T/r656.diff" || die "the diff does not apply to the hair copy"
(cd "$T/hair" && md5sum -c --quiet "$T/MD5S-656") || die "hair files differ from the tested copy"
echo "BUILD OK"
[ -z "${DRY:-}" ] || { echo "DRY RUN - nothing changed"; rm -rf "$T"; exit 0; }
[ ! -e "$NEW" ] || die "$NEW exists"
TS=$(date +%m%d%H%M); BK=/root/backup/pre-656-$TS; mkdir -p "$BK"; OLDF=$(for f in $FILES; do [ -e "$HD/$f" ] && echo "$f"; done); (cd "$HD" && tar czf "$BK/hair-files.tgz" $OLDF); printf '%s\n' $OLDF > "$BK/FILES.txt"  # (654) only the files that were there (the new one stays, unused by 2.99.655)
mv "$T/rel" "$NEW"; chown -R uyurpyzubx0m:uyurpyzubx0m "$NEW"
for s in $SITES; do ln -sfn ../../releases/2.99.656 "$A/sites/$s/current.new" && mv -T "$A/sites/$s/current.new" "$A/sites/$s/current"; chown -h uyurpyzubx0m:uyurpyzubx0m "$A/sites/$s/current"; done
for f in $FILES; do cat "$T/hair/$f" > "$HD/$f"; done
/scripts/restartsrv_apache_php_fpm --graceful >/dev/null 2>&1 || die "php-fpm reload"   # a release switch MUST reload PHP
for s in $SITES demo; do echo "$s -> $(readlink "$A/sites/$s/current")"; done; grep -h "define('APP_VERSION'" "$HD/inc/core.php"
rm -rf "$T"; echo "backup: $BK"; echo "DEPLOY656-OK"
