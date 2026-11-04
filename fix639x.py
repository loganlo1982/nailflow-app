#!/usr/bin/env python3
# fix639x (CHAT, anh Logan 04/11 00:59 "nut Dat hen de ke ben dau +"): Appointments – the blue Book / Đặt hẹn button leaves the top right of the
# day strip (it covered the dates) and sits in the row under it, right after the zoom [- 🔍 +]. Same button, same openBook(). 2 files: appts.js, desk-easy.css.
# python3 fix639x.py <release dir>   (kiem)   /   ... go
import sys, os, shutil, time
a = sys.argv[1:]; go = bool(a) and a[-1] == 'go'
if go: a = a[:-1]
if not a: sys.exit('usage: python3 fix639x.py <release dir> [go]')
R = a[0].rstrip('/'); J = 'assets/admin/appts.js'; C = 'assets/desk-easy.css'
MV = "{ const c = $('#apCols'), f2 = $('#apFindIc'); if (c && f2) { if (f2.parentNode !== c) c.appendChild(f2); f2.style.top = ''; f2.style.height = ''; $('#p-appts')?.classList.remove('has-find-ic'); } } /* (639x) Book next to + */"
P = [(J, "  { const f = $('#apFindIc'); if (f) { f.style.top = strip.offsetTop + 'px'; f.style.height = strip.offsetHeight + 'px'; } }",
         "  { const f = $('#apFindIc'); if (f && !f.closest('#apCols')) { f.style.top = strip.offsetTop + 'px'; f.style.height = strip.offsetHeight + 'px'; } } " + MV),
     (J, "  const l = apLabel(d), tk = $('#apTk', b); tk.textContent = l.t; tk.classList.toggle('on', !!l.on); b.hidden = false; }",
         "  const l = apLabel(d), tk = $('#apTk', b); tk.textContent = l.t; tk.classList.toggle('on', !!l.on); b.hidden = false; " + MV + " }")]
CSS = ('\n/* (639x – anh Logan 04/11 00:59) Appointments: Book / Đặt hẹn in the row under the dates, right after [- 🔍 +] (the dates are no longer covered) */\n'
       'html[data-app="admin"] #apCols{justify-content:flex-start}\n'
       'html[data-app="admin"] #apCols .ap-z{margin-left:auto}\n'
       'html[data-app="admin"] #apCols .ap-find-ic.ap-book-ic{position:static;flex:none;width:auto;min-width:0;height:auto;padding:0;border:0;background:transparent!important;box-shadow:none}\n'
       'html[data-app="admin"] #apCols .ap-find-ic.ap-book-ic span{width:auto;padding:12px 16px;border-radius:15px;white-space:nowrap}\n')
s = open(os.path.join(R, J), encoding='utf-8').read(); cs = open(os.path.join(R, C), encoding='utf-8').read()
for f, o, n in P: print(f, 'anchors', s.count(o))
if any(s.count(o) != 1 for f, o, n in P) or '(639x)' in s or '639x' in cs: print('STOP – nothing changed'); sys.exit(1)
if not go: print('check OK – run again with: go'); sys.exit(0)
os.makedirs(os.path.expanduser('~/app/old'), exist_ok=True); t = time.strftime('%m%d%H%M')
for f in (J, C): shutil.copy2(os.path.join(R, f), os.path.expanduser('~/app/old/' + f.replace('/', '__') + '.pre-639x-' + t))
for f, o, n in P: s = s.replace(o, n)
open(os.path.join(R, J), 'w', encoding='utf-8').write(s); open(os.path.join(R, C), 'w', encoding='utf-8').write(cs.rstrip('\n') + '\n' + CSS)
print('OK 639x – JS/CSS: no restart, reload the pages')
