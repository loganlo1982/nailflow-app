#!/usr/bin/env python3
# LAMWEB 627 muc 4 – TEST TIEN TREN MySQL/InnoDB RIENG (DB TEST, khong phai DB that). Chi PHP CLI + ban sao app + php -S 127.0.0.1 (khong web that, khong cron).
#   NF_TEST_DB_NAME=nf_test626 NF_TEST_DB_USER=... NF_TEST_DB_PASS=... [NF_TEST_DB_HOST=127.0.0.1] python3 m627.py <app folder>
#   Mat khau CHI trong bien moi truong: config.php cua ban sao doc getenv() – khong ghi mat khau vao file / log / man hinh.
#   An toan: ten DB PHAI bat dau "nf_test"; DB phai RONG (hoac chi co bang do chinh script nay tao lan truoc – co dau nftest_db); xong thi XOA het bang da tao.
#   NF_TEST_SQLITE=1: chay thu tren SQLite (de LAMWEB kiem script) – khong dung MySQL.
# Chay: B1 4 may checkout cung ve · B2 2 may cung gift card · B3 bam 3 lan · B4 loi DB giua chung (trigger) -> rollback · B5 = M15/M28: bo app_lock -> PHAI thay sai.
import os, sys, json, shutil, subprocess, time, threading, urllib.request, urllib.error, http.cookiejar, tempfile, re
APP0 = os.path.abspath(sys.argv[1]); LITE = os.environ.get('NF_TEST_SQLITE') == '1'
DBN = os.environ.get('NF_TEST_DB_NAME', ''); OUT = []
def say(s): OUT.append(s); print(s, flush=True)
if not LITE and not re.match(r'^nf_test\w*$', DBN): sys.exit('DUNG: NF_TEST_DB_NAME phai bat dau bang nf_test (DB TEST rieng) – khong chay.')
if not LITE and not (os.environ.get('NF_TEST_DB_USER') and 'NF_TEST_DB_PASS' in os.environ): sys.exit('DUNG: thieu NF_TEST_DB_USER / NF_TEST_DB_PASS (bien moi truong).')
W = tempfile.mkdtemp(prefix='nf627-'); PORT = 19951
def mkapp(name, mutate=None):
    d = W + '/' + name; shutil.copytree(APP0, d, symlinks=True)
    for f in ('inc/config.php', 'error_log'):
        try: os.remove(d + '/' + f)
        except OSError: pass
    if LITE: cfg = "return array('driver'=>'sqlite','sqlite_path'=>'%s/db.sqlite','site_url'=>'http://127.0.0.1:%d');" % (W, PORT)
    else: cfg = "return array('driver'=>'mysql','db_host'=>(getenv('NF_TEST_DB_HOST') ?: '127.0.0.1'),'db_name'=>getenv('NF_TEST_DB_NAME'),'db_user'=>getenv('NF_TEST_DB_USER'),'db_pass'=>getenv('NF_TEST_DB_PASS'),'site_url'=>'http://127.0.0.1:%d');" % PORT
    open(d + '/inc/config.php', 'w').write('<?php\n' + cfg + '\n')
    for f, a, b in (mutate or []):
        p = d + '/' + f; s = open(p, encoding='utf-8').read(); assert s.count(a) == 1, ('anchor', f); open(p, 'w', encoding='utf-8').write(s.replace(a, b))
    return d
