/* (2.99.206 – order 407) checkout-receipt.js – part 2 of 2 of checkout.js (Checkout – receipts, print, send receipt). Global scope: every part sees the others; loaded in this order. */
/** Paid: change to give back, then (2.99.73) the receipt itself right away – as on Receipt #… – with big Print / Text receipt, and Done. */
function showPaid(r, salon, change, back) { // back = (2.99.268 – order 478) the rest of a group to check out next
  const giftAll = r.gift > 0 && r.collect <= 0.004, VI = I18.lang() === 'vi', L = (en, vi) => VI ? vi : en;
  /* (2.99.141) SO-LUAT "RECEIPT SAU CHECKOUT": iPad / iPhone → a BIG QR (white around it, scannable on a dark screen) the customer scans for the e-receipt;
     AN Desk (the desk computer) → no QR: 🖨 Print first and biggest (by itself when Settings → Receipt says so); 💬 Text receipt → the 🧾 Send receipt list
     of the owner / managers (the desk never sees the number). */
  const deskTxt = !IS_DESK ? '' : r.canQueue === false ? `<button type="button" class="btn rc-dktext" id="rcQueue" disabled>💬 ${esc(L('No number to text', 'Không có số để nhắn'))}</button>`
    : r.queued ? `<button type="button" class="btn rc-dktext" id="rcQueue" disabled>✓ ${esc(L('Sent to the owner / manager', 'Đã gửi tới admin/manager'))}</button>`
    : `<button type="button" class="btn rc-dktext" id="rcQueue">💬 Text receipt</button>`;
  /* (2.99.169 – order 355) ONE small popup in the middle, no scrolling on AN Desk: "✓ Paid $101.00", one small line (Cash · Receipt #1054 · NAME · Change),
     one row of big buttons (AN Desk: 🖨 Print · 💬 Text receipt · ✓ Done; iPad / iPhone: the QR to scan + 💬 Text receipt · ✓ Done, Print as a small link),
     "Show receipt ▾" (closed at first). Done / ✕ / Esc / Enter → back to Checkout. The receipt itself (print, QR, text) is the same as before. */
  const meta = [esc(r.method), 'Receipt #' + r.no, esc(r.name)].concat(change > 0 ? ['<b class="rc-pchg">Change ' + money(change) + '</b>'] : []).join(' · ');
  const extra = `${r.gift > 0 ? `<div class="paid-gift">🎁 Gift card ****${esc(r.giftLast)} balance: <b>${money(r.giftLeft)}</b></div>` : ''}${r.tip > 0 ? `<div class="muted">💳 Card tip ${money(r.tip)} (${r.tips.map(x => esc(x.tech) + ' ' + money(x.amt)).join(', ')}) – on the card machine</div>` : ''}`;
  const doneB = `<button type="button" class="btn rc-done rc-pbtn rc-pdone" id="rcNone">✓ Done</button>`;
  openSheet(`<div class="rc-pop"><div class="rc-popc">
    <button class="x rc-popx" type="button" aria-label="Close">✕</button>
    <div class="paid-box rc-phead"><div class="paid-ok">✓ ${giftAll && !r.giftSale ? 'Paid with gift card' : 'Paid ' + money(r2(r.collect + (r.giftSale ? r.giftSale.amount : 0)))}</div><div class="rc-pmeta">${meta}</div>${extra}</div>
    ${r.link && !IS_DESK ? `<div class="paid-qr rc-qr"><div class="paid-qr-i" id="rcQr" role="img" aria-label="QR code of the receipt link"></div><p data-raw><b>Scan to get your receipt</b><br><span>Escanee para su recibo</span></p></div>` : ''}
    ${IS_DESK ? `<div class="rc-prow"><button type="button" class="btn primary rc-dkprint rc-pbtn" id="rcPrint">🖨 Print</button>${deskTxt.replace('class="btn rc-dktext"', 'class="btn rc-dktext rc-pbtn"')}${doneB}</div>`
      : `<div class="rc-prow">${r.canText ? `<a class="btn primary rc-pbtn" id="rcText" href="${esc(smsHref(r.phone, r.textBody))}">💬 Text receipt</a>` : ''}${doneB}</div>
        <div class="rc-plinks"><button type="button" class="linkbtn" id="rcPrint">🖨 Print</button>${r.phone ? `<button type="button" class="linkbtn rc-next" id="rcNext">📅 Book next visit <small>(2–3 weeks)</small></button>` : ''}</div>`}
    <button type="button" class="linkbtn rc-show" id="rcShow" aria-expanded="false">Show receipt ▾</button>
    <div class="rc-paper" id="rcPaper" hidden>${receiptHTML(r, salon)}</div></div></div>`, (sh) => { sh.classList.add('pos-rc', 'rc-popsh'); // (2.99.92) the receipt screen after Checkout; (2.99.169) a small popup in the middle
    receiptButtons(sh, r, salon);
    { const im = $('#rcPaper img', sh); if (im) { im.loading = 'eager'; const pre = new Image(); pre.src = im.src; } } // (2.99.169) the receipt is folded: its logo is loaded anyway, so 🖨 Print starts at once
    $('#rcShow', sh).addEventListener('click', (e) => { const p = $('#rcPaper', sh), open = p.hidden; p.hidden = !open; e.currentTarget.setAttribute('aria-expanded', String(open)); e.currentTarget.textContent = open ? 'Hide receipt ▴' : 'Show receipt ▾'; });
    window.addEventListener('keydown', (e) => { if (e.key === 'Enter' && sh.isConnected && sh.classList.contains('rc-popsh') && !e.target.closest('a, button, input, textarea')) { e.preventDefault(); closeSheet(); } }, { signal: sheetAC ? sheetAC.signal : undefined }); // Enter = Done (Esc closes as every sheet)
    setTimeout(() => { try { $('#rcNone', sh).focus({ preventScroll: true }); } catch (e) {} }, 50);
    if (back) { // (2.99.268 – order 478) Done / ✕ / Enter → the Checkout of the rest of the group
      const nb = $('#rcNone', sh); if (nb) nb.textContent = '✓ ' + L('Done → rest of the group', 'Xong → phần còn lại của nhóm');
      let gone = false; const go = () => { if (gone) return; gone = true; setTimeout(() => openCheckout({ id: back.id, status: 'arrived', name: back.name }, true), 120); };
      $$('#rcNone, .rc-popx', sh).forEach(x => x.addEventListener('click', go));
      window.addEventListener('keydown', (e) => { if (e.key === 'Enter' && sh.isConnected && !e.target.closest('a, button, input, textarea')) go(); }, { signal: sheetAC ? sheetAC.signal : undefined }); }
    if (r.link && !IS_DESK) giftQr(r.link).then(svg => { const q = $('#rcQr', sh); if (q && svg) q.innerHTML = svg; else if (q) q.closest('.paid-qr').hidden = true; }); // (2.99.101)
    $('#rcQueue', sh)?.addEventListener('click', async (e) => { const b = e.currentTarget; if (b.disabled) return; b.disabled = true;
      try { await api('rq_add', { id: r.id }); r.queued = true; b.textContent = '✓ ' + L('Sent to the owner / manager', 'Đã gửi tới admin/manager'); }
      catch (x) { b.disabled = false; oops(x); } });
    if (IS_DESK && salon && salon.deskPrint) setTimeout(() => { if (sh.contains($('#rcPrint', sh))) printReceipt(r, salon); }, 400); // Settings → Receipt: AN Desk prints by itself
    $('#rcNone', sh).addEventListener('click', closeSheet);
    $('#rcNext', sh)?.addEventListener('click', () => { // (2.99.95) the same customer, tech and services, 2 weeks from today (they can pick up to 3 weeks)
      const first = (r.lines || []).filter(l => l.appt === (r.lines[0] || {}).appt), svc = [...new Set(first.map(l => +l.sid).filter(Boolean))], tech = +((first.find(l => +l.staff) || {}).staff || 0);
      const dt = new Date(); dt.setDate(dt.getDate() + 14); const ds = dt.toLocaleDateString('en-CA');
      closeSheet(); openBookSheet({ next: true, date: ds, phone: String(r.phone || '').replace(/\D/g, '').slice(-10), name: r.name.split(',')[0].replace(/ \+\d+$/, ''), staff: tech, services: svc });
      setTimeout(() => toast('📅 Suggested: 2–3 weeks from today – pick the day and time on step 3', 4500), 500); });
  });
}
/* (2.99.141) 🧾 SEND RECEIPT – Home icon (owner + managers): receipts the desk asked to text. "Text" opens Messages with the receipt text (1 text, short link);
   ~3 s later it leaves the list for "✓ Sent today". "Drop" = off the list without texting. Waiting over 24 h → folded "Older". */
