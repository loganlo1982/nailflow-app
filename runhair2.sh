#!/bin/bash
P=$1; B=https://raw.githubusercontent.com/loganlo1982/nailflow-app/2a64ab931ec2fa09a03f64e1df67a28685be0eb0
H=/home/nailflow/demo.hair.nailflowapp.com; W=/root/fhair2; rm -rf $W; mkdir -p $W; cd $W
for f in fixHAIR-chu.py fixHAIR-b.py; do curl -sfL -o $f $B/$f || { echo CURL FAIL; exit 1; }; done; sha256sum fixHAIR-chu.py fixHAIR-b.py | cut -c1-8 | tr '\n' ' '; echo
if [ "$P" = copy ]; then T=/root/thair2; rm -rf $T; cp -a $H $T; else T=$H; fi
python3 fixHAIR-chu.py $T go | tail -1; python3 fixHAIR-b.py $T go | tail -1; python3 fixHAIR-b.py $T go | tail -1
cd $T && php -r 'require "inc/core.php"; $n=0; foreach(q("SELECT name,pin_hash FROM staff WHERE active=1")->fetchAll() as $r) { $ok=password_verify("1234",(string)$r["pin_hash"]); $n+=$ok; echo $r["name"],"=",$ok?"1234":"?"," "; } echo "\n";'
if [ "$P" = copy ]; then rm -rf $T; else chown -R nailflow:nailflow $H/assets $H/inc; for u in admin/ tech/ assets/hair-words.js assets/admin-core.js ''; do curl -s -o /dev/null -w "/$u %{http_code}\n" https://demo.hair.nailflowapp.com/$u; done; fi
echo XONG-$P
