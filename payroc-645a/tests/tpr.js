const fs = require('fs'); const { execSync, spawn } = require('child_process');
const P = 18997, PW = fs.readFileSync('/home/claude/qa/envUI/.pw', 'utf8').trim(), KEY = 'TESTKEY-1234567890abcd';
const ST = '/home/claude/payroc/fake/state.json', DB = '/home/claude/payroc/env/app/sites/s001/data/db.sqlite';
const res = {}; const ok = (k, c, i) => { res[k] = c ? 'PASS' : 'FAIL ' + String(JSON.stringify(i)).slice(0, 400); };
let cookie = '', csrf = '';
const http = require('http');
function api(action, body) { return new Promise((resolve) => {
  const data = body === undefined ? null : JSON.stringify(body);
  const rq = http.request({ host: '127.0.0.1', port: P, path: '/api.php?action=' + action, method: data === null ? 'GET' : 'POST', headers: Object.assign({ Host: 's001.qa.test', 'Content-Type': 'application/json', Cookie: cookie, 'X-CSRF': csrf }, data !== null ? { 'Content-Length': Buffer.byteLength(data) } : {}) }, (r) => {
    let t = ''; r.on('data', c => t += c); r.on('end', () => { const sc = (r.headers['set-cookie'] || []).join(';'); if (/salonsess=/.test(sc)) cookie = 'salonsess=' + /salonsess=([^;]+)/.exec(sc)[1];
      let j; try { j = JSON.parse(t); } catch (e) { j = { raw: t.slice(0, 300) }; } j._http = r.statusCode; resolve(j); }); });
  rq.on('error', e => resolve({ _http: 0, err: e.message })); if (data !== null) rq.write(data); rq.end(); }); }
