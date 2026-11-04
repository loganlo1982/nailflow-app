#!/bin/bash
# CHAT 03/11 toi: len 638a b c d e g d2 (LAMWEB) + fixC638a (CHAT). Phase: copy | live
P=$1; S=ff98679a0b9e96bd4c6467dd32967824524b456c; B=https://raw.githubusercontent.com/loganlo1982/nailflow-app/$S
W=/root/f638; rm -rf $W; mkdir -p $W; cd $W
L="fix638a.py fix638b.py fix638c.py fix638d.py fix638e.py fix638g.py fix638d2.py fixC638a.py"
for f in $L test618-638d2.zip; do curl -sfL -o $f $B/$f || { echo "CURL FAIL $f"; exit 1; }; done
sha256sum $L test618-638d2.zip | cut -c1-8 | tr '\n' ' '; echo; echo "can f8968327 c1eda073 5e360e35 1be88390? -> xem tren"
REL=$(readlink -f /home/uyurpyzubx0m/app/sites/an/current); ANW=/home/uyurpyzubx0m/public_html/api.php; LNW=/home/uyurpyzubx0m/lovenails/api.php
echo "REL=$REL"
if [ "$P" = copy ]; then
  rm -rf /root/t638 /root/t638w; cp -a $REL /root/t638; mkdir /root/t638w; cp $LNW /root/t638w/LN_api.php; cp $ANW /root/t638w/AN_api.php
  WEB="/root/t638w/AN_api.php /root/t638w/LN_api.php"; T=/root/t638
elif [ "$P" = live ]; then WEB="$ANW $LNW"; T=$REL
else echo "usage: copy|live"; exit 1; fi
for x in a b c d e g d2; do python3 $W/fix638$x.py $T $WEB go 2>&1 | tail -1; done
python3 $W/fixC638a.py $T go | tail -1
echo -n "moc: "; grep -c "2.99.638b" $T/api.php $WEB | tr '\n' ' '; grep -c "638C-a" $T/assets/admin/calls.js; ls $T/inc/dejavoo*.php | wc -l
if [ "$P" = copy ]; then
  K=/root/nftest/k638; rm -rf $K; mkdir -p $K; cd $K; unzip -q $W/test618-638d2.zip; cp /root/nftest/kit/clock/nfclock.so clock/ 2>/dev/null
  NF_WEB_APIS="$WEB" ./run-tests.sh $T aicall telnyx telnyx615 review622 mani631 setup632 install633 cross635 setup636 hide636 sec637a sec637b sec637c sec637d sec637e dv638a dv638b dv638c dv638d dv638e dv638g qa638x qa635b book610 mod619 pay619 money626 money627 calls629 sw624 sw605 sw605b sw602b sw590 > /root/kit638.txt 2>&1
  tail -2 /root/kit638.txt; grep "FAIL MOI [1-9]" /root/kit638.txt
fi
echo XONG-$P
