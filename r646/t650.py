# 2.99.650 test: "I can't do this service" skip is not counted in the day's Skips (local SQLite copy, nothing real)
import subprocess, json, os, sys, shutil
A0 = os.path.abspath(sys.argv[1]); K = '/home/claude/kit638h/s'; T5 = K + '/T586'; D = '/home/claude/t650/run'
shutil.rmtree(D, ignore_errors=True); os.makedirs(D); A = D + '/app'; shutil.copytree(A0, A, symlinks=True); DB = D + '/db.sqlite'; shutil.copy(K + '/tdb/base.sqlite', DB)
ENV = {**os.environ, 'TZ': 'America/Chicago', 'NF_SHARED_DIR': T5 + '/shared'}
def sh(*a): return subprocess.run(a, capture_output=True, text=True, env=ENV)
seed = sh('php', T5 + '/seed.php', A, DB, '18995'); assert seed.returncode == 0, seed.stderr; S = json.loads(seed.stdout)
T = S['T']; SV = S['S']; R = []
def ok(n, c, i=''): R.append(bool(c)); print(('✓ ' if c else '✗ ') + n + ('' if c else '   → ' + str(i)[:500]))
def php(code):
    r = sh('php', '-d', 'error_log=' + D + '/err.log', '-r', 'require "%s/inc/core.php"; settings(); require_once "%s/inc/turnauto.php"; if (!function_exists("get_appt")) { define("API_MAIN", 1); require_once "%s/inc/api/_texts.php"; } foreach (["turnq", "apptlog", "push", "push-tech"] as $f) if (is_file(APP_ROOT . "/inc/$f.php")) require_once APP_ROOT . "/inc/$f.php"; %s' % (A, A, A, code)); return (r.stdout + r.stderr).strip()
php('set_setting("turn_skip_max", "1"); set_setting("turn_auto_on", "1");')
names = list(T.keys()); nan = T[names[0]]
def offer(n):
    return php('$d = date("Y-m-d"); q("INSERT INTO appointments (appt_date, start_min, duration, staff_id, service_ids, customer_name, phone, status, source, kind, group_id, created_at, token) VALUES (?, 600, 45, %d, ?, ?, ?, \'arrived\', \'kiosk\', \'appt\', \'\', datetime(\'now\'), ?)", [$d, "%d", "SKIP TEST %d", "+1555555026%d", "tk650%d"]); $a = (int)db()->lastInsertId();'
        ' q("INSERT INTO turn_offers (appt_id, staff_id, kind, state, at) VALUES (?, %d, \'any\', \'open\', ?)", [$a, now_str()]); echo (int)db()->lastInsertId();' % (nan, SV['Pedicure'], n, n, n, nan))
snaps = lambda: php('echo (int)q("SELECT COUNT(*) FROM turn_snap WHERE kind = \'bottom\' AND by_name = \'skip\'")->fetchColumn();')
o1 = offer(1); r = php('echo json_encode(ta_skip(%s, %d, true));' % (o1, nan)); st = php('echo q("SELECT state FROM turn_offers WHERE id = %s")->fetchColumn();' % o1)
ok('1 "cannot do this service" -> ok, state skipcant', '"ok":true' in r and st == 'skipcant', (r, st))
o2 = offer(2); php('ta_skip(%s, %d, true);' % (o2, nan)); o3 = offer(3); php('ta_skip(%s, %d, true);' % (o3, nan))
ok('2 three "cannot do" skips with Skip max 1 -> never sent to the end of the line', snaps() == '0', snaps())
log = php('echo json_encode(q("SELECT * FROM appt_log ORDER BY id DESC LIMIT 1")->fetch());'); ok('3 activity log says "cannot do this service (not counted)"', 'cannot do this service' in log and 'not counted' in log, log)
o4 = offer(4); php('ta_skip(%s, %d);' % (o4, nan)); ok('4 a normal Skip (the 1st counted) -> still in place (1 is not more than 1)', snaps() == '0', snaps())
o5 = offer(5); php('ta_skip(%s, %d);' % (o5, nan)); ok('5 a 2nd normal Skip -> more than 1 -> to the end of the line, as before', snaps() == '1', snaps())
again = php('echo (int)q("SELECT COUNT(*) FROM turn_offers WHERE appt_id = (SELECT appt_id FROM turn_offers WHERE id = %s) AND staff_id = %d AND state = \'open\'")->fetchColumn();' % (o1, nan))
ok('6 the customer is never offered again to the tech who said "cannot do"', again == '0', again)
err = open(D + '/err.log').read() if os.path.exists(D + '/err.log') else ''
ok('7 no PHP warning / error', not any(w in err for w in ('PHP Warning', 'PHP Fatal', 'PHP Notice', 'Deprecated')), err[-500:])
print('PASS %d/%d' % (sum(R), len(R)))
