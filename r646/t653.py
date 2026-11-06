# LAMWEB test 586 – the whole call flow on a local copy (fake SignalWire / STT / Claude; test numbers 555-01xx only). python3 t586.py <app tree>
import subprocess, json, os, sys, time, hmac, hashlib, base64, urllib.request, urllib.parse, shutil
A = sys.argv[1]; D = '/tmp/claude-0/T586'; PORT = 19861; DB = D + '/db.sqlite'; KEY = 'PSK_test_signing_key_0123456789'
R = []; out = open(D + '/test-653.txt', 'w')
def say(s): print(s); out.write(s + '\n'); out.flush()
def ok(n, c, i=''): R.append(bool(c)); say(('✓ ' if c else '✗ ') + n + ('' if c else '   → ' + str(i)[:400]))
def sh(*a): return subprocess.run(a, capture_output=True, text=True, env=ENV)
def sql(q): r = sh('php', D + '/db.php', DB, q); return json.loads(r.stdout or '[]') if r.returncode == 0 else ('ERR', r.stderr)
for f in os.listdir(D + '/calls') if os.path.isdir(D + '/calls') else []: pass
shutil.rmtree(D + '/calls', ignore_errors=True); os.makedirs(D + '/calls'); open(D + '/fake.log', 'w').close()
shutil.copy('/tmp/claude-0/tdb/base.sqlite', DB)
OAI = True
if OAI: json.dump({}, open(D + '/shared/color-ai.json', 'w'))
else: json.dump({'key': 'sk-ant-test-000000000000000000000000'}, open(D + '/shared/color-ai.json', 'w'))
json.dump({'key': 'sk-test-0000000000000000000000000'}, open(D + '/shared/call-ai.json', 'w'))
ENV = {**os.environ, 'TZ': 'America/Chicago', 'NF_SW_BASE': 'http://127.0.0.1:19870', 'NF_STT_URL': 'http://127.0.0.1:19870/stt', 'NF_AI_URL': 'http://127.0.0.1:19870/ai', 'NF_OAI_URL': 'http://127.0.0.1:19870/oai', 'NF_SHARED_DIR': D + '/shared', 'NF_CALLS_DIR': D + '/calls'}
seed = json.loads(sh('php', D + '/seed.php', A, DB, str(PORT)).stdout); S, T, d1 = seed['S'], seed['T'], seed['d1']
GM, PD, FS = S['Gel Manicure'], S['Pedicure'], S['Full Set']
def ai(**k): b = {'intent': 'book', 'customer_name': '', 'customer_phone': '', 'service_ids': [], 'service_text': '', 'tech_id': 0, 'tech_text': '', 'date': d1, 'time': '', 'people': 1, 'salon_side': 'person', 'salon_agreed': False, 'salon_quote': '', 'confidence': 0.95, 'missing': [], 'summary': ''}; b.update(k); return b
scen = {'stt': {
  '3': {'c': '#S1 Hi this is Mia, can I get a gel manicure tomorrow at 2?', 's': 'Sure, tomorrow at 2 is open. OK, see you at 2!'},
  '4': {'c': '#S2 This is Linh, pedicure with Tammy tomorrow at 3 please', 's': 'Let me check the book for you.'},
  '5': {'c': '#S3 How much is a full set?', 's': 'Full set is fifty dollars.'},
  '6': {'c': '#S4 Hi this is Anna, I want a full set tomorrow at 11 with Hana. Thanks!'},
  '7': {'c': '#S5 Bella here, gel manicure tomorrow at 4 with Sisi please, call me back'},
  '8': {'c': '#S6 Hi I want a pedicure tomorrow, Cara', 's': 'ok'},
  '9': {'c': '#S7 Hi Dana, gel manicure tomorrow at noon?', 's': 'Yes ok, noon tomorrow.'},
  '10': {'c': '#S8 chị muốn làm bột thứ bảy 2 giờ, tên Hoa', 's': 'Dạ ok chị, 2 giờ nha.'}},
 'ai': {
  '1': ai(customer_name='Mia', service_ids=[GM], time='14:00', salon_agreed=True, salon_quote='OK, see you at 2', summary='Mia wants a gel manicure tomorrow at 2 PM.'),
  '2': ai(customer_name='Linh', service_ids=[PD], tech_id=T['TAMMY'], tech_text='Tammy', time='15:00', salon_agreed=True, salon_quote='ok sure 3pm', summary='Linh wants a pedicure with Tammy tomorrow 3 PM.'),
  '3': ai(intent='info', summary='Asked the price of a full set.'),
  '4': ai(customer_name='Anna', service_ids=[FS], tech_id=T['HANA'], tech_text='Hana', time='11:00', summary='Voicemail: Anna, full set tomorrow 11 AM with Hana.'),
  '5': ai(customer_name='Bella', service_ids=[GM], tech_id=T['SISI'], tech_text='Sisi', time='16:00', summary='Voicemail: Bella, gel manicure tomorrow 4 PM with Sisi.'),
  '6': ai(customer_name='Cara', service_ids=[PD], time='', salon_agreed=True, salon_quote='ok', confidence=0.9, missing=['time'], summary='Cara wants a pedicure tomorrow, no time.'),
  '7': ai(customer_name='Dana', service_ids=[GM], time='12:00', salon_agreed=True, salon_quote='Yes ok, noon tomorrow', summary='Dana, gel manicure tomorrow at noon.'),
  '8': ai(customer_name='Hoa', service_ids=[FS], time='14:00', date=d1, salon_agreed=True, salon_quote='Dạ ok chị, 2 giờ nha', confidence=0.9, summary='Hoa wants a full set at 2 PM.')}}
