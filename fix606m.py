#!/usr/bin/env python3
# CHAT 01/11 13:15 (anh Logan: "move bat cu luc nao cung duoc"): dragging ONE PART of a booking with 2 techs onto a busy tech was refused
#  for everyone ("... Moved back.", 2.54). Now the OWNER gets the same "Double booking? - Move anyway / Keep old time" as any other booking;
#  managers / desk: unchanged (still refused). Only inc/api/appts.php, 2 lines.
import sys, os, shutil, time, subprocess, hashlib
R = sys.argv[1].rstrip('/'); go = len(sys.argv) > 2 and sys.argv[2] == 'go'
A = [("if ($timeChanged && (empty($in['force']) || $role !== 'admin' || $linkedPart)) {", "if ($timeChanged && (empty($in['force']) || $role !== 'admin')) { // (CHAT 01/11 606m) the owner may move a part of a 2-tech booking too (asked first)"),
     ("if ($linkedPart) fail($msg . ' Moved back.', 409);", "if ($linkedPart && $role !== 'admin') fail($msg . ' Moved back.', 409); // (CHAT 01/11 606m) owner: \"Move anyway?\" below")]
fs = [R + '/inc/api/appts.php']
P = '/home/uyurpyzubx0m/public_html/inc/api/appts.php'
if os.path.isfile(P) and not os.path.islink(P) and os.path.realpath(P) != os.path.realpath(fs[0]): fs.append(P)
for f in fs:
    t = open(f, encoding='utf-8').read(); print(f, hashlib.sha256(t.encode()).hexdigest()[:8], [t.count(a) for a, _ in A])
    if any(t.count(a) != 1 for a, _ in A): sys.exit('ANCHOR FAIL')
if not go: print('check only'); sys.exit()
od = os.path.expanduser('~/app/old'); os.makedirs(od, exist_ok=True); st = time.strftime('%m%d%H%M')
for i, f in enumerate(fs):
    b = od + '/inc__api__appts.php.' + str(i) + '.pre-606m-' + st; shutil.copy2(f, b)
    n = open(f, encoding='utf-8').read()
    for a, c in A: n = n.replace(a, c)
    open(f, 'w', encoding='utf-8').write(n)
    r = subprocess.run(['php', '-l', f], capture_output=True, text=True)
    if r.returncode: shutil.copy2(b, f); sys.exit('PHP FAIL - put back ' + f + r.stdout + r.stderr)
    print('OK', f, hashlib.sha256(n.encode()).hexdigest()[:8], 'backup', b)
