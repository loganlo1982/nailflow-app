# Test 645a – Payroc Cloud at Checkout + receipt Void / Refund (fake Payroc gateway, local SQLite copy, nothing real).
import subprocess, json, os, sys, time, shutil, urllib.request, urllib.error, http.cookiejar, atexit
A0 = os.path.abspath(sys.argv[1]); D = '/home/claude/payroc/kit'; T5 = '/home/claude/kit638d2/run/T586'; PORT = 19914; FP = 19915
R = []; out = open(D + '/test-645p.txt', 'w'); ENV = {**os.environ, 'TZ': 'America/Chicago', 'NO_PROXY': '127.0.0.1', 'no_proxy': '127.0.0.1'}
def say(s): print(s, flush=True); out.write(s + '\n'); out.flush()
def ok(n, c, i=''): R.append(bool(c)); say(('✓ ' if c else '✗ ') + n + ('' if c else '   → ' + str(i)[:400]))
def sh(*a): return subprocess.run(a, capture_output=True, text=True, env=ENV)
A = D + '/app'; shutil.rmtree(A, ignore_errors=True); shutil.copytree(A0, A, symlinks=True); DB = D + '/db.sqlite'; shutil.copy('/home/claude/kit638d2/run/tdb/base.sqlite', DB)
F = D + '/fake'; shutil.rmtree(F, ignore_errors=True); os.makedirs(F); src = open('/home/claude/payroc/fake/index.php').read().replace('127.0.0.1:18998', '127.0.0.1:%d' % FP); open(F + '/index.php', 'w').write(src)
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
try:
    say('== test 645a - Payroc at Checkout (fake gateway) ' + time.strftime('%Y-%m-%d %H:%M %Z') + ' · login ' + str(c))
    a0 = appt(); c, r = api('pr_charge', {'ids': [a0], 'amt': 35}); ok('0 Payroc off: pr_charge refused, nothing sent', c == 400 and not calls('payment-instructions'), (c, r))
    c, t = api('ticket', get='&id=%d' % a0); ok('0 ticket says prOn false', t.get('prOn') is False, t.get('prOn'))
    c, r = co(a0, [{'m': 'Card', 'amt': 35, 'last4': '1111'}]); r0 = int(r['receipt']['id']); ok('1 a NORMAL card checkout is unchanged', c == 200 and rcpt(r0)['status'] == 'paid', (c, r))
    php('require_once "%s/inc/payroc.php"; pr_set_creds("6804001", "SIM-001", "TESTKEY-1234567890abcd", "uat"); set_setting("pr_on", "1");' % A)
    c, r = api('receipt_void', {'id': r0, 'reason': 'test dps', 'dps_done': False}); ok('1 a normal card receipt still needs "Done on DPS"', c == 400 and 'DPS' in r.get('error', ''), (c, r))
    a1 = appt(); c, t = api('ticket', get='&id=%d' % a1); ok('2 ticket says prOn true', t.get('prOn') is True, t.get('prOn'))
    c, v = api('pr_charge', {'ids': [a1], 'amt': 35}); ok('2 pr_charge approved', c == 200 and v.get('ref') and v.get('last4') == '0011', (c, v))
    c, r = co(a1, [{'m': 'Card', 'amt': 35, 'pr_ref': v['ref']}]); rid1 = int(((r or {}).get('receipt') or {}).get('id', 0)); pays = json.loads(rcpt(rid1).get('pays') or '[]')
    ok('2 checkout2 with pr_ref -> receipt PAID, card has Payroc ref/payment/approval, last4 from Payroc', c == 200 and pays and pays[0].get('pr', {}).get('ref') == v['ref'] and pays[0]['pr'].get('pay') and pays[0].get('last4') == '0011', (c, r, pays))
    ok('2 the Payroc payment is marked used', pend()[v['ref']]['st'] == 'used', pend().get(v['ref']))
    a2 = appt(); c, r = co(a2, [{'m': 'Card', 'amt': 35, 'pr_ref': v['ref']}]); ok('3 the same Payroc payment cannot pay a 2nd ticket', c == 409 and not sql("SELECT id FROM receipts WHERE appt_ids LIKE '%%%d%%'" % a2), (c, r))
    c, vd = api('pr_charge', {'ids': [a2], 'amt': 35.01}); ok('4 declined card -> 402', c == 402, (c, vd))
    refd = [k for k, x in pend().items() if x.get('key') == 'T%d' % a2][0]
    c, r = co(a2, [{'m': 'Card', 'amt': 35.01, 'pr_ref': refd}], price=35.01); ok('4 checkout2 with a DECLINED Payroc ref -> refused, NO receipt (never PAID without approval)', c == 409 and 'not approved' in r.get('error', ''), (c, r))
    c, r = co(a2, [{'m': 'Card', 'amt': 35, 'pr_ref': 'NFFAKE123'}]); ok('4 an unknown ref -> refused', c == 409, (c, r))
    a3 = appt(); c, v3 = api('pr_charge', {'ids': [a3], 'amt': 35}); c, r = co(a2, [{'m': 'Card', 'amt': 35, 'pr_ref': v3['ref']}]); ok('5 a payment of another ticket -> refused', c == 409 and 'another ticket' in r.get('error', ''), (c, r))
    c, r = co(a3, [{'m': 'Card', 'amt': 30, 'pr_ref': v3['ref']}, {'m': 'Cash', 'amt': 5}]); ok('6 card part not what Payroc took -> refused', c == 409, (c, r))
    n = len(calls('payment-instructions')); c, v3b = api('pr_charge', {'ids': [a3], 'amt': 35}); ok('7 Pay tapped again: the SAME payment, no 2nd charge', c == 200 and v3b.get('again') and v3b['ref'] == v3['ref'] and len(calls('POST /v1/devices')) == len([x for x in calls('POST /v1/devices')]), (c, v3b))
    ok('7 ... no new instruction sent', len(calls('payment-instructions')) == n, (n, len(calls('payment-instructions'))))
    rid, ref = paid(); nrev = len(calls('/reverse'))
    c, r = api('receipt_void', {'id': rid, 'reason': 'test payroc void', 'dps_done': False}); ok('8 Payroc receipt Void: no DPS tick, Payroc reverse -> receipt VOID', c == 200 and len(calls('/reverse')) == nrev + 1 and rcpt(rid)['status'] == 'void' and 'Payroc' in rcpt(rid).get('void_reason', ''), (c, r, rcpt(rid)))
    ok('8 the Payroc payment is marked voided', pend()[ref]['st'] == 'voided', pend().get(ref))
    rid2, ref2 = paid(price=40, sid=GM); nri = len(calls('refund-instructions'))
    c, r = api('receipt_refund', {'id': rid2, 'amount': 10, 'how': 'Card', 'dps_done': False, 'reason': 'part back'}); ok('9 refund $10 of $40: a Payroc refund instruction on the device -> refund saved', c == 200 and len(calls('POST /v1/devices/SIM-001/refund-instructions')) >= 1 and json.loads(rcpt(rid2).get('refunds') or '[]'), (c, str(r)[:200]))
    c, r = api('receipt_refund', {'id': rid2, 'amount': 10.01, 'how': 'Card', 'dps_done': False, 'reason': 'declined back'}); ok('10 Payroc declines the refund -> 402, NOT saved', c == 402 and 'NOT changed' in r.get('error', ''), (c, r))
    rid3, ref3 = paid(price=50, sid=S['Full Set']); st = fake(); pay3 = pend()[ref3]['pay']; st.setdefault('closed', {})[pay3] = 1; json.dump(st, open(F + '/state.json', 'w'))
    c, r = api('receipt_void', {'id': rid3, 'reason': 'after close', 'dps_done': False}); ok('11 Void after the batch closed: reverse refused -> refund instruction $50 -> receipt VOID, payment "returned"', c == 200 and rcpt(rid3)['status'] == 'void' and pend()[ref3]['st'] == 'returned', (c, str(r)[:200], pend().get(ref3)))
    rid4, ref4 = paid(price=35); c, r = api('receipt_refund', {'id': rid4, 'amount': 35, 'how': 'Card', 'dps_done': False, 'reason': 'all back'}); ok('12 refund ALL in the same batch -> reverse (no card needed)', c == 200 and pend()[ref4]['st'] == 'voided', (c, str(r)[:200]))
    rid7, ref7 = paid(price=35); c, r = api('receipt_tips_edit', {'id': rid7, 'tips': [{'staff': TA, 'amt': 5}], 'tip_total': 5, 'cash_tips': [], 'cash_tip_total': 0}); ok('13 card tip on a Payroc receipt cannot be changed', c == 400 and 'Payroc' in r.get('error', ''), (c, r))
    c, r = api('receipt_tips_edit', {'id': rid7, 'tips': [], 'tip_total': 0, 'cash_tips': [{'staff': TA, 'amt': 5}], 'cash_tip_total': 5}); ok('13 ... a cash tip is fine', c == 200, (c, r))
    a8 = appt(); c, v8 = api('pr_charge', {'ids': [a8], 'amt': 35}); c, r8 = co(a8, [{'m': 'Card', 'amt': 35, 'pr_ref': v8['ref']}, {'m': 'Cash', 'amt': 20}], price=55); rid8 = int(((r8 or {}).get('receipt') or {}).get('id', 0))
    n8 = len(calls('refund-instructions')); c, r = api('receipt_refund', {'id': rid8, 'amount': 50, 'how': 'Card', 'dps_done': False, 'reason': 'more than card'}); ok('14 $35 Payroc + $20 cash: a $50 card refund refused, Payroc NOT asked', rid8 and c == 400 and len(calls('refund-instructions')) == n8, (rid8, c, r))
    rid6, ref6 = paid(price=35); php('set_setting("pr_key", "");'); c, r = api('receipt_void', {'id': rid6, 'reason': 'gone', 'dps_done': True}); ok('15 Payroc not set up any more: receipt NOT voided', c == 409 and rcpt(rid6)['status'] == 'paid', (c, r))
    allaud = php('echo json_encode(q("SELECT * FROM audit_log")->fetchAll());'); ok('16 audit has Payroc rows, never the key', 'Payroc card' in allaud and 'Payroc void' in allaud and 'TESTKEY' not in allaud, '')
    err = open(D + '/php.log').read() + (open(D + '/php-err.log').read() if os.path.exists(D + '/php-err.log') else '')
    ok('17 no PHP warning / error', not any(w in err for w in ('PHP Warning', 'PHP Fatal', 'PHP Notice', 'Deprecated')), err[-600:])
finally:
    say('== %d / %d PASS' % (sum(R), len(R)))
