#!/usr/bin/env python3
# fix639u (CHAT, anh Logan 04/11 00:03): Home (Customers page) icon "Gift card" -> "Gift history" / "Lịch sử thẻ" (it opens the gift card list / history;
# selling is "Sell gift card" on Daily). 1 line label + 1 Vietnamese word. Both fit on 1 line at iPhone 390. JS only, no restart.
# python3 fix639u.py <release dir>   (kiem)   /   ... go
import sys, os, shutil, time
a = sys.argv[1:]; go = bool(a) and a[-1] == 'go'
if go: a = a[:-1]
if not a: sys.exit('usage: python3 fix639u.py <release dir> [go]')
R = a[0].rstrip('/')
P = [('assets/admin-core.js', "['giftcard', 'Gift card', '#2E9E4F']", "['giftcard', 'Gift history', '#2E9E4F']"),
     ('assets/i18n-vi-2.js', "'Gift card': 'Thẻ quà tặng'", "'Gift history': 'Lịch sử thẻ', 'Gift card': 'Thẻ quà tặng'")]
txt = {}
for f, o, n in P:
    s = open(os.path.join(R, f), encoding='utf-8').read(); txt[f] = s
    print(f, 'anchors', s.count(o), 'done', s.count(n))
    if s.count(o) != 1 or s.count(n): print('STOP – nothing changed'); sys.exit(1)
if not go: print('check OK – run again with: go'); sys.exit(0)
os.makedirs(os.path.expanduser('~/app/old'), exist_ok=True); t = time.strftime('%m%d%H%M')
for f, o, n in P:
    p = os.path.join(R, f); shutil.copy2(p, os.path.expanduser('~/app/old/' + f.replace('/', '__') + '.pre-639u-' + t))
    open(p, 'w', encoding='utf-8').write(txt[f].replace(o, n))
print('OK 639u – JS: no restart, reload the pages')
