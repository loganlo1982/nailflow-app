#!/bin/bash
# Undo deploy-645-live.sh: bash rollback-645.sh /root/backup/pre-645-<time>
set -euo pipefail
BK="${1:?backup folder}"; H=/home/uyurpyzubx0m; R=$H/app/releases/2.99.353; PHP=/usr/local/bin/php
[ -f "$BK/release-files.tgz" ] || { echo "no backup in $BK"; exit 1; }
T=$(mktemp -d); tar xzf "$BK/release-files.tgz" -C "$T"
(cd "$T" && find . -type f) | while read -r f; do cat "$T/$f" > "$R/$f"; done
cat "$BK/public_html-api.php" > "$H/public_html/api.php"; cat "$BK/lovenails-api.php" > "$H/lovenails/api.php"
for f in $(cat "$BK/NEW-FILES.txt"); do rm -f "$R/$f"; done
rm -rf "$T"; $PHP -l "$R/inc/core.php" >/dev/null && $PHP -l "$H/public_html/api.php" >/dev/null && echo "ROLLBACK645-OK"
