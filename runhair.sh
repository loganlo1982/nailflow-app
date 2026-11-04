#!/bin/bash
# CHAT 03/11: len fixHAIR-ui (dc46d087) CHI demo.hair. Phase copy | live
P=$1; B=https://raw.githubusercontent.com/loganlo1982/nailflow-app/7dbcaa0dfe20ae3a960902448eacd69b7ca3adc0
H=/home/nailflow/demo.hair.nailflowapp.com; W=/root/fhair; rm -rf $W; mkdir -p $W; cd $W
curl -sfL -o fixHAIR-ui.py $B/fixHAIR-ui.py || { echo CURL FAIL; exit 1; }; sha256sum fixHAIR-ui.py | cut -c1-8
if [ "$P" = copy ]; then rm -rf /root/thair; cp -a $H /root/thair; python3 fixHAIR-ui.py /root/thair go | tail -2; python3 fixHAIR-ui.py /root/thair go | tail -1; rm -rf /root/thair
elif [ "$P" = live ]; then
  python3 fixHAIR-ui.py $H go | tail -2
  chown -R nailflow:nailflow $H/assets $H/admin $H/inc
  for f in $H/admin/index.php $H/inc/api/_kiosk.php; do php -l $f | grep -v 'No syntax'; done
  for u in admin/ desk/ tech/ assets/hair-ui.js assets/hair-ui.css ''; do curl -s -o /dev/null -w "/$u %{http_code}\n" https://demo.hair.nailflowapp.com/$u; done
fi
echo XONG-$P
