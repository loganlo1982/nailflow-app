'use strict';
function ckWire2(X) {
const { techW, K, sh, techName, TIPC, splitProblem, due, t, sub, AO, aoLines, discAmt, offerAmt, aoBest, aoVal, a, err, giftUse, IC, TAXP, tipBig } = X;
const calcPay = (...q) => X.calcPay(...q);
const tipParts = (k) => { const w = techW(); if (K.tipP[k]) {
const ids = w.map(x => x[0]);
if (Object.keys(K.tipP[k]).every(id => ids.includes(+id)) && ids.every(id => id in K.tipP[k]))
return K.tipP[k];
K.tipP[k] = null;
} return tipAlloc(K.tipT[k], w); };
const tipProblem = () => {
for (const k of ['card', 'cash']) {
const tot = r2(K.tipT[k]);
if (tot <= 0)
continue;
if (!techW().length)
return `Choose the tech for the ${k} tip`;
const sum = r2(Object.values(tipParts(k)).reduce((s, v) => s + (+v || 0), 0));
if (Math.abs(sum - tot) > 0.004)
return `${k === 'card' ? 'Card' : 'Cash'} tip: the parts add up to ${money(sum)} – must be ${money(tot)}`;
}
return '';
};
const drawTipParts = () => {
const pb = $('#tkTipParts', sh);
if (!pb)
return;
const w = techW();
pb.innerHTML = ['card', 'cash'].filter(k => K.tipT[k] > 0 && w.length > 1).map(k => {
const p = tipParts(k);
return `<div class="tk-tipk"><span class="muted small">${k === 'card' ? '💳 Card tip' : '💵 Cash tip'} for each tech</span>${w.map(([sid]) => `<div class="tk-tiprow"><span>${esc(techName(sid))}</span><label class="tk-price"><span>$</span><input type="number" inputmode="decimal" step="0.01" min="0" data-tipp="${k}:${sid}" value="${(+p[sid] || 0).toFixed(2)}" aria-label="${k} tip for ${esc(techName(sid))}"></label></div>`).join('')}</div>`;
}).join('');
tipMsg();
};
const tipMsg = () => { const m = $('#tkTipMsg', sh); if (m) {
const pr = tipProblem();
m.textContent = pr;
m.hidden = !pr;
} };
const drawTip = () => {
const box = $('#tkTip', sh);
if (!box)
return;
if (!$('#tkTipT', box))
box.innerHTML = `${TIPC.on ? '<div id="tkTipAsked"></div>' : ''}
<div class="tk-tipedit" id="tkTipEdit" hidden><span class="lbl">Tips <span class="muted">(by hand – 100% the tech's: no $1 rule, no tax)</span></span>
<div class="two" id="tkTipT"><div class="field"><label for="tkTipCard">💳 Card tip</label><label class="tk-price"><span>$</span><input id="tkTipCard" type="number" inputmode="decimal" step="0.01" min="0" data-tipt="card" placeholder="0.00"></label></div>
<div class="field"><label for="tkTipCash">💵 Cash tip</label><label class="tk-price"><span>$</span><input id="tkTipCash" type="number" inputmode="decimal" step="0.01" min="0" data-tipt="cash" placeholder="0.00"></label></div></div>
<div id="tkTipParts"></div></div><p class="err" id="tkTipMsg" hidden></p>`;
drawTipParts();
};
const footGo = () => { const ft = $('#tkFoot', sh); if (!ft)
return; ft.innerHTML = ''; const g = !matchMedia(CK_WIDE).matches ? $('#tkPay [data-go]', sh) : null; if (g)
ft.appendChild(g); ft.hidden = !g; };
const lockFinish = () => { const prob = splitProblem() || tipProblem(); $$('[data-go]', sh).forEach(b => { b.disabled = !!prob; b.title = prob; }); cashGate(); };
const splitGate = () => {
const b = $('#tkPayBox [data-go="split"]', sh);
if (!b || !$('#spCash', sh))
return;
const d = due(), ca = r2(+$('#spCash', sh).value || 0), ot = r2(+($('#spOther', sh)?.value || 0)), card = r2(d - ca - ot), gv = $('#spGiven', sh);
const why = card < -0.004 ? 'Too much' : ot > 0 && !K.spHowOn ? 'Pick Zelle / Venmo / Other' : gv && gv.value !== '' && (+gv.value || 0) + 0.001 < ca ? 'Cash given is less than the cash part' : K.tipT.card > 0 && card <= 0.004 && d > 0.004 ? 'A card tip needs a card part' : '';
if (why) {
b.disabled = true;
b.title = why;
}
else if (!(splitProblem() || tipProblem()) && !K.saving) {
b.disabled = false;
b.title = '';
}
};
const cashGate = () => {
splitGate();
const b = $('#tkPayBox [data-go="cash"]', sh), g = $('#tkGiven', sh);
if (!b || !g)
return;
const short = g.value === '' || (+g.value || 0) + 0.001 < due();
if (short) {
b.disabled = true;
b.title = 'Type or tap the cash received';
}
else if (!(splitProblem() || tipProblem()) && !K.saving) {
b.disabled = false;
b.title = '';
}
};
const drawLoy = () => {
const L = t.loyalty, box = $('#tkLoy', sh);
if (!L) {
box.innerHTML = '';
return;
}
const list = (p) => p.lines.reduce((s, l) => s + (+l.price || 0), 0), all = K.persons.reduce((s, p) => s + list(p), 0);
const mine = K.persons[0].lines, tot = K.persons.length > 1 && all > 0 ? sub() * list(K.persons[0]) / all : sub();
const svcOk = !L.services.length || mine.some(l => L.services.includes(l.sid)), minOk = tot + 0.001 >= (L.min || 0);
const ok = svcOk && minOk && !L.counted;
box.innerHTML = `<div class="loy-box">⭐ Loyalty: <b>${L.points}/${L.need}</b> visits · <span class="loy-count ${ok ? 'yes' : 'no'}">${ok ? '✓ Counts toward rewards' : L.counted ? 'Visit already counted today (1 per day).' : !svcOk ? 'This service does not count.' : `Under ${money(L.min).replace('.00', '')} – doesn't count`}</span></div>`;
};
const drawOffer = () => {
const box = $('#tkOffer', sh);
if (!box)
return;
if (!AO.length) {
box.innerHTML = '';
return;
}
const on = aoLines()[0], b0 = Math.max(0, r2(sub() - discAmt() - offerAmt())), best = AO.find(o => o.key === (aoBest() || AO[0].key)) || AO[0];
const show = on ? on.o : best, others = AO.filter(o => o.key !== show.key);
const ofTxt = (o) => {
const em = (/^([^A-Za-z0-9$]+)\s/.exec(o.line || '') || [, ''])[1];
const mx = +o.max > 0 ? ` (tối đa ${money(+o.max).replace(/\.00$/, '')})` : '';
const ud = o.until ? ` – hạn tới ${new Date(o.until + 'T12:00:00').toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}` : '';
return `${em ? em + ' ' : ''}${o.name || ''} ${o.amt || ''} off${mx}${ud}`.replace(/\s+/g, ' ').trim();
};
const em = (o) => (/^([^A-Za-z0-9$]+)\s/.exec(o.line || '') || [, '🎁'])[1].trim() || '🎁';
const ud = (o) => o.until ? ` · hạn ${(() => { const d = new Date(o.until + 'T12:00:00'); return (d.getMonth() + 1) + '/' + d.getDate(); })()}` : '';
const amt = on ? on.v : aoVal(show, b0), mx = +show.max > 0 ? ` (tối đa ${money(+show.max).replace(/\.00$/, '')})` : '';
box.innerHTML = `<div class="ck-ofc ck-ofy ck-of1${on ? ' on' : ''}" title="${esc(ofTxt(show))}"><button type="button" class="ck-ofm" id="ckOfPick" aria-expanded="${K.ofOpen ? 'true' : 'false'}"><span class="ck-oft"><b>${esc(em(show))} ${esc(show.name || '')}${amt > 0 ? ' −' + esc(money(amt).replace(/\.00$/, '')) : ''}</b><small>${esc(mx + ud(show))}${on ? '' : ' · không dùng lần này'}</small></span>${others.length ? `<span class="ck-ofn" aria-label="${AO.length} ưu đãi – chỉ dùng 1">▾ ${AO.length}</span>` : ''}</button>
<button type="button" class="ck-sw${on ? ' on' : ''}" role="switch" aria-checked="${on ? 'true' : 'false'}" aria-label="Dùng ưu đãi này" ${on ? `data-aox="${esc(show.key)}"` : `data-aoon="${esc(show.key)}"`}><span></span></button></div>
${K.ofOpen && others.length ? `<div class="ck-ofl">${others.map(o => `<button type="button" class="ck-ofo" data-aoon="${esc(o.key)}"><span>${esc(ofTxt(o))}</span><b>−${money(aoVal(o, b0))}</b></button>`).join('')}</div>` : ''}`;
};
const cashBills = (d) => { const nx = Math.max(20, Math.ceil(d / 20) * 20); return [...new Set([20, 50, 100, nx])].sort((a, b) => a - b); };
const giftHome = () => { const g = $('#ckGift', sh), ph = sh.__giftPh; if (g && ph && ph.isConnected && g.parentNode !== ph.parentNode)
ph.after(g); };
const touch = () => matchMedia('(pointer: coarse)').matches;
const winPad = () => {
let f = '';
try {
f = localStorage.getItem('ckPad') || '';
}
catch (e) { }
if (f === 'on')
return true;
if (f === 'off')
return false;
const ua = navigator.userAgent || '';
return /Windows/i.test(ua) && !/Android|iPhone|iPad/i.test(ua) && (navigator.maxTouchPoints || 0) > 0;
};
const WP_IDS = /^(tkGiven|spCash|spGiven|spOther|spTip|tkL4|tkGift)$/, wpMoney = (i) => !/^(tkL4|tkGift)$/.test(i.id);
const wpHTML = () => `<div class="ck-wpad" id="ckWPad" hidden role="group" aria-label="Number pad"><div class="ck-wq" id="ckWQ">${[20, 40, 50, 100].map(v => `<button type="button" data-wq="${v}">$${v}</button>`).join('')}</div>
<div class="tk-pad">${['1', '2', '3', '4', '5', '6', '7', '8', '9', '.', '0', '⌫'].map(k => `<button type="button" data-wk="${k}"${k === '⌫' ? ' class="tk-pad-del" aria-label="Delete"' : k === '.' ? ' class="ck-wdot"' : ''}>${k}</button>`).join('')}</div></div>`;
const wpShow = (i) => {
const pad = $('#ckWPad', sh);
if (!pad || !i)
return;
sh.__wIn = '#' + i.id;
i.__wbuf = String(i.value || '');
pad.hidden = false;
const m = wpMoney(i);
$('#ckWQ', pad).hidden = !m;
const dot = $('.ck-wdot', pad);
if (dot)
dot.disabled = !m;
$$('#tkPayBox input.wp-on, #ckPopGift input.wp-on', sh).forEach(x => x.classList.remove('wp-on'));
i.classList.add('wp-on');
const fit = () => {
const c = i.closest('.ck-popc'), pd = $('#ckWPad', sh);
if (!c || !pd || pd.hidden || !i.isConnected)
return;
const r = i.getBoundingClientRect(), pr = pd.getBoundingClientRect(), cr = c.getBoundingClientRect();
if (r.bottom > pr.top - 8)
c.scrollTop += r.bottom - pr.top + 16;
else if (r.top < cr.top + 8)
c.scrollTop -= cr.top + 8 - r.top;
};
requestAnimationFrame(fit);
setTimeout(fit, 250);
};
const wpKey = (k, q) => {
const i = sh.__wIn && $(sh.__wIn, sh);
if (!i)
return;
const m = wpMoney(i);
let v = i.__wbuf ?? String(i.value || '');
if (q) {
if (!m)
return;
v = String(q);
}
else if (k === '⌫')
v = v.slice(0, -1);
else if (k === '.') {
if (!m || v.includes('.'))
return;
v = (v || '0') + '.';
}
else if (m) {
if (/\.\d\d$/.test(v) || v.replace('.', '').length >= 7)
return;
v = v === '0' ? k : v + k;
}
else {
const mx = +(i.getAttribute('maxlength') || 0) || 19;
if (v.length >= mx)
return;
v += k;
}
i.__wbuf = v;
i.value = m && v.endsWith('.') ? v.slice(0, -1) : v;
i.dispatchEvent(new Event('input', { bubbles: true }));
};
const popWrap = (box) => {
const inner = box.innerHTML;
if (!inner)
return;
const kinds = { card: '💳 Card', cash: '💵 Cash', more: t.gift ? '🎁 Gift / Other' : 'Other', other: 'Other', split: 'Split' };
const nums = false;
box.innerHTML = `<div class="ck-pop" data-enter="keep" role="dialog" aria-modal="true" aria-label="${esc(kinds[K.pay] || 'Pay')}"><div class="ck-popc ck-pop-${esc(K.pay)}">
<div class="ck-poph"><b>${esc(kinds[K.pay] || 'Pay')}</b><button type="button" class="ck-popx" data-popx="1" aria-label="Cancel">✕</button></div>
${inner}${/id="ckPopGift"/.test(inner) ? '' : '<div id="ckPopGift"></div>'}${winPad() ? wpHTML() : ''}${nums ? `<div class="tk-pad ck-poppad" role="group" aria-label="Number pad">${['1', '2', '3', '4', '5', '6', '7', '8', '9', '.', '0', '⌫'].map(k => `<button type="button" data-pk="${k}"${k === '⌫' ? ' aria-label="Delete"' : ''}>${k}</button>`).join('')}</div>` : ''}
<p class="err" id="ckPopErr" hidden></p><button type="button" class="btn block ck-popcancel" data-popx="1">Cancel</button></div></div>`;
box.classList.add('ck-popon');
if (K.pay === 'more' || K.pay === 'split') {
const g = $('#ckGift', sh);
if (g) {
if (!sh.__giftPh || !sh.__giftPh.isConnected) {
sh.__giftPh = document.createComment('gift');
g.before(sh.__giftPh);
}
else if (g.parentNode === sh.__giftPh.parentNode) { }
$('#ckPopGift', sh).append(g);
g.hidden = false;
}
}
$$('#tkPayBox input', sh).forEach(i => { if (/^(tkGiven|spCash|spOther)$/.test(i.id)) {
i.setAttribute('inputmode', 'decimal');
i.setAttribute('enterkeyhint', 'done');
} });
sh.__popIn = sh.__popIn && $(sh.__popIn, sh) ? sh.__popIn : ($('#tkGiven', sh) ? '#tkGiven' : $('#spCash', sh) ? '#spCash' : '');
const f = sh.__popIn && $(sh.__popIn, sh);
if (f && !touch())
setTimeout(() => { try {
f.focus({ preventScroll: true });
}
catch (e) { } }, 30);
if (f)
f.classList.add('pad-on');
if (winPad()) {
const was = sh.__wIn;
$$('input', box).forEach(i => { if (WP_IDS.test(i.id))
i.setAttribute('inputmode', 'none'); });
const g = $('#tkGift', sh);
if (g && g.closest('#tkPayBox') && !K.giftAbc)
g.setAttribute('inputmode', 'none');
const back = was && $(was, box);
if (back)
wpShow(back);
}
};
const popClose = () => { K.pay = ''; sh.__popIn = ''; err(''); drawPay(); };
sh.addEventListener('input', (e) => { if (e.isTrusted && e.target.closest && e.target.closest('#tkPayBox')) {
e.target.__buf = undefined;
e.target.__fresh = false;
} });
sh.addEventListener('focusin', (e) => { const i = e.target; if (i.closest && i.closest('#tkPayBox') && i.tagName === 'INPUT' && i.id !== 'tkGift') {
sh.__popIn = '#' + i.id;
$$('#tkPayBox input.pad-on', sh).forEach(x => x.classList.remove('pad-on'));
i.classList.add('pad-on');
} });
sh.addEventListener('focusin', (e) => { const i = e.target; if (winPad() && i.tagName === 'INPUT' && WP_IDS.test(i.id) && i.closest('#tkPayBox') && !(i.id === 'tkGift' && K.giftAbc))
wpShow(i); });
sh.addEventListener('pointerdown', (e) => { if (e.target.closest && e.target.closest('#ckWPad'))
e.preventDefault(); }, true);
sh.addEventListener('click', (e) => { const b = e.target.closest && e.target.closest('#ckWPad [data-wk], #ckWPad [data-wq]'); if (!b)
return; e.stopPropagation(); e.preventDefault(); wpKey(b.dataset.wk, b.dataset.wq); }, true);
sh.addEventListener('click', (e) => {
const pb = e.target.closest && e.target.closest('[data-pk]');
if (pb) {
e.stopPropagation();
const i = sh.__popIn && $(sh.__popIn, sh);
if (!i)
return;
let v = i.__fresh === false ? (i.__buf ?? String(i.value || '')) : '';
i.__fresh = false;
const k = pb.dataset.pk;
if (k === '⌫')
v = v.slice(0, -1);
else if (k === '.') {
if (!v.includes('.'))
v = (v || '0') + '.';
}
else {
if (/\.\d\d$/.test(v) || v.replace('.', '').length >= 7)
return;
v = v === '0' ? k : v + k;
}
i.value = v.endsWith('.') ? v.slice(0, -1) : v;
i.dispatchEvent(new Event('input', { bubbles: true }));
i.__buf = v;
return;
}
if (e.target.closest && e.target.closest('[data-popx]')) {
e.stopPropagation();
popClose();
return;
}
if (e.target.classList && e.target.classList.contains('ck-pop')) {
e.stopPropagation();
e.preventDefault();
}
}, true);
window.addEventListener('keydown', (e) => {
if (!$('#tkPayBox.ck-popon', sh) || !sh.isConnected)
return;
if (e.key === 'Escape') {
e.preventDefault();
e.stopPropagation();
popClose();
return;
}
if (e.key === 'Enter' && e.target.id !== 'tkGift' && e.target.tagName !== 'BUTTON') {
const g = $('#tkPayBox [data-go]', sh);
if (g && !g.disabled) {
e.preventDefault();
e.stopPropagation();
g.click();
}
}
}, { capture: true, signal: sheetAC ? sheetAC.signal : undefined });
const drawPay = () => {
giftHome();
const d = due(), bar = $('#tkPay', sh), more = ['more', 'other', 'split'].includes(K.pay);
bar.innerHTML = d > 0 ? `${giftUse() > 0 ? `<p class="tk-rest" id="tkRest">Pay the rest: <b>${money(d)}</b></p>` : ''}<button type="button" class="pm pm-card${K.pay === 'card' ? ' on' : ''}" data-pm="card">${IC.card}<span>Thẻ</span></button><button type="button" class="pm pm-cash${K.pay === 'cash' ? ' on' : ''}" data-pm="cash">${IC.cash}<span>Tiền mặt</span></button><button type="button" class="pm pm-more${more ? ' on' : ''}" data-pm="more" aria-expanded="${more ? 'true' : 'false'}">${IC.gift}<span>${t.gift ? 'Gift' : 'Khác'}</span></button>`
: `${K.tipT.card > 0 ? `<p class="pay-big" id="tkTipOnly">Charge the card tip ${money(K.tipT.card)} on the DPS machine</p>` : ''}<button type="button" class="btn green block" data-go="none">Finish ✓</button>`;
{
const gs = $('#ckGift', sh);
if (gs)
gs.hidden = !(more || K.gift || K.giftErr);
}
const box = $('#tkPayBox', sh);
if (d <= 0 || !K.pay) {
box.innerHTML = '';
box.classList.remove('ck-popon');
footGo();
return;
}
if (K.pay === 'more') {
box.innerHTML = `<div class="paybox ck-morebox"><p class="pay-big">Due ${money(d)}</p>${t.gift ? '<p class="hint ck-gifthint">🎁 Gift card: type the number, 📷 Scan or 📱 Phone – below.</p>' : ''}
<div class="ck-more2"><button type="button" class="pm" data-pm="other"><span>Other</span><small>Zelle · Venmo · …</small></button><button type="button" class="pm" data-pm="split"><span>Split</span><small>Cash + card + other</small></button></div></div>`;
popWrap(box);
footGo();
return;
}
const how = `<div class="pay-chips" id="tkHow">${['Zelle', 'Venmo', 'Other'].map(h => `<button type="button" data-how="${h}" class="${K.how === h ? 'on' : ''}">${h}</button>`).join('')}</div>`;
if (K.pay === 'card')
box.innerHTML = `<div class="paybox pb-card"><p class="pay-big" id="tkCardAmt">Charge ${money(d)} ${TAXP > 0 ? '(tax included) ' : ''}on the DPS machine</p>${K.tipT.card > 0 ? `<p class="muted" id="tkCardTip">+ card tip ${money(K.tipT.card)} → ${money(r2(d + K.tipT.card))} with the tip</p>` : ''}
<div class="field"><label for="tkL4">Card last 4 digits <span class="muted">(optional)</span></label><input id="tkL4" type="text" inputmode="numeric" maxlength="4" pattern="[0-9]*" autocomplete="off" placeholder="1234"></div>${typeof dvBox === 'function' ? dvBox() : '' /* (2.99.638c) */}${typeof prBox === 'function' ? prBox() : '' /* (2.99.645a) */}
<button type="button" class="btn primary block" data-go="card">Card approved ✓</button></div>`;
if (K.pay === 'cash') {
box.innerHTML = `<div class="paybox pb-cash"><p class="pay-big" id="tkCashDue">Due ${money(d)}</p>
<div class="field"><label for="tkGiven">Cash received $</label><input id="tkGiven" type="number" inputmode="decimal" step="0.01" min="0" placeholder="${d.toFixed(2)}"></div>
<div class="pay-chips tk-quick" id="tkQuick"><button type="button" data-q="${d}" data-exact="1">Exact</button>${cashBills(d).map(v => `<button type="button" data-q="${v}"${v === Math.ceil(d / 20) * 20 && ![20, 50, 100].includes(v) ? ' data-next="1"' : ''}>$${v}</button>`).join('')}</div>
<p class="pay-change big" id="tkChange"></p><button type="button" class="btn green block" data-go="cash">Cash received ✓</button></div>`;
}
if (K.pay === 'other')
box.innerHTML = `<div class="paybox"><p class="pay-big">Due ${money(d)}</p>${how}<button type="button" class="btn primary block" data-go="other" style="margin-top:12px">Paid ✓</button></div>`;
if (K.pay === 'split') {
const V = K.spv || (K.spv = {}), vv = (k) => V[k] != null && V[k] !== '' ? ` value="${esc(V[k])}"` : '';
box.innerHTML = `<div class="paybox pb-split"><p class="pay-big">Due ${money(d)}</p>
<p class="hint" style="margin:0 0 6px">Type the cash${t.gift ? ' (and the 🎁 gift card)' : ''} – the card pays the rest.</p>${t.gift ? '<div id="ckPopGift" class="sp-gift"></div>' : ''}
<div class="tk-srow"><span>💵 Cash</span><span class="tk-price"><span>$</span><input type="number" inputmode="decimal" step="0.01" min="0" id="spCash" aria-label="Cash amount"${vv('ca')}></span></div>
<!-- (2.99.255 – order 461) no "Cash given (optional)" / "Other" here any more: Gift card · Cash · Card (the rest) · Card tip -->
<div class="tk-srow"><span>💳 Card <small class="muted">(the rest)</small></span><b id="spCardAmt">${money(d)}</b></div>
${TIPC.on || K.tipT.card > 0 ? `<div class="tk-srow sp-tip"><span>💳 Card tip</span><span class="tk-price"><span>$</span><input type="number" inputmode="decimal" step="0.01" min="0" id="spTip" data-tipt="card" aria-label="Card tip" placeholder="0.00" value="${K.tipT.card > 0 ? K.tipT.card.toFixed(2) : ''}"></span></div>
<div id="spTipBox">${tipBig('spTipAsk', 'spTipChg')}</div>` : ''}
<div class="tk-type" id="spType"></div>
<div class="field" style="margin:6px 0 10px"><label for="tkL4">Card last 4 digits <span class="muted">(optional)</span></label><input id="tkL4" type="text" inputmode="numeric" maxlength="4" pattern="[0-9]*" autocomplete="off" placeholder="1234"></div>${typeof dvBox === 'function' ? dvBox() : '' /* (2.99.638c) */}${typeof prBox === 'function' ? prBox() : '' /* (2.99.645a) */}
<p class="pay-left" id="spLeft"></p><button type="button" class="btn primary block" data-go="split">Finish ✓</button></div>`;
if (!K.spHowOn)
$$('#spHow [data-how]', box).forEach(x => x.classList.remove('on'));
}
popWrap(box);
calcPay();
lockFinish();
footGo();
};
Object.assign(X, { tipParts, tipProblem, drawTipParts, tipMsg, drawTip, footGo, lockFinish, splitGate, cashGate, drawLoy, drawOffer, cashBills, giftHome, touch, winPad, WP_IDS, wpMoney, wpHTML, wpShow, wpKey, popWrap, popClose, drawPay });
}
