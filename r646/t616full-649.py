# LAMWEB test 612 – Telnyx (test) next to SignalWire: fake Telnyx requests (TeXML form posts, AI webhooks JSON) + fake Telnyx API. Test numbers 555-01xx only.
import subprocess, json, os, sys, time, urllib.request, urllib.parse, shutil, atexit, re, datetime as _dt
A = sys.argv[1]; D = '/tmp/claude-0/T612'; T5 = '/tmp/claude-0/T586'; PORT = 19877; DB = D + '/db.sqlite'
R = []; out = open('/tmp/claude-0/T616/test-616.txt', 'w')
def say(s): print(s); out.write(s + '\n'); out.flush()
def ok(n, c, i=''): R.append(bool(c)); say(('✓ ' if c else '✗ ') + n + ('' if c else '   → ' + str(i)[:600]))
import glob
[os.remove(x) for x in glob.glob(D + '/calls/txg-*.json')]
os.makedirs(D + '/calls', exist_ok=True); open(D + '/fake_tx.log', 'w').close()
ENV = {**os.environ, 'TZ': 'America/Chicago', 'NF_SHARED_DIR': T5 + '/shared', 'NF_CALLS_DIR': D + '/calls', 'NF_TX_BASE': 'http://127.0.0.1:19872/v2',
       'NF_STT_URL': 'http://127.0.0.1:19870/stt', 'NF_AI_URL': 'http://127.0.0.1:19870/ai', 'NF_OAI_URL': 'http://127.0.0.1:19870/oai', 'NF_SW_BASE': 'http://127.0.0.1:19870'}
def sh(*a): return subprocess.run(a, capture_output=True, text=True, env=ENV)
def sql(q): r = sh('php', T5 + '/db.php', DB, q); return json.loads(r.stdout or '[]') if r.returncode == 0 else ('ERR', r.stderr)
shutil.copy('/tmp/claude-0/tdb/base.sqlite', DB)
json.dump({'key': 'sk-test-0000000000000000000000000'}, open(T5 + '/shared/call-ai.json', 'w'))
seed = json.loads(sh('php', T5 + '/seed.php', A, DB, str(PORT)).stdout); S = seed['S']
H = D + '/h612.php'
open(H, 'w').write("""<?php require '%s/inc/core.php'; settings(); require_once '%s/inc/calls.php'; require_once '%s/inc/calls-tx.php'; tx_table(); $a = $argv[1];
if ($a === 'set') { foreach (json_decode($argv[2], true) as $k => $v) set_setting($k, $v); echo '{}'; }
if ($a === 'tok') echo tx_token();
if ($a === 'cfg') echo json_encode(tx_cfg());
if ($a === 'save') { try { echo json_encode(tx_cfg_save(json_decode($argv[2], true))); } catch (RuntimeException $e) { echo json_encode(['err' => $e->getMessage()]); } }
if ($a === 'setup') { require_once '%s/inc/calls-agent.php'; require_once '%s/inc/calls-ivr.php'; echo json_encode(tx_setup($argv[2] ?? '')); }
if ($a === 'kp') { $k = sodium_crypto_sign_keypair(); echo json_encode(['pub' => base64_encode(sodium_crypto_sign_publickey($k)), 'sec' => base64_encode(sodium_crypto_sign_secretkey($k))]); }
if ($a === 'sign') { echo base64_encode(sodium_crypto_sign_detached($argv[3] . '|' . file_get_contents($argv[4]), base64_decode($argv[2]))); }
if ($a === 'swtool') { require '%s/call_tx.php.lib'; }
if ($a === 'mk') { [$_, $_, $ph, $name, $date, $start, $staff] = $argv; upsert_customer($ph, $name);
  q("INSERT INTO appointments (appt_date, start_min, duration, staff_id, service_ids, customer_name, phone, status, source, kind, group_id, created_at) VALUES (?,?,?,?,?,?,?,'booked','admin','appt','',?)", [$date, (int)$start, 45, (int)$staff, '%d', $name, $ph, now_str()]); echo (int)db()->lastInsertId(); }
""" % (A, A, A, A, A, A, S['Pedicure']))
def h(*a):
    r = sh('php', H, *[str(x) for x in a])
    try: return json.loads(r.stdout)
    except Exception: return r.stdout
