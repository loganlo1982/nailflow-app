#!/bin/bash
# usage: chk.sh R [go]
R=$1; G=$2
cd /root
echo "== 572"; HOME=${HM:-/home/uyurpyzubx0m} python3 fix572.py $R $G 2>&1 | tail -5
echo "== 573"; HOME=${HM:-/home/uyurpyzubx0m} python3 fix573.py $R $G 2>&1 | tail -5
echo "== 574"; HOME=${HM:-/home/uyurpyzubx0m} python3 fix574.py $R $G 2>&1 | tail -5
echo "== 575"; HOME=${HM:-/home/uyurpyzubx0m} python3 fix575.py $R/colors/index.php $G 2>&1 | tail -5
echo "== 576"; HOME=${HM:-/home/uyurpyzubx0m} python3 fix576.py $R/colors/index.php $G 2>&1 | tail -5
echo "== 577"; HOME=${HM:-/home/uyurpyzubx0m} python3 fix577.py $R/assets/admin/appts.js $G 2>&1 | tail -5
echo "== 578"; HOME=${HM:-/home/uyurpyzubx0m} python3 fix578.py $R $G 2>&1 | tail -8
