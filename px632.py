# CHAT 632-proxy: setup_req_host() trusts X-Forwarded-Host only from this server's own proxy (same rule as inc/core/settings.php:247)
import sys,shutil,time,subprocess,hashlib
OLD="function setup_req_host(): string { return strtolower((string)preg_replace('/:\\d+$/', '', rtrim(trim((string)($_SERVER['HTTP_HOST'] ?? '')), '.'))); }"
NEW=("function setup_req_host(): string { $h = (string)($_SERVER['HTTP_HOST'] ?? ''); "
     "/* (2.99.632 CHAT) lovenails.nailflowapp.com = this server's own proxy (Host = the app's address, X-Forwarded-Host = the salon's): trusted only from this server, like inc/core/settings.php */ "
     "if (in_array((string)($_SERVER['REMOTE_ADDR'] ?? ''), ['72.167.37.112', '127.0.0.1'], true) && trim((string)($_SERVER['HTTP_X_FORWARDED_HOST'] ?? '')) !== '') $h = trim(explode(',', (string)$_SERVER['HTTP_X_FORWARDED_HOST'])[0]); "
     "return strtolower((string)preg_replace('/:\\d+$/', '', rtrim(trim($h), '.'))); }")
p=sys.argv[2]+"/inc/setuplink.php"; t=open(p,encoding="utf-8").read()
if "HTTP_X_FORWARDED_HOST" in t: sys.exit("ALREADY")
if t.count(OLD)!=1: sys.exit("STOP anchor %d"%t.count(OLD))
print("anchor ok")
if sys.argv[1]=="go":
    b="/root/app/old/inc__setuplink.php.pre-632px-"+time.strftime("%m%d%H%M")+("-copy" if "/root/" in p else ""); shutil.copy2(p,b)
    n=t.replace(OLD,NEW); open(p,"w",encoding="utf-8").write(n)
    r=subprocess.run(["/usr/local/bin/php","-l",p],capture_output=True,text=True)
    if r.returncode: shutil.copy2(b,p); sys.exit("LINT FAIL put back "+r.stdout[:200])
    print("PATCHED",hashlib.sha256(n.encode()).hexdigest()[:8],"backup",b)
