# Test 647 (built on 645a) – Payroc Cloud at Checkout + receipt Void / Refund (fake Payroc gateway, local SQLite copy, nothing real).
import subprocess, json, os, sys, time, shutil, urllib.request, urllib.error, http.cookiejar, atexit
A0 = os.path.abspath(sys.argv[1]); D = '/home/claude/payroc/kit647'; T5 = '/home/claude/kit638d2/run/T586'; PORT = 19924; FP = 19925
R = []; out = open(D + '/test-647p.txt', 'w'); ENV = {**os.environ, 'TZ': 'America/Chicago', 'NO_PROXY': '127.0.0.1', 'no_proxy': '127.0.0.1'}
def say(s): print(s, flush=True); out.write(s + '\n'); out.flush()
def ok(n, c, i=''): R.append(bool(c)); say(('✓ ' if c else '✗ ') + n + ('' if c else '   → ' + str(i)[:400]))
def sh(*a): return subprocess.run(a, capture_output=True, text=True, env=ENV)
A = D + '/app'; shutil.rmtree(A, ignore_errors=True); shutil.copytree(A0, A, symlinks=True); DB = D + '/db.sqlite'; shutil.copy('/home/claude/kit638d2/run/tdb/base.sqlite', DB)
F = D + '/fake'; shutil.rmtree(F, ignore_errors=True); os.makedirs(F); src = open('/home/claude/payroc/fake647/index.php').read().replace('127.0.0.1:18998', '127.0.0.1:%d' % FP); open(F + '/index.php', 'w').write(src)
def sql(q): r = sh('php', T5 + '/db.php', DB, q); return json.loads(r.stdout or '[]') if r.returncode == 0 else ('ERR', r.stderr)
seed = json.loads(sh('php', T5 + '/seed.php', A, DB, str(PORT)).stdout); S = seed['S']; TT = seed['T']; PD, GM = S['Pedicure'], S['Gel Manicure']; TA = TT['TAMMY']
open(A + '/inc/config.php', 'w').write("<?php\nreturn array('driver'=>'sqlite','sqlite_path'=>'%s','site_url'=>'http://127.0.0.1:%d','pr_base'=>'http://127.0.0.1:%d/v1','pr_idurl'=>'http://127.0.0.1:%d/authorize','pr_wait'=>3);\n" % (DB, PORT, FP, FP))
def php(code):
    r = sh('php', '-d', 'error_log=' + D + '/php-err.log', '-r', 'require "%s/inc/core.php"; settings(); %s' % (A, code)); return (r.stdout + r.stderr).strip()
