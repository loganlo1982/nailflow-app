#!/bin/bash
# 2.99.646 (anh Logan 05/11 02:08 "gom trang toc ve chung tai khoan"): demo.hair.nailflowapp.com moves into the American Nails cPanel account
# (uyurpyzubx0m) as shared-code site 'hair' (type hair) -> same release as nails, visible in AN HQ. Domain and data stay; no DNS change.
# Steps:  bash hair-move.sh build    (new site folders + a copy of the hair DB; nothing live changes)
#         bash hair-move.sh switch   (fresh DB copy, the domain leaves 'nailflow' and joins 'uyurpyzubx0m', AutoSSL, HQ entry)
#         bash hair-move.sh back     (undo the switch: the domain back on 'nailflow' as before)
set -euo pipefail
H=/home/uyurpyzubx0m; A=$H/app; SD=$A/sites/hair; W=$H/hairweb; OLD=/home/nailflow/demo.hair.nailflowapp.com; ODB=/home/nailflow/hair-data
DOM=demo.hair.nailflowapp.com; PHP=/usr/local/bin/php; U=uyurpyzubx0m
die() { echo "STOP: $*"; exit 1; }
case "${1:-}" in
build)
  [ ! -e "$SD" ] && [ ! -e "$W" ] || die "hair site already there"
  grep -q "'hair'" $A/sites.php && die "sites.php has hair"
  mkdir -p "$SD/data" "$SD/sessions" "$SD/backups"; chmod 700 "$SD/data" "$SD/sessions" "$SD/backups"
  cp -p "$ODB/hair.sqlite" "$SD/data/hair.sqlite"; cp -a "$ODB/demo-photos" "$SD/data/" 2>/dev/null || true
  OC="$OLD/inc/config.php" NC="$SD/config.php" NDB="$SD/data/hair.sqlite" NBK="$SD/backups" $PHP -r '
    $c = require getenv("OC"); if (!is_array($c)) exit(1);
    $c["sqlite_path"] = getenv("NDB"); $c["salon_type"] = "hair"; if (isset($c["backup_dir"])) $c["backup_dir"] = getenv("NBK");
    file_put_contents(getenv("NC"), "<?php\n// (2.99.646 - anh Logan 05/11) Hair demo salon (demo.hair.nailflowapp.com) on the shared code, type hair. Moved from the nailflow account.\nreturn " . var_export($c, true) . ";\n");'
  chmod 600 "$SD/config.php"; $PHP -l "$SD/config.php" >/dev/null
  ln -s ../../releases/2.99.646 "$SD/current"
  mkdir -p "$W"
  for e in $(ls -A $H/showapp); do
    if [ -L "$H/showapp/$e" ]; then t=$(readlink "$H/showapp/$e"); ln -s "${t/\/sites\/showapp\//\/sites\/hair\/}" "$W/$e"; fi
  done
  [ -e "$W/api.php" ] || ln -s "$SD/current/api.php" "$W/api.php"
  for f in book-sw.js chg.php nf-maintenance.html robots.txt sms-gw.php .htaccess; do [ -e "$W/$f" ] || cp -p "$H/showapp/$f" "$W/$f"; done
  cp -a "$OLD/uploads" "$W/uploads"; mkdir -p "$W/.well-known"
  grep -n "showapp" "$W/.htaccess" && echo "NOTE: .htaccess mentions showapp"
  cp -p $A/sites.php /root/backup/sites.php.pre-hair-$(date +%m%d%H%M)
  LINE="  'hair'      => ['hosts' => ['$DOM'], 'web' => '$W', 'cron' => []], // (2.99.646 - 05/11) the hair demo salon, moved from the nailflow account"
  F=$A/sites.php L="$LINE" $PHP -r '$f=getenv("F"); $s=file_get_contents($f); $p=strrpos($s, "];"); if($p===false) exit(1); file_put_contents($f, substr($s,0,$p).getenv("L")."\n".substr($s,$p));'
  $PHP -l $A/sites.php >/dev/null; $PHP -r '$m = require "/home/uyurpyzubx0m/app/sites.php"; echo isset($m["hair"]) ? "sites.php ok (" . count($m) . " sites)\n" : "NO"; ' | grep -q "ok" || die "sites.php"
  chown -R $U:$U "$SD" "$W"; chown -h $U:$U "$SD/current"
  echo "BUILD-HAIR-OK"
  ;;
switch)
  [ -d "$SD" ] && [ -d "$W" ] || die "build first"
  ln -sfn "$W" "$H/public_html/hairweb.tmp" && mv -T "$H/public_html/hairweb.tmp" "$H/public_html/hairweb"; chown -h $U:$U "$H/public_html/hairweb"
  cp -p "$ODB/hair.sqlite" "$SD/data/hair.sqlite"; chown $U:$U "$SD/data/hair.sqlite"   # the latest data
  /usr/local/cpanel/bin/uapi --user=nailflow SubDomain delsubdomain domain=$DOM 2>&1 | grep -E "status|errors" | head -3 || true
  /usr/local/cpanel/bin/cpapi2 --user=$U AddonDomain addaddondomain newdomain=$DOM subdomain=demohair dir=public_html/hairweb 2>&1 | grep -iE "result|reason|error" | head -4
  grep -q "^$DOM: $U==" /etc/userdatadomains || { echo "addon failed - putting it back on nailflow"; bash "$0" back; exit 1; }
  /usr/local/cpanel/bin/autossl_check --user=$U >/dev/null 2>&1 &
  echo "SWITCH-HAIR-OK (AutoSSL running in the background)"
  ;;
back)
  /usr/local/cpanel/bin/cpapi2 --user=$U AddonDomain deladdondomain domain=$DOM subdomain=demohair_american-nails-and-spa.com 2>&1 | grep -iE "result|reason" | head -2 || true
  /usr/local/cpanel/bin/uapi --user=nailflow SubDomain addsubdomain domain=demo.hair rootdomain=nailflowapp.com dir=/home/nailflow/demo.hair.nailflowapp.com 2>&1 | grep -E "status|errors" | head -3
  /usr/local/cpanel/bin/autossl_check --user=nailflow >/dev/null 2>&1 &
  echo "BACK-HAIR-OK"
  ;;
*) echo "usage: build | switch | back"; exit 2 ;;
esac
