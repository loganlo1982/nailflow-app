#!/bin/bash
# 2.99.645 – Payroc Cloud into the LIVE release, OFF (setting pr_on stays '0' – nothing changes at Checkout until NailFlow turns it on).
# Anh Logan 04/11 23:52: "Nen dua vao ban chinh ... tat, khi ho chap nhan thi bat len".
# Usage: bash deploy-645-live.sh <git sha>      (dry-run: DRY=1 bash deploy-645-live.sh <sha>)
# Steps: download every file at the sha + check md5 against MD5S-645 -> prove the live base is the expected one
# (changes-to-existing-files.diff applied to a copy of the live files gives exactly the new files) -> backup -> install -> php -l.
set -euo pipefail
S="${1:?git sha}"; B="https://raw.githubusercontent.com/loganlo1982/nailflow-app/$S/payroc-645a"
H=/home/uyurpyzubx0m; R=$H/app/releases/2.99.353; ANAPI=$H/public_html/api.php; LNAPI=$H/lovenails/api.php
PHP=/usr/local/bin/php; T=/root/dep645; TS=$(date +%m%d%H%M); BK=/root/backup/pre-645-$TS
NEW="inc/payroc.php inc/payroc-pay.php inc/api/payroc.php inc/api/prpay.php assets/admin/payroc-hq.js"
MOD="api.php assets/admin-core.js assets/admin/checkout-2b.js assets/admin/checkout-2d.js assets/admin/checkout-receipt.js inc/api/checkout.php inc/checkout-edit.php inc/checkout.php inc/support.php"
ROUTES="/* (2.99.645a - LENH PAYROC) Payroc Cloud: HQ box + sandbox tests (NailFlow only), Checkout card */ 'pr_info' => 'payroc', 'pr_save' => 'payroc', 'pr_check' => 'payroc', 'pr_test' => 'payroc', 'pr_tests_csv' => 'payroc', 'pr_charge' => 'prpay', 'pr_stop' => 'prpay', 'pr_cancel' => 'prpay', 'pr_waiting' => 'prpay', "
die() { echo "STOP: $*"; exit 1; }

rm -rf "$T"; mkdir -p "$T/new" "$T/base"
curl -fsS -o "$T/MD5S-645" "$B/MD5S-645"; curl -fsS -o "$T/changes.diff" "$B/changes-to-existing-files.diff"
for f in $NEW $MOD; do mkdir -p "$(dirname "$T/new/$f")"; curl -fsS -o "$T/new/$f" "$B/release/$f"; done
(cd "$T/new" && md5sum -c --quiet "$T/MD5S-645") || die "downloaded files do not match MD5S-645"

# the live base must be the expected one (nobody changed these files since the sandbox copy)
for f in $NEW; do [ ! -e "$R/$f" ] || die "$R/$f already exists"; done
for f in $MOD; do mkdir -p "$(dirname "$T/base/$f")"; cp -p "$R/$f" "$T/base/$f"; done
patch -s -p1 -d "$T/base" < "$T/changes.diff" || die "the diff does not apply to the live files"
for f in $MOD; do cmp -s "$T/base/$f" "$T/new/$f" || die "live $f + diff != new $f"; done
grep -q "define('APP_VERSION', '2.99.637');" "$R/inc/core.php" || die "APP_VERSION is not 2.99.637"
for a in "$ANAPI" "$LNAPI"; do
  [ "$(grep -c "'ttp_result' => 'dvpay', " "$a")" = 1 ] || die "anchor not found once in $a"
  ! grep -q "'pr_info'" "$a" || die "$a already has pr_info"
done
echo "PRECHECK OK"
[ -z "${DRY:-}" ] || { echo "DRY RUN – nothing changed"; exit 0; }

# backup (whole files + paths)
mkdir -p "$BK"; (cd "$R" && tar czf "$BK/release-files.tgz" $MOD inc/core.php); cp -p "$ANAPI" "$BK/public_html-api.php"; cp -p "$LNAPI" "$BK/lovenails-api.php"
printf '%s\n' "$NEW" > "$BK/NEW-FILES.txt"; echo "backup: $BK"

# install
for f in $MOD; do cat "$T/new/$f" > "$R/$f"; done
for f in $NEW; do install -o uyurpyzubx0m -g uyurpyzubx0m -m 644 "$T/new/$f" "$R/$f"; done
for a in "$ANAPI" "$LNAPI"; do
  A="$a" RT="$ROUTES" $PHP -r '$f=getenv("A"); $s=file_get_contents($f); $k="'"'"'ttp_result'"'"' => '"'"'dvpay'"'"', "; $n=substr_count($s,$k); if($n!==1){fwrite(STDERR,"anchor $n\n"); exit(1);} file_put_contents($f, str_replace($k, $k.getenv("RT"), $s));' || die "route insert failed for $a"
done
sed -i "s/define('APP_VERSION', '2.99.637');/define('APP_VERSION', '2.99.645');/" "$R/inc/core.php"

# check
for f in $NEW $MOD inc/core.php; do case "$f" in *.php) $PHP -l "$R/$f" >/dev/null || die "php -l $f";; esac; done
$PHP -l "$ANAPI" >/dev/null && $PHP -l "$LNAPI" >/dev/null || die "php -l site api.php"
(cd "$R" && md5sum -c --quiet "$T/MD5S-645") || die "installed files differ from MD5S-645"
grep -c "'pr_info' => 'payroc'" "$ANAPI" "$LNAPI"
grep -h "define('APP_VERSION'" "$R/inc/core.php"
rm -rf "$T"
echo "DEPLOY645-OK  (rollback: bash rollback-645.sh $BK)"