A = mkapp('app')
ENV = {**os.environ, 'TZ': 'America/Chicago'}
H = W + '/h.php'
open(H, 'w').write(r"""<?php $A = $argv[1]; require "$A/inc/core.php"; $a = $argv[2];
if ($a === 'init') { $isM = !is_sqlite(); $t = $isM ? q("SELECT table_name FROM information_schema.tables WHERE table_schema = DATABASE()")->fetchAll(PDO::FETCH_COLUMN) : q("SELECT name FROM sqlite_master WHERE type = 'table'")->fetchAll(PDO::FETCH_COLUMN);
  $mine = in_array('settings', $t, true) && (string)q("SELECT v FROM settings WHERE k = 'nftest_db'")->fetchColumn() === '1';
  if ($t && !$mine) { echo json_encode(['err' => 'DB KHONG RONG (' . count($t) . ' bang) va khong phai do script nay tao – DUNG']); exit; }
  require_once "$A/inc/schema.php"; foreach (schema_sql($isM ? 'mysql' : 'sqlite') as $s) { try { db()->exec($s); } catch (PDOException $e) { if (stripos($s, 'CREATE INDEX') === false) throw $e; } }
  settings(); ensure_schema(); set_setting('nftest_db', '1');
  q('DELETE FROM services'); $S = []; foreach ([['Gel Manicure', 30, 40], ['Pedicure', 45, 35], ['Full Set', 60, 50]] as $i => $s) { q('INSERT INTO services (name, duration, price, sort, active) VALUES (?, ?, ?, ?, 1)', [$s[0], $s[1], $s[2], $i]); $S[$s[0]] = (int)db()->lastInsertId(); }
  q('UPDATE staff SET active = 0'); $T = []; foreach (['TAMMY', 'HANA'] as $i => $n) { q('INSERT INTO staff (name, sort, active, online) VALUES (?, ?, 1, 1)', [$n, $i]); $T[$n] = (int)db()->lastInsertId(); }
  $h = []; for ($w = 0; $w < 7; $w++) $h[$w] = ['open' => '00:00', 'close' => '23:59']; set_setting('hours', json_encode($h)); set_setting('gift_on', '1'); set_setting('admin_hash', password_hash($argv[3], PASSWORD_DEFAULT));
  echo json_encode(['S' => $S, 'T' => $T, 'db' => $isM ? 'MySQL ' . q('SELECT VERSION()')->fetchColumn() . ' · ' . q('SELECT @@transaction_isolation')->fetchColumn() . ' · ' . q("SELECT ENGINE FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = 'receipts'")->fetchColumn() : 'SQLite']); }
if ($a === 'q') echo json_encode(q($argv[3])->fetchAll());
if ($a === 'x') { try { db()->exec($argv[3]); echo '{"ok":1}'; } catch (Throwable $e) { echo json_encode(['err' => substr($e->getMessage(), 0, 160)]); } }
if ($a === 'drop') { if ((string)q("SELECT v FROM settings WHERE k = 'nftest_db'")->fetchColumn() !== '1') { echo '{"err":"no marker"}'; exit; }
  $t = is_sqlite() ? [] : q("SELECT table_name FROM information_schema.tables WHERE table_schema = DATABASE()")->fetchAll(PDO::FETCH_COLUMN);
  foreach (is_sqlite() ? [] : q("SELECT trigger_name FROM information_schema.triggers WHERE trigger_schema = DATABASE()")->fetchAll(PDO::FETCH_COLUMN) as $tr) db()->exec("DROP TRIGGER IF EXISTS `$tr`");
  foreach ($t as $x) db()->exec("DROP TABLE IF EXISTS `$x`"); echo json_encode(['dropped' => count($t)]); }
""")
def php(*a):
    r = subprocess.run(['php', H, *[str(x) for x in a]], capture_output=True, text=True, env=ENV)
    try: return json.loads(r.stdout)
    except Exception: return {'err': (r.stdout + r.stderr)[-300:]}
