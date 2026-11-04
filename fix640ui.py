#!/usr/bin/env python3
# fix640ui (CHAT, anh Logan 03/11 22:26 + 22:36): iPhone – nut zoom − / + va "All techs" >= 44px; thu / thang tren thanh ngay de doc hon; nhan nho Payroll / Reports 14px; link Services 44px; o tick Settings 24px.
# Chi THEM CSS cuoi assets/admin-popups.css. Khong doi bo cuc, icon, menu, JS, lich cot, nhan giu keo tha.
# python3 fix640ui.py <release dir>        -> chi kiem
# python3 fix640ui.py <release dir> go     -> sua
import sys, os
R = sys.argv[1]; GO = len(sys.argv) > 2 and sys.argv[2] == 'go'
F = os.path.join(R, 'assets/admin-popups.css')
MARK = '/* (2.99.640ui'
ADD = '''
/* (2.99.640ui - anh Logan 03/11 22:26 muc 2-4) iPhone: vung cham >= 44px (zoom − / +, All techs); thu / thang de doc (11/10px -> 13/12px, thang dam hon, thang tren ngay dang chon mau xanh) */
html[data-app="admin"] .ap-z{border-radius:22px}
html[data-app="admin"] .ap-z button{width:44px;min-height:44px}
html[data-app="admin"] .ap-tk{min-height:44px;padding:10px 14px;border-radius:22px;font-size:15px}
html[data-app="admin"] #dateStrip .day .w{font-size:13px!important}
html[data-app="admin"] #dateStrip .day .m{font-size:12px!important;font-weight:600!important}
html[data-app="admin"] #dateStrip .day.sel .m{color:#2563EB!important}
/* Payroll + Reports: the small grey labels on the number boxes 12-13px -> 14px */
html[data-app="admin"] #prBody .pr-sum span{font-size:14px}
html[data-app="admin"] #rpBody .rp-cards span{font-size:14px}
/* Services & prices: "How turns / rebook work" 22px tall -> 44px, 13px -> 15px */
html[data-app="admin"] .sv-tools .tr-tip.sv-i{min-height:44px;font-size:15px}
/* Settings: the tick boxes 20px -> 24px (the whole line stays tappable) */
html[data-app="admin"] #setBody label.check>input[type="checkbox"]{width:24px;height:24px;flex:none}
'''
s = open(F, encoding='utf-8').read()
a1 = s.count('#dateStrip .day.sel{border-bottom-color:#2563EB!important;background:#E3EDFF!important}')
done = s.count(MARK)
print('anchors', a1, 'done', done)
if done: print('DA CO 640ui – STOP'); sys.exit(1)
if a1 != 1: print('MOC LECH – STOP'); sys.exit(1)
if not GO: print('check OK'); sys.exit(0)
open(F, 'w', encoding='utf-8').write(s.rstrip('\n') + '\n' + ADD)
print('go OK')