json.dump(scen, open(D + '/scen.json', 'w'), ensure_ascii=False)
fk = subprocess.Popen(['python3', D + '/fake.py'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
sv = subprocess.Popen(['php', '-S', '127.0.0.1:%d' % PORT, '-t', A, '/tmp/claude-0/router.php'], env=ENV, stdout=subprocess.DEVNULL, stderr=open(D + '/php.log', 'w')); time.sleep(1.3)
B = 'http://127.0.0.1:%d' % PORT
def post(a, p, sign=True, key=KEY, url=None):
    u = url or (B + '/call_in.php?' + a); body = urllib.parse.urlencode(p).encode(); h = {'Content-Type': 'application/x-www-form-urlencoded'}
    if sign: h['X-SignalWire-Signature'] = base64.b64encode(hmac.new(key.encode(), (u + ''.join(k + p[k] for k in sorted(p))).encode(), hashlib.sha1).digest()).decode()
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, data=body, headers=h), timeout=60); return r.status, r.read().decode()
    except urllib.error.HTTPError as e: return e.code, e.read().decode()
ACC = '11111111-2222-3333-4444-555555555555'
def call(n, frm, sec, stereo=True, vm=False):
    sid = 'CA%04d' % n; rs = 'RE%04d' % n; subprocess.run(['python3', D + '/mkwav.py', rs, str(sec), '1' if stereo else '0'])
    c, x = post('a=answer', {'AccountSid': ACC, 'CallSid': sid, 'From': frm, 'To': '+15156061616', 'CallStatus': 'ringing'})
    if vm: post('a=done', {'AccountSid': ACC, 'CallSid': sid, 'DialCallStatus': 'no-answer'})
    c2, x2 = post('a=rec' + ('&vm=1' if vm else ''), {'AccountSid': ACC, 'CallSid': sid, 'RecordingSid': rs, 'RecordingUrl': '/api/laml/2010-04-01/Accounts/%s/Recordings/%s' % (ACC, rs), 'RecordingStatus': 'completed', 'RecordingDuration': str(sec), 'RecordingChannels': '2' if stereo else '1'})
    for k in range(80):
        row = sql("SELECT * FROM calls WHERE call_sid = '%s'" % sid)
        if row and row[0]['status'] not in ('queued', 'work', 'ring') or (row and row[0]['status'] == 'queued' and row[0]['tries'] >= 1): break
        time.sleep(0.25)
    return (c, x, c2, x2), row
