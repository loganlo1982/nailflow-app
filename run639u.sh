#!/bin/bash
# CHAT 04/11: 639u – Home icon Gift card -> Gift history / Lich su the. live only (JS text).
S=51141c672a174294682f9dd6a75061619e20b287; W=/root/f639u; rm -rf $W; mkdir -p $W; cd $W
for f in fix639u.py fix639v.py; do curl -sfL -o $f https://raw.githubusercontent.com/loganlo1982/nailflow-app/$S/$f || { echo CURL FAIL; exit 1; }; done
sha256sum fix639u.py fix639v.py | cut -c1-8
REL=$(readlink -f /home/uyurpyzubx0m/app/sites/an/current)
python3 fix639u.py $REL go | tail -1; python3 fix639v.py $REL go | tail -1
for u in american-nails-and-spa.com/admin/ lovenails.nailflowapp.com/admin/; do curl -s -o /dev/null -w "$u %{http_code}\n" https://$u; done
echo XONG-639uv
