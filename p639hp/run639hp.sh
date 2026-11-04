#!/bin/bash
# CHAT 04/11 18:00: len chuoi 639h..p (QA-0013 0016 0017 0018 0019 0024 0025 0026 0027) - LAMWEB. Phase copy | live. KHONG restart php-fpm.
P=$1; S=$2; B=https://raw.githubusercontent.com/loganlo1982/nailflow-app/$S/p639hp
W=/root/f639hp; rm -rf $W; mkdir -p $W; cd $W
for f in fix639h.py fix639i.py fix639j.py fix639k.py fix639l.py fix639m.py fix639n.py fix639o.py fix639p.py test618-639p.zip; do curl -sfL -o $f $B/$f || { echo "CURL FAIL $f"; exit 1; }; done
sha256sum fix639?.py | cut -c1-8 | tr '\n' ' '; echo "(can 99c38e87 96711cff 9abf7eb5 50b674c4 0156ec68 cf6bb442 fb668da0 48abc10a eab1c240)"
REL=$(readlink -f /home/uyurpyzubx0m/app/sites/an/current)
chain() { R=$1; shift; for x in h i j k l m n; do python3 $W/fix639$x.py $R go | tail -1 || return 1; done; python3 $W/fix639o.py $R "$@" go | tail -1 || return 1; python3 $W/fix639p.py $R go | tail -1 || return 1; }
if [ "$P" = check ]; then
  for x in h i j k l m n p; do python3 $W/fix639$x.py $REL | tail -2; done; python3 $W/fix639o.py $REL /home/uyurpyzubx0m/lovenails/api.php /home/uyurpyzubx0m/public_html/api.php | tail -4
elif [ "$P" = copy ]; then
  rm -rf /root/t639hp /root/t639hpw; cp -a $REL /root/t639hp; mkdir /root/t639hpw; cp /home/uyurpyzubx0m/public_html/api.php /root/t639hpw/AN_api.php; cp /home/uyurpyzubx0m/lovenails/api.php /root/t639hpw/LN_api.php
  chain /root/t639hp /root/t639hpw/LN_api.php /root/t639hpw/AN_api.php
  K=/root/nftest/k639hp; rm -rf $K; cp -a /root/nftest/kit $K; rm -rf $K/run; cd $K; unzip -qo $W/test618-639p.zip
  S2=$(grep -o '^ALL="[^"]*"' run-tests.sh | sed 's/ALL="//;s/"$//' | tr ' ' '\n' | grep -v -E '^(book611a|book620|turn609|qa639c)$' | tr '\n' ' ')
  NF_WEB_APIS="/root/t639hpw/AN_api.php /root/t639hpw/LN_api.php" ./run-tests.sh /root/t639hp $S2 < /dev/null > /root/kit639hp.txt 2>&1
  tail -2 /root/kit639hp.txt; grep "FAIL MOI [1-9]" /root/kit639hp.txt
elif [ "$P" = live ]; then
  chain $REL /home/uyurpyzubx0m/lovenails/api.php /home/uyurpyzubx0m/public_html/api.php
  sleep 3; for u in american-nails-and-spa.com/ american-nails-and-spa.com/admin/ lovenails.nailflowapp.com/admin/ demo.nailflowapp.com/admin/; do curl -s -o /dev/null -w "$u %{http_code}\n" https://$u; done
fi
echo XONG-$P
