#!/bin/bash
# 2.99.668 = owner declines (carrier answers his leg) -> the caller to the AI; text booking: newest text wins, no duplicate texts, one salon name, people count, add a person by text.
# A NEW release = live 2.99.667 + r668.diff (no new files).
# switch to it (+ php-fpm reload). The hair demo (own copy, nailflow account) gets the same files patched in place (backup first).
# demo (Apple review) stays on 2.99.353. Usage: DIFF_MD5=<md5> bash deploy-668.sh <sha> [DRY=1]     Rollback: bash rollback-668.sh <backup dir>
set -euo pipefail
S="${1:?sha}"; B="https://raw.githubusercontent.com/loganlo1982/nailflow-app/$S/r646"
H=/home/uyurpyzubx0m; A=$H/app; OLD=$A/releases/2.99.667; NEW=$A/releases/2.99.668; T=/root/dep668; PHP=/usr/local/bin/php
HD=/home/nailflow/demo.hair.nailflowapp.com; SITES="an lovenails showapp"
die() { echo "STOP: $*"; exit 1; }
rm -rf "$T"; mkdir -p "$T"
curl -fsS -o "$T/r668.diff" "$B/r668.diff"; curl -fsS -o "$T/MD5S-668" "$B/MD5S-668"
[ "$(md5sum < "$T/r668.diff" | cut -c1-32)" = "${DIFF_MD5:?DIFF_MD5}" ] || die "diff md5"
for s in $SITES; do [ "$(readlink "$A/sites/$s/current")" = "../../releases/2.99.667" ] || die "$s is not on 2.99.667"; done
[ "$(readlink "$A/sites/demo/current")" = "../../releases/2.99.353" ] || die "demo moved"
FILES=$(awk '{print $2}' "$T/MD5S-668")
rm -rf "$T/rel"; cp -a "$OLD" "$T/rel"; rm -f "$T/rel/error_log"
patch -s -p1 -d "$T/rel" < "$T/r668.diff" || die "the diff does not apply to 2.99.667"
find "$T/rel" -name '*.orig' -o -name '*.rej' | grep -q . && die "patch left .orig/.rej"
(cd "$T/rel" && md5sum -c --quiet "$T/MD5S-668") || die "files differ from the tested copy"
for f in $FILES; do case "$f" in *.php) $PHP -l "$T/rel/$f" >/dev/null || die "php -l $f";; esac; done
# the hair copy: the files must be the 2.99.667 ones before patching; NEW files (not in 2.99.667) must not be there yet and are made by the patch
mkdir -p "$T/hair"; for f in $FILES; do mkdir -p "$(dirname "$T/hair/$f")"; if [ ! -e "$OLD/$f" ]; then if [ -e "$HD/$f" ]; then die "hair $f exists already"; fi; continue; fi; cp -p "$HD/$f" "$T/hair/$f"; cmp -s "$HD/$f" "$OLD/$f" || die "hair $f is not the 2.99.667 file"; done
patch -s -p1 -d "$T/hair" < "$T/r668.diff" || die "the diff does not apply to the hair copy"
find "$T/hair" -name '*.orig' -o -name '*.rej' | grep -q . && die "hair patch left .orig/.rej"
(cd "$T/hair" && md5sum -c --quiet "$T/MD5S-668") || die "hair files differ from the tested copy"
echo "BUILD OK"
[ -z "${DRY:-}" ] || { echo "DRY RUN - nothing changed"; rm -rf "$T"; exit 0; }
[ ! -e "$NEW" ] || die "$NEW exists"
TS=$(date +%m%d%H%M); BK=/root/backup/pre-668-$TS; mkdir -p "$BK"; OLDF=$(for f in $FILES; do if [ -e "$HD/$f" ]; then echo "$f"; fi; done); (cd "$HD" && tar czf "$BK/hair-files.tgz" $OLDF); printf '%s\n' $OLDF > "$BK/FILES.txt"  # only the files that were there (the new ones stay, unused by 2.99.667)
NEWF=$(for f in $FILES; do if [ ! -e "$HD/$f" ]; then echo "$f"; fi; done); printf '%s\n' $NEWF > "$BK/NEWFILES.txt"
mv "$T/rel" "$NEW"; chown -R uyurpyzubx0m:uyurpyzubx0m "$NEW"
for s in $SITES; do ln -sfn ../../releases/2.99.668 "$A/sites/$s/current.new" && mv -T "$A/sites/$s/current.new" "$A/sites/$s/current"; chown -h uyurpyzubx0m:uyurpyzubx0m "$A/sites/$s/current"; done
for f in $FILES; do mkdir -p "$(dirname "$HD/$f")"; cat "$T/hair/$f" > "$HD/$f"; done
for f in $NEWF; do chown --reference="$HD/inc/core.php" "$HD/$f"; chmod 644 "$HD/$f"; done   # new hair files: same owner as the rest, not root
/scripts/restartsrv_apache_php_fpm --graceful >/dev/null 2>&1 || die "php-fpm reload"   # a release switch MUST reload PHP
for s in $SITES demo; do echo "$s -> $(readlink "$A/sites/$s/current")"; done; grep -h "define('APP_VERSION'" "$HD/inc/core.php"
rm -rf "$T"; echo "backup: $BK"; echo "DEPLOY668-OK"
