# LAMWEB test 2.99.654 – LIVE BOOKING while the owner is on a Telnyx call (<Start><Transcription> -> ?a=tr -> txl_in / txl_try; after the call txl_after).
# Fake Telnyx (T612/fake_tx.py :19872) + fake STT / AI (T586/fake.py :19870, answers by the LAST '#S<n>' marker in the prompt). Test numbers 555-01xx only.
# python3 t654.py <app tree>     (setup copied from T616/t616full.py)
import subprocess, json, os, sys, time, urllib.request, urllib.parse, shutil, atexit, re, hashlib, fcntl, glob
A = sys.argv[1]; D = '/tmp/claude-0/T654'; T5 = '/tmp/claude-0/T586'; T12 = '/tmp/claude-0/T612'; PORT = 19878; DB = D + '/db.sqlite'; CD = D + '/calls'
os.makedirs(D, exist_ok=True); shutil.rmtree(CD, ignore_errors=True); os.makedirs(CD)
R = []; out = open(D + '/test-654.txt', 'w')
def say(s): print(s); out.write(s + '\n'); out.flush()
def ok(n, c, i=''): R.append(bool(c)); say(('✓ ' if c else '✗ ') + n + ('' if c else '   → ' + str(i)[:600]))
open(T12 + '/fake_tx.log', 'a').close(); open(T5 + '/fake.log', 'a').close()
ENV = {**os.environ, 'TZ': 'America/Chicago', 'NF_SHARED_DIR': T5 + '/shared', 'NF_CALLS_DIR': CD, 'NF_TX_BASE': 'http://127.0.0.1:19872/v2',
       'NF_STT_URL': 'http://127.0.0.1:19870/stt', 'NF_AI_URL': 'http://127.0.0.1:19870/ai', 'NF_OAI_URL': 'http://127.0.0.1:19870/oai', 'NF_SW_BASE': 'http://127.0.0.1:19870'}
def sh(*a): return subprocess.run(a, capture_output=True, text=True, env=ENV)
def sql(q): r = sh('php', T5 + '/db.php', DB, q); return json.loads(r.stdout or '[]') if r.returncode == 0 else ('ERR', r.stderr)
shutil.copy('/tmp/claude-0/tdb/base.sqlite', DB)
os.makedirs(T5 + '/shared', exist_ok=True)
json.dump({'key': 'sk-test-0000000000000000000000000'}, open(T5 + '/shared/call-ai.json', 'w'))
# the fake AI's scenario file is shared with other suites: kept and put back at the end
SC = T5 + '/scen.json'; SCB = D + '/scen.json.bak'
if os.path.exists(SC): shutil.copy(SC, SCB)
def restore():
    if os.path.exists(SCB): shutil.copy(SCB, SC)
atexit.register(restore)
seed = json.loads(sh('php', T5 + '/seed.php', A, DB, str(PORT)).stdout); S, T, d1 = seed['S'], seed['T'], seed['d1']
GM, PD, FS = S['Gel Manicure'], S['Pedicure'], S['Full Set']
H = D + '/h654.php'
open(H, 'w').write("""<?php require '%s/inc/core.php'; settings(); require_once '%s/inc/calls.php'; require_once '%s/inc/calls-tx.php'; tx_table(); cl_table(); $a = $argv[1];
if ($a === 'set') { foreach (json_decode($argv[2], true) as $k => $v) set_setting($k, $v); echo '{}'; }
if ($a === 'tok') echo tx_token();
if ($a === 'save') { try { echo json_encode(tx_cfg_save(json_decode($argv[2], true))); } catch (RuntimeException $e) { echo json_encode(['err' => $e->getMessage()]); } }
if ($a === 'texts') { echo json_encode(['lines' => txl_lines($argv[2]), 'texts' => txl_texts(txl_lines($argv[2]))]); }
if ($a === 'android') { require_once '%s/inc/android.php'; foreach (['as_on' => '1', 'as_device' => 'android', 'ad_transport' => 'winsms', 'ws_key' => ad_enc('WS_test_key_123456789'), 'salon_name' => 'American Nails', 'as_kinds' => json_encode(['confirm' => true, 'change' => true, 'cancel' => true])] as $k => $v) set_setting($k, $v); echo '{}'; }
""" % (A, A, A, A))
def h(*a):
    r = sh('php', H, *[str(x) for x in a])
    try: return json.loads(r.stdout)
    except Exception: return r.stdout