PW = 'adm645-' + os.urandom(3).hex(); php('set_setting("admin_hash", password_hash(%r, PASSWORD_DEFAULT)); set_setting("admin_totp_on", "0"); set_setting("admin_fee_on", "0"); set_setting("tax_pct", "0");' % PW)
fk = subprocess.Popen(['php', '-S', '127.0.0.1:%d' % FP, 'index.php'], cwd=F, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
sv = subprocess.Popen(['php', '-S', '127.0.0.1:%d' % PORT, '-t', A, '/home/claude/kit638d2/run/router.php'], env={**ENV, 'PHP_CLI_SERVER_WORKERS': '4'}, stdout=subprocess.DEVNULL, stderr=open(D + '/php.log', 'w'))
atexit.register(lambda: (sv.terminate(), fk.terminate())); time.sleep(1.2)
B = 'http://127.0.0.1:%d/api.php' % PORT; jar = http.cookiejar.CookieJar(); OP = urllib.request.build_opener(urllib.request.ProxyHandler({}), urllib.request.HTTPCookieProcessor(jar)); CS = [None]
def api(action, body=None, get=''):
    hd = {'Content-Type': 'application/json'}; hd.update({'X-CSRF': CS[0]} if CS[0] else {})
    rq = urllib.request.Request(B + '?action=' + action + get, data=json.dumps(body).encode() if body is not None else None, headers=hd)
    try: r = OP.open(rq, timeout=60); return r.status, json.loads(r.read().decode() or '{}')
    except urllib.error.HTTPError as e:
        try: return e.code, json.loads(e.read().decode() or '{}')
        except Exception: return e.code, {}
c, r = api('login', {'password': PW}); CS[0] = r.get('csrf')
NUM = [0]
def appt(sid=None):
    NUM[0] += 1; ph = '+155555502%02d' % (40 + NUM[0])
    sql("INSERT INTO appointments (appt_date, start_min, duration, staff_id, service_ids, customer_name, phone, status, source, kind, group_id, created_at, token) VALUES ('%s', %d, 45, %d, '%d', 'PR TEST %d', '%s', 'arrived', 'admin', 'appt', '', datetime('now'), 'tq%d')" % (time.strftime('%Y-%m-%d'), 600 + NUM[0] * 5, TA, sid or PD, NUM[0], ph, NUM[0]))
    return sql("SELECT id FROM appointments WHERE phone = '%s' ORDER BY id DESC LIMIT 1" % ph)[0]['id']
def co(aid, pays, sid=None, price=35): return api('checkout2', {'ids': [aid], 'lines': [{'appt': aid, 'sid': sid or PD, 'price': price, 'staff': TA}], 'pays': pays})
def fake(): return json.load(open(F + '/state.json')) if os.path.exists(F + '/state.json') else {'calls': []}
def calls(p): return [c for c in fake()['calls'] if p in c]
def pend(): return json.loads(php('echo setting("pr_pend");') or '{}')
def rcpt(rid): x = sql("SELECT status, pays, void_reason, refunds FROM receipts WHERE id = %d" % rid); return x[0] if x else {}
def paid(price=35, amt=None, sid=None):
    a = appt(sid); c, v = api('pr_charge', {'ids': [a], 'amt': amt or price}); c2, r = co(a, [{'m': 'Card', 'amt': amt or price, 'pr_ref': v.get('ref', '')}], sid=sid, price=price)
    return int(((r or {}).get('receipt') or {}).get('id', 0)), v.get('ref', '')
import threading
try:
    say('== test 647 - Payroc fixes (fake gateway) ' + time.strftime('%Y-%m-%d %H:%M %Z') + ' · login ' + str(c))
    php('require_once "%s/inc/payroc.php"; pr_set_creds("6804001", "SIM-001", "TESTKEY-1234567890abcd", "uat"); set_setting("pr_on", "1");' % A)
    # A: a 5xx twice on the first send = NOT sure (kept); the next tap gets the SAME instruction, never a 2nd sale
    a1 = appt(); c, v = api('pr_charge', {'ids': [a1], 'amt': 35.56})
    ref = [k for k, x in pend().items() if x.get('key') == 'T%d' % a1]
    ok('A1 sale answered 502 twice -> 409 "not sure" (not 402 failed)', c == 409 and 'Not sure' in v.get('error', ''), (c, v))
    ok('A1 ... the try is kept as unsure', ref and pend()[ref[0]]['st'] == 'unsure', pend())
    ni = len(fake().get('instr', {})); c, v2 = api('pr_charge', {'ids': [a1], 'amt': 35.56})
    ok('A2 tap again -> the SAME order approved', c == 200 and v2.get('ref') == ref[0], (c, v2))
    ok('A2 ... no 2nd instruction on the device', len(fake().get('instr', {})) == ni, (ni, len(fake().get('instr', {}))))
    c, r = co(a1, [{'m': 'Card', 'amt': 35.56, 'pr_ref': v2['ref']}], price=35.56); ok('A3 checkout with it -> receipt paid', c == 200, (c, r))
    # B: a void that is not sure (503) -> refused, NO refund sent, receipt unchanged
    rid, refb = paid(price=35.57); nri = len(calls('refund-instructions'))
    c, r = api('receipt_void', {'id': rid, 'reason': 'test 647 void', 'dps_done': False})
    ok('B1 void: reverse 503 -> 409 not sure', c == 409 and 'Not sure' in r.get('error', ''), (c, r))
    ok('B1 ... NO refund sent on the device (no double money back)', len(calls('refund-instructions')) == nri, (nri, len(calls('refund-instructions'))))
    ok('B1 ... receipt still paid', rcpt(rid)['status'] == 'paid', rcpt(rid))
    c, r = api('receipt_refund', {'id': rid, 'amount': 35.57, 'how': 'Card', 'dps_done': False, 'reason': 'all back 647'})
    ok('B2 refund ALL (reverse 503) -> refused too, no refund sent', c == 409 and len(calls('refund-instructions')) == nri, (c, r))
    # (closed batch = clear 400 -> refund fallback still works: covered by t645p test 11)
    # C: Stop works WHILE the charge waits on the device
    a3 = appt(); res = {}
    th = threading.Thread(target=lambda: res.update(x=api('pr_charge', {'ids': [a3], 'amt': 35.77}))); th.start(); time.sleep(1.0)
    t0 = time.time(); c, s3 = api('pr_stop', {'ids': [a3]}); dt = time.time() - t0; th.join(30)
    ok('C1 Stop during the wait -> stopped on the device, at once', c == 200 and s3.get('stopped') is True and dt < 2.0, (c, s3, round(dt, 2)))
    ok('C1 ... the charge ends not paid', res.get('x', (0,))[0] in (402, 409), res.get('x'))
    # D: the test buttons refuse api.payroc.com (real cards)
    php('require_once "%s/inc/payroc.php"; pr_set_creds("", "", "", "std");' % A)
    c, r = api('pr_test', {'op': 'sale', 'amt': 1.00, 'tc': 'x'}); ok('D1 pr_test on api.payroc.com -> refused, nothing sent', c == 400 and 'sandbox' in r.get('error', '') , (c, r))
    php('require_once "%s/inc/payroc.php"; pr_set_creds("", "", "", "uat");' % A)
    err = open(D + '/php.log').read() + (open(D + '/php-err.log').read() if os.path.exists(D + '/php-err.log') else '')
    ok('Z no PHP warning / error', not any(w in err for w in ('PHP Warning', 'PHP Fatal', 'PHP Notice', 'Deprecated')), err[-600:])
finally:
    say('== %d / %d PASS' % (sum(R), len(R)))