def appt(ph): return sql("SELECT id, appt_date, start_min, staff_id, service_ids, customer_name, status, source, note FROM appointments WHERE phone = '%s' ORDER BY id" % ph)
def push(): return sql("SELECT target, kind, title, body FROM push_log ORDER BY id DESC LIMIT 1") if sql("SELECT name FROM sqlite_master WHERE name='push_log'") else []



open(D + '/set590.php', 'w').write("<?php require '%s/inc/core.php'; settings(); require_once '%s/inc/android.php'; foreach (['as_on' => '1', 'as_device' => 'android', 'ad_transport' => 'winsms', 'ws_key' => ad_enc('WS_test_key_123456789'), 'salon_name' => 'American Nails', 'as_kinds' => json_encode(['confirm' => true, 'change' => true, 'cancel' => true])] as $k => $v) set_setting($k, $v); echo 'ok';" % (A, A))
sh('php', D + '/set590.php')
open(D + '/undo.php', 'w').write("<?php require '%s/inc/core.php'; settings(); define('NF_API_LIB',1); foreach (['/inc/outbox.php','/inc/api/_auth.php','/inc/api/_menu.php','/inc/api/_texts.php','/inc/api/_kiosk.php','/inc/api/_out.php'] as $f) require_once '%s' . $f; require_once '%s/api.php'; require_once '%s/inc/calls-job.php'; $GLOBALS['actor']=['admin','Owner'];\n$a = $argv[1];\nif ($a === 'tick') { cl_tick(); echo 'ticked'; }\n" % (A, A, A, A))
d2 = (__import__('datetime').date.today() + __import__('datetime').timedelta(days=2)).isoformat(); d3 = (__import__('datetime').date.today() + __import__('datetime').timedelta(days=3)).isoformat()
open(D + '/mk592.php', 'w').write("<?php require '%s/inc/core.php'; settings(); [$_, $ph, $name, $date, $start, $staff, $n] = $argv; $g = (int)$n > 1 ? bin2hex(random_bytes(6)) : ''; $ids = [];\nupsert_customer($ph, $name);\nfor ($i = 0; $i < (int)$n; $i++) { q(\"INSERT INTO appointments (appt_date, start_min, duration, staff_id, service_ids, customer_name, phone, status, source, kind, group_id, created_at) VALUES (?,?,?,?,?,?,?,'booked','admin','appt',?,?)\", [$date, (int)$start, 45, (int)$staff + $i * ((int)$staff ? 1 : 0), '%d', $i ? $name . ' +' . $i : $name, $ph, $g, now_str()]); $ids[] = (int)db()->lastInsertId(); }\necho implode(',', $ids);" % (A, S['Pedicure']))
def mk(ph, name, date, start, staff=0, n=1): return [int(x) for x in sh('php', D + '/mk592.php', ph, name, date, str(start), str(staff), str(n)).stdout.split(',')]
def ap(i): return sql("SELECT id, appt_date, start_min, staff_id, status FROM appointments WHERE id = %d" % i)[0]
def ob(i, k): return sql("SELECT kind, ref, status FROM outbox WHERE appt_id = %d AND kind = '%s'" % (i, k))
def lastpush(): return sql("SELECT title, body FROM push_log WHERE target = 'admin' ORDER BY id DESC LIMIT 1")
def go(n, ph, j, tc, ts=None, vm=True):
    scen['stt'][str(n)] = {'c': '#S%d ' % (100 + n) + tc} if ts is None else {'c': '#S%d ' % (100 + n) + tc, 's': ts}
    scen['ai'][str(100 + n)] = j; json.dump(scen, open(D + '/scen.json', 'w'), ensure_ascii=False)
    r, row = call(n, ph, n, stereo=not vm, vm=vm); time.sleep(0.8); return mrow('CA%04d' % n)[0]
