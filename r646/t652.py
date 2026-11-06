# test 2.99.652 – setup page Skip question
import subprocess, json, os, sys, time, urllib.request, shutil, atexit, http.cookiejar, re
import subprocess, json, os, sys, time, urllib.request, shutil, atexit, http.cookiejar, re
A0 = os.path.abspath(sys.argv[1]); D = '/tmp/claude-0/T652'; T5 = '/tmp/claude-0/T586'; PA, PB = 19967, 19968
R = []; out = open(D + '/test-652.txt', 'w')
def say(s): print(s, flush=True); out.write(s + '\n'); out.flush()
def ok(n, c, i=''): R.append(bool(c)); say(('✓ ' if c else '✗ ') + n + ('' if c else '   → ' + str(i)[:500]))
ENV = {**os.environ, 'TZ': 'America/Chicago'}
def sh(*a): return subprocess.run(a, capture_output=True, text=True, env=ENV)
S = {}
def mk(tag, port):
    app = D + '/app' + tag; db = D + '/db' + tag + '.sqlite'; shutil.rmtree(app, ignore_errors=True); shutil.copytree(A0, app, symlinks=True); shutil.copy('/tmp/claude-0/tdb/base.sqlite', db)
    seed = json.loads(sh('php', T5 + '/seed.php', app, db, str(port)).stdout); h = D + '/h' + tag + '.php'
    open(h, 'w').write("""<?php require '%s/inc/core.php'; settings(); $a = $argv[1];
if ($a === 'set') { foreach (json_decode($argv[2], true) as $k => $v) set_setting($k, $v); echo '{}'; }
if ($a === 'get') { $k = json_decode($argv[2], true); echo json_encode(array_combine($k, array_map('setting', $k))); }
if ($a === 'hash') { echo password_hash($argv[2], PASSWORD_DEFAULT); }
if ($a === 'cfg') { require_once '%s/inc/turnq.php'; echo json_encode(tq_cfg()); }
""" % (app, app))
    sv = subprocess.Popen(['php', '-S', '127.0.0.1:%d' % port, '-t', app, '/tmp/claude-0/router.php'], env={**ENV, 'PHP_CLI_SERVER_WORKERS': '4'}, stdout=subprocess.DEVNULL, stderr=open(D + '/php' + tag + '.log', 'w'))
    atexit.register(sv.terminate); return {'app': app, 'db': db, 'h': h, 'port': port, 'seed': seed}
X = {'A': mk('A', PA), 'B': mk('B', PB)}; time.sleep(1.3)
def h(t, *a):
    r = sh('php', X[t]['h'], *[str(x) for x in a])
    try: return json.loads(r.stdout)
    except Exception: return r.stdout
def sql(t, q): r = sh('php', T5 + '/db.php', X[t]['db'], q); return json.loads(r.stdout or '[]') if r.returncode == 0 else ('ERR', r.stderr)
def api(t, action, body=None, jar=None, csrf=None, host=None, get=None):
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar)) if jar is not None else urllib.request.build_opener()
    hd = {'Content-Type': 'application/json'}; hd.update({'X-CSRF': csrf} if csrf else {}); hd.update({'Host': host} if host else {})
    u = 'http://127.0.0.1:%d/api.php?action=%s%s' % (X[t]['port'], action, get or '')
    rq = urllib.request.Request(u, data=None if body is None else json.dumps(body).encode(), headers=hd)
    try: r = op.open(rq, timeout=60); b = r.read().decode(); return r.status, (json.loads(b or '{}') if b.strip().startswith('{') else {'_raw': b[:300]})
    except urllib.error.HTTPError as e:
        b = e.read().decode()
        try: return e.code, json.loads(b or '{}')
        except Exception: return e.code, {'_raw': b[:300]}
PW = 'adm632-' + os.urandom(4).hex()
ALLDAY = {str(w): {'open': '09:00', 'close': '21:00'} for w in range(7)}
for t, nm in (('A', 'AMERICAN NAILS TEST'), ('B', 'SALON B TEST')):
    h(t, 'set', json.dumps({'admin_hash': h(t, 'hash', PW), 'salon_name': nm, 'hours': json.dumps(ALLDAY), 'turn_req_mode': 'half', 'turn_count_req': '1', 'turn_min': '25', 'turn_hold_min': '15',
        'turn_skip_max': '3', 'turn_tie': 'clock', 'turn_under': 'bonus', 'turn_multi': 'cust', 'turn_rare_keep': '1', 'turn_pre_open': '1', 'turn_auto_on': '1', 'ck_pick_tech': '0', 'turn_half_svcs': '', 'payroll_week_start': '0'}))
