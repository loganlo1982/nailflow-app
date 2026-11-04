#!/usr/bin/env python3
# CHAT 2.99.638C-a (anh Logan 03/11 13:59 "them nut de goi lai khach"): Messages -> Calls -> 1 cuoc goi: nut "📞 Call back / Gọi lại"
#   truoc day CHI hien khi status = callback hoac voicemail -> cuoc "Needs review" (khach can hen, AI chua dat) khong co nut.
#   Nay: hien cho MOI cuoc goi co so dien thoai (review / callback / missed / done), cung kieu nut cu, dat ngay sau "Book". Chi sua assets/admin/calls.js.
# Run: python3 fixC638a.py <release dir> [go]
import sys, os, shutil, time, hashlib, subprocess
a = sys.argv[1:]; R = a[0].rstrip('/'); go = len(a) > 1 and a[1] == 'go'
p = f'{R}/assets/admin/calls.js'; s = open(p, encoding='utf-8').read()
sha = lambda t: hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
A = "      if (c.status === 'callback' || c.kind === 'vm') act.push(`<a class=\"btn big\" href=\"tel:${esc(c.phone.replace(/[^\\d+]/g, ''))}\">📞 ${esc(T('Call back', 'Gọi lại'))}</a>`);\n"
B = "      if (cbBtn) act.push(cbBtn);\n"
A2 = "    if (c.status === 'done' && !c.appt) act.push("
B2 = "    if (cbBtn && c.status !== 'review' && c.status !== 'callback') act.push(cbBtn); /* (2.99.638C-a) missed / done calls: Call back too */\n" + A2
A3 = "    const act = [];\n"
B3 = ("    const act = [];\n"
      "    const cbDg = String(c.phone || '').replace(/\\D/g, ''); /* (2.99.638C-a - anh Logan 03/11) Call back for EVERY call with a number (was: only callback / voicemail) */\n"
      "    const cbBtn = cbDg.length >= 10 ? `<a class=\"btn big\" href=\"tel:${cbDg.length === 10 ? '+1' + cbDg : '+' + cbDg}\">📞 ${esc(T('Call back', 'Gọi lại'))}</a>` : '';\n")
n = [s.count(A), s.count(A2), s.count(A3)]; al = '2.99.638C-a' in s
print('calls.js sha', sha(s), '(base 7442f1b5) anchors', *n, 'already', al)
if al or n != [1, 1, 1]: sys.exit('STOP - nothing changed')
t = s.replace(A3, B3).replace(A, B).replace(A2, B2)
print('new sha', sha(t))
if not go: sys.exit('check only - run again with: go')
bk = os.path.expanduser('~/app/old'); os.makedirs(bk, exist_ok=True); b = f"{bk}/assets__admin__calls.js.pre-638Ca-{time.strftime('%m%d%H%M')}"
shutil.copy2(p, b); m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m)
if shutil.which('node'):
    r = subprocess.run(['node', '--check', p], capture_output=True, text=True)
    if r.returncode: shutil.copy2(b, p); sys.exit('ERROR node --check: ' + r.stderr[:300] + ' - put back')
print('OK 2.99.638C-a backup', b, '- khong can restart (av() doi ?v=)')
