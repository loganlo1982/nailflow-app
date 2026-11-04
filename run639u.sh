#!/bin/bash
# CHAT 04/11: 639u – Home icon Gift card -> Gift history / Lich su the. live only (JS text).
S=76dfe1162e31a67007f055c66a501852c3cc073f; W=/root/f639u; rm -rf $W; mkdir -p $W; cd $W
curl -sfL -o fix639u.py https://raw.githubusercontent.com/loganlo1982/nailflow-app/$S/fix639u.py || { echo CURL FAIL; exit 1; }
sha256sum fix639u.py | cut -c1-8
REL=$(readlink -f /home/uyurpyzubx0m/app/sites/an/current)
python3 fix639u.py $REL && python3 fix639u.py $REL go | tail -1
for u in american-nails-and-spa.com/admin/ lovenails.nailflowapp.com/admin/; do curl -s -o /dev/null -w "$u %{http_code}\n" https://$u; done
echo XONG-639u
