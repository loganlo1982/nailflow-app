#!/bin/bash
# CHAT 03/11: len 638h (Dejavoo UserChoice). Phase copy | live
P=$1; S=d5a0b3948afc95a669fa9e91d38ae5d292e49d8d; B=https://raw.githubusercontent.com/loganlo1982/nailflow-app/$S
W=/root/f638h; rm -rf $W; mkdir -p $W; cd $W
for f in fix638h.py test618-638h.zip; do curl -sfL -o $f $B/$f || { echo "CURL FAIL $f"; exit 1; }; done
sha256sum fix638h.py test618-638h.zip | cut -c1-8 | tr '\n' ' '; echo "(can 6c292d0b ...)"
REL=$(readlink -f /home/uyurpyzubx0m/app/sites/an/current)
if [ "$P" = copy ]; then
  rm -rf /root/t638h /root/t638hw; cp -a $REL /root/t638h; mkdir /root/t638hw; cp /home/uyurpyzubx0m/public_html/api.php /root/t638hw/AN_api.php; cp /home/uyurpyzubx0m/lovenails/api.php /root/t638hw/LN_api.php
  python3 $W/fix638h.py /root/t638h go | tail -1
  K=/root/nftest/k638h; rm -rf $K; mkdir -p $K; cd $K; unzip -q $W/test618-638h.zip; cp /root/nftest/kit/clock/nfclock.so clock/
  S2=$(grep -o '^ALL="[^"]*"' run-tests.sh | sed 's/ALL="//;s/"$//' | tr ' ' '\n' | grep -v -E '^(book611a|book620|turn609)$' | tr '\n' ' ')
  NF_WEB_APIS="/root/t638hw/AN_api.php /root/t638hw/LN_api.php" ./run-tests.sh /root/t638h $S2 > /root/kit638h.txt 2>&1
  tail -2 /root/kit638h.txt; grep "FAIL MOI [1-9]" /root/kit639.txt
elif [ "$P" = live ]; then
  python3 $W/fix638h.py $REL go | tail -1
  php -l $REL/inc/checkout-edit.php; /scripts/restartsrv_apache_php_fpm >/dev/null 2>&1; sleep 3
  for u in american-nails-and-spa.com/ american-nails-and-spa.com/admin/ lovenails.nailflowapp.com/admin/; do curl -s -o /dev/null -w "$u %{http_code}\n" https://$u; done
fi
echo XONG-$P
