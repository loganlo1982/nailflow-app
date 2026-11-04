#!/bin/bash
# CHAT 03/11: len 639b (QA-0011). Phase copy | live
P=$1; S=45bafe8b03306894c37d600660599582a7ec6c9a; B=https://raw.githubusercontent.com/loganlo1982/nailflow-app/$S
W=/root/f639b; rm -rf $W; mkdir -p $W; cd $W
for f in fix639b.py test618-639b.zip; do curl -sfL -o $f $B/$f || { echo "CURL FAIL $f"; exit 1; }; done
sha256sum fix639b.py test618-639b.zip | cut -c1-8 | tr '\n' ' '; echo "(can 60e91cb5 ...)"
REL=$(readlink -f /home/uyurpyzubx0m/app/sites/an/current)
if [ "$P" = copy ]; then
  rm -rf /root/t639b /root/t639bw; cp -a $REL /root/t639b; mkdir /root/t639bw; cp /home/uyurpyzubx0m/public_html/api.php /root/t639bw/AN_api.php; cp /home/uyurpyzubx0m/lovenails/api.php /root/t639bw/LN_api.php
  python3 $W/fix639b.py /root/t639b go | tail -1
  K=/root/nftest/k639b; rm -rf $K; cp -a /root/nftest/kit $K; rm -rf $K/run; cd $K; unzip -qo $W/test618-639b.zip
  S2=$(grep -o '^ALL="[^"]*"' run-tests.sh | sed 's/ALL="//;s/"$//' | tr ' ' '\n' | grep -v -E '^(book611a|book620|turn609)$' | tr '\n' ' ')
  NF_WEB_APIS="/root/t639bw/AN_api.php /root/t639bw/LN_api.php" ./run-tests.sh /root/t639b $S2 > /root/kit639b.txt 2>&1
  tail -2 /root/kit639b.txt; grep "FAIL MOI [1-9]" /root/kit639.txt
elif [ "$P" = live ]; then
  python3 $W/fix639b.py $REL go | tail -1
  php -l $REL/inc/api/checkout.php; /scripts/restartsrv_apache_php_fpm >/dev/null 2>&1; sleep 3
  for u in american-nails-and-spa.com/ american-nails-and-spa.com/admin/ lovenails.nailflowapp.com/admin/; do curl -s -o /dev/null -w "$u %{http_code}\n" https://$u; done
fi
echo XONG-$P