async function openSendReceipts() {
  const VI = I18.lang() === 'vi', L = (en, vi) => VI ? vi : en;
  S.pageMode = true;
  openSheet(`<div class="sheet-head"><h2>🧾 ${esc(L('Send receipt', 'Gửi hoá đơn'))}</h2><button type="button" class="btn small x">${esc(L('Close', 'Đóng'))}</button></div>
    <p class="hint" style="margin:-4px 0 10px">${esc(L('Receipts the front desk asked to text. "Text" opens Messages with the receipt – you tap send.', 'Hoá đơn máy quầy nhờ nhắn cho khách. "Text" mở Tin nhắn có sẵn hoá đơn – anh bấm gửi.'))}</p><div id="rqBody"><p class="hint">…</p></div>`);
  let D; const fold = { old: false, sent: false }; const gone = new Set();
  const load = async () => { try { D = await api('rq_list'); } catch (e) { const x = $('#rqBody'); if (x) x.innerHTML = `<p class="err">${esc(e.message)}</p>`; return false; } setRqBadge(D.n); return true; };
  const rowH = (c, sent) => `<div class="rvt-row${sent ? ' dim' : ''}" data-q="${c.id}"><div class="rvt-i"><div class="rvt-n">${esc(c.name)}${c.test ? ' <span class="chip tstchip">TEST</span>' : ''} · <b>${money(c.total)}</b></div>
      <div class="rvt-m">🕐 ${esc(c.time)}${c.day !== (S.today || localToday()) ? ' · ' + esc(shortDate(c.day)) : ''}${c.techs.length ? ' · 💅 ' + esc(c.techs.join(', ')) : ''} · #${c.no}</div>
      ${sent ? `<div class="rvt-s">✓ ${esc(L('Texted', 'Đã nhắn'))} ${esc(c.doneAt)}${c.doneBy ? ' · ' + esc(c.doneBy) : ''}</div>` : !c.ok ? `<div class="rvt-s gray">${esc(L('No number to text', 'Không có số để nhắn'))}</div>` : ''}</div>
      ${sent ? '' : `<div class="rq-b">${c.ok ? `<a class="btn primary rvt-b" data-rqt="${c.id}" href="${esc(smsHref(c.phone, c.body))}">Text</a>` : ''}<button type="button" class="linkbtn rq-drop" data-rqd="${c.id}">${esc(L('Drop', 'Bỏ'))}</button></div>`}</div>`;
  const foldH = (k, label, rows, sent) => rows.length ? `<div class="bd-done${fold[k] ? ' open' : ''}"><button type="button" class="bd-done-h" data-fold="${k}" aria-expanded="${fold[k]}">${esc(label)} (${rows.length})</button>${fold[k] ? `<div class="rvt-list">${rows.map(c => rowH(c, sent)).join('')}</div>` : ''}</div>` : '';
  const draw = () => { const box = $('#rqBody'); if (!box || !D) return; const W = D.wait.filter(c => !gone.has(c.id)), O = D.old.filter(c => !gone.has(c.id));
    box.innerHTML = (W.length ? `<div class="rvt-list">${W.map(c => rowH(c, false)).join('')}</div>` : `<p class="muted rvt-empty">${esc(L('No receipts to send ✓', 'Không có hoá đơn chờ gửi ✓'))}</p>`)
      + foldH('old', L('Older (over 24 hours)', 'Cũ hơn (quá 24 giờ)'), O, false) + foldH('sent', '✓ ' + L('Sent today', 'Đã gửi hôm nay'), D.sent, true); };
  if (await load()) draw();
  const box = $('#rqBody'); if (!box) return;
  box.addEventListener('click', async (e) => {
    const f = e.target.closest('[data-fold]'); if (f) { fold[f.dataset.fold] = !fold[f.dataset.fold]; draw(); return; }
    const t = e.target.closest('[data-rqt]'); // Text: Messages opens (the link itself), the row leaves the list ~3 s later
    if (t) { const id = +t.dataset.rqt; api('rq_done', { id, kind: 'sent' }, null, true).then(x => setRqBadge(x.n)).catch(() => {});
      setTimeout(async () => { gone.add(id); if (await load()) draw(); }, 3000); return; }
    const d = e.target.closest('[data-rqd]');
    if (d) { const id = +d.dataset.rqd; d.disabled = true; try { const x = await api('rq_done', { id, kind: 'drop' }); setRqBadge(x.n); gone.add(id); if (await load()) draw(); } catch (x) { d.disabled = false; oops(x); } }
  });
}
/** Print and Text on a receipt (the Paid screen and a receipt opened from the list). */
function receiptButtons(sh, r, salon) {
  $('#rcPrint', sh)?.addEventListener('click', () => printReceipt(r, salon));
  $('#rcText', sh)?.addEventListener('click', () => {
    api('text_sent', { phone: r.phone, name: r.name, body: r.textBody, appt_id: r.appts[0] || 0, kind: 'receipt', receipt_id: r.id }, null, true).catch(() => {});
    setTimeout(() => toast('Receipt texted ✓'), 400);
  });
}
/** The receipt as printed (80 mm paper) and as shown on screen. */
function receiptHTML(r, s) {
  const row = (a, b, c = '') => `<div class="rc-row${c}"><span>${a}</span><span>${b}</span></div>`;
  const multi = new Set(r.lines.map(l => l.appt)).size > 1; let last = null;
  // 2.39.2: a receipt with the money typed for each tech shows one line per tech – never the services booked or their prices
  const lines = r.typed ? r.splits.map((x, i) => row(`${esc((r.splitNames || [])[i] || r.lineName || 'Service')} <small>· ${esc(x.tech)}</small>`, money(x.amt))).join('') : r.lines.map(l => { let h = ''; if (multi && l.appt !== last) { last = l.appt; h = `<div class="rc-who">${esc((r.names || {})[l.appt] || '')}</div>`; } return h + row(`${!l.sid && l.name === 'Design' ? '+ ' : ''}${esc(l.name)} <small>· ${esc(l.tech)}</small>`, money(l.price)); }).join('');
  const payName = (p) => p.m === 'Card' ? 'Card' + (p.last4 ? ' ****' + esc(p.last4) : '') : p.m === 'Other' ? esc(p.how) : 'Cash';
  return `<div class="rc">
    <div class="rc-head">${s.logo ? `<img class="rc-logo" src="${esc(s.logo)}" alt="" loading="lazy" decoding="async">` : ''}<b>${esc(s.name)}</b><div>${esc(s.address)}</div><div>${esc(s.phone)}</div></div>
    <div class="rc-meta"><span>Receipt #${r.no}${r.test ? ' <span class="chip tstchip">TEST</span>' : r.addPay ? ' <span class="chip addpaychip">ADD PAY</span>' : ''}</span><span>${esc(shortDate(r.day))}, ${parseD(r.day).getFullYear()} ${esc(r.time)}</span></div>
    ${r.status === 'void' ? `<div class="rc-void">VOID${r.voidReason ? ' – ' + esc(r.voidReason) : ''}</div>` : ''}
    <div class="rc-name">${esc(r.name)}</div>${lines}
    <div class="rc-sep"></div>
    ${row('Subtotal', money(r.subtotal))}${r.discount ? row('Discount' + (r.discNote ? ' (' + esc(r.discNote) + ')' : ''), '−' + money(r.discount)) : ''}${r.promo ? row(esc(r.promoLabel), '−' + money(r.promo)) : ''}${(r.offers || []).length ? r.offers.map(x => row(esc(x.line ? String(x.line).replace(/^[^A-Za-z0-9$]+/, '') : x.name + ' ' + x.amt), '−' + money(x.value))).join('') : (r.offersUsed || []).map(x => row('🎁 ' + esc(x), '')).join('')}${r.tax ? row(`Tax (${r.taxPct}%)`, money(r.tax)) : ''}
    ${r.deposit || r.gift ? row('Total', money(r.total), ' rc-total') : ''}${r.deposit ? row('Deposit paid online', '−' + money(r.deposit)) : ''}${r.gift ? row(`Gift card ****${esc(r.giftLast)}`, '−' + money(r.gift)) + `<div class="rc-gbal">GIFT CARD ****${esc(r.giftLast)} BALANCE: ${money(r.giftLeft || 0)}${(r.giftLeft || 0) <= 0.004 ? ' (used up)' : ''}</div>` : ''}
    ${row(r.deposit || r.gift ? 'Paid now' : 'TOTAL', money(r.collect), ' rc-total')}
    <div class="rc-sep"></div>
    ${r.pays.map(p => row(payName(p) + (p.add ? ` <small>(added ${esc(shortDate(String(p.at || '').slice(0, 10)))})</small>` : ''), money(p.amt)) + (p.m === 'Cash' && p.change > 0 ? row(`<small>Received ${money(p.given)} · change</small>`, `<small>${money(p.change)}</small>`) : '')).join('')}
    ${r.giftSale ? `<div class="rc-sep"></div>${row(`🎁 Gift card sold ****${esc(r.giftSale.last)}`, money(r.giftSale.amount))}${Object.entries(r.giftSale.by || {}).map(([k, v]) => row(`<small>&nbsp;&nbsp;paid by ${esc(k)}</small>`, `<small>${money(+v)}</small>`)).join('')}${row('Paid in all', money(r2(r.collect + r.giftSale.amount)), ' rc-total')}` : ''}
    ${(r.tips || []).map(x => row(`Tip (card) <small>· ${esc(x.tech)}</small>`, money(x.amt))).join('')}${(r.cashTips || []).map(x => row(`Tip (cash) <small>· ${esc(x.tech)}</small>`, money(x.amt))).join('')}
    ${r.refunds.map(f => row(`Refund ${esc(shortDate(f.at.slice(0, 10)))} (${esc(f.how)}${f.reason ? ' · ' + esc(f.reason) : ''})`, '−' + money(f.amt))).join('')}
    ${/ \(front desk\)$/.test(r.by || '') ? `<div class="rc-by">Checked out by: ${esc(r.by.replace(/ \(front desk\)$/, ''))}</div>` : ''}
    <div class="rc-thanks">Thank you! See you again soon 💅</div></div>`;
}
/** Print a receipt: the same receipt as on screen, on ONE page – a Letter page (the receipt in the middle, big enough to read) or 80 mm
    for a receipt printer (Settings → Receipt). No margins, so the browser has no room for its link / date lines. */
