#!/bin/bash
# Undo deploy-668.sh: bash rollback-668.sh /root/backup/pre-668-<time>   (the 3 sites back to 2.99.667, the hair files back, php-fpm reload)
set -euo pipefail
BK="${1:?backup folder}"; A=/home/uyurpyzubx0m/app; HD=/home/nailflow/demo.hair.nailflowapp.com
[ -f "$BK/hair-files.tgz" ] || { echo "no backup in $BK"; exit 1; }
for s in an lovenails showapp; do ln -sfn ../../releases/2.99.667 "$A/sites/$s/current.new" && mv -T "$A/sites/$s/current.new" "$A/sites/$s/current"; chown -h uyurpyzubx0m:uyurpyzubx0m "$A/sites/$s/current"; done
T=$(mktemp -d); tar xzf "$BK/hair-files.tgz" -C "$T"; for f in $(cat "$BK/FILES.txt"); do cat "$T/$f" > "$HD/$f"; done; rm -rf "$T"
/scripts/restartsrv_apache_php_fpm --graceful >/dev/null 2>&1; echo "ROLLBACK668-OK"
