#!/bin/bash
# CHAT 03/11 23:50: len chuoi 639c d e f g (QA-0021 0009 0015 0014 0010) – LAMWEB. Phase copy | live
P=$1; S=__SHA__; B=https://raw.githubusercontent.com/loganlo1982/nailflow-app/$S
W=/root/f639cg; rm -rf $W; mkdir -p $W; cd $W
for f in fix639c.py fix639d.py fix639e.py fix639f.py fix639g.py test618-639g.zip; do curl -sfL -o $f $B/$f || { echo "CURL FAIL $f"; exit 1; }; done
sha256sum fix639?.py | cut -c1-8 | tr '\n' ' '; echo "(can 6d60f165 33433ce7 5b388fda f86fca96 0d39f43b)"
REL=$(readlink -f /home/uyurpyzubx0m/app/sites/an/current)
chain() { for x in c d e f g; do python3 $W/fix639$x.py "$1" go | tail -1 || return 1; done; }
if [ "$P" = copy ]; then
  rm -rf /root/t639cg /root/t639cgw; cp -a $REL /root/t639cg; mkdir /root/t639cgw; cp /home/uyurpyzubx0m/public_html/api.php /root/t639cgw/AN_api.php; cp /home/uyurpyzubx0m/lovenails/api.php /root/t639cgw/LN_api.php
  chain /root/t639cg
  K=/root/nftest/k639cg; rm -rf $K; cp -a /root/nftest/kit $K; rm -rf $K/run; cd $K; unzip -qo $W/test618-639g.zip
  S2=$(grep -o '^ALL="[^"]*"' run-tests.sh | sed 's/ALL="//;s/"$//' | tr ' ' '\n' | grep -v -E '^(book611a|book620|turn609|qa639[h-z])$' | tr '\n' ' ')
  NF_WEB_APIS="/root/t639cgw/AN_api.php /root/t639cgw/LN_api.php" ./run-tests.sh /root/t639cg $S2 > /root/kit639cg.txt 2>&1
  tail -2 /root/kit639cg.txt; grep "FAIL MOI [1-9]" /root/kit639cg.txt
elif [ "$P" = live ]; then
  chain $REL
  for f in inc/api/_out.php inc/api/links.php inc/api/public.php inc/calls.php inc/calls-agent.php inc/calls-ivr.php inc/calls-job.php inc/calls-ask.php inc/calls-talk.php inc/sms-short.php; do [ -f $REL/$f ] && php -l $REL/$f | grep -v "No syntax"; done
  /scripts/restartsrv_apache_php_fpm >/dev/null 2>&1; sleep 3
  for u in american-nails-and-spa.com/ american-nails-and-spa.com/admin/ lovenails.nailflowapp.com/admin/; do curl -s -o /dev/null -w "$u %{http_code}\n" https://$u; done
fi
echo XONG-$P
