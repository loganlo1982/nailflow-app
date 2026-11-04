#!/usr/bin/env python3
# CHAT 03/11 22:10 (anh Logan "HAIR DEMO: FIX QA FINDINGS" muc 2): CHI demo.hair. Chu tiem dat hen NGOAI GIO MO CUA (vd 7:45 PM khi dong 7 PM):
#  truoc: chu tiem duoc dat toi 1 tieng sau gio dong KHONG hoi (luat 2.99.387 cua nail). Nay (hair): luon hien "Book outside opening hours? (...)" + xac nhan
#  truoc khi qua buoc 1 va truoc khi luu. Khong cam chu tiem dat ngoai gio. Chi assets/admin/book.js. Nail KHONG doi.
import sys, os, shutil, time, hashlib, subprocess
a = sys.argv[1:]; R = a[0].rstrip('/'); go = len(a) > 1 and a[1] == 'go'
if not os.path.isfile(R + '/inc/hair.php'): sys.exit('STOP: not the hair site')
p = R + '/assets/admin/book.js'; s = open(p, encoding='utf-8').read(); sha = lambda t: hashlib.sha256(t.encode()).hexdigest()[:8]
A1 = "if (M.other && !M.outOk) return askOther(go); return go(); }"
B1 = "if ((M.other || outHrs(M.date, M.start)) && !M.outOk) return askOther(go); return go(); } /* (hair-c CHAT 03/11) outside the opening hours: always asked */"
A2 = "      if (ANY) return anyBook();\n      save(false); });"
B2 = "      if (ANY) return anyBook();\n      if (outHrs(M.date, M.start) && !M.outOk) return askOther(() => save(false)); /* (hair-c CHAT 03/11) asked again before saving */\n      save(false); });"
n = [s.count(A1), s.count(A2)]; al = 'hair-c CHAT 03/11' in s; print('book.js sha', sha(s), 'anchors', n, 'already', al)
if al or n != [1, 1]: sys.exit('STOP - nothing changed')
t = s.replace(A1, B1).replace(A2, B2)
if not go: sys.exit('check only (new ' + sha(t) + ') - run again with: go')
bk = R + '/inc/old-hairc-' + time.strftime('%m%d%H%M'); os.makedirs(bk, exist_ok=True); b = bk + '/assets__admin__book.js'; shutil.copy2(p, b)
m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m)
if shutil.which('node'):
    r = subprocess.run(['node', '--check', p], capture_output=True, text=True)
    if r.returncode: shutil.copy2(b, p); sys.exit('ERROR ' + r.stderr[:300] + ' - put back')
print('OK hair-c', sha(t), 'backup', bk)