ALLDAY = json.dumps({str(w): {'open': '00:00', 'close': '23:59'} for w in range(7)})
h('set', json.dumps({'hours': ALLDAY, 'call_owner': '5155550177', 'call_fwd': '+15155550176', 'salon_name': 'AMERICAN NAILS AND SPA', 'call_on': '1'}))
h('android')
r0 = h('save', json.dumps({'key': 'KEY0123456789abcdefTEST_tx_key_99', 'number': '(515) 513-6667', 'on': True}))
TOK = h('tok')
CFG = A + '/inc/config.php'; CFG0 = open(CFG).read()
sv = subprocess.Popen(['php', '-S', '127.0.0.1:%d' % PORT, '-t', A, '/tmp/claude-0/router.php'], env={**ENV, 'PHP_CLI_SERVER_WORKERS': '4'}, stdout=subprocess.DEVNULL, stderr=open(D + '/php.log', 'w')); time.sleep(1.2)
fk = subprocess.Popen(['python3', T5 + '/fake.py'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
ft = subprocess.Popen(['python3', T12 + '/fake_tx.py'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
atexit.register(lambda: (sv.terminate(), fk.terminate(), ft.terminate())); time.sleep(0.8)
B = 'http://127.0.0.1:%d/call_tx.php' % PORT
def req(a, body, extra='', js=False):
    raw = json.dumps(body).encode() if js else urllib.parse.urlencode(body).encode(); hd = {'Content-Type': 'application/json' if js else 'application/x-www-form-urlencoded'}
    try: r = urllib.request.urlopen(urllib.request.Request(B + '?a=' + a + '&t=' + TOK + extra, data=raw, headers=hd), timeout=60); return r.status, r.read().decode()
    except urllib.error.HTTPError as e: return e.code, ''
def xs(sid): return '&sid=' + urllib.parse.quote(sid, safe='')
def row(sid): x = sql("SELECT * FROM calls WHERE call_sid = '%s'" % sid); return x[0] if x else {}
def ai(**k):
    b = {'intent': 'book', 'customer_name': '', 'customer_phone': '', 'service_ids': [], 'service_text': '', 'tech_id': 0, 'tech_text': '', 'date': d1, 'time': '', 'people': 1,
         'salon_side': 'person', 'salon_agreed': True, 'salon_quote': '', 'confidence': 0.95, 'missing': [], 'summary': '', 'party': [], 'same_services': False, 'tech_last': False, 'mani_type': '', 'pedi_type': ''}
    b.update(k); return b
SCEN = {'stt': {}, 'ai': {}}
def setai(n, j): SCEN['ai'][str(n)] = j; json.dump(SCEN, open(SC, 'w'), ensure_ascii=False)
def setstt(c, s): SCEN['stt']['5'] = {'c': c, 's': s}; json.dump(SCEN, open(SC, 'w'), ensure_ascii=False)   # every fake Telnyx recording = T586/wav/RE0003.wav (5 s, 2 channels: quiet = caller, loud = salon)
json.dump(SCEN, open(SC, 'w'))
def nai(): return len([l for l in open(T5 + '/fake.log').read().splitlines() if l.startswith('AI ') or l.startswith('OAI ')])
def fbase(sid): return CD + '/txl-' + hashlib.md5(sid.encode()).hexdigest()
def nlines(sid): f = fbase(sid) + '.jsonl'; return len([l for l in open(f).read().splitlines() if l.strip()]) if os.path.exists(f) else 0
def state(sid):
    try: return json.load(open(fbase(sid) + '.json'))
    except Exception: return {}
def unthrottle(sid):
    st = state(sid)
    if st: st['at'] = 0; json.dump(st, open(fbase(sid) + '.json', 'w'))
def settle(sid, want):
    """wait until the piece is saved and its reading (if any) is over: the state's n moves inside the call's lock, then the lock is free"""
    t0 = time.time()
    while time.time() - t0 < 6 and nlines(sid) < want: time.sleep(0.05)
    t0 = time.time()
    while time.time() - t0 < 1.5 and int(state(sid).get('n', 0)) < nlines(sid): time.sleep(0.05)
    lf = fbase(sid) + '.lock'
    if os.path.exists(lf):
        t0 = time.time(); fh = open(lf, 'a')
        while time.time() - t0 < 20:
            try: fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB); fcntl.flock(fh, fcntl.LOCK_UN); break
            except OSError: time.sleep(0.1)
        fh.close()
    time.sleep(0.15)
def piece(sid, txt, track=None, final='true', fast=False, wait=True, js=False):
    if not fast: unthrottle(sid)
    want = nlines(sid) + 1; b = {'CallSid': sid, 'Transcript': txt, 'AccountSid': 'ACC1'}
    if final is not None: b['IsFinal'] = final
    if track: b['Track'] = track
    c, x = req('tr', b, xs(sid), js=js)
    if wait and c == 200: settle(sid, want)   # (an old release without ?a=tr answers 404: nothing to wait for)
    return c
def call_in(sid, frm):
    c, x = req('in', {'CallSid': sid, 'From': frm, 'To': '+15155136667', 'AccountSid': 'ACC1'}); return x
def human(sid): req('amd', {'CallSid': sid + 'L', 'AnsweredBy': 'human', 'AccountSid': 'ACC1'}, xs(sid))
def hangup(sid): req('after', {'CallSid': sid, 'DialCallStatus': 'completed', 'DialCallDuration': '60'}, xs(sid))
def rec(sid, rs, dur='3'):
    req('rec', {'CallSid': sid, 'RecordingSid': rs, 'RecordingUrl': 'http://127.0.0.1:19872/media/%s.wav' % rs, 'RecordingDuration': dur, 'RecordingStatus': 'completed', 'AccountSid': 'ACC1', 'RecordingChannels': '2'}, xs(sid))
    for k in range(60):
        r = row(sid)
        if r.get('status') not in ('queued', 'work', 'talked', 'ring'): break
        time.sleep(0.25)
    time.sleep(0.3); return row(sid)
def booked(ph): return sql("SELECT id, appt_date, start_min, staff_id, service_ids, customer_name, status, group_id FROM appointments WHERE phone = '%s' AND status = 'booked' ORDER BY id" % ph)
def appt(i): x = sql("SELECT id, start_min, service_ids, status, confirm_state FROM appointments WHERE id = %d" % int(i)); return x[0] if x else {}
def alog(i): return sql("SELECT action, detail FROM appt_log WHERE appt_id = %d ORDER BY id" % int(i))
# one text = its outbox row (+ its Android queue copy autosend src 'ob:<outbox id>', not counted twice) or an autosend row of its own
def texts(ph): return sql("SELECT kind, src, state FROM autosend WHERE phone = '%s' AND kind = 'confirm' AND src NOT LIKE 'ob:%%'" % ph) + sql("SELECT kind, ref, status FROM outbox WHERE phone = '%s' AND kind = 'confirm'" % ph)
def pmax(): x = sql("SELECT MAX(id) AS m FROM push_log"); return int((x[0]['m'] if x and x[0]['m'] else 0) or 0)
def pushes(since): return sql("SELECT title, body FROM push_log WHERE target = 'admin' AND id > %d ORDER BY id" % since)
Q = 'Sure, tomorrow at 2 works.'
say('== LAMWEB test 2.99.654 – live booking on a Telnyx call the owner answered ' + time.strftime('%Y-%m-%d %H:%M %Z') + ' · fake Telnyx / STT / AI · texts only into the queue tables')

# ---------- 1. tx_live off (default) ----------
x = call_in('v3:L1', '+15555550171')
ok('1 tx_live off (default): ?a=in TeXML has NO <Transcription> (the Dial as before)', '<Transcription' not in x and '<Start>' not in x and '<Dial ' in x, x)
human('v3:L1'); n0 = nai(); p0 = pmax()
setai(101, ai(customer_name='Olive', service_ids=[GM], time='14:00', salon_quote=Q))
piece('v3:L1', '#S101 Hi this is Olive, gel manicure tomorrow at 2 please'); piece('v3:L1', Q)
ok('1 off: ?a=tr pieces → no AI reading, nothing booked, no push', nai() == n0 and not booked('+15555550171') and not pushes(p0) and row('v3:L1').get('status') == 'ring', (nai() - n0, booked('+15555550171'), pushes(p0)))

# ---------- 2. tx_live on: the TeXML ----------
h('set', json.dumps({'tx_live': '1'}))
x = call_in('v3:L2', '+15555550172')
cb = 'transcriptionCallback="http://127.0.0.1:%d/call_tx.php?a=tr&amp;t=%s&amp;sid=v3%%3AL2"' % (PORT, TOK)
ok('2 tx_live on: <Start><Transcription transcriptionEngine="Deepgram" transcriptionTracks="both" + the ?a=tr callback (t= + sid=) BEFORE <Dial>',
   '<Start><Transcription ' in x and 'transcriptionEngine="Deepgram"' in x and 'transcriptionTracks="both"' in x and cb in x and 'transcriptionCallbackMethod="POST"' in x
   and '</Start>' in x and x.find('<Start>') < x.find('<Dial ') and x.find('</Start>') < x.find('<Dial ') and '>+15155550176</Number></Dial>' in x, x)
ok('2 … the rest of the TeXML unchanged (the notice first, the Dial records both channels, amd + after callbacks)', x.find('This call may be recorded.') < x.find('<Start>') and 'record="record-from-answer-dual"' in x and 'a=amd&amp;t=' + TOK in x and 'a=after&amp;t=' + TOK in x, x)
h('set', json.dumps({'call_fwd': ''})); x = call_in('v3:L2B', '+15555550172'); h('set', json.dumps({'call_fwd': '+15155550176'}))
ok('2 AI-only path (no forward number): unchanged – no <Transcription>, no Dial to an iPhone', '<Transcription' not in x and '<Start>' not in x and 'machineDetection' not in x, x)

# ---------- 3 + 4 + 5 + 6 + 8: one call the owner answered ----------
SA, PA = 'v3:L3', '+15555550173'
call_in(SA, PA); human(SA)
ok('3 (setup) AMD human → screen human, call still ring', row(SA).get('screen') == 'human' and row(SA).get('status') == 'ring', row(SA))
n0 = nai(); p0 = pmax()
piece(SA, 'Hi this is Mia, I would like a gel manicure please'); piece(SA, 'Sure, which day works for you')
ok('4 pieces before a day / time is said → NO AI reading at all, nothing booked', nai() == n0 and not booked(PA) and nlines(SA) == 2, (nai() - n0, booked(PA), nlines(SA)))
setai(201, ai(customer_name='Mia', service_ids=[GM], time='14:00', salon_quote=Q, summary='Mia gel manicure tomorrow 2 PM'))
piece(SA, '#S201 Tomorrow at 2 please')
ok('3 the day / time said but the salon has not said OK yet → read by the AI, not booked yet', nai() == n0 + 1 and not booked(PA), (nai() - n0, booked(PA)))
piece(SA, Q)
b3 = booked(PA); r3 = row(SA)
ok('3 the salon said OK → booked WHILE the call is still ring (1 appointment, Gel Manicure tomorrow 2 PM)', len(b3) == 1 and b3[0]['start_min'] == 840 and b3[0]['appt_date'] == d1 and b3[0]['service_ids'] == str(GM) and r3.get('status') == 'ring', (b3, r3.get('status'), r3.get('reason')))
ok('3 the calls row: appt_id = the booking, conf_at = \'\' (no text time yet)', b3 and int(r3.get('appt_id') or 0) == b3[0]['id'] and (r3.get('conf_at') or '') == '', {k: r3.get(k) for k in ('appt_id', 'conf_at', 'conf_done', 'status', 'result')})
ok('3 NO confirmation text queued yet (autosend / outbox)', texts(PA) == [], texts(PA))
pp = pushes(p0)
ok('3 the owner\'s push: "📞 Booked (on the call)" (· the text goes after the call), never "📞 Booked"', any(p['title'] == '📞 Booked (on the call)' and 'the text goes after the call' in p['body'] for p in pp) and not any(p['title'] == '📞 Booked' for p in pp), pp)
A1 = b3[0]['id'] if b3 else 0
# 5 a second person
setai(202, ai(customer_name='Mia', time='14:00', people=2, party=[{'name': 'Mia', 'service_ids': [GM], 'service_text': 'gel manicure', 'tech_id': 0, 'tech_text': ''}, {'name': 'Kim', 'service_ids': [PD], 'service_text': 'pedicure', 'tech_id': 0, 'tech_text': ''}], salon_quote=Q, summary='Mia + Kim'))
piece(SA, '#S202 Oh and my sister Kim wants a pedicure too, same time')
b5 = booked(PA); r5 = row(SA)
ok('5 the caller adds a 2nd person → the first booking cancelled (log "Changed on the call")', appt(A1).get('status') == 'cancelled' and any(l['action'] == 'cancelled' and 'Changed on the call' in l['detail'] for l in alog(A1)), (appt(A1), alog(A1)))
ok('5 … a group of 2 booked (only 2 booked rows for that phone, same group, 2 PM), the call still ring, still no text', len(b5) == 2 and b5[0]['group_id'] != '' and b5[0]['group_id'] == b5[1]['group_id'] and all(b['start_min'] == 840 for b in b5) and r5.get('status') == 'ring' and texts(PA) == [], (b5, r5.get('status'), texts(PA)))
G1 = [b['id'] for b in b5]
# 6 the time changes
Q3 = 'Yes 3 is fine'
J203 = ai(customer_name='Mia', time='15:00', people=2, party=[{'name': 'Mia', 'service_ids': [GM], 'service_text': 'gel manicure', 'tech_id': 0, 'tech_text': ''}, {'name': 'Kim', 'service_ids': [PD], 'service_text': 'pedicure', 'tech_id': 0, 'tech_text': ''}], salon_quote=Q3, summary='Mia + Kim at 3')
setai(203, J203)
piece(SA, '#S203 Actually can we make it 3 instead'); piece(SA, Q3)
b6 = booked(PA)
ok('6 the caller changes the time → the 2 PM ones cancelled, 2 people booked at 3 PM (still only 2 booked rows)', all(appt(i).get('status') == 'cancelled' for i in G1) and len(b6) == 2 and all(b['start_min'] == 900 for b in b6), ([appt(i) for i in G1], b6))
G2 = [b['id'] for b in b6]; nb_before = pmax()
# 8 hang up -> the recording says the same
hangup(SA)
nl = nlines(SA); piece(SA, '#S201 late words after the hang-up tomorrow at 2', wait=False); time.sleep(1.2)
ok('8 a piece after the hang-up (call no longer ring) → ignored (not saved, nothing changed)', nlines(SA) == nl and [b['id'] for b in booked(PA)] == G2, (nl, nlines(SA), booked(PA)))
setstt('#S203 Hi this is Mia, gel manicure tomorrow, and my sister Kim a pedicure, can we make it 3', 'Yes 3 is fine')
r8 = rec(SA, 'RECL3'); b8 = booked(PA)
ok('8 recording read with the SAME answer → the live booking is kept (same appointment ids), calls.status = booked', [b['id'] for b in b8] == G2 and r8.get('status') == 'booked' and int(r8.get('appt_id') or 0) == G2[0], (b8, G2, r8.get('status'), r8.get('reason'), r8.get('appt_id')))
time.sleep(0.5)
ok('8 … exactly ONE YOU\'RE BOOKED text for the group', len(texts(PA)) == 1, texts(PA))
pp = pushes(nb_before)
ok('8 … no second "📞 Booked" push (nor a 2nd "Booked (on the call)")', not any(p['title'].startswith('📞 Booked') for p in pp), pp)
ok('8 … the words of the call (.jsonl) are deleted once the call is decided', not os.path.exists(fbase(SA) + '.jsonl'), os.listdir(CD))

# ---------- 9. the recording says something different ----------
SB, PB = 'v3:L9', '+15555550174'
call_in(SB, PB); human(SB)
Q9 = 'Sure, tomorrow at 11 works.'
setai(211, ai(customer_name='Nina', service_ids=[GM], time='11:00', salon_quote=Q9))
piece(SB, '#S211 Hi this is Nina, gel manicure tomorrow at 11'); piece(SB, Q9)
b9 = booked(PB); L9 = b9[0]['id'] if b9 else 0
ok('9 (setup) booked on the call: Gel Manicure 11 AM', len(b9) == 1 and b9[0]['service_ids'] == str(GM), b9)
hangup(SB)
setai(212, ai(customer_name='Nina', service_ids=[PD], time='11:00', salon_quote=Q9))
setstt('#S212 Hi this is Nina, a pedicure tomorrow at 11', Q9)
r9 = rec(SB, 'RECL9'); b9 = booked(PB); time.sleep(0.5)
ok('9 recording with a DIFFERENT answer (pedicure) → the live booking cancelled ("Replaced by the recording")', appt(L9).get('status') == 'cancelled' and any('Replaced by the recording' in l['detail'] for l in alog(L9)), (appt(L9), alog(L9)))
ok('9 … a new one booked from the recording (Pedicure 11 AM), calls.status booked, ONE text', len(b9) == 1 and b9[0]['service_ids'] == str(PD) and b9[0]['id'] != L9 and r9.get('status') == 'booked' and int(r9.get('appt_id') or 0) == b9[0]['id'] and len(texts(PB)) == 1, (b9, r9.get('status'), r9.get('reason'), texts(PB)))

# ---------- 10. the recording does not confirm it ----------
def live_then(sid, ph, n, name, hh, qq):
    call_in(sid, ph); human(sid)
    setai(n, ai(customer_name=name, service_ids=[GM], time='%02d:00' % hh, salon_quote=qq))
    piece(sid, '#S%d Hi this is %s, gel manicure tomorrow at %d' % (n, name, hh % 12 or 12)); piece(sid, qq)
    b = booked(ph); hangup(sid); return b[0]['id'] if len(b) == 1 else 0
# 10a missing time
SC1, PC1 = 'v3:L10A', '+15555550175'; Q10 = 'Sure, tomorrow at 12 works.'
L10 = live_then(SC1, PC1, 221, 'Opal', 12, Q10); p0 = pmax()
setai(222, ai(customer_name='Opal', service_ids=[GM], time='', missing=['time'], salon_quote=Q10))
setstt('#S222 Hi this is Opal, gel manicure tomorrow', Q10)
r10 = rec(SC1, 'RECL10A'); time.sleep(0.5); pp = pushes(p0)
ok('10a recording not bookable (no time) → the live booking stays booked (same id), NO text', L10 and [b['id'] for b in booked(PC1)] == [L10] and texts(PC1) == [], (L10, booked(PC1), texts(PC1)))
ok('10a … calls.status booked, reason "Booked on the call – the recording did not confirm it…", push "📞 Check booking"', r10.get('status') == 'booked' and (r10.get('reason') or '').startswith('Booked on the call – the recording did not confirm it') and any(p['title'] == '📞 Check booking' for p in pp), (r10.get('status'), r10.get('reason'), pp))
# 10b the recording: everything the same but the salon did NOT say OK
SC2, PC2 = 'v3:L10B', '+15555550176'; Q10b = 'Sure, tomorrow at 1 works.'
L10b = live_then(SC2, PC2, 223, 'Pearl', 13, Q10b); p0 = pmax()
setai(224, ai(customer_name='Pearl', service_ids=[GM], time='13:00', salon_agreed=False, salon_quote=''))
setstt('#S224 Hi this is Pearl, gel manicure tomorrow at 1', 'Let me check the book and call you back.')
r10b = rec(SC2, 'RECL10B'); time.sleep(0.5); pp = pushes(p0)
ok('10b recording: same booking but NO salon OK → the live booking stays, NO text, "📞 Check booking"', L10b and [b['id'] for b in booked(PC2)] == [L10b] and texts(PC2) == [] and any(p['title'] == '📞 Check booking' for p in pp), (L10b, booked(PC2), texts(PC2), r10b.get('reason'), pp))
# 10c the recording cannot be read (nothing heard)
SC3, PC3 = 'v3:L10C', '+15555550177'; Q10c = 'Sure, tomorrow at 5 works.'
L10c = live_then(SC3, PC3, 225, 'Quinn', 17, Q10c); p0 = pmax()
setstt('', '')
r10c = rec(SC3, 'RECL10C'); time.sleep(0.5); pp = pushes(p0)
ok('10c recording cannot be read (nothing heard) → the live booking stays, NO text', L10c and [b['id'] for b in booked(PC3)] == [L10c] and texts(PC3) == [], (L10c, booked(PC3), texts(PC3)))
ok('10c … the owner is asked to check it ("📞 Check booking", the call shows booked) – calls-live.php header: "cannot be read / no OK -> stays, NO text, 📞 Check booking"', r10c.get('status') == 'booked' and any(p['title'] == '📞 Check booking' for p in pp), (r10c.get('status'), r10c.get('reason'), pp))

# ---------- 7. not answered by a person ----------
# (2.99.655 - requirement changed, documented: real calls #187/#188 05/11 - the owner ANSWERED but Telnyx AMD said machine (screen 'vm', amd-skip, the call stayed
#  with the owner). 'vm' is now read live; only "not answered yet" (screen empty) and the AI part (kind 'agent' / screen 'vmai') never book live.)
for sid, ph, amd, lab in [('v3:L7A', '+15555550178', None, 'no AMD (screen empty)')]:
    call_in(sid, ph)
    if amd: req('amd', {'CallSid': sid + 'L', 'AnsweredBy': amd, 'AccountSid': 'ACC1'}, xs(sid))
    setai(231, ai(customer_name='Rose', service_ids=[GM], time='18:00', salon_quote='Sure, tomorrow at 6 works.'))
    n0 = nai(); piece(sid, '#S231 Hi this is Rose, gel manicure tomorrow at 6'); piece(sid, 'Sure, tomorrow at 6 works.')
    ok('7 not a person on the iPhone – %s (screen=%r) → ?a=tr never books, no AI reading' % (lab, row(sid).get('screen')), not booked(ph) and nai() == n0 and (row(sid).get('screen') or '') in ('', 'vm'), (booked(ph), nai() - n0, row(sid).get('screen')))
# (2.99.655) AMD guessed 'vm' while the owner answered (the call stays with the owner, kind 'call') -> read live and booked
SV, PV = 'v3:L7B', '+15555550179'
call_in(SV, PV); req('amd', {'CallSid': SV + 'L', 'AnsweredBy': 'machine_start', 'AccountSid': 'ACC1'}, xs(SV))
setai(233, ai(customer_name='Ruth', service_ids=[GM], time='18:30', salon_agreed=True, salon_quote='Sure, tomorrow at 6:30 works.'))
piece(SV, '#S233 Hi this is Ruth, gel manicure tomorrow at 6:30'); piece(SV, 'Sure, tomorrow at 6:30 works.')
ok("7b AMD said machine but the owner talked (screen 'vm', kind 'call' – real calls #187/#188) → booked on the call", row(SV).get('screen') == 'vm' and len(booked(PV)) == 1, (row(SV).get('screen'), row(SV).get('kind'), booked(PV)))
# the AI part (kind 'agent', screen 'vmai') never books live
SA, PA2 = 'v3:L7D', '+15555550181'
call_in(SA, PA2); sql("UPDATE calls SET kind = 'agent', screen = 'vmai' WHERE call_sid = '%s'" % SA)
setai(234, ai(customer_name='Ava', service_ids=[GM], time='19:30', salon_agreed=True, salon_quote='You are booked for 7:30.'))
n0 = nai(); piece(SA, '#S234 Hi this is Ava, gel manicure tomorrow at 7:30'); piece(SA, 'You are booked for 7:30.')
ok('7c the AI part (kind agent / screen vmai) → ?a=tr never books, no AI reading (the AI assistant books itself)', not booked(PA2) and nai() == n0, (booked(PA2), nai() - n0))
# screened 'person' (2.99.591) counts as the owner
SP, PP = 'v3:L7C', '+15555550180'
call_in(SP, PP); req('screened', {'SpeechResult': 'Hello, American Nails', 'AccountSid': 'ACC1'}, xs(SP))
setai(232, ai(customer_name='Sky', service_ids=[GM], time='19:00', salon_quote='Sure, tomorrow at 7 works.'))
piece(SP, '#S232 Hi this is Sky, gel manicure tomorrow at 7'); piece(SP, 'Sure, tomorrow at 7 works.')
ok('7 the screened owner (screen person) → booked on the call', row(SP).get('screen') == 'person' and len(booked(PP)) == 1 and row(SP).get('status') == 'ring', (row(SP).get('screen'), booked(PP)))

# ---------- 11. Track field ----------
SN, PN = 'v3:L11A', '+15555550181'
call_in(SN, PN); human(SN)
setai(241, ai(customer_name='Tess', service_ids=[GM], time='10:00', salon_quote='Sure, tomorrow at 10 works.'))
piece(SN, '#S241 Hi this is Tess, gel manicure tomorrow at 10'); piece(SN, 'Sure, tomorrow at 10 works.')
tx = h('texts', SN); tx = tx if isinstance(tx, dict) else {'lines': [], 'texts': ['', '']}
ok('11 no Track field from Telnyx → both texts = the whole talk, booked', len(booked(PN)) == 1 and tx['texts'][0] == tx['texts'][1] and 'Tess' in tx['texts'][1] and 'Sure, tomorrow at 10 works.' in tx['texts'][0] and all(l['k'] == '' for l in tx['lines']), (booked(PN), tx))
ST, PT = 'v3:L11B', '+15555550182'
call_in(ST, PT); human(ST)
setai(242, ai(customer_name='Uma', service_ids=[GM], time='16:00', salon_quote='Sure, tomorrow at 4 works.'))
piece(ST, '#S242 Hi this is Uma, gel manicure tomorrow at 4', track='inbound'); piece(ST, 'Sure, tomorrow at 4 works.', track='outbound')
tx = h('texts', ST); tx = tx if isinstance(tx, dict) else {'lines': [], 'texts': ['', '']}
ok('11 Track inbound / outbound → caller text vs salon text split (k c / s), booked', [l['k'] for l in tx['lines']] == ['c', 's'] and tx['texts'] == ['#S242 Hi this is Uma, gel manicure tomorrow at 4', 'Sure, tomorrow at 4 works.'] and len(booked(PT)) == 1, (tx, booked(PT)))
SU, PU = 'v3:L11C', '+15555550183'
call_in(SU, PU); human(SU)
setai(243, ai(customer_name='Vera', service_ids=[GM], time='20:00', salon_quote='Sure, tomorrow at 8 works.'))
piece(SU, '#S243 Hi this is Vera, gel manicure tomorrow at 8', track='inbound'); piece(SU, 'Sure, tomorrow at 8 works.', track='inbound')
tx = h('texts', SU); tx = tx if isinstance(tx, dict) else {'lines': [], 'texts': ['x', 'x']}
ok('11 with Track: an "OK" said only on the CALLER\'s leg is not the salon\'s OK → not booked', tx['texts'][1] == '' and not booked(PU), (tx, booked(PU)))

# ---------- 12. IsFinal=false ----------
SF, PF = 'v3:L12', '+15555550184'
call_in(SF, PF); human(SF)
setai(251, ai(customer_name='Wren', service_ids=[GM], time='09:00', salon_quote='Sure, tomorrow at 9 works.'))
n0 = nai(); piece(SF, '#S251 Hi this is Wren, gel manicure tomorrow at 9', final='false', wait=False); piece(SF, 'Sure, tomorrow at 9 works.', final='false', wait=False); time.sleep(1.5)
ok('12 IsFinal=false pieces are ignored (not saved, no AI reading, nothing booked)', nlines(SF) == 0 and nai() == n0 and not booked(PF), (nlines(SF), nai() - n0, booked(PF)))
piece(SF, '#S251 Hi this is Wren, gel manicure tomorrow at 9', final='1'); piece(SF, 'Sure, tomorrow at 9 works.', final=None)
ok('12 … IsFinal=1 / no IsFinal field = final (saved, booked)', nlines(SF) == 2 and len(booked(PF)) == 1, (nlines(SF), booked(PF)))

# ---------- 13. throttle + the max readings ----------
SG, PG = 'v3:L13', '+15555550185'
call_in(SG, PG); human(SG)
setai(261, ai(customer_name='Xena', service_ids=[GM], time='12:30', salon_quote='Sure, tomorrow at 12:30 works.'))
n0 = nai(); piece(SG, '#S261 Hi this is Xena, gel manicure tomorrow at 12:30'); piece(SG, 'Let me check', fast=True)
ok('13 two pieces within 3 s → only ONE AI reading (TXL_GAP)', nai() == n0 + 1 and state(SG).get('reads') == 1 and nlines(SG) == 2, (nai() - n0, state(SG), nlines(SG)))
time.sleep(3.2); piece(SG, 'Sure, tomorrow at 12:30 works.', fast=True)
ok('13 … the next piece after 3 s → read again (all the words: booked)', nai() == n0 + 2 and len(booked(PG)) == 1, (nai() - n0, booked(PG)))
SM, PM = 'v3:L13M', '+15555550186'
call_in(SM, PM); human(SM)
setai(262, ai(customer_name='Yara', service_ids=[GM], time='13:30', salon_quote='Sure, tomorrow at 1:30 works.'))
piece(SM, 'Hello'); st = state(SM); st['reads'] = 60; json.dump(st, open(fbase(SM) + '.json', 'w'))
n0 = nai(); piece(SM, '#S262 Hi this is Yara, gel manicure tomorrow at 1:30'); piece(SM, 'Sure, tomorrow at 1:30 works.')
ok('13 60 readings done (TXL_MAX_N) → no more AI readings on that call, nothing booked', nai() == n0 and not booked(PM), (nai() - n0, booked(PM), state(SM)))

# ---------- 14. one person: party [] vs party [1 entry] = the same booking (no re-booking) ----------
SH, PH = 'v3:L14', '+15555550188'; Q14 = 'Sure, tomorrow at 10:30 works.'
call_in(SH, PH); human(SH)
setai(281, ai(customer_name='Abby', service_ids=[GM], time='10:30', party=[], salon_quote=Q14))
piece(SH, '#S281 Hi this is Abby, gel manicure tomorrow at 10:30'); piece(SH, Q14)
b14 = booked(PH); L14 = b14[0]['id'] if len(b14) == 1 else 0
J282 = ai(customer_name='Abby', service_ids=[], time='10:30', party=[{'name': 'Abby', 'service_ids': [GM], 'service_text': 'gel manicure', 'tech_id': 0, 'tech_text': ''}], salon_quote=Q14)
setai(282, J282); n0 = nai()
piece(SH, '#S282 yes just me, the gel manicure')
ok('14 one person read again as party [1 entry] (service_ids []) → read by the AI but NOT re-booked (same appointment, nothing cancelled)', L14 and nai() == n0 + 1 and [b['id'] for b in booked(PH)] == [L14] and not any('Changed on the call' in l['detail'] for l in alog(L14)), (L14, nai() - n0, booked(PH), alog(L14)))
hangup(SH); setstt('#S282 Hi this is Abby, gel manicure tomorrow at 10:30', Q14)
r14 = rec(SH, 'RECL14'); time.sleep(0.5)
ok('14 … the recording (party [1 entry]) = the same → kept (same id), booked, ONE text', [b['id'] for b in booked(PH)] == [L14] and r14.get('status') == 'booked' and len(texts(PH)) == 1, (booked(PH), r14.get('status'), r14.get('reason'), texts(PH)))

# ---------- 15. the call ends in review before the recording is read (long call) ----------
SL, PL = 'v3:L15', '+15555550189'; Q15 = 'Sure, tomorrow at 9 works.'
call_in(SL, PL); human(SL)
setai(283, ai(customer_name='Beth', service_ids=[GM], time='21:00', salon_quote=Q15))
piece(SL, '#S283 Hi this is Beth, gel manicure tomorrow at 9 at night'); piece(SL, Q15)
b15 = booked(PL); L15 = b15[0]['id'] if len(b15) == 1 else 0
hangup(SL); setstt('#S283 Hi this is Beth, gel manicure tomorrow at 9', Q15); p0 = pmax(); n0 = nai()
r15 = rec(SL, 'RECL15', dur='1300'); time.sleep(0.5); pp = pushes(p0)
ok('15 long call (dur 1300 s > CL_MAX_SEC, not read by the AI) after a live booking → the booking stays (same id), NO text', L15 and nai() == n0 and [b['id'] for b in booked(PL)] == [L15] and texts(PL) == [], (L15, nai() - n0, booked(PL), texts(PL)))
ok('15 … calls.status booked, reason "Booked on the call – Long call…", push "📞 Check booking" (no "📞 Needs review")', r15.get('status') == 'booked' and (r15.get('reason') or '').startswith('Booked on the call – Long call') and any(p['title'] == '📞 Check booking' for p in pp) and not any(p['title'] == '📞 Needs review' for p in pp), (r15.get('status'), r15.get('reason'), pp))

# ---------- 16. JSON body: IsFinal false (a real JSON false) ----------
SJ, PJ = 'v3:L16', '+15555550190'
call_in(SJ, PJ); human(SJ)
piece(SJ, 'Hi this is Cora, gel manicure tomorrow', final=False, js=True, wait=False); time.sleep(1.2)
ok('16 JSON body with "IsFinal": false → ignored (not saved)', nlines(SJ) == 0, nlines(SJ))
piece(SJ, 'Hi this is Cora, gel manicure', final=True, js=True)
ok('16 … JSON "IsFinal": true → saved', nlines(SJ) == 1, nlines(SJ))

# ---------- demo site ----------
SD, PDm = 'v3:LDEMO', '+15555550187'
open(CFG, 'w').write(CFG0.replace("return array(", "return array('demo'=>true, ", 1))
try:
    call_in(SD, PDm); human(SD)
    setai(271, ai(customer_name='Zoe', service_ids=[GM], time='11:30', salon_quote='Sure, tomorrow at 11:30 works.'))
    n0 = nai(); piece(SD, '#S271 Hi this is Zoe, gel manicure tomorrow at 11:30'); piece(SD, 'Sure, tomorrow at 11:30 works.')
    ok('D demo site (is_demo_site) → never booked live, no AI reading', row(SD).get('call_sid') == SD and not booked(PDm) and nai() == n0, (row(SD), booked(PDm), nai() - n0))
finally: open(CFG, 'w').write(CFG0)

# ---------- no PHP errors ----------
time.sleep(0.5); logs = open(D + '/php.log').read()
bad = [l for l in logs.splitlines() if any(w in l for w in ['PHP Warning', 'PHP Fatal', 'PHP Deprecated', 'Uncaught', '654 live', '654 tx tr'])]
ok('Z no PHP warnings / errors, no "654 live" / "654 tx tr" errors; the key / secret never logged', not bad and 'KEY0123' not in logs and TOK not in logs, bad[:6])
say('KET QUA: %d/%d' % (sum(R), len(R))); sys.exit(0 if all(R) else 1)
