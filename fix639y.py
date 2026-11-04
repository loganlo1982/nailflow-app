#!/usr/bin/env python3
# fix639y (CHAT, anh Logan 04/11 01:07 "cac nut dep theo ngay hang thang loi"): Settings -> Auto texts: every kind of text = the name on its own line,
# then [📱 Điện thoại chủ | 🤖 Auto 601] full width, 2 equal halves, 44 px – all rows line up. "Phone chủ" -> "Điện thoại chủ" (same word everywhere).
# Only looks: promo-via.css (end) + 1 word in settings-asend.js. Same buttons, same saving.
import sys, os, shutil, time
a = sys.argv[1:]; go = bool(a) and a[-1] == 'go'
if go: a = a[:-1]
R = a[0].rstrip('/'); J = 'assets/admin/settings-asend.js'; C = 'assets/promo-via.css'
O = "📱 ${LV('My phone', 'Phone chủ')}</button>"; N = "📱 ${LV('My phone', 'Điện thoại chủ')}</button>"
CSS = ('\n/* (639y – anh Logan 04/11 01:07) Auto texts: name on top, the 2 buttons under it full width, equal halves – every row lines up */\n'
       '#setBody .pv-row{flex-direction:column;align-items:stretch;gap:8px;padding:10px 0}\n'
       '#setBody .pv-row>.check,#setBody .pv-row>.as-kl{flex:none;margin:0}\n'
       '#setBody .pv-row .pv-seg{display:flex;width:100%;margin-left:0;border-radius:12px}\n'
       '#setBody .pv-row .pv-seg button{flex:1 1 0;min-width:0;min-height:44px;font-size:16px;padding:8px 6px;text-align:center}\n')
s = open(os.path.join(R, J), encoding='utf-8').read(); cs = open(os.path.join(R, C), encoding='utf-8').read()
print('anchors', s.count(O), 'done', '639y' in cs)
if s.count(O) != 1 or '639y' in cs: print('STOP – nothing changed'); sys.exit(1)
if not go: print('check OK – run again with: go'); sys.exit(0)
os.makedirs(os.path.expanduser('~/app/old'), exist_ok=True); t = time.strftime('%m%d%H%M')
for f in (J, C): shutil.copy2(os.path.join(R, f), os.path.expanduser('~/app/old/' + f.replace('/', '__') + '.pre-639y-' + t))
open(os.path.join(R, J), 'w', encoding='utf-8').write(s.replace(O, N)); open(os.path.join(R, C), 'w', encoding='utf-8').write(cs.rstrip('\n') + '\n' + CSS)
print('OK 639y – JS/CSS: no restart, reload the pages')