function printReceipt(r, s) {
  if ((s.paper || 'letter') === '80mm') return printHTML(`<div data-raw>${receiptHTML(r, s)}</div>`); // data-raw: printed in English, like the customer's link
  let pa = $('#printArea'); if (!pa) { pa = document.createElement('div'); pa.id = 'printArea'; document.body.appendChild(pa); }
  pa.innerHTML = `<div class="rc-letter" data-raw>${receiptHTML(r, s)}</div>`;
  let ps = $('#printPage'); if (!ps) { ps = document.createElement('style'); ps.id = 'printPage'; document.head.appendChild(ps); }
  ps.textContent = '@media print{@page{size:letter portrait;margin:0}}';
  document.body.classList.add('printing', 'print-rc-letter');
  const done = () => { document.body.classList.remove('printing', 'print-rc-letter'); window.removeEventListener('afterprint', done); };
  window.addEventListener('afterprint', done);
  const go = () => setTimeout(() => { try { window.print(); } catch (e) {} if (!('onafterprint' in window)) setTimeout(done, 1000); }, 60);
  const img = $('img', pa); if (img && !img.complete) { img.onload = img.onerror = go; setTimeout(go, 1500); } else go(); // the logo first
}
/** (2.99.95) No internet: the paper walk-in sheet (time, name, tech, services, $, tip, how paid) – made on this device, no server needed. */
function printWalkinSheet() {
  let pa = $('#printArea'); if (!pa) { pa = document.createElement('div'); pa.id = 'printArea'; document.body.appendChild(pa); }
  const name = S.day?.salon || 'American Nails & Spa', rows = Array.from({ length: 22 }, () => '<tr><td></td><td></td><td></td><td></td><td></td><td></td><td>Card · Cash · Gift</td></tr>').join('');
  pa.innerHTML = `<div class="ws-sheet" data-raw><h1>${esc(name)} – Walk-in sheet (no internet)</h1><p class="ws-d">Date: ____________________ &nbsp; Written by: ____________________</p>
    <table><thead><tr><th style="width:9%">Time</th><th style="width:21%">Name</th><th style="width:12%">Tech</th><th style="width:26%">Services</th><th style="width:9%">$</th><th style="width:8%">Tip</th><th style="width:15%">Paid by</th></tr></thead><tbody>${rows}</tbody></table>
    <p class="ws-f">When the internet is back: enter each one (Book → Walk-in, then Checkout) and write ✓ next to it.</p></div>`;
  let ps = $('#printPage'); if (!ps) { ps = document.createElement('style'); ps.id = 'printPage'; document.head.appendChild(ps); }
  ps.textContent = '@media print{@page{size:letter landscape;margin:10mm}body.printing #printArea{width:auto !important;padding:0 !important}}';
  document.body.classList.add('printing', 'print-letter');
  const done = () => { document.body.classList.remove('printing', 'print-letter'); window.removeEventListener('afterprint', done); };
  window.addEventListener('afterprint', done);
  setTimeout(() => { try { window.print(); } catch (e) {} if (!('onafterprint' in window)) setTimeout(done, 1000); }, 60);
}
/** Print one piece (receipt, close day) on its own: 80 mm wide for the counter's receipt printer (browser print). */
function printHTML(html) {
  let pa = $('#printArea'); if (!pa) { pa = document.createElement('div'); pa.id = 'printArea'; document.body.appendChild(pa); }
  pa.innerHTML = html;
  // the page: 80 mm wide and as long as the receipt (a receipt printer cuts after it); measured off screen at the printed width
  pa.style.cssText = 'display:block;position:absolute;left:-9999px;top:0;width:72mm';
  const mm = Math.ceil(pa.getBoundingClientRect().height * 25.4 / 96) + 8; pa.style.cssText = '';
  let ps = $('#printPage'); if (!ps) { ps = document.createElement('style'); ps.id = 'printPage'; document.head.appendChild(ps); }
  ps.textContent = `@media print{@page{size:80mm ${Math.max(60, mm)}mm;margin:0}}`; // no margins: no room for the browser's link / date lines
  document.body.classList.add('printing');
  const done = () => { document.body.classList.remove('printing'); window.removeEventListener('afterprint', done); };
  window.addEventListener('afterprint', done);
  setTimeout(() => { try { window.print(); } catch (e) {} if (!('onafterprint' in window)) setTimeout(done, 1000); }, 60);
}
/* (2.99.92) Checkout like a POS – only the LOOK changes (every box, button, number and rule is the same one as before).
   (2.99.140) kiểu A: 900 px and wider (iPad landscape, the desk computer) = 2 columns – left: the techs' cards, "+ Add tech", the offer, tip / discount;
   right: the totals, "Typing money for <TECH>", 4 quick prices, the number pad (always there), Card · Cash · Gift / Other.
   Narrower (iPhone, iPad upright) = 1 column; Card · Cash · Gift / Other stay at the bottom; a tap on a money box brings the number pad up from the bottom.
   theme: 'auto' (follows the device), 'light', 'dark' (the desk: always dark). */