ALLDAY = json.dumps({str(w): {'open': '00:00', 'close': '23:59'} for w in range(7)})
h('set', json.dumps({'hours': ALLDAY, 'call_owner': '5155550177', 'call_fwd': '+15155550176', 'salon_name': 'AMERICAN NAILS AND SPA', 'call_on': '1'}))
TOK = h('tok')
sv = subprocess.Popen(['php', '-S', '127.0.0.1:%d' % PORT, '-t', A, '/tmp/claude-0/router.php'], env={**ENV, 'PHP_CLI_SERVER_WORKERS': '4'}, stdout=subprocess.DEVNULL, stderr=open(D + '/php.log', 'w')); time.sleep(1.2)
fk = subprocess.Popen(['python3', T5 + '/fake.py'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
ft = subprocess.Popen(['python3', D + '/fake_tx.py'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
atexit.register(lambda: (sv.terminate(), fk.terminate(), ft.terminate())); time.sleep(0.8)
B = 'http://127.0.0.1:%d/call_tx.php' % PORT
SIGN = None
def req(a, body, form=False, tok=None, extra='', hdr=None, sign=True):
    raw = urllib.parse.urlencode(body).encode() if form else json.dumps(body).encode()
    hd = {'Content-Type': 'application/x-www-form-urlencoded' if form else 'application/json', **(hdr or {})}
    if SIGN and sign and 'telnyx-signature-ed25519' not in hd:
        ts = str(int(time.time())); open(D + '/.b', 'wb').write(raw); hd['telnyx-timestamp'] = ts; hd['telnyx-signature-ed25519'] = h('sign', SIGN, ts, D + '/.b')
    u = B + '?a=' + a + '&t=' + (TOK if tok is None else tok) + extra
    try: r = urllib.request.urlopen(urllib.request.Request(u, data=raw, headers=hd), timeout=60); return r.status, r.read().decode()
    except urllib.error.HTTPError as e: return e.code, ''
def row(cid): x = sql("SELECT * FROM calls WHERE call_sid = '%s'" % cid); return x[0] if x else {}
_t = _dt.date.today(); TOM = (_t + _dt.timedelta(days=1)).isoformat()
say('== LAMWEB test 2.99.612 – LENH 612 Telnyx (test) ' + time.strftime('%Y-%m-%d %H:%M %Z') + ' · fake Telnyx (docs shapes: TeXML form posts, assistant webhooks JSON, REST /v2) · nothing real called')
# 0 settings
r = h('save', json.dumps({'key': 'KEY0123456789abcdefTEST_tx_key_99', 'number': '(515) 513-6667', 'on': True}))
ok('0 Settings: key saved encrypted, shown only "…y_99" (never the key)', r.get('keySet') and r.get('keyTail') == 'y_99' and 'KEY0123' not in json.dumps(r) and 'KEY0123' not in json.dumps(sql("SELECT v FROM settings WHERE k = 'tx_key'")), r)
r = h('save', json.dumps({'pub': 'not-a-key'})); ok('0 a wrong Public Key → a clear error', 'Public Key' in r.get('err', ''), r)
r = h('save', json.dumps({'number': '123'})); ok('0 a wrong number → error', 'digits' in r.get('err', ''), r)
# 1 setup against the fake Telnyx API
st = h('setup'); ok('1 "Set up automatically" (TELNYX-API-612 order): key checked (GET /phone_numbers?filter[phone_number]=15155136667, no +) · outbound voice profile (none → created) · TeXML Application · number put on it · AI assistant – each step OK', isinstance(st, list) and [x['t'] for x in st] == ['API key', 'Outbound voice profile', 'TeXML Application', 'Number +15155136667', 'AI assistant'] and all(x['ok'] for x in st), st)
ab = json.load(open(D + '/last-_v__ai_assistants.json'))
ins = ab.get('instructions', '')
ok('1 assistant: the SAME prompt as SignalWire (cl_agent_prompt) with the facts as {{now}} {{days}} {{menu}} {{techs}} {{caller_name}} {{upcoming}}; no "ALREADY played" line; greeting "Thank you for calling American Nails And Spa. Sorry we missed you – how can I help?"',
   all(v in ins for v in ['{{now}}', '{{days}}', '{{menu}}', '{{techs}}', '{{caller_name}}', '{{upcoming}}', 'Never say a price', 'find_appointments']) and 'ALREADY' not in ins and ab.get('greeting') == 'Thank you for calling American Nails And Spa. Sorry we missed you – how can I help?', (ins[:300], ab.get('greeting')))
tl = ab.get('tools', []); wh = [t['webhook']['name'] for t in tl if t['type'] == 'webhook']
ok('1 (616 doi y) tools: 10 webhook tools (cl_agent_ai + transfer_owner CUA MINH) + hangup, KHONG co transfer Telnyx', wh == ['find_appointments', 'check_times', 'book', 'cancel', 'move', 'add_person', 'change_services', 'late', 'add_note', 'transfer_owner']
   and not any(t['type'] == 'transfer' for t in tl) and any(t['type'] == 'hangup' for t in tl), wh)
w0 = [t for t in tl if t['type'] == 'webhook' and t['webhook']['name'] == 'book'][0]['webhook']
ok('1 tool URL = call_tx.php?a=tool&t=<secret>&fn=book, POST, body = the same JSON schema, preset_query_params {"ccid": "{{call_control_id}}"} (the AI cannot change it), timeout 8 s', w0['url'].endswith('a=tool&t=' + TOK + '&fn=book') and w0['method'] == 'POST' and 'persons' in w0['body_parameters']['properties'] and w0.get('preset_query_params') == {'ccid': '{{call_control_id}}'} and [t for t in tl if t['type'] == 'webhook'][0]['timeout_ms'] == 8000, w0)
ok('1 assistant settings (CHAT F/G): model zai-org/GLM-5.3-Flash · voice = Maeve from GET /v2/text-to-speech/voices (no voice set; kept in tx_voice) · STT deepgram/flux en + keyterms (services, techs) · 300 s · idle 30 s · krisp · its own recording ON (2.99.646 anh Logan 05/11: the AI part is recorded as proof) · data_retention on · barge-in (not the greeting) · vars webhook a=vars 4000 ms + defaults "(no data)"',
   ab.get('model') == 'zai-org/GLM-5.3-Flash' and ab['voice_settings']['voice'] == 'Telnyx.Ultra.02a924f6-1111-2222-3333-444455556666' and ab['transcription']['model'] == 'deepgram/flux' and 'pedicure' in ab['transcription']['settings']['keyterm'] and 'tammy' in ab['transcription']['settings']['keyterm']
   and ab['telephony_settings'] == {'time_limit_secs': 300, 'noise_suppression': 'krisp', 'user_idle_timeout_secs': 30, 'recording_settings': {'enabled': True, 'channels': 'dual', 'format': 'mp3'}} and ab['privacy_settings'] == {'data_retention': True}
   and ab['interruption_settings'] == {'enable': True, 'disable_greeting_interruption': True} and ab.get('dynamic_variables_webhook_url', '').endswith('a=vars&t=' + TOK) and ab.get('dynamic_variables_webhook_timeout_ms') == 4000 and ab['dynamic_variables']['days'] == '(no data)', {k: ab.get(k) for k in ['model', 'voice_settings', 'transcription', 'telephony_settings', 'privacy_settings']})
ap = json.load(open(D + '/last-_v__texml_applications.json'))
ok('1 TeXML Application: Voice URL = call_tx.php?a=in&t=<secret> POST + outbound_voice_profile_id (the Dial to the iPhone is an outbound call)', ap.get('voice_url', '').endswith('/call_tx.php?a=in&t=' + TOK) and ap.get('voice_method') == 'post' and ap.get('outbound') == {'outbound_voice_profile_id': 'OVP-1'}, ap)
fl = open(D + '/fake_tx.log').read(); ok('1 the number got the application (PATCH /phone_numbers/PN-1 connection_id APP-1)', 'PATCH /v2/phone_numbers/PN-1 {"connection_id": "APP-1"}' in fl, fl[-400:])
st = h('setup', 'ai'); ok('1 "Update AI" → POST /ai/assistants/assistant-test-1 (update, not a new one)', len(st) == 1 and st[0]['ok'] and 'updated assistant-test-1' in st[0]['msg'], st)
ok('1 (2.99.613) the voice picked once is kept (setting tx_voice), not asked again', 'GET /v2/text-to-speech/voices' in open(D + '/fake_tx.log').read() and open(D + '/fake_tx.log').read().count('GET /v2/text-to-speech/voices') == 1, open(D + '/fake_tx.log').read().count('GET /v2/text-to-speech/voices'))
# 2 security
c, _ = req('in', {'CallSid': 'v3:X', 'From': '+15555550101'}, form=True, tok='wrong'); ok('2 a wrong secret → 403', c == 403, c)
kp = h('kp'); h('save', json.dumps({'pub': kp['pub']})); SIGN = kp['sec']
c, _ = req('status', {'CallSid': 'v3:S'}, form=True); ok('2 Public Key pasted: a correctly signed request (Ed25519 over "timestamp|body") → 200', c == 200, c)
if os.environ.get('NF_DIAG'):  # (621-C) diag.sh: WHY a signed request is refused here – test keys / test copy only, nothing real
    open(A + '/_diag.php', 'w').write("<?php header('Content-Type: application/json'); echo json_encode(['php_time' => time(), 'sapi' => PHP_SAPI, 'php' => PHP_VERSION, 'sodium' => function_exists('sodium_crypto_sign_verify_detached'), 'tz' => date_default_timezone_get(), 'display_errors' => ini_get('display_errors'), 'error_log' => ini_get('error_log'), 'opcache' => ini_get('opcache.enable_cli') . '/' . ini_get('opcache.enable'), 'prepend' => ini_get('auto_prepend_file'), 'sig_hdr' => strlen((string)($_SERVER['HTTP_TELNYX_SIGNATURE_ED25519'] ?? '')), 'ts_hdr' => (string)($_SERVER['HTTP_TELNYX_TIMESTAMP'] ?? ''), 'body_len' => strlen((string)file_get_contents('php://input'))]);")
    def raw(u, data, hd):
        try: r = urllib.request.urlopen(urllib.request.Request(u, data=data, headers=hd), timeout=30); return r.status, r.read().decode()[:200], dict(r.headers)
        except urllib.error.HTTPError as e: return e.code, e.read().decode(errors='replace')[:200], dict(e.headers)
    body = urllib.parse.urlencode({'CallSid': 'v3:S'}).encode(); ts = str(int(time.time())); open(D + '/.b', 'wb').write(body)
    sg = h('sign', SIGN, ts, D + '/.b'); sr = sh('php', H, 'sign', SIGN, ts, D + '/.b')
    hd = {'Content-Type': 'application/x-www-form-urlencoded', 'telnyx-timestamp': ts, 'telnyx-signature-ed25519': str(sg)}
    say('DIAG python time %s · php CLI time %s · ts sent %s' % (int(time.time()), sh('php', '-r', 'echo time();').stdout, ts))
    say('DIAG sign helper: rc %d · stdout len %d (want 88) %r · stderr %r' % (sr.returncode, len(sr.stdout), sr.stdout[:20], sr.stderr[:200]))
    say('DIAG probe php -S: %r' % (raw('http://127.0.0.1:%d/_diag.php' % PORT, body, hd)[:2],))
    st_, bd_, hh_ = raw(B + '?a=status&t=' + TOK, body, hd); say('DIAG signed a=status -> HTTP %s · body %r' % (st_, bd_))
    st2, bd2, _x = raw(B + '?a=status&t=' + TOK, body, {'Content-Type': 'application/x-www-form-urlencoded'}); say('DIAG unsigned a=status -> HTTP %s · body %r' % (st2, bd2))
    pub = sh('php', '-r', "require '%s/inc/core.php'; settings(); require_once '%s/inc/calls-tx.php'; echo tx_pub();" % (A, A))
    say('DIAG tx_pub (DB, giai ma): %s · stderr %r' % ('GIONG key test' if pub.stdout.strip() == kp['pub'] else 'KHAC: len %d %r' % (len(pub.stdout), pub.stdout[:12]), pub.stderr[:200]))
    vr = sh('php', '-r', "$k = base64_decode('%s'); $p = substr($k, 32); echo sodium_crypto_sign_verify_detached(base64_decode('%s'), '%s|' . file_get_contents('%s'), $p) ? 'verify CLI OK' : 'verify CLI SAI';" % (SIGN, str(sg).strip(), ts, D + '/.b'))
    say('DIAG verify trong CLI: %r %r' % (vr.stdout[:40], vr.stderr[:200]))
    say('DIAG php.log (cuoi, bo Accepted/Closing): ' + ' | '.join([l for l in open(D + '/php.log').read().splitlines() if 'Accepted' not in l and 'Closing' not in l][-6:])[-700:])
    sys.exit(0)
c, _ = req('status', {'CallSid': 'v3:S'}, form=True, hdr={'telnyx-timestamp': str(int(time.time())), 'telnyx-signature-ed25519': 'A' * 88}); ok('2 a wrong signature → 403', c == 403, c)
ts = str(int(time.time()) - 400); open(D + '/.b', 'wb').write(b'CallSid=v3%3AS'); sg = h('sign', SIGN, ts, D + '/.b')
c, _ = req('status', {'CallSid': 'v3:S'}, form=True, hdr={'telnyx-timestamp': ts, 'telnyx-signature-ed25519': sg}); ok('2 a signature older than 5 minutes → 403', c == 403, c)
c, _ = req('status', {'CallSid': 'v3:S', 'ConnectionId': 'APP-1'}, form=True, sign=False); ok('2 no signature header (Telnyx may not sign the TeXML fetch): the secret + ConnectionId = our app → allowed (logged)', c == 200, c)
c, _ = req('status', {'CallSid': 'v3:S', 'ConnectionId': 'OTHER'}, form=True, sign=False); ok('2 no signature + another ConnectionId → 403', c == 403, c)
h('set', json.dumps({'tx_sig_strict': '1'})); c, _ = req('status', {'CallSid': 'v3:S'}, form=True, sign=False); h('set', json.dumps({'tx_sig_strict': '0'})); ok('2 tx_sig_strict = 1: no signature → 403', c == 403, c)
ok('2 the Public Key is kept encrypted too', 'Public' not in json.dumps(sql("SELECT v FROM settings WHERE k = 'tx_pub'")) and kp['pub'] not in json.dumps(sql("SELECT v FROM settings WHERE k = 'tx_pub'")), '')
# 3 the call comes in
c, x = req('in', {'CallSid': 'v3:CA1', 'From': '+15555550102', 'To': '+15155136667', 'AccountSid': 'ACC1'}, form=True)
ok('3 TeXML: <Say> only "This call may be recorded." → <Dial timeout=20 answerOnBridge callerId=caller record=record-from-answer-dual recordingStatusCallback=a=rec action=a=after><Number machineDetection>+15155550176',
   c == 200 and '<Say voice="woman" language="en-US">This call may be recorded.</Say>' in x and 'timeout="20"' in x and 'answerOnBridge="true"' in x and 'callerId="+15555550102"' in x and 'record="record-from-answer-dual"' in x
   and 'recordingChannels="dual"' in x and 'a=rec&amp;t=' + TOK + '&amp;sid=v3%3ACA1' in x and 'a=after&amp;t=' + TOK in x and 'machineDetection="Enable"' in x and 'url="' in x and 'a=screen&amp;t=' + TOK in x and '>+15155550176</Number></Dial>' in x and x.startswith('<?xml'), x)
r3 = row('v3:CA1'); ok('3 the calls row: Telnyx CallSid, the caller\'s number, ring, prov tx', r3.get('from_phone') == '+15555550102' and r3.get('status') == 'ring' and r3.get('prov') == 'tx', r3)
c, x = req('in', {'CallSid': 'v3:CA2', 'From': 'anonymous', 'To': '+15155136667'}, form=True)
ok('3 a blocked / private number → the 594 sentence + hang up (no ring, no recording)', "Sorry, we can&apos;t take calls from a blocked or private number" in x and '<Hangup/>' in x and '<Dial' not in x, x)
h('set', json.dumps({'tx_on': '0'})); c, x = req('in', {'CallSid': 'v3:CA3', 'From': '+15555550103'}, form=True); h('set', json.dumps({'tx_on': '1'}))
ok('3 Telnyx turned off → "please call the salon" + hang up', 'Please call the salon' in x and '<Hangup/>' in x and '<Dial' not in x, x)
# 4 the Dial ended
c, x = req('after', {'CallSid': 'v3:CA1', 'DialCallStatus': 'completed', 'DialCallDuration': '35'}, form=True, extra='&sid=v3%3ACA1')
ok('4 the iPhone answered → <Hangup/>, the call = talked', '<Hangup/>' in x and '<Connect' not in x and row('v3:CA1')['status'] == 'talked', (x, row('v3:CA1').get('status')))
req('in', {'CallSid': 'v3:CB1', 'From': '+15555550111', 'To': '+15155136667'}, form=True)
c, x = req('after', {'CallSid': 'v3:CB1', 'DialCallStatus': 'no-answer'}, form=True, extra='&sid=v3%3ACB1')
ok('4 no answer → <Connect action=a=aiend><AIAssistant id="assistant-test-1"/></Connect>', '<Connect action="' in x and 'a=aiend&amp;t=' + TOK in x and '<AIAssistant id="assistant-test-1">' in x, x)
for k, s in [('CB2', 'busy'), ('CB3', 'failed'), ('CB4', 'canceled')]:
    req('in', {'CallSid': 'v3:' + k, 'From': '+15555550112', 'To': '+15155136667'}, form=True); c, x = req('after', {'CallSid': 'v3:' + k, 'DialCallStatus': s}, form=True, extra='&sid=v3%3A' + k)
    ok('4 ' + s + ' (declined) → the AI', '<AIAssistant' in x, x)
req('in', {'CallSid': 'v3:CB5', 'From': '+15555550113', 'To': '+15155136667'}, form=True)
c, x = req('screen', {'CallSid': 'v3:CB5-leg'}, form=True, extra='&sid=v3%3ACB5'); ok('4 a=screen (the iPhone leg, before it is connected): <Gather speech 3 s> → a=screened', '<Gather input="speech"' in x and 'a=screened&amp;t=' + TOK in x, x)
c, x = req('screened', {'SpeechResult': "Hi you've reached Logan, please leave a message after the tone", 'AccountSid': 'ACC1'}, form=True, extra='&sid=v3%3ACB5'); time.sleep(0.5); ok('4 the iPhone\'s own voicemail greeting heard → that leg hangs up, the call marked vmai + the caller moved to the AI (612b: REST update call with <Connect><AIAssistant>)', '<Hangup/>' in x and row('v3:CB5')['screen'] == 'vmai' and 'POST /v2/texml/Accounts/' in open(D + '/fake_tx.log').read() and 'AIAssistant' in open(D + '/fake_tx.log').read(), (x, row('v3:CB5').get('screen')))
c, x = req('after', {'CallSid': 'v3:CB5', 'DialCallStatus': 'completed'}, form=True, extra='&sid=v3%3ACB5')
ok('4 … the Dial says "completed" but it was the voicemail → the AI, not the iPhone voicemail', '<AIAssistant' in x, x)
req('in', {'CallSid': 'v3:CB6', 'From': '+15555550114', 'To': '+15155136667'}, form=True)
c, x = req('screened', {'SpeechResult': 'Hello?'}, form=True, extra='&sid=v3%3ACB6'); ok('4 a person answers ("Hello?") → connected (empty Response) + marked person (612p)', x.endswith('<Response></Response>') and row('v3:CB6').get('screen') == 'person', (x, row('v3:CB6').get('screen')))
req('amd', {'CallSid': 'v3:CB6', 'AnsweredBy': 'machine_start'}, form=True, extra='&sid=v3%3ACB6'); c, x = req('after', {'CallSid': 'v3:CB6', 'DialCallStatus': 'completed'}, form=True, extra='&sid=v3%3ACB6')
ok('4 (612p doi y) "Hello?" + AMD machine → KHONG chuyen (nguoi da noi), Dial completed → <Hangup/>', '<Hangup/>' in x and '<AIAssistant' not in x and row('v3:CB6').get('screen') == 'person', (x, row('v3:CB6').get('screen')))
# 5 dynamic variables
ap1 = h('mk', '+15555550111', 'MAI TEST', TOM, 600, seed['T']['TAMMY'] if isinstance(seed['T'], dict) else 0)
t0 = time.time(); c, x = req('vars', {'data': {'event_type': 'assistant.initialization', 'payload': {'telnyx_end_user_target': '+15555550111', 'telnyx_agent_target': '+15155136667', 'call_control_id': 'v3:CB1', 'assistant_id': 'assistant-test-1'}}}); ms = (time.time() - t0) * 1000
dv = json.loads(x or '{}').get('dynamic_variables', {})
ok('5 a=vars: {"dynamic_variables": {now, days, menu, techs, caller_name, upcoming, call_ref}} in %d ms (< 300)' % ms, ms < 300 and dv.get('call_ref') == str(row('v3:CB1')['id']) and 'Pedicure' in dv.get('menu', '') and dv.get('caller_name', '').lower().startswith('mai') and ('appt_id %s' % ap1) in dv.get('upcoming', ''), dv)
c, x = req('vars', {'data': {'payload': {'telnyx_end_user_target': '+15555550111', 'call_control_id': 'v3:UNKNOWN'}}}); dv2 = json.loads(x).get('dynamic_variables', {})
ok('5 call control id not known → the same caller\'s Telnyx call of the last 15 min', dv2.get('call_ref') == str(row('v3:CB1')['id']), dv2)
# 6 tools = the SignalWire code
REF = row('v3:CB1')['id']
c, x = req('tool', {}, extra='&fn=find_appointments&ccid=v3%3ACB1'); fa = json.loads(x).get('result', '')
ok('6 find_appointments → {"result": …} the caller\'s appointment (number of THE CALL)', ('appt_id %s' % ap1) in fa or str(ap1) in fa, fa)
swr = sh('php', '-r', "define('NF_API_LIB',1); require '%s/inc/core.php'; settings(); foreach (['/inc/outbox.php','/inc/api/_auth.php','/inc/api/_menu.php','/inc/api/_texts.php','/inc/api/_kiosk.php','/inc/api/_out.php'] as $f) require_once '%s'.$f; require_once '%s/api.php'; require_once '%s/inc/calls-job.php'; require_once '%s/inc/calls-ivr.php'; require_once '%s/inc/calls-agent.php'; require_once '%s/inc/replies.php'; echo json_encode(cl_agent_tool(['function'=>'find_appointments','argument'=>['parsed'=>[[]]],'caller_id_num'=>'+15555550111','call_id'=>'swcmp1']));" % ((A,) * 7)).stdout
ok('6 the same answer as SignalWire\'s cl_agent_tool for the same caller', json.loads(swr or '{}').get('response') == fa, (swr[:200], fa[:200]))
c, x = req('tool', {'date': TOM, 'time': '14:00', 'persons': [{'name': 'Mai', 'service_ids': [S['Pedicure']], 'tech_id': 0}], 'new_ok': True, 'caller_number': '+15555550199'}, extra='&fn=book&ccid=v3%3ACB1')
bk = json.loads(x).get('result', '')
ok('6 book (same day: ALREADY_HAS → new_ok, like SignalWire; a number in the body is ignored) → booked for +15555550111, the number of the call', len(sql("SELECT id FROM appointments WHERE phone = '+15555550111' AND start_min = 840 AND status = 'booked'")) == 1 and not sql("SELECT id FROM appointments WHERE phone = '+15555550199'"), bk)
c, x = req('tool', {}, extra='&fn=find_appointments&ccid={{call_control_id}}'); ok('6 ccid not filled in → "connect you to the salon" (never a guess)', 'connect you to the salon' in json.loads(x).get('result', ''), x)
c, x = req('tool', {}, extra='&fn=find_appointments&ccid=v3%3ANOPE'); ok('6 a ccid of no Telnyx call → "connect you to the salon"', 'connect you to the salon' in json.loads(x).get('result', ''), x)
c, x = req('tool', {}, extra='&fn=find_appointments'); ok('6 no ccid → "connect you to the salon"', 'connect you to the salon' in json.loads(x).get('result', ''), x)
# 7 the AI ended
c, x = req('aiend', {'CallSid': 'v3:CB1', 'Reason': 'hangup'}, form=True, extra='&sid=v3%3ACB1'); time.sleep(1.5)
r7 = row('v3:CB1')
ok('7 aiend (hangup) → <Hangup/>; the transcript fetched (GET /ai/conversations?metadata->call_control_id=eq.v3:CB1 → messages) → text_c / text_s / summary like SignalWire', '<Hangup/>' in x and 'pedicure tomorrow at 2' in (r7.get('text_c') or '') and "You're all set" in (r7.get('text_s') or '') and 'summary' in (r7.get('ai_json') or ''), (x, r7.get('text_c'), r7.get('text_s')))
ok('7 the booking made by the tool stays; the call shows booked (not "Needs review")', r7.get('status') not in ('ring', 'review'), r7.get('status'))
c, x = req('aiend', {'CallSid': 'v3:CB2', 'Reason': 'service_error'}, form=True, extra='&sid=v3%3ACB2')
ok('7 (616 doi y) aiend service_error → <Dial timeout="20" action=a=xfer> the owner phone (+15155550177)', '<Dial timeout="20"' in x and 'a=xfer' in x and '+15155550177</Dial>' in x, x)
# 7b the cron: an AI call still without its transcript
req('in', {'CallSid': 'v3:CC1', 'From': '+15555550115', 'To': '+15155136667'}, form=True); req('after', {'CallSid': 'v3:CC1', 'DialCallStatus': 'no-answer'}, form=True, extra='&sid=v3%3ACC1')
sql("UPDATE calls SET created_at = '%s' WHERE call_sid = 'v3:CC1'" % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - 120)))
due = sh('php', '-r', "require '%s/inc/core.php'; settings(); require_once '%s/inc/calls-tx.php'; echo tx_due() ? 'yes' : 'no';" % (A, A)).stdout
c, _ = req('sweep', {}); time.sleep(2); r7b = row('v3:CC1')
ok('7 cron (1 min, cron/turn.php → a=sweep): an AI call without its transcript after 1 min → fetched', due == 'yes' and 'pedicure tomorrow at 2' in (r7b.get('text_c') or ''), (due, r7b.get('text_c')))
# 649 the owner answered and the CALLER hung up first (no Dial action): never "missed", no missed text, the recording is read
req('in', {'CallSid': 'v3:Z649A', 'From': '+15555550131', 'To': '+15155136667', 'AccountSid': 'ACC1'}, form=True)
req('amd', {'CallSid': 'v3:Z649AL', 'AnsweredBy': 'human'}, form=True, extra='&sid=v3%3AZ649A')
req('status', {'CallSid': 'v3:Z649A', 'CallStatus': 'completed'}, form=True); rb = row('v3:Z649A')
ok('649 answered by the owner, caller hung up first -> NOT missed, no missed-call text', rb.get('status') == 'ring' and rb.get('tb_state', '') in ('', 'off'), rb)
c, _ = req('rec', {'CallSid': 'v3:Z649A', 'RecordingSid': 'RECZ649', 'RecordingUrl': 'http://127.0.0.1:19872/media/REC1.mp3', 'RecordingDuration': '40', 'RecordingStatus': 'completed', 'AccountSid': 'ACC1', 'RecordingChannels': '2'}, form=True, extra='&sid=v3%3AZ649A')
time.sleep(4); rb = row('v3:Z649A')
ok('649 ... its recording is kept and read (like any answered call)', rb.get('file', '').endswith('.wav') and rb.get('status') not in ('ring', 'missed'), rb)
req('in', {'CallSid': 'v3:Z649B', 'From': '+15555550132', 'To': '+15155136667', 'AccountSid': 'ACC1'}, form=True)
req('status', {'CallSid': 'v3:Z649B', 'CallStatus': 'completed'}, form=True); rb2 = row('v3:Z649B')
ok('649 hung up while still ringing (never answered) -> missed + the missed-call text, as before', rb2.get('status') == 'missed' and rb2.get('tb_state') in ('wait', 'off'), rb2)
# 8 recording of an answered call
c, _ = req('rec', {'CallSid': 'v3:CA1', 'RecordingSid': 'REC1', 'RecordingUrl': 'http://127.0.0.1:19872/media/REC1.mp3', 'RecordingDuration': '35', 'RecordingStatus': 'completed', 'AccountSid': 'ACC1', 'RecordingChannels': '2'}, form=True, extra='&sid=v3%3ACA1')
time.sleep(4); r8 = row('v3:CA1'); fl = open(D + '/fake_tx.log').read()
ok('8 a=rec: the file fetched AT ONCE without a key (RecordingUrl lives 10 min), WAV kept, deleted on Telnyx (DELETE …/Recordings/REC1.json), then read at once (cl_job)', r8.get('file', '').endswith('.wav') and 'GET media /media/REC1.wav auth \n' in fl and 'DELETE /v2/texml/Accounts/ACC1/Recordings/REC1.json auth True' in fl and r8.get('status') not in ('queued', 'talked', 'ring', 'work'), (r8.get('file'), r8.get('status'), r8.get('reason'), fl[-300:]))
req('in', {'CallSid': 'v3:CA9', 'From': '+15555550119', 'To': '+15155136667'}, form=True); req('after', {'CallSid': 'v3:CA9', 'DialCallStatus': 'completed'}, form=True, extra='&sid=v3%3ACA9')
c, _ = req('rec', {'CallSid': 'v3:CA9', 'RecordingSid': 'REC9', 'RecordingUrl': 'http://127.0.0.1:19872/media/EXPIRED9.wav', 'RecordingDuration': '20', 'RecordingStatus': 'completed', 'AccountSid': 'ACC1'}, form=True, extra='&sid=v3%3ACA9')
time.sleep(3); fl = open(D + '/fake_tx.log').read()
ok('8 link expired (403) → retried with the key (Telnyx host) → GET /v2/recordings/REC9 → download_urls.wav → kept', row('v3:CA9').get('file', '').endswith('.wav') and 'GET /v2/recordings/REC9' in fl, (row('v3:CA9').get('file'), row('v3:CA9').get('reason')))
# 9 SignalWire unchanged + no secrets
logs = open(D + '/php.log').read()
ok('9 no PHP warnings / errors; the key / secret / Public Key never logged', not any(w in logs for w in ['PHP Warning', 'PHP Fatal', 'PHP Deprecated', 'Uncaught']) and 'KEY0123' not in logs and TOK not in logs, [l for l in logs.splitlines() if 'PHP' in l][:5])
ok('9 Telnyx payloads logged (first 10 of each kind, field names) for CHAT', '612 tx in #1' in logs and '612 tx after #1' in logs, '')
import threading, glob
# ===== LENH-615 muc 15/16: 612b..q + loi tim thay (LAMWEB) =====
say('== 615 – test them cho 612b..q (moi ban 1-2 test) + loi review')
def reqp(a, body, extra):
    raw = urllib.parse.urlencode(body).encode(); hd = {'Content-Type': 'application/x-www-form-urlencoded'}
    if SIGN:
        ts = str(int(time.time())); bf = D + '/.b-' + str(threading.get_ident()); open(bf, 'wb').write(raw); hd['telnyx-timestamp'] = ts; hd['telnyx-signature-ed25519'] = h('sign', SIGN, ts, bf)
    return hd, raw, B + '?a=' + a + '&t=' + TOK + extra
def fire(hd, raw, u):
    try: r = urllib.request.urlopen(urllib.request.Request(u, data=raw, headers=hd), timeout=60); return r.status
    except urllib.error.HTTPError as e: return e.code
def rd(sid): return open(D + '/fake_tx.log').read().count('/texml/Accounts/ACC1/Calls/' + urllib.parse.quote(sid, safe=''))
def leg(sid, frm):
    req('in', {'CallSid': sid, 'From': frm, 'To': '+15155136667', 'AccountSid': 'ACC1'}, form=True)
    return '&sid=' + urllib.parse.quote(sid, safe='')
def cb(sid, frm):
    req('in', {'CallSid': sid, 'From': frm, 'To': '+15155136667', 'AccountSid': 'ACC1'}, form=True); req('after', {'CallSid': sid, 'DialCallStatus': 'no-answer'}, form=True, extra='&sid=' + urllib.parse.quote(sid, safe=''))
def tool(sid, fn, **a):
    c, x = req('tool', a, extra='&fn=' + fn + '&ccid=' + urllib.parse.quote(sid, safe=''))
    try: return json.loads(x).get('result', '')
    except Exception: return x
# 612b
e = leg('v3:Q1', '+15555550131'); c, x = req('screened', {'SpeechResult': "You've reached Logan please leave a message after the tone", 'AccountSid': 'ACC1'}, form=True, extra=e); time.sleep(0.4)
ok('612b hop thu iPhone (screened) → leg Hangup + 1 REST "update call" cho cuoc khach + screen vmai + kind agent', '<Hangup/>' in x and rd('v3:Q1') == 1 and row('v3:Q1').get('screen') == 'vmai' and row('v3:Q1').get('kind') == 'agent', (x, rd('v3:Q1'), row('v3:Q1').get('screen')))
fl = urllib.parse.unquote_plus(open(D + '/fake_tx.log').read()); ok('612b REST body = Texml <Connect action=aiend><AIAssistant id="assistant-test-1">', 'Texml=' in fl and 'AIAssistant id="assistant-test-1' in fl and 'a=aiend' in fl, fl[-300:])
# 612c / 612d / 612e: MP3 (mpg123 = /tmp/claude-0/T616/mpg123 stand-in, ffmpeg)
PH = D + '/h615.php'
open(PH, 'w').write("""<?php require '%s/inc/core.php'; settings(); require_once '%s/inc/calls.php'; require_once '%s/inc/calls-tx.php'; tx_table(); $a = $argv[1];
if ($a === 'wav') { $f = cl_dir() . '/.t615.mp3'; copy('%s/x.mp3', $f); try { echo tx_wavify($f) ? 'WAV' : 'FALSE'; } catch (Throwable $e) { echo 'ERR ' . get_class($e) . ': ' . $e->getMessage(); } @unlink($f); }
if ($a === 'fetch') { $n0 = count(glob(cl_dir() . '/.dl-*')); try { tx_fetch((int)$argv[2], 'http://127.0.0.1:19872/media/MP3X1.mp3', 'ACC1', 'MP3X1'); echo 'OK'; } catch (Throwable $e) { echo 'ERR ' . $e->getMessage(); } echo ' dl+' . (count(glob(cl_dir() . '/.dl-*')) - $n0); }
if ($a === 'cli') { tx_cli_mp3(); echo 'done'; }
""" % (A, A, A, D))
def ph(*a, dis=False): return sh('php', *(['-d', 'disable_functions=exec,shell_exec,system,passthru,proc_open,popen'] if dis else []), PH, *[str(x) for x in a]).stdout
r = ph('wav'); ok('612c tx_wavify MP3 2 kenh → WAV (mpg123, CLI)', r == 'WAV', r)
r = ph('wav', dis=True); ok('L4 web (exec TAT) – tx_wavify KHONG nem Error (tra false, de cron 612d/e lam)', r == 'FALSE', r)
cb('v3:Q2', '+15555550132'); qid = int(row('v3:Q2')['id'])
r = ph('fetch', qid, dis=True); ok('L4b exec tat: tx_fetch loi KHONG de lai file tam .dl-* (MP3 moi cuoc)', r.endswith('dl+0'), r)
sql("UPDATE calls SET prov = 'tx', status = 'review', kind = 'call', reason = 'Telnyx recording: exec', rec_sid = 'MP3X2', file = '' WHERE id = %d" % qid)
r = ph('cli'); rq = row('v3:Q2'); fl = open(D + '/fake_tx.log').read()
ok('612d/e cron tx_cli_mp3: cuoc review (MP3) → GET /recordings/MP3X2 → WAV → queued', (rq.get('file') or '').endswith('.wav') and rq.get('status') != 'review', (r, rq.get('status'), rq.get('file'), rq.get('reason')))
ok('L10 (moi) cron tx_cli_mp3 … roi XOA ban ghi am tren Telnyx (DELETE recording MP3X2) nhu duong web', any(l.startswith('DELETE') and 'MP3X2' in l for l in fl.splitlines()), [l for l in fl.splitlines() if 'MP3X2' in l])
# 612f tx_guard
cb('v3:Q3', '+15555550133'); g = [tool('v3:Q3', 'find_appointments') for _ in range(3)]
ok('612f tx_guard: cung tool + cung tham so lan 3 → "STOP … transfer"', 'STOP' in g[2] and 'STOP' not in g[1], [x[:40] for x in g])
# 612h vmpart + PASSED today
e = leg('v3:Q4', '+15555550134'); req('vmpart', {'UnstableSpeechResult': 'the person you are calling is not available', 'AccountSid': 'ACC1'}, form=True, extra=e); time.sleep(0.3)
c, x = req('screened', {'SpeechResult': 'the person you are calling is not available please leave a message after the tone', 'AccountSid': 'ACC1'}, form=True, extra=e); time.sleep(0.3)
ok('612h vmpart "not available" → vmai + chuyen AI NGAY; screened sau → Hangup, KHONG chuyen lan 2', row('v3:Q4').get('screen') == 'vmai' and rd('v3:Q4') == 1 and '<Hangup/>' in x, (rd('v3:Q4'), row('v3:Q4').get('screen'), x))
cb('v3:Q5', '+15555550135'); _pt = time.localtime(time.time() - 300); r = tool('v3:Q5', 'check_times', date=time.strftime('%Y-%m-%d', _pt), time=time.strftime('%H:%M', _pt), persons=[{'name': 'A', 'service_ids': [S['Pedicure']], 'tech_id': 0}])
ok('612h hom nay gio da qua → "PASSED … NEXT <thu>"', r.startswith('PASSED'), r[:120])
# 612k Verizon
e = leg('v3:Q6', '+15555550136'); req('vmpart', {'UnstableSpeechResult': 'your call has been forwarded to an automated voice messaging system', 'AccountSid': 'ACC1'}, form=True, extra=e); time.sleep(0.3)
ok('612k Verizon "has been forwarded to an automated voice messaging system" → vmai + 1 chuyen AI', row('v3:Q6').get('screen') == 'vmai' and rd('v3:Q6') == 1, (row('v3:Q6').get('screen'), rd('v3:Q6')))
# 612l cancel bye + L2
cb('v3:Q7', '+15555550137'); a1 = h('mk', '+15555550137', 'KIM', TOM, 600, 0); a2 = h('mk', '+15555550137', 'KIM', (_t + _dt.timedelta(days=2)).isoformat(), 600, 0)
tool('v3:Q7', 'find_appointments'); r = tool('v3:Q7', 'cancel', appt_id=a1, said_date=TOM, said_time='10:00')
ok('612l huy xong → "Okay, it\'s cancelled. Have a good day!" + hangup', r.startswith('CANCELLED') and 'Have a good day' in r, r[:200])
ok('L2 khach con hen KHAC → KHONG bao bye + cup ngay (con hen co the can huy tiep)', 'hang up right away' not in r, r[-200:])
# 612o
e = leg('v3:Q8', '+15555550138'); req('vmpart', {'UnstableSpeechResult': 'you call', 'AccountSid': 'ACC1'}, form=True, extra=e)
req('amd', {'AnsweredBy': 'machine_end_beep', 'AccountSid': 'ACC1'}, form=True, extra=e); time.sleep(0.3)
c, x = req('screened', {'SpeechResult': 'you call', 'AccountSid': 'ACC1'}, form=True, extra=e); time.sleep(0.3)
ok('612o AMD machine + Gather dung som ("you call", khong co loi chao) → AI, 1 lan chuyen', row('v3:Q8').get('screen') == 'vmai' and rd('v3:Q8') == 1, (row('v3:Q8').get('screen'), rd('v3:Q8'), x))
# 612p
e = leg('v3:Q9', '+15555550139'); req('screened', {'SpeechResult': 'Hello', 'AccountSid': 'ACC1'}, form=True, extra=e); req('amd', {'AnsweredBy': 'machine_start', 'AccountSid': 'ACC1'}, form=True, extra=e); c, x = req('after', {'CallSid': 'v3:Q9', 'DialCallStatus': 'completed', 'DialCallDuration': '40'}, form=True, extra=e)
ok('612p chu noi "Hello" → person; AMD machine sau KHONG chuyen; Dial xong → Hangup', rd('v3:Q9') == 0 and '<Hangup/>' in x and row('v3:Q9').get('kind') == 'call', (rd('v3:Q9'), x, row('v3:Q9').get('kind')))
e = leg('v3:Q10', '+15555550140'); req('vmpart', {'UnstableSpeechResult': 'hi this is the voicemail of', 'AccountSid': 'ACC1'}, form=True, extra=e); c, x = req('screened', {'SpeechResult': '', 'AccountSid': 'ACC1'}, form=True, extra=e)
req('amd', {'AnsweredBy': 'machine_end_other', 'AccountSid': 'ACC1'}, form=True, extra=e); time.sleep(0.3)
ok('612p/q nghe 1-2 s (trong) roi AMD machine + da nghe tieng hop thu → chuyen AI', rd('v3:Q10') == 1 and row('v3:Q10').get('screen') == 'vmai', (rd('v3:Q10'), row('v3:Q10').get('screen')))
# 612q + L8 / L9
e = leg('v3:Q11', '+15555550141'); c, x0 = req('screened', {'SpeechResult': '', 'AccountSid': 'ACC1'}, form=True, extra=e); req('amd', {'AnsweredBy': 'machine_start', 'AccountSid': 'ACC1'}, form=True, extra=e)
ok('612q chu bat may IM LANG (khong nghe gi) + AMD machine → KHONG chuyen', rd('v3:Q11') == 0, rd('v3:Q11'))
c, x = req('after', {'CallSid': 'v3:Q11', 'DialCallStatus': 'completed', 'DialCallDuration': '60'}, form=True, extra=e)
ok('L8 (moi) … chu noi 60 s roi cup → after <Hangup/> (khong dua khach vao AI), kind call', '<Hangup/>' in x and '<AIAssistant' not in x and row('v3:Q11').get('kind') == 'call', (x[-120:], row('v3:Q11').get('screen'), row('v3:Q11').get('kind')))
e = leg('v3:Q12', '+15555550142'); req('amd', {'AnsweredBy': 'machine_start', 'AccountSid': 'ACC1'}, form=True, extra=e); c, x = req('screened', {'SpeechResult': '', 'AccountSid': 'ACC1'}, form=True, extra=e); time.sleep(0.3)
ok('L9 (moi) AMD machine TRUOC, chu im lang (screened rong) → noi may (Response rong), KHONG cup leg chu', x.endswith('<Response></Response>') and rd('v3:Q12') == 0, (x, rd('v3:Q12'), row('v3:Q12').get('screen')))
# L1
e = leg('v3:Q13', '+15555550143'); c, x = req('screened', {'SpeechResult': 'Hello thank you for calling American Nails and Spa how can I help you', 'AccountSid': 'ACC1'}, form=True, extra=e); time.sleep(0.3)
ok('L1 chu chao dai 13 tu ("Hello thank you for calling American Nails and Spa…") → NGUOI, khong chuyen AI', x.endswith('<Response></Response>') and rd('v3:Q13') == 0, (x, rd('v3:Q13'), row('v3:Q13').get('screen')))
# L3 race
bad = []
for k in range(20):
    sid = 'v3:QR%d' % k; e = leg(sid, '+155555501%02d' % (50 + k)); req('vmpart', {'UnstableSpeechResult': 'hello is not', 'AccountSid': 'ACC1'}, form=True, extra=e)
    ev = threading.Event(); pre = [reqp('amd', {'AnsweredBy': 'machine_start', 'AccountSid': 'ACC1'}, e)] + [reqp('vmpart', {'UnstableSpeechResult': 'the person is not available please leave a message' + ' .' * j, 'AccountSid': 'ACC1'}, e) for j in range(3)]
    def g(p, ev=ev): ev.wait(); fire(*p)
    th = [threading.Thread(target=g, args=(p,)) for p in pre]; [t.start() for t in th]; time.sleep(0.2); ev.set(); [t.join() for t in th]; time.sleep(0.2)
    if rd(sid) != 1: bad.append((sid, rd(sid)))
ok('L3 3 vmpart + 1 amd CUNG LUC (20 vong) → moi cuoc chuyen AI DUNG 1 lan', not bad, bad)
# L5
import glob as _gl
nt = len(_gl.glob(D + '/calls/txg-*') + _gl.glob(D + '/calls/txh-*'))
code = open(A + '/inc/calls-tx.php').read() + open(A + '/inc/calls.php').read() + open(A + '/cron/turn.php').read()
ok('L5 file tam txg-*.json / txh-*.txt co duoc don (unlink / glob)', re.search(r"unlink[^;]*tx[gh]-|glob\([^)]*tx[gh]-", code) is not None, '%d file txg/txh trong thu muc ghi am, code khong xoa' % nt)

# ===== 2.99.616 (LENH-616-GOP: 616 + 617) =====
say('== 616 – transfer an toan (B2 / 617.2) · missed call text (617.1) · chong trung (B1) · aiend khong sleep · thoi gian AI (617.4) · don file (617.3)')
def xs(sid): return urllib.parse.quote(sid, safe='')
def flog(): return open(D + '/fake_tx.log').read()
# tools: no Telnyx transfer; transfer_owner = our webhook
st = h('setup', 'ai'); fs_ = sorted(glob.glob(D + '/last-_v__ai_assistants*.json'), key=os.path.getmtime); ab = json.load(open(fs_[-1])); tl = ab.get('tools', [])
wt = [t for t in tl if t['type'] == 'webhook' and t['webhook']['name'] == 'transfer_owner']
ok('616 B2 assistant: KHONG con tool "transfer" cua Telnyx; transfer_owner = webhook cua minh (fn=transfer_owner, ccid)', not any(t['type'] == 'transfer' for t in tl) and wt and 'fn=transfer_owner' in wt[0]['webhook']['url'] and wt[0]['webhook']['preset_query_params'] == {'ccid': '{{call_control_id}}'}, [t['type'] for t in tl])
# the account kept from ?a=in
req('in', {'CallSid': 'v3:X0', 'From': '+15555550160', 'To': '+15155136667', 'AccountSid': 'ACC1'}, form=True)
ok('616 AccountSid giu tu ?a=in (setting tx_acct) – de tool transfer goi REST', sql("SELECT v FROM settings WHERE k = 'tx_acct'") == [{'v': 'ACC1'}], sql("SELECT v FROM settings WHERE k = 'tx_acct'"))
# owner = a different phone -> REST update -> Dial 20 s action=xfer
h('set', json.dumps({'call_owner': '5155550177'})); cb('v3:X1', '+15555550161'); n0 = flog().count('Calls/v3%3AX1')
r = tool('v3:X1', 'transfer_owner', reason='price question'); fl = urllib.parse.unquote_plus(flog())
ok('616 B2 co "Owner phone" (khac iPhone) → REST update call: <Dial timeout="20" action=a=xfer>+15155550177</Dial>; AI chi noi "One moment…"', r.startswith('CONNECTING') and flog().count('Calls/v3%3AX1') == n0 + 1 and '<Dial timeout="20"' in fl and 'a=xfer' in fl and '+15155550177</Dial>' in fl, (r, fl[-260:]))
ok('616 … ket qua cuoc "📞 Transferred to the owner – price question"', 'Transferred to the owner' in (row('v3:X1').get('result') or ''), row('v3:X1').get('result'))
c, x = req('xfer', {'CallSid': 'v3:X1', 'DialCallStatus': 'no-answer'}, form=True, extra='&sid=' + xs('v3:X1'))
ok('616 B2 chu KHONG bat → <Say> "…the salon will call you back shortly" + Hangup (khong vao hop thu), status callback', 'call you back shortly' in x and '<Hangup/>' in x and '<Dial' not in x and row('v3:X1').get('status') == 'callback', (x, row('v3:X1').get('status')))
cb('v3:X2', '+15555550162'); tool('v3:X2', 'transfer_owner'); c, x = req('xfer', {'CallSid': 'v3:X2', 'DialCallStatus': 'completed'}, form=True, extra='&sid=' + xs('v3:X2'))
ok('616 B2 chu bat may → Hangup (xong), khong callback', x.endswith('<Response><Hangup/></Response>') and row('v3:X2').get('status') != 'callback', (x, row('v3:X2').get('status')))
# owner = the iPhone (AN live 22:30) / empty -> no transfer
h('set', json.dumps({'call_owner': '+15155550176'})); cb('v3:X3', '+15555550163'); n0 = flog().count('Calls/v3%3AX3')
r = tool('v3:X3', 'transfer_owner')
ok('616 B2 "Owner phone" = CHINH iPhone (nhu AN 22:30) → KHONG chuyen; AI noi "The salon will call you back shortly" + hangup; status callback', r.startswith('NO_ONE') and 'call you back shortly' in r and flog().count('Calls/v3%3AX3') == n0 and row('v3:X3').get('status') == 'callback', (r, row('v3:X3').get('status')))
h('set', json.dumps({'call_owner': ''})); cb('v3:X4', '+15555550164'); r = tool('v3:X4', 'transfer_owner')
ok('616 B2 "Owner phone" TRONG → giong tren (callback, khong goi iPhone)', r.startswith('NO_ONE') and row('v3:X4').get('status') == 'callback', (r, row('v3:X4').get('status')))
c, x = req('aiend', {'CallSid': 'v3:X4', 'Reason': 'service_error'}, form=True, extra='&sid=' + xs('v3:X4'))
ok('616 B2 aiend loi + khong co ai → <Say> call you back + Hangup (KHONG <Dial> iPhone)', '<Dial' not in x and 'call you back' in x, x)
h('set', json.dumps({'call_owner': '5155550177'})); cb('v3:X5', '+15555550165'); c, x = req('aiend', {'CallSid': 'v3:X5', 'Reason': 'stt_error'}, form=True, extra='&sid=' + xs('v3:X5'))
ok('616 B2 aiend loi + co Owner phone → <Dial timeout="20" action=a=xfer>+15155550177', '<Dial timeout="20"' in x and 'a=xfer' in x and '+15155550177</Dial>' in x, x)
pl = sql("SELECT name FROM sqlite_master WHERE name = 'push_log'")
pu = sql("SELECT title, body FROM push_log WHERE title LIKE '%Call back%' ORDER BY id") if pl else []
ok('616 B2 moi lan callback → push "📞 Call back" cho chu (so khach + ly do)', len(pu) >= 3 and any('555' in (p_['body'] or '') for p_ in pu), pu[-3:] if pu else 'push_log: ' + str(pl))
# 617.1 missed call text
open(D + '/set616.php', 'w').write("<?php require '%s/inc/core.php'; settings(); require_once '%s/inc/android.php'; foreach (['as_on' => '1', 'as_device' => 'android', 'ad_transport' => 'winsms', 'ws_key' => ad_enc('WS_test_key_123456789'), 'call_tb_on' => '1'] as $k => $v) set_setting($k, $v); echo 'ok';" % (A, A))
sh('php', D + '/set616.php')
open(D + '/tick616.php', 'w').write("<?php require '%s/inc/core.php'; settings(); define('NF_API_LIB',1); foreach (['/inc/outbox.php','/inc/api/_auth.php','/inc/api/_menu.php','/inc/api/_texts.php','/inc/api/_kiosk.php','/inc/api/_out.php'] as $f) require_once '%s' . $f; require_once '%s/api.php'; require_once '%s/inc/calls-job.php'; $GLOBALS['actor']=['admin','Owner']; cl_tick(); echo 'ticked';" % (A, A, A, A))
def tick(): return sh('php', D + '/tick616.php')
def mt(ph): return sql("SELECT kind, src, body FROM autosend WHERE phone = '%s' AND kind = 'missed' ORDER BY id" % ph) if sql("SELECT name FROM sqlite_master WHERE name='autosend'") else []
MP = '+15155550197'
cb('v3:NOUSER1', MP); c, x = req('aiend', {'CallSid': 'v3:NOUSER1', 'Reason': 'hangup'}, form=True, extra='&sid=' + xs('v3:NOUSER1')); time.sleep(0.5); tk = tick()
ok('617.1 khach cup khi AI vua chao (khong noi gi) → missed + 1 tin "Sorry we missed your call…" (outbox, khong gui that)', row('v3:NOUSER1').get('status') == 'missed' and len(mt(MP)) == 1, (row('v3:NOUSER1').get('status'), row('v3:NOUSER1').get('tb_state'), mt(MP), tk.stderr[-200:]))
cb('v3:NOUSER2', MP); req('aiend', {'CallSid': 'v3:NOUSER2', 'Reason': 'hangup'}, form=True, extra='&sid=' + xs('v3:NOUSER2')); time.sleep(0.5); tick()
ok('617.1 goi lai trong 30 phut → KHONG gui lan 2', len(mt(MP)) == 1 and row('v3:NOUSER2').get('tb_state') == 'skip', (mt(MP), row('v3:NOUSER2').get('tb_state')))
NP = '+15155550198'
cb('v3:NOCONV1', NP); sql("UPDATE calls SET created_at = '%s' WHERE call_sid = 'v3:NOCONV1'" % time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - 240)))
req('sweep', {}); time.sleep(1.5); tick()
ok('617.1 cup truoc khi AI noi (khong co conversation, > 3 phut) → cron sweep: missed + 1 tin', row('v3:NOCONV1').get('status') == 'missed' and len(mt(NP)) == 1, (row('v3:NOCONV1').get('status'), mt(NP)))
SP = '+15155550196'
req('in', {'CallSid': 'v3:ST1', 'From': SP, 'To': '+15155136667', 'AccountSid': 'ACC1'}, form=True); req('status', {'CallSid': 'v3:ST1', 'CallStatus': 'completed'}, form=True); tick()
ok('617.1 cup khi iPhone dang do chuong (status callback, chua ai bat) → missed + 1 tin', row('v3:ST1').get('status') == 'missed' and len(mt(SP)) == 1, (row('v3:ST1').get('status'), mt(SP)))
cb('v3:TALK1', '+15155550195'); c, x = req('aiend', {'CallSid': 'v3:TALK1', 'Reason': 'hangup'}, form=True, extra='&sid=' + xs('v3:TALK1')); time.sleep(0.5); tick()
ok('617.1 khach CO noi voi AI → KHONG phai missed, khong tin missed call', row('v3:TALK1').get('status') != 'missed' and not mt('+15155550195'), (row('v3:TALK1').get('status'), mt('+15155550195')))
ok('617.4 thoi gian AI noi chuyen (dur_sec tu sent_at / created_at cua messages) > 0', int(row('v3:TALK1').get('dur_sec') or 0) > 0, row('v3:TALK1').get('dur_sec'))
# aiend without the sleeps
cb('v3:NOCONV2', NP); t0 = time.time(); req('aiend', {'CallSid': 'v3:NOCONV2', 'Reason': 'hangup'}, form=True, extra='&sid=' + xs('v3:NOCONV2')); dt = time.time() - t0
ok('616 aiend khong sleep 4 + 10 s (chua co transcript → de cron) – request xong < 3 s', dt < 3, round(dt, 1))
# B1 add_person twice
cb('v3:AD1', '+15555550194'); ad = h('mk', '+15555550194', 'LAN', TOM, 780, 0); tool('v3:AD1', 'find_appointments')
ra = tool('v3:AD1', 'add_person', appt_id=ad, said_date=TOM, said_time='13:00', persons=[{'name': 'Mai', 'service_ids': [S['Pedicure']], 'tech_id': 0}])
rb = tool('v3:AD1', 'add_person', appt_id=ad, said_date=TOM, said_time='13:00', persons=[{'name': 'Mai', 'service_ids': [S['Pedicure']], 'tech_id': 0}])
nm = sql("SELECT COUNT(*) AS n FROM appointments WHERE phone = '+15555550194' AND status = 'booked'")[0]['n']
ok('616 B1 add_person 2 lan cung nguoi (model goi lai) → chi them 1 (2 hen tong)', int(nm) == 2, (nm, ra[:80], rb[:80]))
# 617.2 the hint line
js = open(A + '/assets/admin/calls-tx.js', encoding='utf-8').read()
ok('617.2 Settings → Calls: 1 dong giai thich duoi "Owner phone for questions" (tx-own-hint, sau dong hint cu, khong doi thu tu)', 'tx-own-hint' in js and "querySelector('#clOwn')" in js, '')
# 617.3 clean once an hour
cd_ = D + '/calls'; open(cd_ + '/txg-old.json', 'w').write('{}'); os.utime(cd_ + '/txg-old.json', (time.time() - 90000, time.time() - 90000)); open(cd_ + '/txh-new.txt', 'w').write('x'); os.utime(cd_ + '/txh-new.txt', (time.time(), time.time()))
try: os.remove(cd_ + '/.tx-clean')
except OSError: pass
r = sh('php', '-r', "require '%s/inc/core.php'; settings(); require_once '%s/inc/calls.php'; require_once '%s/inc/calls-tx.php'; tx_tmp_clean(); echo 'ok';" % (A, A, A)).stdout
ok('617.3 don file tam > 24 h (txg-old xoa, txh-new giu), toi da 1 lan / gio (.tx-clean)', not os.path.exists(cd_ + '/txg-old.json') and os.path.exists(cd_ + '/txh-new.txt') and os.path.exists(cd_ + '/.tx-clean'), (r, os.listdir(cd_)[:8]))
h('set', json.dumps({'call_owner': '5155550177'}))
say('PASS %d/%d' % (sum(R), len(R)))
