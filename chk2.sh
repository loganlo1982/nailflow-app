#!/bin/bash
# chk2.sh R [go]  (HM = backup home)
R=$1; G=$2; cd /root
echo "== 602"; HOME=${HM:-/home/uyurpyzubx0m} python3 fix602.py $R $G 2>&1 | tail -14
echo "== 603"; HOME=${HM:-/home/uyurpyzubx0m} python3 fix603.py $R $G 2>&1 | tail -8