const CK_WIDE = '(min-width: 900px)';
function posSetup(sh, theme, ctx) {
  sh.classList.add('pos', 'ckA'); sh.dataset.ckt = theme || 'auto'; ctx = ctx || {};
  const sig = sheetAC ? sheetAC.signal : undefined, mq = matchMedia(CK_WIDE), wide = () => mq.matches;
  /* (2.99.277 – order 489, hình checkout-mau2) LEFT (scrolls on its own): the tech cards 2 by 2, + Thêm thợ · Giảm giá · Sửa tip · 🎁 Bán gift card, the offer (1 line).
     RIGHT (~400 px, never scrolls): 1 small line + TỔNG CỘNG, Thẻ · Tiền mặt · Gift (64 px), the orange "Khách tự chọn tip", "Đang gõ tiền: …" + quick prices,
     the number pad filling what is left. Phone: the same, down; Thẻ · Tiền mặt · Gift stuck at the bottom. */
  const L = ['#tkTop', '#tkSplit', '#tkPeople', '#tkLoy', '#tkTip', '#ckLinks', '#tkGs', '#tkOffer', '#ckDisc'], R = ['#tkTot', '#ckBar', '#tkTipBig', '#tkPayBox', '#ckGift', '#tkErr', '.ck-padwrap'];
  const ORDER = ['#tkTop', '#tkSplit', '#tkPeople', '#tkLoy', '#tkTip', '#ckLinks', '#tkGs', '#tkOffer', '#ckDisc', '#tkTot', '#tkTipBig', '#tkPayBox', '#ckGift', '#tkErr', '#ckBar'];
  const get = (s) => sh.querySelector(s);
  // the number pad: taps go into the box last chosen – the iPhone / iPad keyboard stays away
  const pw = document.createElement('div'); pw.className = 'ck-padwrap';
  pw.innerHTML = `<div class="ck-padh"><span class="ck-padfor" id="ckPadFor" aria-live="polite"></span><button type="button" class="ck-padc" data-k="C">Xoá</button><button type="button" class="ck-padok" id="ckPadOk">Xong ✓</button></div>
    <div class="ck-quick" id="ckQuick" role="group" aria-label="Quick prices"></div>
    <div class="tk-pad" role="group" aria-label="Number pad">${['1', '2', '3', '4', '5', '6', '7', '8', '9', '.', '0', '⌫'].map(k => `<button type="button" data-k="${k}"${k === '⌫' ? ' aria-label="Delete" class="tk-pad-del"' : ''}>${k}</button>`).join('')}</div>`;
  const pad = $('.tk-pad', pw);
  const isNum = (e) => e && e.tagName === 'INPUT' && e.id !== 'tkGift' && !e.closest('#tkPayBox') && !(e.id === 'tkL4' && !wide()) && sh.contains(e) && !e.closest('.ck-svc') && (e.type === 'number' || /^(decimal|numeric|none)$/.test(e.getAttribute('inputmode') || ''));
  const selOf = (t) => t.id ? '#' + t.id : [...t.attributes].filter(a => a.name.startsWith('data-')).map(a => `[${a.name}="${a.value}"]`).join('') || '';
  let sel = '', buf = null, fresh = true; // (2.99.111) fresh: the box was just chosen – the first number REPLACES what is in it
  const tgt = () => (sel && sh.querySelector(sel)) || (wide() ? sh.querySelector('[data-spa="0"]') || sh.querySelector('[data-spp^="0:"]') : null);
  const open = (on) => { sh.classList.toggle('ck-padopen', !!on && !wide()); };
  const head = () => { const t = tgt(), f = $('#ckPadFor', pw), q = $('#ckQuick', pw); if (!f || !q) return;
    const lb = t && ctx.label ? ctx.label(t) : ['Typing', '']; f.innerHTML = `<span>${esc(lb[0])}</span>${lb[1] ? ' <b>' + esc(lb[1]) + '</b>' : ''}`;
    const qp = t && ctx.quick ? ctx.quick(t) : null; const k = (qp || []).join(',');
    if (q.dataset.k !== k) { q.dataset.k = k; q.innerHTML = (qp || []).map(v => `<button type="button" data-qv="${v}">${money(v).replace(/\.00$/, '')}</button>`).join(''); }
    q.hidden = !qp; };
  const mark = () => { $$('.pad-on', sh).forEach(x => x.classList.remove('pad-on', 'pad-fresh')); const t = tgt(); if (t) { t.classList.add('pad-on'); if (fresh && String(t.value || '') !== '') t.classList.add('pad-fresh'); } head(); };
  sh.__padPick = (t, noFocus) => { if (!t) return; if (selOf(t) === sel && noFocus && (wide() || sh.classList.contains('ck-padopen'))) return; sel = selOf(t); buf = null; fresh = true; t.setAttribute('inputmode', 'none');
    if (!noFocus) { try { t.focus({ preventScroll: true }); t.select(); } catch (e) {} open(true); if (!wide()) setTimeout(() => { try { t.scrollIntoView({ block: 'center', behavior: 'smooth' }); } catch (e) {} }, 30); }
    mark(); };
  sh.addEventListener('pointerdown', (e) => { const sl = e.target.closest && e.target.closest('.tk-sp select, .tk-sp [data-sptb]'); if (sl) sh.__padPick(sl.closest('.tk-sp').querySelector('[data-spa], [data-spp]'), true); }, true); // the tech's name (the ▼ list still opens): that row's box is the one the pad types into
  sh.addEventListener('pointerdown', (e) => { if (isNum(e.target)) e.target.setAttribute('inputmode', 'none'); }, true); // before the focus: no keyboard
  let userAt = 0; ['pointerdown', 'keydown'].forEach(ev => sh.addEventListener(ev, () => { userAt = Date.now(); }, true)); // (2.99.277 – order 489) the pad opens only for a person's tap / Tab – not when the screen focuses a box by itself
  sh.addEventListener('focusin', (e) => { if (isNum(e.target)) { const s = selOf(e.target); if (s !== sel) { sel = s; buf = null; fresh = true; try { e.target.select(); } catch (x) {} } if (Date.now() - userAt < 1500) open(true); mark(); } });
  pw.addEventListener('pointerdown', (e) => { if (e.target.closest('button')) e.preventDefault(); }); // the box keeps its focus
  const put = (t, v) => { t.value = v; t.dispatchEvent(new Event('input', { bubbles: true })); t.dispatchEvent(new Event('change', { bubbles: true })); };
  pw.addEventListener('click', (e) => {
    e.stopPropagation(); // the pad is not a tap on the Checkout behind it
    if (e.target.closest('#ckPadOk')) { open(false); const t = tgt(); if (t) try { t.blur(); } catch (x) {} return; }
    const qb = e.target.closest('[data-qv]'); if (qb) { const t = tgt(); if (!t) return; if (selOf(t) !== sel) sel = selOf(t); put(t, (+qb.dataset.qv).toFixed(2)); buf = null; fresh = true; mark(); return; } // a quick price: that tech's money (typing next replaces it)
    const b = e.target.closest('[data-k]'); const t = tgt(); if (!b || !t) return;
    if (selOf(t) !== sel) { sel = selOf(t); buf = null; fresh = true; }
    const k = b.dataset.k; let v = fresh ? '' : (buf ?? String(t.value || '')); fresh = false; // (2.99.111) a new number replaces the old one (never added after it)
    if (k === '⌫') v = v.slice(0, -1); else if (k === 'C') v = ''; else if (k === '.') { if (!v.includes('.')) v = (v || '0') + '.'; }
    else { if (/\.\d\d$/.test(v) || v.replace('.', '').length >= 7) return; v = v === '0' ? k : v + k; }
    buf = v; put(t, v.endsWith('.') ? v.slice(0, -1) : v); mark(); // a number box cannot hold "12." – the pad keeps it
  });
  const mo = new MutationObserver(() => { const t = tgt(); if (t && !t.classList.contains('pad-on')) mark(); else if (!t && sel) head(); }); mo.observe(sh, { childList: true, subtree: true }); if (sig) sig.addEventListener('abort', () => mo.disconnect()); // a row drawn again keeps its blue frame
  // (2.99.111) a tap ANYWHERE on a tech's card (not the ▼ tech list, ✕, + Service) or on the discount / tip / gift card box chooses that money box
  sh.addEventListener('click', (e) => {
    const t0 = e.target; if (t0.closest('.ck-padwrap, .ck-svc')) return;
    if (t0.closest('select, button, a')) { if (!wide()) open(false); return; } // (2.99.140) iPhone: a tap on anything else puts the pad away
    let box = null; const row = t0.closest('.tk-sp');
    if (row) box = (t0.closest('.ck-part') || row).querySelector('[data-spa], [data-spp]'); // (2.99.194) a line: its own box
    else { if (t0.closest('#tkPayBox')) return; /* (2.99.169) the pay popup has its own pad */ const f = t0.closest('.tk-price, .tk-disc, #tkGiftRow, #tkTipT .field, .tk-srow'); if (f) box = f.querySelector('input'); }
    if (!box || box.disabled) { if (!wide()) open(false); return; }
    if (isNum(box)) { if (t0 !== box || !box.classList.contains('pad-on') || !sh.classList.contains('ck-padopen')) sh.__padPick(box); return; }
    if (t0 !== box) { box.focus(); } try { box.select(); } catch (x) {} // the gift card number / card last 4 (iPhone): its own keyboard
  }, { signal: sig });
  const lay = () => {
    const cols = sh.querySelector('.tk-cols');
    if (wide() && !cols) {
      const c = document.createElement('div'); c.className = 'tk-cols'; const l = document.createElement('div'); l.className = 'tk-l'; const r = document.createElement('div'); r.className = 'tk-r';
      const first = get('#tkTop'); if (!first) return; first.before(c); c.append(l, r);
      if (!pw.isConnected) sh.append(pw);
      L.forEach(s => { const e = get(s); if (e) l.append(e); }); R.forEach(s => { const e = get(s); if (e) r.append(e); });
    } else if (!wide()) { if (cols) { ORDER.forEach(s => { const e = get(s); if (e) cols.before(e); }); cols.remove(); } sh.append(pw);
      const bar = get('#ckBar'), tb = get('#tkTipBig'); if (bar && tb) bar.append(tb); } // (2.99.277 – order 489) phone: the orange tip button stays in sight with Thẻ · Tiền mặt · Gift
    open(false); if (wide() && !sel) { const f = sh.querySelector('[data-spa="0"]') || sh.querySelector('[data-spp^="0:"]'); if (f) sh.__padPick(f, true); } mark();
  };
  setTimeout(() => { if ((!sig || !sig.aborted) && wide() && !sel) { const f = sh.querySelector('[data-spa="0"]') || sh.querySelector('[data-spp^="0:"]'); if (f) sh.__padPick(f); } }, 60); // (2.99.111) the 1st tech's money box is chosen
  lay(); mq.addEventListener('change', lay, sig ? { signal: sig } : undefined); // the iPad turned: 2 columns ↔ 1 column
}
/** (2.99.59) A change on a receipt of a CLOSED payroll week: ask first; the closed week is not changed – the difference goes into next week. */
function payClosedAsk(box, go) {
  confirmIn(box, 'This receipt is in a payroll week that is already CLOSED (paid). The closed week stays as it was; the difference for each tech goes into next week as “Adjustment from last week” (Activity log). Go ahead?', 'Yes, change it', go, true);
}
const carryTxt = (c) => (c || []).length ? ' · next week: ' + c.map(x => `${x.name} ${x.amt > 0 ? '+' : '−'}${money(Math.abs(x.amt))}`).join(', ') : '';
/** A receipt: print, text; the owner can Void or Refund it (with a reason – receipts are never deleted). */
async function openReceipt(id) {
  let x; try { x = await api('receipt', null, { id }); } catch (e) { return oops(e); }
  const r = x.receipt, s = x.salon, left = r2(r.total - (r.deposit || 0) - r.refund); // (2.99.59) gift card money can go back on the card
  const rcEd = !IS_MGR && !IS_DESK && r.status === 'paid' && !(r.refund > 0) && (r.paySplits || []).length > 0; // (2.99.199 – order 398) the owner: tap a tech / a line to change it
  openSheet(`${head('Receipt #' + r.no, `${esc(shortDate(r.day))} · ${esc(r.time)} · ${esc(r.by)}${r.phone ? '<br>' + esc(r.name) + ' · ' + phL(r.phone) : ''}`)}
    ${r.status === 'void' ? `<p class="warnline">VOID · ${esc(r.voidReason)} · ${esc(r.voidBy)} · ${esc(shortDate(r.voidAt.slice(0, 10)))} ${esc(r.voidAt.slice(11, 16))}</p>` : ''}
    <div class="rc-paper">${receiptHTML(r, s)}</div>
    ${(r.adminFee && (r.paySplits || []).length) || (rcEd && (r.paySplits || []).length) || (r.paySplits || []).some(x => (x.lines || []).length) || (!r.typed && r.splits && r.splits.length) ? `<div class="rc-split"><span class="lbl">Techs${r.adminFee ? ` <span class="muted">(after the $1 rule)</span>` : ''}</span>${((r.paySplits || []).length ? r.paySplits : r.splits).map((x, i) => `<div class="tk-row"><span>${rcEd && !x.feeOnly ? `<button type="button" class="lnk rc-ed" data-rce="${i}:-1">${esc(x.tech)}</button>` : esc(x.tech)}</span><span>${money(x.amt)}</span></div>${(x.lines || []).map((l, k) => `<div class="tk-row rc-line"><span>${rcEd ? `<button type="button" class="lnk rc-ed" data-rce="${i}:${k}">↳ ${esc(l.n || 'Service')} ${money(l.g)}</button>` : `↳ ${esc(l.n || 'Service')} ${money(l.g)}`}</span><span>${+l.a > 0 ? '−' + money(+l.a) + ' $1 rule' : ''}</span></div>`).join('')}`).join('')}${r.techsEdited ? `<p class="hint small rc-edited">✎ ${esc(r.techsEdited)}</p>` : ''}</div>` : ''}
    ${!IS_MGR && !IS_DESK && r.testPhone ? `<div class="rc-ap"><span>${r.addPay ? '<span class="chip addpaychip">ADD PAY</span> counted for the techs' : '<span class="chip tstchip">TEST</span> not counted'}</span>${r.addPay ? '<button type="button" class="btn small" id="rcAddPay">🧪 Make it TEST</button>' : ''}</div>` : ''}
    ${rcEd ? '<p class="hint small rc-edhint">Tap a tech or a “↳ Service” line to change who did it, its money, or split it.</p>' : ''}
    <div class="rc-opts"><button type="button" class="btn" id="rcPrint">🖨 Print</button>${r.canText ? `<a class="btn" id="rcText" href="${esc(smsHref(r.phone, r.textBody))}">💬 Text receipt</a>` : ''}</div>
    ${!IS_MGR && !IS_DESK && r.status === 'paid' ? `<div class="rc-opts rc-danger">${left > 0 ? '<button type="button" class="btn ghost" id="rcRefund">↩ Refund</button>' : ''}${r.refund > 0 ? '' : '<button type="button" class="btn red" id="rcVoid">Void</button>'}</div>` : ''}
    ${!IS_MGR && !IS_DESK && r.status === 'paid' ? '<button type="button" class="linkbtn" id="rcTipEdit">✎ Edit tips</button><div id="rcTipBox"></div>' : ''}
    ${!IS_MGR && !IS_DESK && r.status === 'paid' && (r.moneyLines || []).length ? `<button type="button" class="linkbtn" id="rcMoneyEdit">${LV('✎ Fix service prices', '✎ Sửa tiền dịch vụ')}</button>` : ''}${r.moneyEdited ? `<p class="hint small rc-moneyed">${esc(r.moneyEdited)}</p>` : ''}
    ${window.RcSwap ? RcSwap.btn(r) : ''}
    ${!IS_DESK && r.status === 'paid' && r.redoUntil && (S.today || localToday()) <= r.redoUntil ? `<button type="button" class="btn rc-redo" id="rcRedo">🔁 Redo (free fix)${r.redos ? ` <small>(${r.redos} already)</small>` : ''}</button><div id="rcRedoBox"></div>` : ''}
    ${r.status === 'paid' && (r.offerUses || []).length ? `<div class="ap-offers">${r.offerUses.map(u => `<div class="ap-ofu">✅ ${esc(u.text.replace(/^Discount:/, 'Discount used:'))} <span class="muted">· ${esc(u.by || '')}</span>${IS_DESK ? '' : ` <button type="button" class="linkbtn" data-ofu="${u.id}">Undo</button>`}</div>`).join('')}</div>` : ''}
    <div id="rcBox"></div>
    ${r.texted ? `<p class="hint" style="margin-top:10px">Texted ${esc(shortDate(r.texted.slice(0, 10)))} ${esc(r.texted.slice(11, 16))}</p>` : ''}`, (sh) => { if (innerWidth >= 700) sh.classList.add('pos-rc'); // (2.99.92) the receipt full screen on the iPad
    receiptButtons(sh, r, s);
    if (window.RcSwap) RcSwap.bind(sh, r); // (2.99.294 – order 511) Đổi khách
    const box = $('#rcBox', sh);
    $('#rcRedo', sh)?.addEventListener('click', async () => { // (2.99.102) a $0 visit today linked to this receipt: no turn, no money, not a visit, no Rewards, no payroll
      const rb = $('#rcRedoBox', sh); let d; try { d = await ensureDay(S.today || localToday()); } catch (e) { return oops(e); }
      const orig = ((r.lines || []).find(l => +l.staff) || {}).staff || 0;
      rb.innerHTML = `<div class="confirm"><p><b>Redo (free fix)</b> – checked in now, $0. Who does it? <small class="muted">(no turn, no money, not counted as a visit)</small></p><div class="svc-chips">${(d.staff || []).map(t => `<button type="button" data-rdt="${t.id}" class="${t.id === orig ? 'on' : ''}">${esc(t.name)}${t.id === orig ? ' <small>(original)</small>' : ''}</button>`).join('')}</div>
        <div class="row" style="margin-top:8px"><button type="button" class="btn small primary" id="rdGo">Check in the Redo</button><button type="button" class="btn small" id="rdNo">Go back</button></div></div>`;
      let pick = orig; $$('[data-rdt]', rb).forEach(b => b.addEventListener('click', () => { pick = +b.dataset.rdt; $$('[data-rdt]', rb).forEach(x => x.classList.toggle('on', x === b)); }));
      $('#rdNo', rb).addEventListener('click', () => { rb.innerHTML = ''; });
      $('#rdGo', rb).addEventListener('click', async (e) => { const bt = e.currentTarget; bt.disabled = true; try { await api('redo_create', { id: r.id, staff: pick }); closeSheet(); toast('🔁 Redo checked in ($0)'); S.day = null; setTab('checkin'); } catch (er) { oops(er); bt.disabled = false; } }); });
    const done = (y, msg) => { toast(msg); openReceipt(y.receipt.id); if (S.tab === 'history' || S.tab === 'checkout') setTab(S.tab); else refreshCurrent(); };
    $('#rcMoneyEdit', sh)?.addEventListener('click', () => rcMoneyEdit(r)); // (2.99.345 – lệnh 580)
    $('#rcTipEdit', sh)?.addEventListener('click', () => { // (2.99.54) change the tips after the payment (Activity log + Money & security log)
      const techs = [...new Map([...(r.splits || []), ...(r.tips || []), ...(r.cashTips || [])].filter(x => x.staff).map(x => [x.staff, x.tech])).entries()];
      const cur = (list, sid) => ((list || []).find(x => x.staff === sid) || {}).amt || 0;
      const tb = $('#rcTipBox', sh);
      tb.innerHTML = `<div class="card"><table class="rp-t"><tr><th>Tech</th><th>💳 Card tip</th><th>💵 Cash tip</th></tr>${techs.map(([sid, nm]) => `<tr><td>${esc(nm)}</td>
        <td><input class="inp" type="number" inputmode="decimal" step="0.01" min="0" data-et="card:${sid}" value="${cur(r.tips, sid).toFixed(2)}"></td>
        <td><input class="inp" type="number" inputmode="decimal" step="0.01" min="0" data-et="cash:${sid}" value="${cur(r.cashTips, sid).toFixed(2)}"></td></tr>`).join('')}</table>
        <button type="button" class="btn primary block" id="rcTipSave" style="margin-top:8px">Save tips</button><p class="err" id="rcTipErr" hidden></p></div>`;
      $('#rcTipSave', sh).addEventListener('click', async (ev) => { const sb = ev.currentTarget; if (sb.disabled) return; sb.disabled = true; setTimeout(() => { if (sb.isConnected) sb.disabled = false; }, 4000); // (2.99.92)
        const get = (k) => $$(`[data-et^="${k}:"]`, tb).map(i => ({ staff: +i.dataset.et.split(':')[1], amt: r2(i.value) })).filter(x => x.amt > 0);
        const card = get('card'), cash = get('cash');
        const go = async (okc) => { const y = await api('receipt_tips_edit', { id: r.id, tips: card, tip_total: r2(card.reduce((s0, x) => s0 + x.amt, 0)), cash_tips: cash, cash_tip_total: r2(cash.reduce((s0, x) => s0 + x.amt, 0)), ok_closed: okc });
          toast('Tips saved ✓' + carryTxt(y.carry) + (y.tipNote ? ' · ' + y.tipNote : ''), y.tipNote ? 8000 : 5000); openReceipt(y.receipt.id); refreshCurrent(); };
        try { await go(false); }
        catch (e) { if (e.message === 'PAYROLL_CLOSED') return payClosedAsk(tb, () => go(true).catch(oops)); const er = $('#rcTipErr', sh); er.textContent = e.message; er.hidden = false; } });
    });
    /* (2.99.194 – order 392) the owner: one tech's money on this receipt → its service lines (e.g. $60 = $30 + $30); the $1 rule again line by line.
       Only the techs' pay changes (that tech, the $1 tech) – never the customer's total, tips or how it was paid. Money & security log. */
    $$('[data-rce]', sh).forEach(b => b.addEventListener('click', () => { const [i, k] = b.dataset.rce.split(':').map(Number); rcLinesEdit(r, i, k); })); // (2.99.199 – order 398)
    $('#rcAddPay', sh)?.addEventListener('click', async (e) => { const b = e.currentTarget; b.disabled = true; // (2.99.198 – order 397) TEST ↔ ADD PAY (Money & security log)
      try { const y = await api('receipt_addpay', { id: r.id, on: !r.addPay }); toast(y.addPay ? `#${r.no}: ADD PAY – counted for the techs ✓` : `#${r.no}: TEST – not counted`, 5000); openReceipt(r.id); refreshCurrent(); }
      catch (x) { b.disabled = false; oops(x); } });
    $('#rcFeeFix', sh)?.addEventListener('click', () => {
      const fb = $('#rcFeeBox', sh), feeTo = ((r.paySplits || []).find(y => y.feeOnly || +y.fee > 0) || {}).staff;
      const techs = (r.paySplits || []).filter(x => !x.feeOnly && +x.gross > 0 && x.staff !== feeTo);
      let cur = techs[0], L = [];
      const reset = () => { L = (cur.lines || []).length ? cur.lines.map(l => ({ name: l.n || 'Service', amt: +l.g })) : [{ name: 'Service', amt: +cur.gross }, { name: 'Service', amt: null }]; };
      const draw = () => { const sum = r2(L.reduce((s0, l) => s0 + (+l.amt || 0), 0)), ok = Math.abs(sum - +cur.gross) < 0.006;
        fb.innerHTML = `<div class="card rc-fee"><p><b>$1 rule lines</b> – each service on its own. The customer’s total, tips and payment stay the same.</p>
          ${techs.length > 1 ? `<div class="svc-chips">${techs.map(x => `<button type="button" data-fft="${x.staff}" class="${x.staff === cur.staff ? 'on' : ''}">${esc(x.tech)}</button>`).join('')}</div>` : ''}
          <p>${esc(cur.tech)}: <b>${money(+cur.gross)}</b> on this receipt · now $1 rule −${money(r2(+cur.gross - +cur.amt))}</p>
          ${L.map((l, k) => `<div class="tk-row rc-fl"><input class="inp" data-ffn="${k}" maxlength="40" value="${esc(l.name)}" aria-label="Service ${k + 1}"><input class="inp" type="number" inputmode="decimal" step="0.01" min="0" data-ffa="${k}" value="${l.amt === null ? '' : (+l.amt).toFixed(2)}" placeholder="0.00" aria-label="Money ${k + 1}">${L.length > 1 ? `<button type="button" class="btn small" data-ffx="${k}" aria-label="Remove">✕</button>` : ''}</div>`).join('')}
          <button type="button" class="linkbtn" id="ffAdd">+ Line</button>
          <p class="${ok ? 'muted' : 'err'}" id="ffSum">Lines: ${money(sum)} ${ok ? '✓' : `– must be ${money(+cur.gross)}`}</p>
          <div class="row"><button type="button" class="btn small primary" id="ffSave"${ok ? '' : ' disabled'}>Save</button><button type="button" class="btn small" id="ffNo">Go back</button></div><p class="err" id="ffErr" hidden></p></div>`; };
      reset(); draw();
      fb.oninput = (e) => { const t0 = e.target; if (t0.dataset.ffn !== undefined) L[+t0.dataset.ffn].name = t0.value; if (t0.dataset.ffa !== undefined) { L[+t0.dataset.ffa].amt = t0.value === '' ? null : Math.max(0, +t0.value || 0);
        const sum = r2(L.reduce((s0, l) => s0 + (+l.amt || 0), 0)), ok = Math.abs(sum - +cur.gross) < 0.006, ps = $('#ffSum', fb); ps.className = ok ? 'muted' : 'err'; ps.textContent = `Lines: ${money(sum)} ${ok ? '✓' : '– must be ' + money(+cur.gross)}`; $('#ffSave', fb).disabled = !ok; } };
      fb.onclick = async (e) => { const b = e.target.closest('button'); if (!b) return;
        if (b.dataset.fft) { cur = techs.find(x => x.staff === +b.dataset.fft) || cur; reset(); draw(); return; }
        if (b.dataset.ffx !== undefined) { L.splice(+b.dataset.ffx, 1); draw(); return; }
        if (b.id === 'ffAdd') { L.push({ name: 'Service', amt: null }); draw(); return; }
        if (b.id === 'ffNo') { fb.innerHTML = ''; return; }
        if (b.id === 'ffSave') { b.disabled = true; try { const y = await api('receipt_fee_lines', { id: r.id, staff: cur.staff, lines: L.map(l => ({ name: l.name, amt: r2(+l.amt || 0) })) });
          toast(`${y.fix.tech}: $1 rule ${money(y.fix.before)} → ${money(y.fix.after)} ✓`, 6000); openReceipt(r.id); refreshCurrent(); }
          catch (x2) { b.disabled = false; const er = $('#ffErr', fb); er.textContent = x2.message; er.hidden = false; } } };
    });
    $$('[data-ofu]', sh).forEach(b => b.addEventListener('click', () => confirmIn(box, 'Undo this discount? The offer is given back (if it is not over).', 'Undo', async () => { // (2.99.49)
      try { await api('offer_undo', { id: +b.dataset.ofu }); toast('Offer given back'); openReceipt(r.id); refreshCurrent(); } catch (e) { oops(e); } }, true)));
    /* (2.99.95) money that went on a card: refunded on the DPS machine first – a red box + "Done on DPS" before it can be saved */
    const isP5 = (r.pays || []).some(p => p.m === 'Card' && (p.dv || p.pr /* (2.99.645a) Payroc too */)); /* (2.99.638d) paid on the Dejavoo P5: it gives the money back by itself */
    const isPR = (r.pays || []).some(p => p.m === 'Card' && p.pr); /* (2.99.645a) paid on Payroc: Payroc gives it back by itself (same as the P5) */
    const dpsBox = (amt) => amt > 0.004 ? (isPR ? `<div class="dps-back"><b>${money(amt)} ${LV('goes back to the card through Payroc by itself (a refund: the customer taps the card on the Payroc device)', 'tự trả về thẻ qua Payroc (hoàn 1 phần: khách chạm thẻ lại trên máy Payroc)')}</b><input type="checkbox" id="dpsDone" checked hidden></div>` : isP5 ? `<div class="dps-back"><b>${money(amt)} ${LV('goes back to the card on the P5 by itself (a refund: the customer taps the card on the P5)', 'tự trả về thẻ qua máy P5 (hoàn 1 phần: khách chạm thẻ lại trên P5)')}</b><input type="checkbox" id="dpsDone" checked hidden></div>` : `<div class="dps-back"><b>Refund ${money(amt)} on the DPS machine now</b><label class="check"><input type="checkbox" id="dpsDone"><span>Done on DPS</span></label></div>`) : '';
    const gsV = r.giftSale && r.giftSale.live ? r.giftSale : null; /* (2.99.627 L2) the gift card sold on this bill is voided with it */
    const cardOf = () => r2((r.pays || []).filter(p => p.m === 'Card').reduce((t0, p) => t0 + (+p.amt || 0), 0) + (+r.tip || 0) + (gsV ? +((gsV.by || {}).Card || 0) : 0));
    $('#rcVoid', sh)?.addEventListener('click', () => {
      box.innerHTML = `<div class="confirm"><p>Void receipt #${r.no}? The appointments go back to “checked in” so they can be paid again. The receipt stays, marked VOID.</p>${gsV ? `<p><b>This also voids gift card …${esc(gsV.last)} (${money(gsV.amount)}).</b></p>` : ''}${dpsBox(cardOf())}
        <div class="field"><label for="rcWhy">Reason</label><input id="rcWhy" class="inp" maxlength="160" placeholder="e.g. wrong amount, paid twice"></div>
        <div class="row"><button type="button" class="btn small redfill" data-yes>Void receipt</button><button type="button" class="btn small" data-no>Go back</button></div><p class="err" hidden></p></div>`;
      $('[data-no]', box).addEventListener('click', () => { box.innerHTML = ''; });
      $('[data-yes]', box).addEventListener('click', async (e) => {
        e.target.disabled = true;
        if (cardOf() > 0.004 && !$('#dpsDone', box)?.checked) { e.target.disabled = false; const er = $('.err', box); er.textContent = `Refund ${money(cardOf())} on the DPS machine first, then tick “Done on DPS”.`; er.hidden = false; return; }
        const go = async (okc) => { const y = await api('receipt_void', { id: r.id, reason: $('#rcWhy', box).value, ok_closed: okc, dps_done: !!$('#dpsDone', box)?.checked }, null, isP5 /* (2.99.638d) the P5 may take up to 2 minutes */); done(y, `Receipt #${r.no} voided` + carryTxt(y.carry)); if (y.tipNote) setTimeout(() => toast(y.tipNote, 7000), 1200); };
        try { await go(false); }
        catch (x2) { if (x2.message === 'PAYROLL_CLOSED') return payClosedAsk(box, () => go(true).catch(oops)); e.target.disabled = false; const er = $('.err', box); er.textContent = x2.message; er.hidden = false; }
      });
      box.scrollIntoView({ block: 'nearest', behavior: 'smooth' }); $('#rcWhy', box).focus();
    });
    $('#rcRefund', sh)?.addEventListener('click', () => { // (2.99.59) part of the money back: how much, to what, which tech pays (by their money unless typed), the $1 rule again
      let how = r.gift > 0 && r2(r.collect - r.refund) <= 0 ? 'Gift card' : r.pays[0]?.m === 'Other' ? 'Other' : (r.pays[0]?.m || 'Cash'), typed = null, prev = null;
      box.innerHTML = `<div class="confirm"><p>Give money back on receipt #${r.no}? The receipt stays; the refund is written on it and taken off the day's report and the techs' pay.</p>
        <div class="field"><label for="rfAmt">Amount $ <span class="muted">(up to ${money(left)})</span></label><input id="rfAmt" class="inp" type="number" inputmode="decimal" step="0.01" min="0.01" max="${left}" value="${left.toFixed(2)}"></div>
        <span class="lbl">Refund to</span><div class="pay-chips" id="rfHow">${['Card', 'Cash', 'Gift card', 'Other'].map(h => `<button type="button" data-h="${h}" class="${h === how ? 'on' : ''}">${h === 'Gift card' ? '🎁 Gift card' : h}</button>`).join('')}</div>
        <p class="hint" id="rfGiftHint" hidden></p><div id="rfDps"></div>
        <span class="lbl" style="margin-top:10px">Taken from <span class="muted">(by each tech’s money – change it if needed)</span></span><div id="rfTechs"></div><p class="hint" id="rfFee"></p>
        <div class="field" style="margin-top:10px"><label for="rfWhy">Reason <span class="muted">(needed)</span></label><input id="rfWhy" class="inp" maxlength="160" placeholder="e.g. customer not happy with the color"></div>
        <div class="row"><button type="button" class="btn small redfill" data-yes>Refund</button><button type="button" class="btn small" data-no>Go back</button></div><p class="err" hidden></p></div>`;
      const dpsDraw = () => { const d = $('#rfDps', box); if (d) { const was = !!$('#dpsDone', box)?.checked; d.innerHTML = how === 'Card' ? dpsBox(+$('#rfAmt', box).value || 0) : ''; const c = $('#dpsDone', box); if (c) c.checked = was; } };
      const gh = () => { dpsDraw(); const h = $('#rfGiftHint', box); h.hidden = how !== 'Gift card'; h.textContent = r.giftLast ? `Goes back on the gift card ****${r.giftLast}.` : 'A new gift card is made for the customer (its code shows after).'; };
      const preview = async () => {
        const amt = +$('#rfAmt', box).value || 0;
        try { prev = await api('refund_preview', null, { id: r.id, amount: amt, how, techs: typed ? JSON.stringify(typed) : '' }); } catch (x) { $('#rfFee', box).textContent = x.message; return; }
        if (!typed) $('#rfTechs', box).innerHTML = prev.techs.map(t => `<div class="tk-srow"><span>${esc(t.tech)}</span><span class="tk-price"><span>$</span><input type="number" inputmode="decimal" step="0.01" min="0" data-rft="${t.staff}" value="${t.amt.toFixed(2)}"></span></div>`).join('') || '<p class="muted">—</p>';
        $('#rfFee', box).textContent = (prev.tax ? `Sales tax ${money(prev.tax)} goes back to the customer – not taken from the techs. ` : '') + (prev.fee.length ? prev.fee.map(f => `${f.tech}: the row is under ${money(f.min || 39).replace('.00', '')} now → the $${f.amt === 1 ? '1' : f.amt.toFixed(2)} goes back to ${f.tech} (not to the $1 rule).`).join(' ') : ''); // (2.99.88)
      };
      $('#rfAmt', box).addEventListener('input', () => { typed = null; preview(); dpsDraw(); });
      box.addEventListener('input', (e) => { if (e.target.dataset.rft === undefined) return; typed = $$('[data-rft]', box).map(i => ({ staff: +i.dataset.rft, amt: r2(+i.value || 0) })); clearTimeout(box._t); box._t = setTimeout(preview, 300); });
      $$('[data-h]', box).forEach(b => b.addEventListener('click', () => { how = b.dataset.h; $$('[data-h]', box).forEach(y => y.classList.toggle('on', y === b)); gh(); preview(); }));
      gh(); preview();
      $('[data-no]', box).addEventListener('click', () => { box.innerHTML = ''; });
      $('[data-yes]', box).addEventListener('click', async (e) => {
        e.target.disabled = true;
        if (how === 'Card' && !$('#dpsDone', box)?.checked) { e.target.disabled = false; const er = $('.err', box); er.textContent = `Refund ${money(+$('#rfAmt', box).value || 0)} on the DPS machine first, then tick “Done on DPS”.`; er.hidden = false; return; }
        const goRf = async (okc) => { const y = await api('receipt_refund', { id: r.id, amount: +$('#rfAmt', box).value || 0, how, dps_done: !!$('#dpsDone', box)?.checked, reason: $('#rfWhy', box).value, ok_closed: okc, techs: typed || (prev ? prev.techs.map(t => ({ staff: t.staff, amt: t.amt })) : null) }, null, isP5 && how === 'Card' /* (2.99.638d) the customer taps the card on the P5 */); /* (2.99.639b QA-0011) */
          done(y, (y.refund && y.refund.gift ? `Refund saved · gift card ${y.refund.gift}` : 'Refund saved') + carryTxt(y.carry)); };
        try { await goRf(false); }
        catch (x2) { if (x2.message === 'PAYROLL_CLOSED') return payClosedAsk(box, () => goRf(true).catch(oops)); e.target.disabled = false; const er = $('.err', box); er.textContent = x2.message; er.hidden = false; }
      });
      box.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    });
  });
}
/** One receipt in a list. */
const rcItem = (r) => `<button type="button" class="item rc-item${r.status === 'void' ? ' is-void' : ''}" data-rc="${r.id}"><span class="time">${esc(r.time)}</span><div class="main"><div class="t1">#${r.no} ${r.test ? '<span class="chip tstchip">TEST</span> ' : r.addPay ? '<span class="chip addpaychip">ADD PAY</span> ' : ''}${esc(r.name)}${r.people > 1 ? ` <b class="grp-n">👤 ${r.people}</b>` : ''} ${r.status === 'void' ? '<span class="chip cancelled">VOID</span>' : r.refund > 0 ? `<span class="chip warn">refund ${money(r.refund)}</span>` : ''}</div>
  <div class="t2">${r.phone ? phL(r.phone) + ' · ' : ''}${r.typed ? esc((r.splitNames || []).join(', ') || r.lineName || 'Service') : esc([...new Set(r.lines.map(l => l.name))].join(', '))} · ${r.splits && r.splits.length ? r.splits.map(x => esc(x.tech) + ' ' + money(x.amt)).join(', ') : esc([...new Set(r.lines.map(l => l.tech))].join(', '))} · ${esc(r.method)}${r.tip > 0 ? ` · 💳 tip ${money(r.tip)}` : ''}</div></div><b class="amt">${money(r.total)}</b></button>`;
