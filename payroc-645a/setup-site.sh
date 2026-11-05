#!/bin/bash
# Payroc SANDBOX test site – separate app root, separate data, separate web folder. Does NOT touch app/, sites.php, AN, LN, demo or showapp.
set -e
U=uyurpyzubx0m; H=/home/$U; R=$H/app-payroc; V=$R/releases/2.99.353-pr; W=$H/payrocsandbox
G=https://raw.githubusercontent.com/loganlo1982/nailflow-app/0e623a6363c04931a22f34436d3edd9ba83ba910/payroc-645a
[ -e $R ] && { echo "app-payroc exists - stop"; exit 1; }
mkdir -p $R/releases $R/sites/payroc/data $R/sites/payroc/sessions
cp -a $H/app/releases/2.99.353 $V
cd $V
curl -sf -o /tmp/pr645.diff $G/changes-to-existing-files.diff
patch -p1 --dry-run < /tmp/pr645.diff > /tmp/pr645-dry.txt || { cat /tmp/pr645-dry.txt; echo "PATCH DOES NOT FIT - stop"; rm -rf $R; exit 1; }
patch -p1 < /tmp/pr645.diff; rm -f /tmp/pr645.diff /tmp/pr645-dry.txt
for f in inc/payroc.php inc/payroc-pay.php inc/api/payroc.php inc/api/prpay.php assets/admin/payroc-hq.js; do curl -sf -o $f $G/release/$f; done
for f in api.php inc/checkout.php inc/api/checkout.php inc/checkout-edit.php inc/support.php inc/payroc.php inc/payroc-pay.php inc/api/payroc.php inc/api/prpay.php; do php -l $f | grep -v "^No syntax" || true; done
cat > $R/sites.php <<'P'
<?php
// Payroc SANDBOX test site only (anh Logan 04/11/2026). Separate from the live app/sites.php.
return ['payroc' => ['hosts' => ['payrocsandbox.american-nails-and-spa.com'], 'web' => '/home/uyurpyzubx0m/payrocsandbox', 'cron' => [], 'main' => true]];
P
cat > $R/sites/payroc/config.php <<'P'
<?php
// Payroc SANDBOX test site – FAKE data (copy of the Show salon), sandbox payments only, no real texts.
return array('driver' => 'sqlite', 'sqlite_path' => '/home/uyurpyzubx0m/app-payroc/sites/payroc/data/payroc.sqlite', 'site_url' => 'https://payrocsandbox.american-nails-and-spa.com', 'demo' => true, 'noindex' => true);
P
cp $H/app/sites/showapp/data/showapp.sqlite $R/sites/payroc/data/payroc.sqlite
ln -s ../../releases/2.99.353-pr $R/sites/payroc/current
mkdir -p $W/uploads
for l in $(find $H/showapp -maxdepth 1 -type l); do n=$(basename $l); t=$(readlink $l); ln -sfn "${t/\/app\/sites\/showapp\//\/app-payroc\/sites\/payroc\/}" $W/$n; done
for f in $(find $H/showapp -maxdepth 1 -type f); do cp -p $f $W/; done
chown -R $U:$U $R $W; chmod 700 $R/sites/payroc/data $R/sites/payroc/sessions; chmod 600 $R/sites/payroc/config.php
uapi --user=$U SubDomain addsubdomain domain=payrocsandbox rootdomain=american-nails-and-spa.com dir=payrocsandbox | grep -E "status|errors" | head -3
echo "links: $(find $W -maxdepth 1 -type l | wc -l) · release $(grep -o "APP_VERSION', '[^']*" $V/inc/core.php)"
curl -s -o /dev/null -w "local HTTP %{http_code}\n" --resolve payrocsandbox.american-nails-and-spa.com:80:127.0.0.1 http://payrocsandbox.american-nails-and-spa.com/api.php?action=info
echo DONE
