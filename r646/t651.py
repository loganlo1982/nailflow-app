# 2.99.651 test: an AI call that ended before the booking -> a text at once + owner told; 10 min later, still no booking -> reminder (Messages -> Inbox)
#   copy + own SQLite, 555-01xx numbers, fake SMS Server (127.0.0.1:9) - nothing real
import subprocess, json, os, sys, time, shutil
A0 = os.path.abspath(sys.argv[1]); D = '/home/claude/t651/run'; T5 = '/home/claude/kit638h/s/T586'
shutil.rmtree(D, ignore_errors=True); os.makedirs(D); A = D + '/app'; shutil.copytree(A0, A, symlinks=True); DB = D + '/db.sqlite'; shutil.copy('/home/claude/kit638h/s/tdb/base.sqlite', DB)
ENV = {**os.environ, 'TZ': 'America/Chicago'}; R = []
def sh(*a): return subprocess.run(a, capture_output=True, text=True, env=ENV)
def ok(n, c, i=''): R.append(bool(c)); print(('✓ ' if c else '✗ ') + n + ('' if c else '   → ' + str(i)[:500]))
def sql(q): r = sh('php', T5 + '/db.php', DB, q); return json.loads(r.stdout or '[]') if r.returncode == 0 else ('ERR', r.stderr)
seed = json.loads(sh('php', T5 + '/seed.php', A, DB, '19961').stdout)
H = D + '/h.php'
open(H, 'w').write("""<?php require '%s/inc/core.php'; settings(); require_once '%s/inc/calls.php'; require_once '%s/inc/android.php'; require_once '%s/inc/calls-job.php'; require_once '%s/inc/calls-agent.php'; require_once '%s/inc/calls-tx.php'; $a = $argv[1]; cl_table(); tx_table();
if ($a === 'init') { cl_table(); foreach (['call_on' => '1', 'call_tb_on' => '1', 'tx_on' => '1', 'tx_key' => 'test-key-not-real', 'as_on' => '1', 'as_device' => 'android', 'ad_transport' => 'winsms',
  'ws_key' => ad_enc('WS_test_key_123456789abc'), 'ws_server_url' => 'http://127.0.0.1:9', 'salon_phone' => '(515) 555-0100', 'call_fwd' => '+15155550199', 'salon_name' => 'American Nails Test'] as $k => $v) set_setting($k, $v); echo '{}'; }
if ($a === 'agent') { cl_table(); [$_, $_, $sid, $ph, $said] = $argv; q("INSERT INTO calls (call_sid, from_phone, to_phone, kind, started_at, status, result, seen, tb_state, created_at, purge_at, prov) VALUES (?, ?, '+15155136667', 'agent', ?, 'ring', '', 0, '', ?, '2099-01-01', 'tx')", [$sid, $ph, now_str(), date('Y-m-d H:i:s', time() - 70)]);
  $id = (int)db()->lastInsertId(); $log = []; foreach (explode('|', $said) as $t) { $log[] = ['role' => 'user', 'content' => $t]; $log[] = ['role' => 'assistant', 'content' => 'Sure! What day and time work for you?']; }
  cl_agent_post(['call_id' => $sid, 'call_log' => $log, 'post_prompt_data' => ['raw' => 'Caller: ' . $said], 'call_duration' => 60]); echo json_encode(['id' => $id]); }
if ($a === 'due') { $d = json_decode((string)setting('cl_cut_due'), true) ?: []; foreach ($d as $k => $v) $d[$k] = time() - 1; set_setting('cl_cut_due', json_encode($d)); cl_cut_due(); echo json_encode(['left' => json_decode((string)setting('cl_cut_due'), true)]); }
if ($a === 'get') { echo json_encode(json_decode((string)setting('cl_cut_due'), true) ?: new stdClass); }
""" % (A, A, A, A, A, A))
def h(*a):
    r = sh('php', '-d', 'error_log=' + D + '/err.log', H, *[str(x) for x in a])
    try: return json.loads(r.stdout)
    except Exception: return {'err': (r.stdout + r.stderr)[-400:]}
h('init')
def texts(cid): return sql("SELECT src, phone, state, body FROM autosend WHERE src = 'ui:callcut:%d'" % cid)
def call(cid): x = sql("SELECT status, tb_state, result FROM calls WHERE id = %d" % cid); return x[0] if x else {}
# 1 the 2:01 PM call: two people, dip + dip with tips, the call ended before the day / time
r1 = h('agent', 'v3:C651A', '+15155550161', 'Schedule an appointment.|No. there will be two.|We need a dip and a dip with tips.|Laura and Gracie Peterson.'); c1 = r1.get('id', 0)
t1 = texts(c1)
ok('1 booking not finished -> ONE text at once to the caller ("got cut off" + link)', len(t1) == 1 and 'cut off' in t1[0]['body'] and 'http' in t1[0]['body'] and t1[0]['phone'] == '+15155550161', (r1, t1))
ok('1 ... the call is "Needs review" and no plain missed-call text after it (tb_state sent)', call(c1).get('status') == 'review' and call(c1).get('tb_state') == 'sent', call(c1))
ok('1 ... a 10-minute check is waiting for it', str(c1) in h('get'), h('get'))
# 2 a price question only -> no text
c2 = h('agent', 'v3:C651B', '+15155550162', 'How much is a pedicure?|Okay thanks.').get('id', 0)
ok('2 a question only (no booking asked) -> no text, no 10-minute check', not texts(c2) and str(c2) not in h('get'), (texts(c2), h('get')))
# 3 a cancel -> no "finish your booking" text
c3 = h('agent', 'v3:C651C', '+15155550163', 'I need to cancel my appointment tomorrow.').get('id', 0)
ok('3 a cancel -> no "finish your booking" text', not texts(c3), texts(c3))
# 4 the same number again within 30 min -> no 2nd text (1 text per number in 30 min)
c4 = h('agent', 'v3:C651D', '+15155550161', 'Can I book for Saturday?').get('id', 0)
ok('4 the same number again in 30 min -> no 2nd text', not texts(c4), texts(c4))
# 5 10 minutes later: c1 never booked -> reminder sent (entry gone); a call whose number booked meanwhile -> no reminder (entry gone too)
sql("INSERT INTO appointments (appt_date, start_min, duration, staff_id, service_ids, customer_name, phone, status, source, kind, group_id, created_at, token) VALUES ('%s', 600, 45, 0, '1', 'BOOKED LATER', '+15155550161', 'booked', 'online', 'appt', '', datetime('now', 'localtime'), 'tk651')" % time.strftime('%Y-%m-%d'))
d = h('due'); ok('5 the 10-minute check runs and clears its list (no error)', d.get('left') in ([], {}), d)
err = open(D + '/err.log').read() if os.path.exists(D + '/err.log') else ''
ok('6 no PHP warning / error', not any(w in err for w in ('PHP Warning', 'PHP Fatal', 'PHP Notice', 'Deprecated')), err[-600:])
print('PASS %d/%d' % (sum(R), len(R)))