def mrow(sid): return sql("SELECT * FROM calls WHERE call_sid = '%s'" % sid)
T1, T2, T3 = T['TAMMY'], T['HANA'], T['SISI']
say('== test 2.99.653 – the tech from last time (owner answered, booked from the recording) ' + time.strftime('%Y-%m-%d %H:%M %Z') + ' · fake SignalWire / STT / AI · texts only into the SMS Server queue')
open(D + '/h594.php', 'w').write("<?php require '%s/inc/core.php'; settings(); require_once '%s/inc/calls.php'; cl_table(); $a = $argv[1];\n"
 "if ($a === 'set') { set_setting($argv[2], $argv[3]); echo 'ok'; }\n"
 "if ($a === 'save') { try { echo json_encode(cl_cfg_save(json_decode($argv[2], true))); } catch (RuntimeException $e) { echo json_encode(['err' => $e->getMessage()]); } }\n"
 "if ($a === 'list') echo json_encode(['l' => cl_list(10), 'n' => cl_badge()]);\n"
 "if ($a === 'poke') { cl_cron_poke(); echo 'poked'; }\n" % (A, A))
def h(*a): r = sh('php', D + '/h594.php', *a); return r.stdout
def P(name='', sids=None, text='', tid=0, tt=''): return {'name': name, 'service_ids': sids or [], 'service_text': text, 'tech_id': tid, 'tech_text': tt}
def grp(ph): return sql("SELECT id, appt_date, start_min, duration, staff_id, service_ids, customer_name, status, source, group_id, note FROM appointments WHERE phone = '%s' AND status <> 'cancelled' ORDER BY id" % ph)
def conf(ph):
    for k in range(12):
        r = sql("SELECT id, kind, ref FROM outbox WHERE phone = '%s' AND kind = 'confirm'" % ph)
        if r: return r
        time.sleep(0.25)
    return r
d2 = (__import__('datetime').date.today() + __import__('datetime').timedelta(days=2)).isoformat()
T1, T2, T3 = T['TAMMY'], T['HANA'], T['SISI']
import atexit; atexit.register(lambda: (sv.terminate(), fk.terminate()))
open(D + '/h602.php', 'w').write("<?php require '%s/inc/core.php'; settings(); require_once '%s/inc/calls.php'; cl_table(); $a = $argv[1];\n"
 "if ($a === 'svc') { $i = 0; foreach (json_decode($argv[2], true) as $s) { q('INSERT INTO services (name, duration, price, sort, active) VALUES (?, ?, ?, ?, 1)', [$s[0], $s[1], $s[2], 10 + $i++]); } echo json_encode(array_column(q('SELECT id, name FROM services WHERE active = 1')->fetchAll(), 'id', 'name')); }\n"
 "if ($a === 'off') { q('UPDATE services SET active = 0 WHERE name = ?', [$argv[2]]); echo '{}'; }\n"
 "if ($a === 'on') { q('UPDATE services SET active = 1 WHERE name = ?', [$argv[2]]); echo '{}'; }\n"
 "if ($a === 'in') { require_once '%s/inc/android.php'; $GLOBALS['actor'] = ['system', 'Android']; echo json_encode(ad_incoming($argv[2], $argv[3])); }\n"
 "if ($a === 'set') { foreach (json_decode($argv[2], true) as $k => $v) set_setting($k, $v); echo '{}'; }\n"
 "if ($a === 'kinds') { require_once '%s/inc/calls-ask.php'; echo json_encode(cla_kinds()); }\n" % (A, A, A, A))
def h(*a):
    r = sh('php', D + '/h602.php', *a)
    try: return json.loads(r.stdout or '{}')
    except Exception: print('RAW', a, r.stdout[:400], r.stderr[:400]); raise
