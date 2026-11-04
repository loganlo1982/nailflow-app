#!/bin/bash
# CHAT 03/11 toi: len 638a+b+c (LAMWEB) + fixC638a (CHAT). Phase: copy | live
P=$1; S=693374fb64c790c8dd118ccafc8be58da9b9f73e; B=https://raw.githubusercontent.com/loganlo1982/nailflow-app/$S
W=/root/f638; mkdir -p $W; cd $W
for f in fix638a.py fix638b.py fix638c.py fixC638a.py test618-638c.zip; do [ -s $f ] || curl -sfL -o $f $B/$f || { echo "CURL FAIL $f"; exit 1; }; done
sha256sum fix638a.py fix638b.py fix638c.py fixC638a.py test618-638c.zip | cut -c1-8 | tr '\n' ' '; echo " (can f8968327 416df19b c240fc77 1be88390 e25af995)"
REL=$(readlink -f /home/uyurpyzubx0m/app/sites/an/current); ANW=/home/uyurpyzubx0m/public_html/api.php; LNW=/home/uyurpyzubx0m/lovenails/api.php
echo "REL=$REL"; ls -l $ANW $LNW | cut -c1-160
if [ "$P" = copy ]; then
  rm -rf /root/t638 /root/t638w; cp -a $REL /root/t638; mkdir /root/t638w; cp $LNW /root/t638w/LN_api.php
  WEB="/root/t638w/LN_api.php"; if [ ! -L $ANW ]; then cp $ANW /root/t638w/AN_api.php; WEB="/root/t638w/AN_api.php $WEB"; fi
  T=/root/t638
elif [ "$P" = live ]; then
  WEB="$LNW"; [ -L $ANW ] || WEB="$ANW $WEB"; T=$REL
else echo "usage: run638.sh copy|live"; exit 1; fi
python3 $W/fix638a.py $T go | tail -1 || exit 1
python3 $W/fix638b.py $T $WEB go | tail -1
python3 $W/fix638c.py $T $WEB go | tail -1
python3 $W/fixC638a.py $T go | tail -1
grep -c "2.99.638b" $T/api.php $T/pub/api.php $WEB; grep -c "638C-a" $T/assets/admin/calls.js
if [ "$P" = copy ]; then
  K=/root/nftest/k638c; rm -rf $K; mkdir -p $K; cd $K; unzip -q $W/test618-638c.zip; cp /root/nftest/kit/clock/nfclock.so clock/ 2>/dev/null
  NFW="$WEB"; [ -f /root/t638w/AN_api.php ] || NFW="/root/t638/api.php $WEB"
  NF_WEB_APIS="$NFW" ./run-tests.sh $T aicall telnyx telnyx615 review622 mod619 pay619 money626 money627 calls629 mani631 setup632 cross635 qa635b setup636 hide636 sec637a sec637b sec637c sec637d sec637e dv638a dv638b dv638c install633 book610 sw605b sw602b sw590 sw624 > $W/kit.txt 2>&1
  tail -2 $W/kit.txt; grep "FAIL MOI [1-9]" $W/kit.txt
fi
echo XONG-$P
