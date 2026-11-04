#!/bin/bash
# CHAT 03/11: len 639a (QA-0012). Phase copy | live
P=$1; S=d5a0b3948afc95a669fa9e91d38ae5d292e49d8d; B=https://raw.githubusercontent.com/loganlo1982/nailflow-app/$S
W=/root/f639; rm -rf $W; mkdir -p $W; cd $W
for f in fix639a.py test618-639a.zip; do curl -sfL -o $f $B/$f || { echo "CURL FAIL $f"; exit 1; }; done
sha256sum fix639a.py test618-639a.zip | cut -c1-8 | tr '\n' ' '; echo "(can 7a6ebf87 ...)"
REL=$(readlink -f /home/uyurpyzubx0m/app/sites/an/current)
if [ "$P" = copy ]; then
  rm -rf /root/t639 /root/t639w; cp -a $REL /root/t639; mkdir /root/t639w; cp /home/uyurpyzubx0m/public_html/api.php /root/t639w/AN_api.php; cp /home/uyurpyzubx0m/lovenails/api.php /root/t639w/LN_api.php
  python3 $W/fix639a.py /root/t639 go | tail -1
  K=/root/nftest/k639; rm -rf $K; mkdir -p $K; cd $K; unzip -q $W/test618-639a.zip; cp /root/nftest/kit/clock/nfclock.so clock/
  S2=$(grep -o '^ALL="[^"]*"' run-tests.sh | sed 's/ALL="//;s/"$//' | tr ' ' '\n' | grep -v -E '^(book611a|book620|turn609)$' | tr '\n' ' ')
  NF_WEB_APIS="/root/t639w/AN_api.php /root/t639w/LN_api.php" ./run-tests.sh /root/t639 $S2 > /root/kit639.txt 2>&1
  tail -2 /root/kit639.txt; grep "FAIL MOI [1-9]" /root/kit639.txt
elif [ "$P" = live ]; then
  python3 $W/fix639a.py $REL go | tail -1
  php -l $REL/inc/checkout-edit.php; /scripts/restartsrv_apache_php_fpm >/dev/null 2>&1; sleep 3
  for u in american-nails-and-spa.com/ american-nails-and-spa.com/admin/ lovenails.nailflowapp.com/admin/; do curl -s -o /dev/null -w "$u %{http_code}\n" https://$u; done
fi
echo XONG-$P