/** Close day: card / cash / other, refunds, sales and sales tax, sales per tech, customers, the cash counted (printable, 80 mm). No tips.
    form: the "Cash counted in the drawer" box (on screen; the print shows what was saved). */
/* ================= (2.99.56) TIP SCREEN for the customer (Checkout → "💳 Card tip") ================= */
/** Full screen, English, big buttons. o: { names: "Hana & Logan", service: money before discounts (no tax), due: what goes on the card, pcts: [15, 20, 25] }.
    Resolves with the tip (0 = No tip) after "✅ Done", or null when the staff taps Back. The customer cannot leave this screen any other way. */
function openTipScreen(o) {
  return new Promise((done) => {
    const pcts = (o.pcts && o.pcts.length === 3 ? o.pcts : [15, 20, 25]), svc = r2(o.service), due = r2(o.due);
    const amt = (p) => r2(svc * p / 100);
    let tip = null, custom = ''; let ES = false; try { ES = localStorage.getItem('tipLang') === 'es'; } catch (e) {} // (2.99.103) English | Español for the customer
    const TL = (en, es) => ES ? es : en;
    const ov = document.createElement('div'); ov.className = 'tip-ov'; ov.setAttribute('role', 'dialog'); ov.setAttribute('aria-modal', 'true'); ov.setAttribute('data-raw', '');
    const logo = S.day?.logo || '../assets/icon-192.png';
    const paint = () => { ov.innerHTML = `<button type="button" class="tip-back" id="tipBack" aria-label="Back (staff)">‹ Back</button><div class="tip-lang"><button type="button" data-tl="en" class="${ES ? '' : 'on'}">English</button><button type="button" data-tl="es" class="${ES ? 'on' : ''}">Español</button></div>
      <div class="tip-in"><img class="tip-logo" src="${esc(logo)}" alt="">
        <h1 class="tip-h">${TL('Add a tip for your nail tech? 💅', '¿Desea dejar propina a su técnico? 💅')}</h1>
        ${o.names ? `<p class="tip-tech">${esc(o.names)}</p>` : ''}
        <p class="tip-svc">${TL('Service', 'Servicio')}: <b>${money(svc)}</b></p>
        <div class="tip-pcts">${pcts.map(p => `<button type="button" class="tip-b" data-tp="${p}"><b>${p}%</b><span>${money(amt(p))}</span></button>`).join('')}</div>
        <div class="tip-row2"><button type="button" class="tip-b tip-cus" id="tipCus">${TL('Custom', 'Otra cantidad')}</button><button type="button" class="tip-no" id="tipNo">${TL('No tip', 'Sin propina')}</button></div>
        <div class="tip-sum" id="tipSum" hidden></div>
        <button type="button" class="tip-done" id="tipDone" hidden>✅ ${TL('Done', 'Listo')}</button></div>
      <div class="tip-pad" id="tipPad" hidden><div class="tip-pad-in"><p class="tip-pad-h">${TL('Enter tip amount', 'Escriba la propina')}</p><div class="tip-pad-v" id="tipPadV">$0.00</div>
        <div class="tip-keys">${['1', '2', '3', '4', '5', '6', '7', '8', '9', '.', '0', '⌫'].map(k => `<button type="button" data-k="${k}">${k}</button>`).join('')}</div>
        <div class="tip-pad-b"><button type="button" class="tip-no" id="tipPadX">${TL('Cancel', 'Cancelar')}</button><button type="button" class="tip-done" id="tipPadOk">OK</button></div></div></div>`; };
    paint(); document.body.appendChild(ov); document.body.classList.add('tip-open');
    // no way out for the customer: the browser's back goes nowhere while the screen is up
    const trap = () => { try { history.pushState({ tipScreen: 1 }, ''); } catch (e) {} };
    const key = (e) => { if (e.key === 'Escape') { e.preventDefault(); e.stopImmediatePropagation(); } }; // Escape would close the Checkout underneath
    trap(); window.addEventListener('popstate', trap); window.addEventListener('keydown', key, true);
    const end = (v) => { window.removeEventListener('popstate', trap); window.removeEventListener('keydown', key, true); ov.remove(); document.body.classList.remove('tip-open'); done(v); };
    const show = () => {
      $$('[data-tp]', ov).forEach(b => b.classList.toggle('on', tip !== null && b.dataset.sel === '1'));
      $('#tipCus', ov).classList.toggle('on', ov.dataset.mode === 'custom'); $('#tipNo', ov).classList.toggle('on', ov.dataset.mode === 'no');
      $('#tipCus', ov).innerHTML = ov.dataset.mode === 'custom' ? `${TL('Custom', 'Otra cantidad')} · ${money(tip)}` : TL('Custom', 'Otra cantidad');
      const s = $('#tipSum', ov); s.hidden = tip === null; s.innerHTML = tip === null ? '' : `${tip > 0 ? `${TL('Tip', 'Propina')} <b>${money(tip)}</b> · ` : TL('No tip · ', 'Sin propina · ')}${TL('Total on card', 'Total con tarjeta')}: <b class="tip-tot">${money(r2(due + tip))}</b>`;
      $('#tipDone', ov).hidden = tip === null;
    };
    const bindAll = () => {
    $$('[data-tp]', ov).forEach(b => b.addEventListener('click', () => { $$('[data-tp]', ov).forEach(x => { x.dataset.sel = x === b ? '1' : ''; }); ov.dataset.mode = 'pct'; tip = amt(+b.dataset.tp); show(); }));
    $('#tipNo', ov).addEventListener('click', () => { $$('[data-tp]', ov).forEach(x => { x.dataset.sel = ''; }); ov.dataset.mode = 'no'; tip = 0; show(); });
    const padV = () => { $('#tipPadV', ov).textContent = '$' + (custom === '' ? '0.00' : custom); };
    $('#tipCus', ov).addEventListener('click', () => { custom = ''; padV(); $('#tipPad', ov).hidden = false; });
    $$('[data-k]', ov).forEach(b => b.addEventListener('click', () => { const k = b.dataset.k;
      if (k === '⌫') custom = custom.slice(0, -1);
      else if (k === '.') { if (!custom.includes('.')) custom = (custom || '0') + '.'; }
      else if (!/\.\d\d$/.test(custom) && (custom.replace('.', '').length < 5)) custom = custom === '0' ? k : custom + k;
      padV(); }));
    $('#tipPadX', ov).addEventListener('click', () => { $('#tipPad', ov).hidden = true; });
    $('#tipPadOk', ov).addEventListener('click', () => { const v = r2(+custom || 0); $('#tipPad', ov).hidden = true; if (custom === '') return;
      $$('[data-tp]', ov).forEach(x => { x.dataset.sel = ''; }); ov.dataset.mode = v > 0 ? 'custom' : 'no'; tip = Math.min(1000, v); show(); });
    $('#tipDone', ov).addEventListener('click', () => { if (tip !== null) end(tip); });
    $('#tipBack', ov).addEventListener('click', () => end(null));
    $$('[data-tl]', ov).forEach(x => x.addEventListener('click', () => { ES = x.dataset.tl === 'es'; try { localStorage.setItem('tipLang', x.dataset.tl); } catch (e) {} const keepT = tip, keepM = ov.dataset.mode; paint(); bindAll(); tip = keepT; ov.dataset.mode = keepM || ''; show(); })); // (2.99.103)
    };
    bindAll();
  });
}
/** "HANA" → "Hana"; several techs: "Hana & Logan". */
const tipNames = (list) => list.map(n => String(n || '').toLowerCase().replace(/(^|[\s-])\S/g, c => c.toUpperCase())).filter(Boolean).join(' & ');