def sql(q): return php(A, 'q', q)
PW = os.urandom(8).hex()
I = php(A, 'init', PW)
if 'err' in I: say('!! ' + str(I['err'])); sys.exit(2)
S, T = I['S'], I['T']; PD, GM = S['Pedicure'], S['Gel Manicure']; TA, HA = T['TAMMY'], T['HANA']
say('== LAMWEB m627 · %s · %s · app %s' % (time.strftime('%Y-%m-%d %H:%M'), I['db'], APP0))
SV = [None]
def serve(app):
    if SV[0]: SV[0].terminate(); SV[0].wait(); time.sleep(0.5)
    SV[0] = subprocess.Popen(['php', '-S', '127.0.0.1:%d' % PORT, '-t', app], env={**ENV, 'PHP_CLI_SERVER_WORKERS': '6'}, stdout=subprocess.DEVNULL, stderr=open(W + '/php.log', 'a')); time.sleep(1.2)
    jar = http.cookiejar.CookieJar(); op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar)); cs = [None]
    def api(action, body=None):
        hd = {'Content-Type': 'application/json'}; hd.update({'X-CSRF': cs[0]} if cs[0] else {})
        rq = urllib.request.Request('http://127.0.0.1:%d/api.php?action=%s' % (PORT, action), data=json.dumps(body).encode() if body is not None else None, headers=hd)
        try: r = op.open(rq, timeout=60); return r.status, json.loads(r.read().decode() or '{}')
        except urllib.error.HTTPError as e:
            try: return e.code, json.loads(e.read().decode() or '{}')
            except Exception: return e.code, {}
    c, r = api('login', {'password': PW}); cs[0] = r.get('csrf'); return api
api = serve(A)
NUM = [100]
def new(name, st, sid):
    NUM[0] += 1; ph = '+151555501%02d' % (NUM[0] % 100); d = time.strftime('%Y-%m-%d')
    php(A, 'x', "INSERT INTO appointments (appt_date, start_min, duration, staff_id, service_ids, customer_name, phone, status, source, kind, group_id, created_at, token) VALUES ('%s', %d, 45, %d, '%d', '%s', '%s', 'arrived', 'admin', 'appt', '', '%s', '%s')" % (d, 300 + NUM[0], st, sid, name, ph, time.strftime('%Y-%m-%d %H:%M:%S'), os.urandom(8).hex()))
    return int(sql("SELECT id FROM appointments WHERE token <> '' ORDER BY id DESC LIMIT 1")[0]['id'])
def co(api, aid, sid, st, p, pays, **k):
    b = {'ids': [aid], 'lines': [{'appt': aid, 'sid': sid, 'price': p, 'staff': st}], 'splits': [{'staff': st, 'amt': p}], 'pays': pays}; b.update(k); return api('checkout2', b)
def nrc(): return int(sql('SELECT COUNT(*) AS n FROM receipts')[0]['n'])
def gift(code, amt): php(A, 'x', "INSERT INTO giftcards (code, amount, balance, status, buyer_phone, to_phone, created_at) VALUES ('%s', %s, %s, 'active', '+15155550190', '', '%s')" % (code, amt, amt, time.strftime('%Y-%m-%d %H:%M:%S')))
def gbal(code): x = sql("SELECT balance FROM giftcards WHERE code = '%s'" % code); return round(float(x[0]['balance']), 2) if x else None
RES = []
def res(name, okk, info): RES.append(okk); say(('PASS ' if okk else 'FAIL ') + name + ('' if okk else '  -> ' + str(info)[:200]))
def together(n, fn):
    out = [None] * n; ev = threading.Event()
    def g(k): ev.wait(); out[k] = fn(k)
    th = [threading.Thread(target=g, args=(k,)) for k in range(n)]; [t.start() for t in th]; time.sleep(0.2); ev.set(); [t.join() for t in th]; return out
def b1(api, tag):
    a = new('M B1 ' + tag, HA, GM); n0 = nrc(); out = together(4, lambda k: co(api, a, GM, HA, 40, [{'m': 'Card', 'amt': 40}]))
    return nrc() - n0, [x[0] for x in out]
def b2(api, tag):
    code = 'MYSQLB2' + tag; gift(code, 40); a1, a2 = new('M B2A ' + tag, TA, PD), new('M B2B ' + tag, HA, PD)
    out = together(2, lambda k: co(api, (a1, a2)[k], PD, (TA, HA)[k], 35, [], gift_code=code, gift_amount=35))
    return sum(1 for x in out if x[0] == 200), gbal(code), [x[0] for x in out]
