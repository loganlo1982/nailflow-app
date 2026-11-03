import sys,shutil,time,subprocess,hashlib
A=["const API_ROUTES = [", "const API_ROUTES = [/* (2.99.632 - LENH 632) the salon setup link */ 'setup_new' => 'setuplink', 'setup_prev' => 'setuplink', 'setup_prev_clear' => 'setuplink', 'setup_info' => 'setuplink', 'setup_turn' => 'setuplink', 'setup_shop' => 'setuplink', 'setup_staff_one' => 'setuplink', 'setup_staff_off' => 'setuplink', 'setup_staff_end' => 'setuplink', "]
for p in sys.argv[2:]:
    t=open(p,encoding="utf-8").read()
    if "setuplink" in t: print("ALREADY",p); continue
    if t.count(A[0])!=1: print("STOP anchor",p,t.count(A[0])); continue
    print(p,"anchor ok")
    if sys.argv[1]!="go": continue
    b="/root/app/old/"+p.strip("/").replace("/","__")+".pre-632-"+time.strftime("%m%d%H%M"); shutil.copy2(p,b)
    n=t.replace(A[0],A[1]); open(p,"w",encoding="utf-8").write(n)
    r=subprocess.run(["/usr/local/bin/php","-l",p],capture_output=True,text=True)
    if r.returncode: shutil.copy2(b,p); print("LINT FAIL -> put back",p,r.stdout[:200]); continue
    print("PATCHED",p,hashlib.sha256(n.encode()).hexdigest()[:8],"backup",b)