SV = h('svc', json.dumps([['Dip Powder', 45, 40], ['Regular Manicure', 30, 20], ['Gel Pedicure', 50, 45], ['Builder Gel', 75, 60], ['Fill', 45, 35], ['Polish Change', 0, 10]]))
DIP, RMA, GPE, FS2 = SV['Dip Powder'], SV['Regular Manicure'], SV['Gel Pedicure'], SV['Full Set']
K = h('kinds'); ok('K this salon\'s menu → dip = Dip Powder · gel = Gel Manicure (not Builder Gel) · acrylic = Full Set (not Fill) · regular pedicure = Pedicure · gel pedicure = Gel Pedicure', K['dip'] == DIP and K['gel'] == GM and K['acr'] == FS and K['preg'] == PD and K['pgel'] == GPE and K['mreg'] == RMA and K['pdip'] == 0, K)
def asks(ph): return sql("SELECT src, body, state FROM autosend WHERE phone = '%s' AND src LIKE 'ui:callask:%%' ORDER BY id" % ph)
def confs(ph): return sql("SELECT src, kind, state FROM autosend WHERE phone = '%s' AND kind = 'confirm' AND src NOT LIKE 'ui:call%%'" % ph) + sql("SELECT ref FROM outbox WHERE phone = '%s' AND kind = 'confirm'" % ph)
def one(ph): x = sql("SELECT id, service_ids, staff_id, note, duration, status, start_min FROM appointments WHERE phone = '%s' AND status = 'booked' ORDER BY id" % ph); return x
import datetime as _dt
past = (_dt.date.today() - _dt.timedelta(days=20)).isoformat(); older = (_dt.date.today() - _dt.timedelta(days=40)).isoformat()
def visit(ph, name, date, staff, status='paid'):
    sql("INSERT INTO customers (phone, name) SELECT '%s', '%s' WHERE NOT EXISTS (SELECT 1 FROM customers WHERE phone = '%s')" % (ph, name, ph))
    sql("INSERT INTO appointments (appt_date, start_min, duration, staff_id, service_ids, customer_name, phone, status, source, kind, created_at) VALUES ('%s', 660, 45, %d, '%d', '%s', '%s', '%s', 'admin', 'appt', '%s 10:00:00')" % (date, staff, GM, name, ph, status, date))