/* (2.99.199 – order 398, SO-LUAT 10/10) Receipt → tap a tech / a "↳ Service" line (owner only): who did each line – the tech chips (photo + name, the one now
   lit), the money of each line (the lines must add up to the receipt's services – red, Save off when not), "✂ Split line" (one line → two halves), Save / Cancel.
   Save: the $1 rule line by line, each tech's money, the $1 tech, Payroll, Tech report, AN Desk, Close day, AN Tech, the turn – worked out again on the server.
   The customer's total, tips (they stay with their tech – Edit tips) and how it was paid never change. Money & security log + "Techs edited … by …". */
async function rcLinesEdit(r, pi, pk) {
  let staff = []; try { const d = await api('day', null, { date: r.day }); staff = (d.staff || []).filter(s => s.id); } catch (e) {}
  const ps = (r.paySplits || []).filter(x => !x.feeOnly);
  (r.paySplits || []).forEach(x => { if (!x.feeOnly && !staff.find(s => s.id === x.staff)) staff.push({ id: x.staff, name: x.tech }); });
  const total = r2(ps.reduce((a, x) => a + +(x.gross ?? x.amt), 0));
  let L = []; let hi = 0;
  (r.paySplits || []).forEach((x, i) => { if (x.feeOnly) return; const ls = (x.lines || []).length ? x.lines : [{ n: 'Service', g: +(x.gross ?? x.amt) }];
    ls.forEach((l, k) => { if (i === pi && (k === pk || (pk < 0 && k === 0))) hi = L.length; L.push({ staff: x.staff, name: l.n || 'Service', amt: +l.g }); }); });
  document.querySelector('.rce-bg')?.remove();
  const bg = document.createElement('div'); bg.className = 'rce-bg'; bg.setAttribute('role', 'dialog'); bg.setAttribute('aria-modal', 'true'); bg.setAttribute('aria-label', 'Who did each service');
  document.body.append(bg);
  const av = (s) => (typeof techAv === 'function' ? techAv(s, 'fill') : esc(String(s.name || '?')[0]));
  const sum = () => r2(L.reduce((a, l) => a + (+l.amt || 0), 0));
  const draw = () => { const sm = sum(), ok = Math.abs(sm - total) < 0.006;
    bg.innerHTML = `<div class="rce"><div class="rce-h"><b>Who did each service · #${r.no}</b><button type="button" class="rce-x" data-x="1" aria-label="Close">✕</button></div>
      <p class="hint small">Total, tips and payment stay the same. The $1 rule is worked out again for each line.</p>
      ${L.map((l, k) => `<div class="rce-l${k === hi ? ' on' : ''}" data-l="${k}"><div class="rce-chips" role="group" aria-label="Tech for line ${k + 1}">${staff.map(s => `<button type="button" class="rce-c${s.id === l.staff ? ' on' : ''}" data-st="${k}:${s.id}" aria-pressed="${s.id === l.staff}"><span class="rce-av">${av(s)}</span><span>${esc(s.name)}</span></button>`).join('')}</div>
        <div class="rce-r"><span class="rce-n">${esc(l.name)}</span><label class="rce-m"><span>$</span><input type="number" inputmode="decimal" step="0.01" min="0" data-am="${k}" value="${l.amt === null ? '' : (+l.amt).toFixed(2)}" aria-label="Money of line ${k + 1}"></label>
        <button type="button" class="btn small" data-sp="${k}">✂ Split line</button>${L.length > 1 ? `<button type="button" class="btn small" data-rm="${k}" aria-label="Remove line ${k + 1}">✕</button>` : ''}</div></div>`).join('')}
      <p class="${ok ? 'rce-ok' : 'err'}" id="rceSum">Lines ${money(sm)} ${ok ? '✓' : `– must be ${money(total)}`}</p>
      <div class="row rce-b"><button type="button" class="btn primary" id="rceSave"${ok ? '' : ' disabled'}>Save</button><button type="button" class="btn" data-x="1">Cancel</button></div><p class="err" id="rceErr" hidden></p></div>`; };
  draw(); setTimeout(() => bg.querySelector(`[data-l="${hi}"]`)?.scrollIntoView({ block: 'center' }), 50);
  bg.addEventListener('input', (e) => { const i = e.target.dataset.am; if (i === undefined) return; L[+i].amt = e.target.value === '' ? null : Math.max(0, +e.target.value || 0);
    const sm = sum(), ok = Math.abs(sm - total) < 0.006, p = bg.querySelector('#rceSum'); p.className = ok ? 'rce-ok' : 'err'; p.textContent = `Lines ${money(sm)} ${ok ? '✓' : '– must be ' + money(total)}`; bg.querySelector('#rceSave').disabled = !ok; });
  bg.addEventListener('click', async (e) => {
    if (e.target === bg || e.target.closest('[data-x]')) { bg.remove(); return; }
    const b = e.target.closest('button'); if (!b) return;
    if (b.dataset.st) { const [k, sid] = b.dataset.st.split(':').map(Number); L[k].staff = sid; hi = k; draw(); return; }
    if (b.dataset.sp !== undefined) { const k = +b.dataset.sp, a = +L[k].amt || 0, h = Math.floor(a * 50) / 100; L.splice(k + 1, 0, { staff: L[k].staff, name: L[k].name, amt: r2(a - h) }); L[k].amt = h; hi = k + 1; draw(); return; }
    if (b.dataset.rm !== undefined) { L.splice(+b.dataset.rm, 1); hi = Math.min(hi, L.length - 1); draw(); return; }
    if (b.id === 'rceSave') { b.disabled = true;
      try { const y = await api('receipt_lines', { id: r.id, lines: L.map(l => ({ staff: l.staff, name: l.name, amt: r2(+l.amt || 0) })) });
        bg.remove(); toast(`#${r.no}: techs changed ✓ · ${y.after}`, 6000); openReceipt(r.id); refreshCurrent(); }
      catch (x) { b.disabled = false; const er = bg.querySelector('#rceErr'); er.textContent = x.message; er.hidden = false; } }
  });
  bg.addEventListener('keydown', (e) => { if (e.key === 'Escape') bg.remove(); });
}

