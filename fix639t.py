#!/usr/bin/env python3
# fix639t (CHAT, anh Logan 03/11 23:52 "lam cho 2 ben giong nhau"): Check-in -> Tech out today: the same 2-line help as the hair demo
# (a tech called in sick -> tap the name -> move / Anyone / cancel each booking; each customer gets a text). Text only (EN / VI), 1 file.
# python3 fix639t.py <release dir>   (kiem)   /   ... go
import sys, os, shutil, time
a = sys.argv[1:]; go = bool(a) and a[-1] == 'go'
if go: a = a[:-1]
if not a: sys.exit('usage: python3 fix639t.py <release dir> [go]')
R = a[0].rstrip('/'); F = os.path.join(R, 'assets/admin/checkin.js')
OLD = '<p>Choose the tech who is out. Then move each booking to a free tech, Anyone, or cancel – and queue the texts.</p>'
NEW = ('<p>${LV(\'<b>A tech called in sick or can’t come today?</b> Tap their name below. You will see each of their bookings today: move it to a free tech, to Anyone, or cancel it.\', '
       '\'<b>Thợ gọi báo nghỉ hoặc không đến được hôm nay?</b> Bấm tên thợ bên dưới. Sẽ hiện từng lịch hẹn hôm nay của thợ đó: chuyển sang thợ khác đang rảnh, sang Anyone, hoặc hủy.\')}</p>'
       '<p>${LV(\'📱 Each customer then gets a text about the change, so nobody comes in without knowing.\', \'📱 Mỗi khách sẽ nhận tin nhắn báo thay đổi, nên không ai đến mà không biết.\')}</p>')
s = open(F, encoding='utf-8').read(); n = s.count(OLD)
print('anchors', n, 'done', s.count('A tech called in sick'))
if s.count('A tech called in sick') or n != 1: print('STOP – nothing changed'); sys.exit(1)
if not go: print('check OK – run again with: go'); sys.exit(0)
os.makedirs(os.path.expanduser('~/app/old'), exist_ok=True)
b = os.path.expanduser('~/app/old/assets__admin__checkin.js.pre-639t-' + time.strftime('%m%d%H%M')); shutil.copy2(F, b)
open(F, 'w', encoding='utf-8').write(s.replace(OLD, NEW)); print('OK 639t – backup', b, '– JS: no restart, reload the pages')
