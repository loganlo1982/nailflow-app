#!/usr/bin/env python3
# fix639w (CHAT, anh Logan 04/11 00:29): Vietnamese label of the Home icon: "Lịch sử thẻ" -> "Lịch sử gift card" (2 lines at iPhone 390, last row). 1 word in i18n-vi-2.js.
import sys, os, shutil, time
a = sys.argv[1:]; go = bool(a) and a[-1] == 'go'
if go: a = a[:-1]
R = a[0].rstrip('/'); F = os.path.join(R, 'assets/i18n-vi-2.js')
O = "'Gift history': 'Lịch sử thẻ'"; N = "'Gift history': 'Lịch sử gift card'"
s = open(F, encoding='utf-8').read(); print('anchors', s.count(O), 'done', s.count(N))
if s.count(O) != 1 or s.count(N): print('STOP – nothing changed'); sys.exit(1)
if not go: print('check OK'); sys.exit(0)
os.makedirs(os.path.expanduser('~/app/old'), exist_ok=True); shutil.copy2(F, os.path.expanduser('~/app/old/assets__i18n-vi-2.js.pre-639w-' + time.strftime('%m%d%H%M')))
open(F, 'w', encoding='utf-8').write(s.replace(O, N)); print('OK 639w – reload the pages')