const fake = () => fs.existsSync(ST) ? JSON.parse(fs.readFileSync(ST, 'utf8')) : { calls: [], instr: {} };
const posts = () => fake().calls.filter(c => /^POST .*payment-instructions/.test(c)).length;
const sq = (a, k) => execSync(`php /home/claude/payroc/sq.php ${a} ${k}`).toString();
const setting = (k) => sq('get', k);
(async () => {
  const lg = await api('login', { password: PW }); csrf = lg.csrf; ok('login', !!csrf, lg);
  for (const k of ['pr_on', 'pr_key', 'pr_tid', 'pr_sn', 'pr_tok', 'pr_log', 'pr_pend', 'pr_tests', 'pr_host']) sq('del', k);
  let j = await api('pr_info'); ok('info_not_ready', j.ok && !j.pr.ready && !j.pr.on, j);
  j = await api('pr_save', { on: true }); ok('on_needs_codes', j._http === 400, j);
  j = await api('pr_save', { tid: '68', sn: '', key: '' }); ok('tid_checked', j._http === 400, j);
  j = await api('pr_save', { tid: '6804001', sn: 'SIM-001', key: KEY, host: 'uat' });
  ok('save', j.ok && j.pr.key === '…abcd' && j.pr.tid === '6804001' && j.pr.ready && j.pr.dev, j);
  ok('key_not_returned', !JSON.stringify(j).includes(KEY), {});
  ok('key_encrypted_db', setting('pr_key') !== '' && !setting('pr_key').includes(KEY), setting('pr_key').slice(0, 20));
  j = await api('pr_check', {}); ok('check_token', j.check && j.check.ok, j);
  ok('token_encrypted', !/tok\d/.test(setting('pr_tok')), setting('pr_tok').slice(0, 30));
  j = await api('pr_save', { tid: '', sn: '', key: 'WRONGKEY-000000000000' }); j = await api('pr_check', {}); ok('bad_key', j.check && !j.check.ok && !JSON.stringify(j).includes('WRONGKEY'), j.check);
  await api('pr_save', { tid: '', sn: '', key: KEY });
  const T = async (op, x) => (await api('pr_test', Object.assign({ op }, x))).test || {};
  let t = await T('sale', { amt: 10, tc: 'TC1' }); ok('t_sale_ok', t.st === 'approved' && t.code === 'A' && t.last4 === '0011' && !!t.approval && !!t.pay, t);
  const saleId = t.id;
  t = await T('sale', { amt: 10.01, tc: 'decline' }); ok('t_decline', t.st === 'declined' && t.code === 'D', t);
  t = await T('sale', { amt: 10.99, tc: 'cancel' }); ok('t_cancel_device', t.st === 'cancelled', t);
  t = await T('sale', { amt: 10.88, tc: 'fail' }); ok('t_failure', t.st === 'failure' && /offline/i.test(t.msg), t);
  t = await T('sale', { amt: 10.77, tc: 'wait' }); ok('t_waiting', t.st === 'waiting', t);
  t = await T('stop', { id: t.id }); ok('t_stop', t.st === 'cancelled', t);
  t = await T('void', { id: saleId }); ok('t_void', t.void === 'reversed', t);
  t = await T('refund', { amt: 5, tc: 'TC3' }); ok('t_refund', t.st === 'approved' && t.code === 'A', t);
  let p0 = posts(); t = await T('sale', { amt: 10.55, tc: '500' }); ok('t_500_same_key', t.st === 'approved' && posts() === p0 + 2 && Object.keys(fake().instr).length > 0, { t, p: posts() - p0 });
  j = await api('pr_tests_csv'); ok('csv', j.csv && j.csv.includes('TC1') && !j.csv.includes(KEY) && !/476173\*+/.test(j.csv), (j.csv || '').slice(0, 200));
  ok('log_clean', !setting('pr_log').includes(KEY) && !/tok\d/.test(setting('pr_log')) && !/\d{6}\*+\d{4}/.test(setting('pr_log')), setting('pr_log').slice(0, 200));
  // ---- Checkout charge
  j = await api('pr_save', { tid: '', sn: '', key: '', on: true }); ok('on', j.pr.on, j);
  p0 = posts(); j = await api('pr_charge', { ids: [101], amt: 25 }); ok('charge_ok', j.ok && j.ref && j.last4 === '0011' && j.amt === 25, j); const ref1 = j.ref;
  const p1 = posts(); j = await api('pr_charge', { ids: [101], amt: 25 }); ok('charge_twice_no_new', j.again && j.ref === ref1 && posts() === p1, { j, p: posts() - p1 });
  j = await api('pr_charge', { ids: [101], amt: 30 }); ok('charge_other_amt_409', j._http === 409 && j.prPaid && j.prPaid.ref === ref1, j);
  j = await api('pr_charge', { ids: [102], amt: 25.01 }); ok('charge_decline', j._http === 402 && /declined/i.test(j.error), j);
  j = await api('pr_charge', { ids: [102], amt: 25 }); ok('charge_after_decline', j.ok && j.ref, j);
  p0 = posts(); j = await api('pr_charge', { ids: [103], amt: 25.77 }); ok('charge_waiting_409', j._http === 409 && /still on the Payroc device/.test(j.error), j);
  let f = fake(); const wid = Object.keys(f.instr).slice(-1)[0]; f.release = { [wid]: 1 }; fs.writeFileSync(ST, JSON.stringify(f));
  j = await api('pr_charge', { ids: [103], amt: 25.77 }); ok('charge_waiting_then_paid_no_new', j.ok && j.ref && posts() === p0 + 1, { j, p: posts() - p0 });
  p0 = posts(); j = await api('pr_charge', { ids: [104], amt: 25.55 }); ok('charge_500_one_instr', j.ok && posts() === p0 + 2, { j, p: posts() - p0 });
  // network lost: fake gateway down
  execSync("for p in $(pgrep -f '^php -S 127.0.0.1:18998'); do kill $p; done; true"); await new Promise(r => setTimeout(r, 400));
  j = await api('pr_charge', { ids: [105], amt: 25 }); ok('charge_net_down_unsure', j._http === 409 && /Not sure/.test(j.error), j);
  const pend = JSON.parse(setting('pr_pend')); const row = Object.values(pend).find(r => r.key === 'T105'); ok('pend_unsure_kept_key', row && row.st === 'unsure' && row.idem, row);
  spawn('php', ['-S', '127.0.0.1:18998', 'index.php'], { cwd: '/home/claude/payroc/fake', detached: true, stdio: 'ignore' }).unref(); await new Promise(r => setTimeout(r, 700));
  p0 = posts(); j = await api('pr_charge', { ids: [105], amt: 25 }); ok('charge_recover_same_key', j.ok && j.ref, j);
  j = await api('pr_charge', { ids: [105], amt: 25 }); ok('charge_recover_again_same', j.again, j);
  // cancel (void) approved not used
  j = await api('pr_cancel', { ref: ref1 }); ok('cancel_void', j.ok, j);
  j = await api('pr_waiting'); ok('waiting_list', j.on && !j.waiting.find(x => x.ref === ref1) && j.waiting.length >= 3, j);
  j = await api('pr_cancel', { ref: ref1 }); ok('cancel_twice_404', j._http === 404, j);
  // pr_take guards through checkout2 (no appointment needed for the failing checks)
  j = await api('pr_save', { tid: '', sn: '', key: '', on: false }); j = await api('pr_charge', { ids: [106], amt: 5 }); ok('off_refuses', j._http === 400, j);
  const fl = Object.entries(res).filter(([k, v]) => v !== 'PASS'); console.log(Object.keys(res).length + ' checks, ' + fl.length + ' fail'); fl.forEach(x => console.log(x[0], x[1]));
})();