sql('A', "UPDATE staff SET commission_pct = 40, pay_method = 'check', notify = 1, online_hours = '{\"1\":[\"10:00\",\"18:00\"]}' WHERE name = 'TAMMY'")
sql('A', "UPDATE staff SET notify = 1, pay_method = 'cash', pay_note = 'old note', off_days = '2', mix_check_pct = 70, online = 0 WHERE name = 'HANA'")
def login(t):
    j = http.cookiejar.CookieJar(); c, r = api(t, 'login', {'password': PW}, j); return j, r.get('csrf')
say('== LAMWEB test 2.99.632 – LENH 632 salon setup link ' + time.strftime('%Y-%m-%d %H:%M %Z') + ' · 2 local salons (A, B), SQLite, nothing real')
JA, CA = login('A'); JB, CB = login('B')
say('== test 2.99.652 – setup page: Skip question = the same number the turn engine uses')
JA, CA = login('A')
def newtok():
    c, r = api('A', 'setup_new', {}, JA, CA); return (re.search(r'[?&]t=([0-9a-f]+)', r.get('url', '')) or [None, ''])[1]
from playwright.sync_api import sync_playwright
pw = sync_playwright().start(); br = pw.chromium.launch()
def page(val):
    h('A', 'set', json.dumps({'turn_skip_max': str(val)})); tok = newtok()
    pg = br.new_page(viewport={'width': 390, 'height': 844}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('http://127.0.0.1:%d/setup/?t=%s' % (PA, tok)); pg.wait_for_selector('[name="q8"]', timeout=15000); return pg, errs
# 1 what the page shows for each saved value
for val, want, num in ((0, '0', None), (1, 'N', '1'), (3, 'N', '3')):
    pg, errs = page(val); chk = pg.eval_on_selector('[name="q8"]:checked', 'e => e.value'); n = pg.eval_on_selector('[data-n="q8"]', 'e => e.value')
    ok('1 saved turn_skip_max=%d -> page shows "%s"%s' % (val, want, ' with %s' % num if num else ''), chk == want and (num is None or n == num) and not errs, (chk, n, errs)); pg.close()
pg, errs = page(2); vals = pg.eval_on_selector_all('[name="q8"]', 'l => l.map(e => e.value)')
ok('2 choices: N (common), skip on the first time = NailFlow will set it up, always keep', vals == ['N', 'L:skipfirst', '0'], vals)
ok('2 "first time" shows the NailFlow-will-set-this-up tag + its example', 'skipfirst' in pg.content() and pg.locator('label.o', has=pg.locator('[value="L:skipfirst"]')).locator('.tag.later').count() == 1 and pg.locator('label.o', has=pg.locator('[value="L:skipfirst"]')).locator('.ex').count() == 1, '')
max_ = pg.eval_on_selector('[data-n="q8"]', 'e => e.max'); ok('2 number box goes up to 20 (the server limit)', max_ == '20', max_)
# 3 save N=2 -> turn_skip_max 2 -> engine: 2 Skips keep, the 3rd goes to the end (sk > 2)
pg.check('[name="q8"][value="N"]'); pg.fill('[data-n="q8"]', '2'); o2 = pg.evaluate('turnOut()')
ok('3 "more than 2" -> sends turn_skip_max 2 (was 3)', o2['set'].get('turn_skip_max') == 2, o2); pg.close()
for val in (1, 5):
    pg, errs = page(val); o2 = pg.evaluate('turnOut()'); ok('3 open + save without touching keeps turn_skip_max %d (no drift)' % val, o2['set'].get('turn_skip_max') == val, o2); pg.close()
pg, errs = page(4); pg.check('[name="q8"][value="L:skipfirst"]'); o2 = pg.evaluate('turnOut()')
ok('4 "first time" -> no turn_skip_max sent, a note for NailFlow (skipfirst)', 'turn_skip_max' not in o2['set'] and any(n['q'] == 'q8' and n['pick'] == 'skipfirst' for n in o2['notes']), o2)
pg.check('[name="q8"][value="0"]'); o2 = pg.evaluate('turnOut()'); ok('4 "always keeps" -> 0', o2['set'].get('turn_skip_max') == 0, o2)
# 5 the real save through the page -> the DB
pg.check('[name="q8"][value="N"]'); pg.fill('[data-n="q8"]', '2'); pg.click('#saveTurn'); pg.click('#go'); pg.wait_for_timeout(1500)
got = h('A', 'get', json.dumps(['turn_skip_max'])); cfg = h('A', 'cfg')
ok('5 saved through the page: turn_skip_max = 2, engine skipMax = 2', got['turn_skip_max'] == '2' and cfg.get('skipMax') == 2, (got, cfg)); pg.close()
br.close(); pw.stop()
say('KET QUA: %d/%d' % (sum(R), len(R))); sys.exit(0 if all(R) else 1)