/* (2.99.345 – lệnh 580) ✎ SỬA TIỀN DỊCH VỤ (owner only, a paid receipt): the price of each service line (the techs stay – to move money between techs: tap a tech).
   Shows the old total → the new total and the difference. + more: "Collected" Card / Cash → a NEW payment line (the old ones never change); − less: the Refund
   (Card / Cash back). A reason is a must. The $1 rule, each tech's money, Payroll / Report / Close day worked out again on the server. The TURN does not change. */
function rcMoneyEdit(r) {
  const names = {}; (r.paySplits || []).forEach(x => { names[x.staff] = x.tech; }); (r.splits || []).forEach(x => { names[x.staff] = names[x.staff] || x.tech; });
  const L = (r.moneyLines || []).map(l => ({ staff: l.staff, n: l.n, g: +l.g, amt: +l.g }));
  const pct = r.tax > 0 ? +(r.taxPct || 0) : 0; let how = '', reason = '';
  document.querySelector('.rce-bg')?.remove();
  const bg = document.createElement('div'); bg.className = 'rce-bg rcm-bg'; bg.setAttribute('role', 'dialog'); bg.setAttribute('aria-modal', 'true'); bg.setAttribute('aria-label', 'Fix service prices'); document.body.append(bg);
  const calc = () => { const d = r2(L.reduce((a, l) => a + (+l.amt || 0) - l.g, 0)); const t = pct ? r2(Math.abs(d) * pct / 100) : 0; const pay = r2(Math.abs(d) + t);
    const up = L.some(l => (+l.amt || 0) > l.g + 0.004), down = L.some(l => (+l.amt || 0) < l.g - 0.004); return { d, pay, nt: r2(r.total + (d >= 0 ? pay : -pay)), mixed: up && down }; };
  const draw = () => { const c = calc(), sgn = c.d > 0 ? '+' : c.d < 0 ? '−' : '';
    const ok = Math.abs(c.d) >= 0.005 && !c.mixed && how && reason.trim().length >= 3;
    bg.innerHTML = `<div class="rce"><div class="rce-h"><b>${LV('✎ Fix service prices', '✎ Sửa tiền dịch vụ')} · #${r.no}</b><button type="button" class="rce-x" data-x="1" aria-label="Close">✕</button></div>
      <p class="hint small">${LV('Change the price of each service. Tips stay. <b>Turns do not change</b> (kept as at checkout).', 'Sửa giá từng dịch vụ. Tip giữ nguyên. <b>Turn không đổi</b> (giữ như lúc checkout).')}</p>
      ${L.map((l, k) => `<div class="rce-l"><div class="rce-r"><span class="rce-n">${esc(l.n)} <small>· ${esc(names[l.staff] || '')}</small><br><small class="muted">${money(l.g)}</small></span><label class="rce-m"><span>$</span><input type="number" inputmode="decimal" step="0.01" min="0" data-mm="${k}" value="${(+l.amt).toFixed(2)}" aria-label="New price of ${esc(l.n)}"></label></div></div>`).join('')}
      <p class="rcm-sum" id="rcmSum"><span>${LV('Old total', 'Tổng cũ')} <b>${money(r.total)}</b> → ${LV('new total', 'tổng mới')} <b>${money(c.nt)}</b></span> <b class="${c.d > 0 ? 'rcm-up' : c.d < 0 ? 'rcm-dn' : ''}">${sgn ? sgn + money(c.pay) : '±$0'}</b>${pct && c.d ? ` <small class="muted">(${LV('tax included', 'gồm thuế')} ${money(r2(c.pay - Math.abs(c.d)))})</small>` : ''}</p>
      ${c.mixed ? `<p class="err">${LV('Each fix: only raise OR only lower prices.', 'Mỗi lần sửa: chỉ tăng HOẶC chỉ giảm giá.')}</p>` : ''}
      ${c.d > 0 ? `<p class="lbl">${LV(`Collected ${money(c.pay)} more by`, `Đã thu thêm ${money(c.pay)} bằng`)}</p>` : c.d < 0 ? `<p class="lbl">${LV(`Refund ${money(c.pay)} by`, `Hoàn lại ${money(c.pay)} (Refund) bằng`)}</p>` : ''}
      ${c.d ? `<div class="rcm-how" role="group">${['Card', 'Cash'].map(m => `<button type="button" class="btn${how === m ? ' primary' : ''}" data-how="${m}" aria-pressed="${how === m}">${m === 'Card' ? '💳 Card' : '💵 Cash'}</button>`).join('')}</div>` : ''}
      <label class="rcm-why">${LV('Reason (required)', 'Lý do (bắt buộc)')}<input id="rcmWhy" maxlength="160" autocomplete="off" placeholder="${LV('Wrong price typed – card charged $155', 'Nhập sai giá – thẻ quẹt $155')}" value="${esc(reason)}"></label>
      <div class="row rce-b"><button type="button" class="btn primary" id="rcmSave"${ok ? '' : ' disabled'}>${LV('Save', 'Lưu')}</button><button type="button" class="btn" data-x="1">${LV('Cancel', 'Huỷ')}</button></div><p class="err" id="rcmErr" hidden></p></div>`; };
  const upd = () => { const f = document.activeElement && document.activeElement.dataset ? document.activeElement.dataset.mm : undefined; const pos = f !== undefined ? document.activeElement.selectionStart : null; const w = document.activeElement && document.activeElement.id === 'rcmWhy';
    draw(); if (f !== undefined) { const e = bg.querySelector(`[data-mm="${f}"]`); if (e) { e.focus(); try { e.setSelectionRange(pos, pos); } catch (x) {} } } else if (w) { const e = bg.querySelector('#rcmWhy'); e.focus(); e.setSelectionRange(e.value.length, e.value.length); } };
  draw();
  bg.addEventListener('change', (e) => { const i = e.target.dataset.mm; if (i === undefined) return; L[+i].amt = Math.max(0, +e.target.value || 0); how = ''; upd(); });
  bg.addEventListener('input', (e) => { if (e.target.id === 'rcmWhy') { reason = e.target.value; const c = calc(); bg.querySelector('#rcmSave').disabled = !(Math.abs(c.d) >= 0.005 && !c.mixed && how && reason.trim().length >= 3); } });
  bg.addEventListener('click', async (e) => {
    if (e.target === bg || e.target.closest('[data-x]')) { bg.remove(); return; }
    const b = e.target.closest('button'); if (!b) return;
    if (b.dataset.how) { how = b.dataset.how; upd(); return; }
    if (b.id === 'rcmSave') { b.disabled = true;
      try { const y = await api('receipt_money', { id: r.id, lines: L.map(l => ({ staff: l.staff, amt: r2(+l.amt || 0) })), how, reason: reason.trim() });
        bg.remove(); toast(`#${r.no}: ${money(y.before)} → ${money(y.after)} ✓`, 6000); openReceipt(r.id); if (typeof refreshCurrent === 'function') refreshCurrent(); }
      catch (x) { b.disabled = false; const er = bg.querySelector('#rcmErr'); er.textContent = x.message; er.hidden = false; } }
  });
  bg.addEventListener('keydown', (e) => { if (e.key === 'Escape') bg.remove(); });
}
