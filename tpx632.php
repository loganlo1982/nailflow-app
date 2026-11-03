<?php
// CHAT test 632-proxy: php tpx632.php <app dir> <token>   (SALON_ID=lovenails)
$A=$argv[1]; require "$A/inc/core.php"; settings(); require_once "$A/inc/audit.php"; require_once "$A/inc/setuplink.php"; $T=$argv[2]; $n=0; $f=0;
$c=function($name,$srv,$want) use($T,&$n,&$f){ $_SERVER=array_merge(['REMOTE_ADDR'=>'','HTTP_HOST'=>'','HTTP_X_FORWARDED_HOST'=>''],$srv); $ok=setup_check($T)!==null; $n++; if($ok!==$want)$f++; echo ($ok===$want?'✓ ':'✗ '),$name,PHP_EOL; };
$c('direct on the salon address',['REMOTE_ADDR'=>'9.9.9.9','HTTP_HOST'=>'lovenails.nailflowapp.com'],true);
$c('through this server proxy (Host = app address, X-Forwarded-Host = salon address)',['REMOTE_ADDR'=>'72.167.37.112','HTTP_HOST'=>'lovenails.american-nails-and-spa.com','HTTP_X_FORWARDED_HOST'=>'lovenails.nailflowapp.com'],true);
$c('X-Forwarded-Host sent by an outside client is NOT trusted',['REMOTE_ADDR'=>'9.9.9.9','HTTP_HOST'=>'lovenails.american-nails-and-spa.com','HTTP_X_FORWARDED_HOST'=>'lovenails.nailflowapp.com'],false);
$c('proxy but another forwarded host',['REMOTE_ADDR'=>'72.167.37.112','HTTP_HOST'=>'lovenails.american-nails-and-spa.com','HTTP_X_FORWARDED_HOST'=>'evil.example'],false);
$c('wrong host',['REMOTE_ADDR'=>'9.9.9.9','HTTP_HOST'=>'evil.example'],false);
echo "PASS ",$n-$f,"/",$n,PHP_EOL;
