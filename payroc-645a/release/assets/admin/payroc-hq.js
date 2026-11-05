/* (2.99.645a - LENH PAYROC) Settings -> Payments: one box at the END "Payroc (NailFlow)" – Payroc Cloud codes (Terminal ID, device serial number, API key),
   "Card on Payroc" on/off, "Check the connection" (a token only), and the SANDBOX test runner for Payroc's certification (test orders only, never a ticket).
   ONLY for NailFlow (like the Dejavoo box); the server refuses everyone else. Nothing else on the page changes. Loaded with Settings (LAZY_FILES). */
'use strict';
(function () {
  if (typeof SET_PAGES === 'undefined') return;
  const vi = () => (typeof helpLang === 'function' ? !!helpLang() : true);
  const T = (en, v) => (vi() ? v : en);
  const mine = () => !IS_MGR && (!S.nfOnly || !!S.support);
  const say = (b, t, bad) => { const p = b.querySelector('#prMsg'); if (p) { p.textContent = t; p.style.color = bad ? 'var(--danger, #c0392b)' : ''; } };
  const logRows = (l) => (l || []).slice(0, 8).map(x => `<li>${esc(x.at || '')} · ${esc(x.op || '')}${x.amount != null ? ' $' + esc(x.amount) : ''} · ${esc(x.status || '')}${x.code ? ' ' + esc(x.code) : ''}${x.last4 ? ' · ••' + esc(x.last4) : ''}</li>`).join('');
  const testRows = (l) => (l || []).slice(0, 12).map(t => `<li>${esc(t.at || '')} · ${esc(t.tc || '')} ${esc(t.op || '')} $${esc(t.amt)} · <b>${esc(t.st || '')}</b>${t.code ? ' ' + esc(t.code) : ''}${t.approval ? ' · ' + esc(t.approval) : ''}${t.void ? ' · void: ' + esc(t.void) : ''}${t.refund ? ' · refund: ' + esc(t.refund) : ''}${t.msg ? ' · ' + esc(t.msg) : ''}
    ${t.st === 'inProgress' || t.st === 'waiting' ? ` <button type="button" class="btn" data-prt="poll" data-id="${esc(t.id)}">${esc(T('Result', 'Kết quả'))}</button> <button type="button" class="btn" data-prt="stop" data-id="${esc(t.id)}">${esc(T('Stop', 'Dừng'))}</button>` : ''}
    ${t.op === 'sale' && t.st === 'approved' && !t.void ? ` <button type="button" class="btn" data-prt="void" data-id="${esc(t.id)}">Void</button>` : ''}${t.op === 'sale' && t.st === 'approved' && !t.void && !t.refund ? ` <button type="button" class="btn" data-prt="refund_ref" data-id="${esc(t.id)}">${esc(T('Refund', 'Hoàn tiền'))}</button>` : ''}</li>`).join('');
  async function box(b) {
    if (!mine() || b.querySelector('#prBox')) return;
    const d = document.createElement('div'); d.className = 'card'; d.id = 'prBox'; d.style.marginTop = '12px'; b.appendChild(d);
    let j; try { j = await api('pr_info'); } catch (e) { d.remove(); return; }
    const v = j.pr || {};
    d.innerHTML = `<h3 style="margin-top:0">💳 Payroc <span class="muted">(NailFlow · Sandbox)</span></h3>
      <p class="hint">${esc(T('Payroc Cloud – sandbox (test) only, no real money. API: ', 'Payroc Cloud – chỉ sandbox (thử), không có tiền thật. API: '))}${esc(v.api || '')}</p>
      <div class="field"><label for="prTid">Terminal ID</label><input id="prTid" autocomplete="off" value="${esc(v.tid || '')}" placeholder="6804001"></div>
      <div class="field"><label for="prSn">${esc(T('Device serial number', 'Số serial máy (hoặc mã của Cloud Simulator)'))}</label><input id="prSn" autocomplete="off" value="${esc(v.sn || '')}"></div>
      <div class="field"><label for="prKey">API key</label><input id="prKey" type="password" autocomplete="new-password" value="" placeholder="${esc(v.key || T('not set', 'chưa có'))}"></div>
      <div class="field"><label for="prHost">${esc(T('Test host', 'Máy chủ thử'))}</label><select id="prHost"><option value="uat"${v.host === 'uat' ? ' selected' : ''}>api.uat.payroc.com</option><option value="std"${v.host === 'std' ? ' selected' : ''}>api.payroc.com (${esc(T('test key', 'key thử'))})</option></select></div>
      <p class="hint">${esc(T('Empty = keep the one saved. The key is never shown again.', 'Để trống = giữ mã đã lưu. Key không bao giờ hiện lại.'))}</p>
      <label class="chk"><input type="checkbox" id="prOn" ${v.on ? 'checked' : ''}> ${esc(T('Card on Payroc at Checkout', 'Cà thẻ qua Payroc ở Checkout'))}</label>
      <div class="navbtns" style="margin-top:10px"><button type="button" class="btn" id="prSave">${esc(T('Save', 'Lưu'))}</button> <button type="button" class="btn" id="prCheck">${esc(T('Check the connection', 'Kiểm kết nối'))}</button></div>
      <p class="hint" id="prMsg"></p><ul class="hint" id="prLog" style="margin:6px 0 0;padding-left:18px">${logRows(j.log)}</ul>
      <h4>${esc(T('Sandbox tests (certification)', 'Thử sandbox (để nộp Certification)'))}</h4>
      <div class="field"><label for="prTc">${esc(T('Test case name', 'Tên test case'))}</label><input id="prTc" autocomplete="off" placeholder="TC1"></div>
      <div class="field"><label for="prAmt">${esc(T('Test amount $', 'Số tiền thử $'))}</label><input id="prAmt" inputmode="decimal" autocomplete="off" value="10.00"></div>
      <div class="navbtns"><button type="button" class="btn" data-prt="sale">${esc(T('Test sale', 'Thử bán'))}</button> <button type="button" class="btn" data-prt="refund">${esc(T('Test refund on the device', 'Thử hoàn tiền trên máy'))}</button> <button type="button" class="btn" id="prCsv">CSV</button></div>
      <ul class="hint" id="prTests" style="margin:6px 0 0;padding-left:18px">${testRows(j.tests)}</ul>`;
    const fill = (r) => { if (r.log) d.querySelector('#prLog').innerHTML = logRows(r.log); if (r.tests) d.querySelector('#prTests').innerHTML = testRows(r.tests); if (r.pr) d.querySelector('#prKey').placeholder = r.pr.key || T('not set', 'chưa có'); };
    d.querySelector('#prSave').onclick = async () => {
      const body = { tid: d.querySelector('#prTid').value.trim(), sn: d.querySelector('#prSn').value.trim(), key: d.querySelector('#prKey').value.trim(), host: d.querySelector('#prHost').value, on: d.querySelector('#prOn').checked };
      try { const r = await api('pr_save', body); d.querySelector('#prKey').value = ''; fill(r); say(d, T('Saved.', 'Đã lưu.')); } catch (e) { say(d, e.message || String(e), true); }
    };
    d.querySelector('#prCheck').onclick = async () => {
      say(d, T('Checking…', 'Đang kiểm…'));
      try { const r = await api('pr_check', {}); fill(r); say(d, r.check && r.check.ok ? T('Connected (token OK).', 'Kết nối được (token OK).') : T('Not connected: ', 'Chưa kết nối: ') + ((r.check && r.check.msg) || ''), !(r.check && r.check.ok)); } catch (e) { say(d, e.message || String(e), true); }
    };
    d.querySelector('#prCsv').onclick = async () => { try { const r = await api('pr_tests_csv'); const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([r.csv], { type: 'text/csv' })); a.download = 'payroc-sandbox-tests.csv'; a.click(); } catch (e) { say(d, e.message || String(e), true); } };
    d.addEventListener('click', async (e) => {
      const x = e.target.closest('[data-prt]'); if (!x) return;
      const op = x.dataset.prt; say(d, T('Waiting for Payroc…', 'Đang chờ Payroc…'));
      try { const r = await api('pr_test', { op, id: x.dataset.id || '', amt: +d.querySelector('#prAmt').value || 0, tc: d.querySelector('#prTc').value.trim() }, null, true); fill(r); say(d, (r.test && r.test.st) || ''); } catch (er) { say(d, er.message || String(er), true); }
    });
  }
  const wrap = (fn) => { if (typeof fn !== 'function' || fn.__pr) return fn;
    const w = function (b) { const r = fn.apply(this, arguments); try { if (b) Promise.resolve(r).then(() => box(b)); } catch (e) {} return r; };
    for (const x of Object.keys(fn)) w[x] = fn[x]; w.__pr = 1; return w; };
  SET_PAGES.pay = wrap(SET_PAGES.pay);
})();