def pushes(): return sql("SELECT title, body FROM push_log WHERE target = 'admin' ORDER BY id DESC LIMIT 3")
Q = 'Sure, tomorrow at 2 works.'
# 1. owner answered, "the lady from last time, I forgot her name" -> the tech of the last PAID visit (an older visit with another tech is not used)
visit('+15555550181', 'LILY', older, T3); visit('+15555550181', 'LILY', past, T2)
r = go(81, '+15555550181', ai(customer_name='Lily', service_ids=[GM], time='14:00', tech_last=True, salon_agreed=True, salon_quote=Q, summary='Lily wants the tech from last time'), 'Hi this is Lily, gel manicure tomorrow at 2 with the lady who did my nails last time, I forgot her name', Q, vm=False)
a = one('+15555550181')
ok('1 "the tech from last time" → booked with HANA (the last paid visit), not SISI (an older one)', r['status'] == 'booked' and len(a) == 1 and a[0]['staff_id'] == T2, (r['status'], r['reason'], a))
ok('1 the note says "the tech from last time"', a and 'the tech from last time' in a[0]['note'], a)
ok('1 the owner\'s push names her: "– HANA (the tech from last time)"', any(p['title'] == '📞 Booked' and 'HANA (the tech from last time)' in p['body'] for p in pushes()), pushes())
# 2. no past visit -> NOT booked, the owner checks
r = go(82, '+15555550182', ai(customer_name='Nora', service_ids=[GM], time='14:00', tech_last=True, salon_agreed=True, salon_quote=Q, summary='Nora wants the tech from last time'), 'Nora, gel manicure tomorrow at 2, same girl as before', Q, vm=False)
ok('2 no past visit → not booked, reason "wants the tech from last time – no past visit…"', r['status'] != 'booked' and not one('+15555550182') and 'tech from last time' in (r['reason'] or ''), (r['status'], r['reason']))
# 3. only a cancelled / booked (not done) visit -> not used
visit('+15555550183', 'OLGA', past, T2, 'cancelled')
r = go(83, '+15555550183', ai(customer_name='Olga', service_ids=[GM], time='14:00', tech_last=True, salon_agreed=True, salon_quote=Q, summary='x'), 'Olga, gel manicure tomorrow at 2, same tech as before', Q, vm=False)
ok('3 only a CANCELLED visit → not used → not booked', r['status'] != 'booked' and not one('+15555550183'), (r['status'], r['reason']))
# 4. that tech is not working here any more -> not booked
sql("INSERT INTO staff (name, active) VALUES ('GONE TECH', 0)"); gone = sql("SELECT id FROM staff WHERE name = 'GONE TECH'")[0]['id']
visit('+15555550184', 'PIA', past, gone)
r = go(84, '+15555550184', ai(customer_name='Pia', service_ids=[GM], time='14:00', tech_last=True, salon_agreed=True, salon_quote=Q, summary='x'), 'Pia, gel manicure tomorrow at 2, the lady from last time', Q, vm=False)
ok('4 last tech no longer active → not booked (owner checks)', r['status'] != 'booked' and not one('+15555550184'), (r['status'], r['reason']))
# 5. a name said wins over "last time"
visit('+15555550185', 'QUINN', past, T2)
r = go(85, '+15555550185', ai(customer_name='Quinn', service_ids=[GM], time='15:00', tech_id=T1, tech_text='Tammy', tech_last=True, salon_agreed=True, salon_quote='Sure, tomorrow at 3 works.', summary='x'), 'Quinn, gel manicure tomorrow at 3 with Tammy', 'Sure, tomorrow at 3 works.', vm=False)
a = one('+15555550185'); ok('5 a tech NAMED (Tammy) wins over "last time" (Hana)', r['status'] == 'booked' and a and a[0]['staff_id'] == T1 and 'last time' not in a[0]['note'], (r['status'], r['reason'], a))
# 6. that tech is busy at that time -> not booked
visit('+15555550186', 'RUBY', past, T2)
r = go(86, '+15555550186', ai(customer_name='Ruby', service_ids=[GM], time='14:00', tech_last=True, salon_agreed=True, salon_quote=Q, summary='x'), 'Ruby, gel manicure tomorrow at 2, the girl from last time', Q, vm=False)
ok('6 HANA already has Lily at 2 → not booked, owner checks (never a 2nd customer on her)', r['status'] != 'booked' and not one('+15555550186'), (r['status'], r['reason']))
# 7. an old AI answer with no tech_last -> Any tech as before
r = go(87, '+15555550187', ai(customer_name='Sara', service_ids=[GM], time='16:00', salon_agreed=True, salon_quote='Sure, tomorrow at 4 works.', summary='x'), 'Sara, gel manicure tomorrow at 4', 'Sure, tomorrow at 4 works.', vm=False)
a = one('+15555550187'); ok('7 no tech_last (old answer) → booked as before, no "last time" note', r['status'] == 'booked' and a and 'last time' not in a[0]['note'], (r['status'], r['reason'], a))
# 8. the AI schema asks for tech_last (strict: required)
sc = json.loads(sh('php', '-r', "require '%s/inc/core.php'; require_once '%s/inc/calls-job.php'; echo json_encode(cl_ai_schema());" % (A, A)).stdout or '{}')
ok('8 the AI answer schema has tech_last (boolean, required) + the prompt explains it', sc.get('schema', {}).get('properties', {}).get('tech_last') == {'type': 'boolean'} and 'tech_last' in sc['schema']['required'] and 'tech_last' in open(A + '/inc/calls-job.php').read(), sc.get('schema', {}).get('required'))
say('KET QUA: %d/%d' % (sum(R), len(R))); sys.exit(0 if all(R) else 1)
