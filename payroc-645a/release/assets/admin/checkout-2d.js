'use strict';
function ckWire4(X) {
const { sh, soloGo, K, hasParts, syncParts, drawSplit, calc, tidySplit, ckPickTech, svcMoney, AO, drawOffer, aoOn, aoTurnOn, drawPeople, techW, err, techName, sub, due, TIPC, drawTipParts, splitProblem, drawPay, calcPay, t, drawHead, gsAmt, tipProblem, total, typed, tipParts, offerAmt, giftUse } = X;
sh.addEventListener('click', async (e) => {
const b = e.target.closest('button');
if (!b) {
const c = e.target.closest('.tk-person[data-solo]');
if (c && sh.contains(c) && !e.target.closest('input, textarea, select, [data-renbox] *'))
soloGo(+c.dataset.solo);
return;
}
if (!sh.contains(b))
return;
if (b.dataset.sppx !== undefined) {
const [j, k] = b.dataset.sppx.split(':').map(Number), x = K.split[j];
if (!x || !hasParts(x))
return;
x.parts.splice(k, 1);
if (!x.parts.length) {
delete x.parts;
x.amt = null;
x.cleared = 1;
}
else if (x.parts.length === 1) {
const l = x.parts[0];
delete x.parts;
x.amt = l && l.amt !== null && l.amt !== '' ? r2(+l.amt || 0) : null;
}
else
syncParts(x);
drawSplit();
calc();
return;
}
if (b.dataset.tog !== undefined) {
const j = +b.dataset.tog;
if (K.open.has(j))
K.open.delete(j);
else
K.open.add(j);
drawSplit();
return;
}
if (b.dataset.click) {
$('#' + b.dataset.click, sh)?.click();
return;
}
if (b.dataset.spclr !== undefined) {
const x = K.split[+b.dataset.spclr];
if (!x)
return;
x.amt = null;
x.cleared = 1;
x.svc = [];
drawSplit();
calc();
return;
}
if (b.dataset.spx !== undefined) {
K.split.splice(+b.dataset.spx, 1);
K.open = new Set();
tidySplit();
drawSplit();
calc();
return;
}
if (b.dataset.sptb !== undefined) {
ckPickTech(+b.dataset.sptb);
return;
}
if (b.id === 'tkSpAdd') {
const lp = [...K.split].reverse().find(y => y.pid);
K.split.push({ staff: 0, amt: null, added: true, ...(lp ? { pid: lp.pid } : {}) });
drawSplit();
calc();
ckPickTech(K.split.length - 1);
return;
}
if (b.dataset.svc !== undefined) {
svcMoney(+b.dataset.svc);
return;
}
if (b.id === 'ckOfPick') {
if (AO.length < 2) {
$('#tkOffer .ck-sw', sh)?.click();
return;
}
K.ofOpen = !K.ofOpen;
drawOffer();
return;
}
if (b.id === 'ckDiscBtn') {
const d = $('#ckDisc', sh), op = d.hidden;
d.hidden = !op;
b.setAttribute('aria-expanded', String(op));
if (op) {
const i = $('#tkDisc', sh);
if (sh.__padPick)
sh.__padPick(i);
else
i.focus();
}
return;
}
if (b.dataset.aox !== undefined || b.dataset.aoon !== undefined) {
K.ofOpen = false;
aoOn();
K.aoOwn = true;
if (b.dataset.aox !== undefined)
K.ao[b.dataset.aox] = false;
else
aoTurnOn(b.dataset.aoon);
calc();
return;
}
if (b.dataset.ren) {
const p = K.persons.find(x => x.id === +b.dataset.ren);
if (p)
renameBox($(`[data-renbox="${p.id}"]`, sh), p.id, p.name, (nm) => { p.name = nm; drawPeople(); drawSplit(); });
return;
}
if (b.dataset.off) {
soloGo(b.dataset.off);
return;
}
if (b.id === 'ckUnsplit') {
const bk = window.CK_BACK;
if (!bk)
return;
window.CK_BACK = null;
closeSheet();
openCheckout({ id: bk.id, status: 'arrived', name: bk.name }, true);
return;
}
if (b.dataset.of !== undefined) {
K.offer = b.dataset.of;
K.offerOwn = true;
calc();
return;
}
if (b.dataset.dt) {
K.discType = b.dataset.dt;
$$('#tkDt button', sh).forEach(x => x.classList.toggle('on', x === b));
calc();
return;
}
if (b.id === 'tkEditTip') {
const e = $('#tkTipEdit', sh), op = e.hidden;
e.hidden = !op;
b.setAttribute('aria-expanded', String(op));
b.textContent = op ? '✕ Close tip boxes' : '✎ Edit tip';
if (op)
$('#tkTipCard', sh)?.focus();
return;
}
if (b.id === 'tkGiftAbc') {
giftAbc(!K.giftAbc);
$('#tkGift', sh).value = '';
$('#tkGift', sh).focus();
return;
}
if (b.id === 'tkGiftGo') {
giftGo();
return;
}
if (b.id === 'tkGiftX') {
K.gift = null;
K.giftErr = '';
$('#tkGift', sh).value = '';
calc();
$('#tkGift', sh)?.focus();
return;
}
if (b.id === 'tkGiftPh') {
const bx = $('#tkGiftPhBox', sh);
bx.hidden = !bx.hidden;
if (bx.hidden)
return;
bx.innerHTML = `<p class="hint" style="margin:6px 0">Find by phone – ask the customer to type their number:</p><div class="linkbox"><input class="inp" id="tkGPh" type="tel" inputmode="tel" placeholder="(515) 555-1234" autocomplete="off" aria-label="Customer's phone number"><button type="button" class="btn small primary" id="tkGPhGo">Find</button></div><div id="tkGPhRes"></div>`;
const ip = $('#tkGPh', bx);
ip.focus();
const go = async () => {
const res = $('#tkGPhRes', bx);
res.innerHTML = '<p class="hint">Looking…</p>';
try {
const r = await api('gift_by_phone', { phone: ip.value }, IS_DESK ? dkK() : undefined);
ip.value = '';
res.innerHTML = r.cards.length ? r.cards.map((c, i) => `<button type="button" class="btn small tk-gphc" data-gpi="${i}">🎁 ${esc(c.masked)} · balance ${money(c.balance)}</button>`).join('') : '<p class="err">No gift card with money on it for this number.</p>';
$$('[data-gpi]', res).forEach(x => x.addEventListener('click', () => { const c = r.cards[+x.dataset.gpi]; if (!/^\d+$/.test(c.code))
giftAbc(true); $('#tkGift', sh).value = c.code; bx.hidden = true; $('#tkGiftGo', sh).click(); }));
}
catch (x) {
res.innerHTML = `<p class="err">${esc(x.message)}</p>`;
}
};
$('#tkGPhGo', bx).addEventListener('click', go);
ip.addEventListener('keydown', (e) => { if (e.key === 'Enter')
go(); });
return;
}
if (b.id === 'tkGiftScan') {
const c = await openScanner('Scan gift card', { input: $('#tkGift', sh) });
if (c) {
if (!/^\d+$/.test(c))
giftAbc(true);
$('#tkGift', sh).value = c;
$('#tkGiftGo', sh).click();
}
return;
}
if (b.id === 'tkSellGift') {
openGiftSell(null, { bill: true, onAdd: (g) => { K.giftSale = g; calc(); } });
return;
}
if (b.dataset.gsx) {
K.giftSale = null;
calc();
return;
}
if (b.id === 'tkTipAsk' || b.id === 'tkTipAgain' || b.id === 'spTipAsk' || b.id === 'tkTipChg' || b.id === 'spTipChg') {
const w = techW();
if (!w.length)
return err('Type the money for the tech first.');
const v = await openTipScreen({ names: tipNames(w.map(([sid]) => techName(sid))), service: sub(), due: due(), pcts: TIPC.pcts });
if (v === null)
return;
K.tipT.card = v;
K.tipP.card = null;
K.tipAsked = true;
const ip = $('#tkTipCard', sh);
if (ip)
ip.value = v > 0 ? v.toFixed(2) : '';
const sp2 = $('#spTip', sh);
if (sp2)
sp2.value = v > 0 ? v.toFixed(2) : '';
drawTipParts();
calc();
return;
}
if (b.dataset.pm) {
const sp0 = splitProblem();
if (sp0 && /^Chọn thợ trước/.test(sp0)) {
err(sp0);
const s0 = $('.ck-pick[data-sptb]', sh);
if (s0)
ckPickTech(+s0.dataset.sptb);
return;
}
K.pay = K.pay === b.dataset.pm ? '' : b.dataset.pm;
sh.__popIn = '';
err('');
drawPay();
return;
}
if (b.dataset.how) {
K.how = b.dataset.how;
K.spHowOn = true;
calcPay();
$$('[data-how]', sh).forEach(x => x.classList.toggle('on', x.dataset.how === K.how));
return;
}
if (b.dataset.q) {
const gi = $('#tkGiven', sh);
gi.value = (+b.dataset.q).toFixed(2);
gi.__fresh = true;
calcPay();
return;
}
if (b.dataset.go) {
if (b.disabled)
return;
finish(b.dataset.go, b);
}
});
const giftWhy = (m) => /not found/i.test(m) ? 'Card not found – not sold yet or wrong code' : /cancel|void/i.test(m) ? 'This card was voided' : /\$0|no money left/i.test(m) ? 'Card used up ($0.00 left)' : m;
const giftGo = async () => {
err('');
const inp = $('#tkGift', sh), code = (inp?.value || '').trim();
if (!code) {
inp?.focus();
return;
}
const go = $('#tkGiftGo', sh);
if (go)
go.disabled = true;
try {
const r = await api('gift_lookup', { code });
if (r.card.problem)
throw new Error(r.card.problem);
K.gift = { code: r.card.code, balance: +r.card.balance, masked: r.card.masked || '****' + String(r.card.code).replace(/[^A-Z0-9]/gi, '').slice(-4) };
K.giftErr = '';
inp.value = '';
if (K.pay === 'more') {
K.pay = '';
drawPay();
}
else if (K.pay === 'split')
drawPay();
calc();
setTimeout(() => {
const t = due() > 0 ? $('#tkPay', sh) : ($('#tkFoot:not([hidden]) [data-go]', sh) || $('#tkPay', sh));
$('#tkGiftInfo', sh)?.scrollIntoView({ block: 'start', behavior: 'smooth' });
if (due() > 0 && t) {
t.classList.remove('tk-flash');
void t.offsetWidth;
t.classList.add('tk-flash');
}
}, 60);
}
catch (x) {
K.gift = null;
K.giftErr = giftWhy(x.message);
calc();
}
finally {
if (go)
go.disabled = false;
}
};
$('#tkGift', sh)?.addEventListener('keydown', (e) => { if (e.key === 'Enter') {
e.preventDefault();
giftGo();
} });
const giftAbc = (on) => {
K.giftAbc = on;
const i = $('#tkGift', sh), b = $('#tkGiftAbc', sh);
if (!i)
return;
i.setAttribute('inputmode', on ? 'text' : 'numeric');
if (on)
i.removeAttribute('pattern');
else
i.setAttribute('pattern', '[0-9]*');
if (b)
b.textContent = on ? 'Plastic card (numbers only)? 123' : 'Card number has letters (web card)? ABC';
};
$('#tkGift', sh)?.addEventListener('input', (e) => { const i = e.target, web = /^[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$/i.test(i.value.trim()), v = K.giftAbc || web ? i.value.toUpperCase().replace(/[^A-Z0-9-]/g, '') : i.value.replace(/\D/g, ''); if (v !== i.value)
i.value = v; if (K.giftErr) {
K.giftErr = '';
calc();
} });
const askAddPay = (go) => {
$('.ck-ap', sh)?.remove();
const ov = document.createElement('div');
ov.className = 'ck-svc ck-ap';
ov.setAttribute('role', 'dialog');
ov.setAttribute('aria-label', 'Test or add pay');
ov.innerHTML = `<div class="ck-svc-in"><div class="ck-svc-h"><b>This is the owner's number – ${esc(t.pretty || '')}</b><button type="button" class="ck-svc-x" aria-label="Close">✕</button></div>
<p class="hint">Is this a test, or money added for the techs?</p>
<div class="ck-ap-b"><button type="button" class="btn block" data-ap="0">🧪 Test – don't count</button><button type="button" class="btn primary block" data-ap="1">💵 Add pay for the techs</button></div>
<p class="hint small">Add pay: counted in the techs' pay, Payroll, Tech report and Close day like any ticket ($1 rule too) – no turn, no rewards, no text.</p></div>`;
sh.append(ov);
$('[data-ap="1"]', ov).focus();
ov.addEventListener('click', (e) => {
e.stopPropagation();
if (e.target === ov || e.target.closest('.ck-svc-x')) {
ov.remove();
return;
}
const b = e.target.closest('[data-ap]');
if (!b)
return;
K.addpay = b.dataset.ap === '1';
ov.remove();
drawHead();
go();
});
};
const finish = async (kind, btn) => {
if (K.saving)
return;
err('');
if (sub() <= 0 && !(gsAmt() > 0)) {
$('[data-spa="0"]', sh)?.focus();
return err('Type the money for each tech.');
}
const sp = splitProblem();
if (sp) {
$('#tkSplit', sh).scrollIntoView({ block: 'nearest', behavior: 'smooth' });
return err(sp + '.');
}
const tpp = tipProblem();
if (tpp) {
$('#tkTip', sh).scrollIntoView({ block: 'nearest', behavior: 'smooth' });
return err(tpp + '.');
}
{
const dRaw = r2(K.persons.reduce((s0, p) => s0 + p.deposit, 0));
if (dRaw > total() + 0.004)
return err(`Deposit is more than the total – refund ${money(r2(dRaw - total()))} or change the ticket.`);
}
if (K.tipT.card > 0 && due() > 0.004 && !['card', 'split'].includes(kind))
return err('A card tip needs a card part – take the tip off (Edit tip) or pay by card / Split.');
const d = due(), l4 = ($('#tkL4', sh)?.value || '').trim();
if (l4 && !/^\d{4}$/.test(l4))
return err('Card: type only the last 4 digits (or leave it empty).');
let pays = [], change = 0;
if (kind === 'card')
pays = [{ m: 'Card', amt: d, last4: l4 }];
else if (kind === 'cash') {
const g = +$('#tkGiven', sh).value || d;
if (g + 0.001 < d)
return err('The cash received is less than the amount due.');
pays = [{ m: 'Cash', amt: d, given: g }];
change = r2(g - d);
}
else if (kind === 'other')
pays = [{ m: 'Other', amt: d, how: K.how }];
else if (kind === 'split') {
const ca = r2(+$('#spCash', sh).value || 0), ot = r2(+($('#spOther', sh)?.value || 0)), card = r2(d - ca - ot);
if (card < -0.004)
return err(`Cash + other is more than ${money(d)}.`);
if (K.tipT.card > 0 && card <= 0.004)
return err('A card tip needs a card part – take the tip off or pay part by card.');
if (ot > 0 && !K.spHowOn)
return err('Other: pick Zelle / Venmo / Other.');
const gv = r2(+($('#spGiven', sh)?.value || 0));
if (gv > 0 && gv + 0.001 < ca)
return err('Cash given is less than the cash part.');
if (gv > 0)
change = r2(gv - ca);
pays = [{ m: 'Card', amt: Math.max(0, card), last4: l4 }, { m: 'Cash', amt: ca, ...(gv > 0 ? { given: gv } : {}) }, { m: 'Other', amt: ot, how: K.how }].filter(p => p.amt > 0);
if (Math.abs(r2(pays.reduce((s, p) => s + p.amt, 0)) - d) > 0.005)
return err(`The payments must add up to ${money(d)}.`);
}
btn.disabled = true;
K.saving = true;
try {
const dvP = pays.find(p => p.m === 'Card' && p.amt > 0); /* (2.99.638c) Card on the P5: charged first, the receipt after */
if (dvP && window.DV_ON && $('#tkP5', sh) && $('#tkP5', sh).checked) { const v = await dvPay(K.persons.map(p => p.id), r2(dvP.amt)); dvP.dv_ref = v.ref; if (v.last4) dvP.last4 = v.last4; }
else if (dvP && window.PR_ON && $('#tkPR', sh) && $('#tkPR', sh).checked) { const v = await prPay(K.persons.map(p => p.id), r2(dvP.amt)); dvP.pr_ref = v.ref; if (v.last4) dvP.last4 = v.last4; } /* (2.99.645a) Card on Payroc: charged first, the receipt after */
const r = await api('checkout2', { ao_on: aoOn().map(o => o.key), ids: K.persons.map(p => p.id), amount: sub(),
splits: sub() <= 0 && gsAmt() > 0 ? K.split.filter(x => x.staff).map(x => ({ staff: x.staff, amt: 0 })) : K.split.filter(x => typed(x) && +x.amt > 0).flatMap(x => hasParts(x) ? x.parts.filter(p => +p.amt > 0).map(p => ({ staff: x.staff, amt: r2(+p.amt), name: p.name || 'Service' })) : [{ staff: x.staff, amt: r2(x.amt) }]),
tips: K.tipT.card > 0 ? Object.entries(tipParts('card')).map(([k, v]) => ({ staff: +k, amt: r2(+v) })) : [], tip_total: r2(K.tipT.card),
cash_tips: K.tipT.cash > 0 ? Object.entries(tipParts('cash')).map(([k, v]) => ({ staff: +k, amt: r2(+v) })) : [], cash_tip_total: r2(K.tipT.cash),
addpay: K.addpay === true,
disc_type: K.discType, disc_val: K.discType === '%' ? Math.min(100, K.disc) : Math.min(K.disc, sub()), offer: offerAmt() > 0 ? K.offer : '', gift_code: K.gift ? K.gift.code : '', gift_amount: giftUse(), pays, gift_sale: K.giftSale ? { amount: gsAmt(), phone: K.giftSale.phone || '', code: K.giftSale.code || '' } : null });
const back = window.CK_BACK;
window.CK_BACK = null;
showPaid(r.receipt, r.salon, change, back);
refreshCurrent();
}
catch (x) {
btn.disabled = false;
K.saving = false;
err(x.message);
}
};
}

/* (2.99.638c - LENH-638 A) Checkout -> Card -> "💳 Card on the P5" (only when Settings -> Payments -> Dejavoo P5 is on: the ticket says dvOn).
   Pay: the card part goes to the P5 FIRST (up to 2 minutes for the customer), then the receipt is saved with the P5's card details. One P5 payment
   per ticket: tapping Pay again (after an error, a lost answer) never charges twice – the server gives back the payment already approved. */
if (typeof ckTicket === 'function') { const ckT0 = ckTicket; ckTicket = async function (id) { const t = await ckT0(id); try { window.DV_ON = !!(t && t.dvOn); window.PR_ON = !!(t && t.prOn); } catch (e) {} return t; }; }
function dvBox() {
  if (!window.DV_ON) return '';
  const vi = typeof LV === 'function' ? LV(0, 1) === 1 : true;
  return `<label class="chk" style="margin:4px 0 10px"><input type="checkbox" id="tkP5" checked> 💳 ${vi ? 'Cà trên máy P5 (gửi số tiền qua máy)' : 'Card on the P5 (send the amount to it)'}</label>`;
}
async function dvPay(ids, amt) {
  const vi = typeof LV === 'function' ? LV(0, 1) === 1 : true;
  const w = document.createElement('div'); w.className = 'sheet-wait'; w.setAttribute('role', 'status');
  w.style.cssText = 'position:fixed;inset:0;z-index:9999;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,.55)';
  w.innerHTML = `<div class="card" style="max-width:340px;text-align:center"><p style="font-size:1.2em;margin:0 0 8px">💳 ${money(amt)}</p><p style="margin:0">${vi ? 'Đang chờ khách quẹt / chạm thẻ trên máy P5…' : 'Waiting for the customer on the P5…'}</p><p class="hint" style="margin:8px 0 0">${vi ? 'Tối đa 2 phút. Huỷ thì bấm Cancel trên máy P5.' : 'Up to 2 minutes. To stop, press Cancel on the P5.'}</p></div>`;
  document.body.appendChild(w);
  try {
    for (let n = 0; n < 2; n++) {
      try { return await api('dv_charge', { ids, amt }, null, true); }
      catch (e) {
        const m = String(e && e.message || e);
        const paid = /already took|took \$/.test(m) && n === 0;
        if (!paid) throw e;
        w.hidden = true;
        if (!confirm(m + '\n\n' + (vi ? 'Huỷ khoản đã cà trên P5 (Void) rồi cà lại số mới?' : 'Cancel (void) that P5 payment and charge the new amount?'))) throw e;
        w.hidden = false;
        const lst = await api('dv_waiting'); const mine = (lst.waiting || []).find(x => x.key === 'T' + ids.map(Number).sort((a, b) => a - b).join('-'));
        if (!mine) throw e;
        await api('dv_cancel', { ref: mine.ref });
      }
    }
    throw new Error('P5: try again.');
  } finally { w.remove(); }
}

/* (2.99.645a - LENH PAYROC) Checkout -> Card -> "💳 Card on Payroc" (only when Settings -> Payments -> Payroc is on: the ticket says prOn; never together
   with the P5 box – the P5 wins when both are on). Pay: the card part goes to the Payroc device FIRST, then the receipt is saved with Payroc's card details.
   One Payroc payment per ticket: tapping Pay again never charges twice – the server asks Payroc about the first try before anything else. */
function prBox() {
  if (!window.PR_ON || window.DV_ON) return '';
  const vi = typeof LV === 'function' ? LV(0, 1) === 1 : true;
  return `<label class="chk" style="margin:4px 0 10px"><input type="checkbox" id="tkPR" checked> 💳 ${vi ? 'Cà qua Payroc (gửi số tiền xuống máy)' : 'Card on Payroc (send the amount to the device)'}</label>`;
}
async function prPay(ids, amt) {
  const vi = typeof LV === 'function' ? LV(0, 1) === 1 : true;
  const w = document.createElement('div'); w.className = 'sheet-wait'; w.setAttribute('role', 'status');
  w.style.cssText = 'position:fixed;inset:0;z-index:9999;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,.55)';
  w.innerHTML = `<div class="card" style="max-width:340px;text-align:center"><p style="font-size:1.2em;margin:0 0 8px">💳 ${money(amt)}</p><p style="margin:0">${vi ? 'Đang chờ khách quẹt / chạm thẻ trên máy Payroc…' : 'Waiting for the customer on the Payroc device…'}</p><p class="hint" style="margin:8px 0 0">${vi ? 'Tối đa 2 phút.' : 'Up to 2 minutes.'}</p><button type="button" class="btn" id="prStop" style="margin-top:8px">${vi ? 'Dừng trên máy' : 'Stop on the device'}</button></div>`;
  document.body.appendChild(w);
  w.querySelector('#prStop').onclick = async () => { try { await api('pr_stop', { ids }); } catch (e) {} };
  try {
    for (let n = 0; n < 2; n++) {
      try { return await api('pr_charge', { ids, amt }, null, true); }
      catch (e) {
        const m = String(e && e.message || e);
        if (!(/already took|took \$/.test(m) && n === 0)) throw e;
        w.hidden = true;
        if (!confirm(m + '\n\n' + (vi ? 'Huỷ khoản đã cà qua Payroc (Void) rồi cà lại số mới?' : 'Cancel (void) that Payroc payment and charge the new amount?'))) throw e;
        w.hidden = false;
        const lst = await api('pr_waiting'); const mine = (lst.waiting || []).find(x => x.key === 'T' + ids.map(Number).sort((a, b) => a - b).join('-'));
        if (!mine) throw e;
        await api('pr_cancel', { ref: mine.ref });
      }
    }
    throw new Error('Payroc: try again.');
  } finally { w.remove(); }
}