n, codes = b1(api, 'OK'); res('B1 4 may checkout CUNG 1 ve cung luc -> 1 hoa don (%s)' % codes, n == 1, (n, codes))
okn, bal, codes = b2(api, 'OK'); res('B2 2 may CUNG gift card 40$ (moi may 35$) -> 1 may, so du 5 (%s)' % codes, okn == 1 and bal == 5, (okn, bal, codes))
a = new('M B3', TA, PD); n0 = nrc(); out = [co(api, a, PD, TA, 35, [{'m': 'Cash', 'amt': 35}]) for _ in range(3)]
res('B3 bam Thanh toan 3 lan -> 1 hoa don (%s)' % [x[0] for x in out], nrc() == n0 + 1 and out[0][0] == 200 and all(x[0] >= 400 for x in out[1:]), [x[0] for x in out])
gift('MYSQLB4FAIL', 50); a = new('M B4', TA, S['Full Set']); n0 = nrc()
trg = ("CREATE TRIGGER t627_fail BEFORE UPDATE OF balance ON giftcards WHEN OLD.code = 'MYSQLB4FAIL' BEGIN SELECT RAISE(ABORT, 'test627'); END" if LITE else
       "CREATE TRIGGER t627_fail BEFORE UPDATE ON giftcards FOR EACH ROW BEGIN IF OLD.code = 'MYSQLB4FAIL' AND NEW.balance <> OLD.balance THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'test627'; END IF; END")
tr = php(A, 'x', trg)
if 'err' in tr: say('NOT TESTED B4 (khong tao duoc TRIGGER – can quyen TRIGGER): ' + tr['err'][:120])
else:
    c, r = co(api, a, S['Full Set'], TA, 50, [{'m': 'Cash', 'amt': 20}], gift_code='MYSQLB4FAIL', gift_amount=30); php(A, 'x', 'DROP TRIGGER t627_fail')
    st4 = sql('SELECT status, receipt_id FROM appointments WHERE id = %d' % a)[0]
    res('B4 loi DB giua chung -> ROLLBACK: khong hoa don, hen chua tra, gift card van 50', c >= 400 and nrc() == n0 and st4['status'] != 'paid' and int(st4['receipt_id']) == 0 and gbal('MYSQLB4FAIL') == 50, (c, r.get('error'), st4, gbal('MYSQLB4FAIL')))
# B5 = M15 / M28: the same app WITHOUT app_lock('money') – the tests must see it go wrong (else they prove nothing on this DB)
M = mkapp('mut', [('inc/checkout.php', "    app_lock('money'); // (2.99.69)", "    // (2.99.69)"), ('inc/api/checkout.php', "    app_lock('money'); /* (2.99.457", "    /* (2.99.457")])
api = serve(M)
n, codes = b1(api, 'M15'); okn, bal, codes2 = b2(api, 'M28')
say('B5 (bo app_lock): B1 -> %d hoa don cho 1 ve %s · B2 -> %d may thanh cong, so du %s %s' % (n, codes, okn, bal, codes2))
if LITE: say('     (SQLite tu khoa ca file -> B5 chi co nghia tren MySQL)')
else: res('B5 M15 BAT DUOC: khong khoa -> 2+ hoa don cho 1 ve (test B1 phat hien duoc)', n >= 2, n)
say('     M28 (gift): %s' % ('so du AM / 2 may duoc -> lop 2 (627 L3) CHUA co' if (okn >= 2 or (bal is not None and bal < 0)) else 'van 1 may, so du khong am -> lop 2 tru gift (627 L3) chan duoc ca khi khong khoa'))
if SV[0]: SV[0].terminate()
lg = open(W + '/php.log').read(); bad = [l for l in lg.splitlines() if 'PHP Fatal' in l or 'Uncaught' in l]
if bad: say('PHP loi: ' + bad[0][:200])
d = php(A, 'drop'); say('don DB test: %s' % d)
shutil.rmtree(W, ignore_errors=True)
say('== %d/%d PASS%s' % (sum(RES), len(RES), '' if LITE else ' (MySQL)'))
