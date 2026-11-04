'use strict';
function renderDateStrip() {
const strip = $('#dateStrip'), hours = S.day?.allHours || {}, closedDates = S.day?.closedDates || [];
const today = S.today || localToday(), hi = S.date > today ? S.date : today;
const count = Math.round((parseD(hi) - parseD(today)) / 864e5) + 61;
const chip = (ds) => {
const d = parseD(ds), dow = d.getDay();
const closed = !!hours[dow]?.closed || closedDates.some(c => ds >= c.from && ds <= c.to);
const cls = ['day', dow === 0 || dow === 6 ? 'wk' : '', ds === S.date ? 'sel' : '', ds === today ? 'today' : '', closed ? 'closed' : ''].join(' ');
return `<button type="button" class="${cls}" data-d="${ds}"><span class="l1"><span class="n">${pad(d.getDate())}</span><span class="w">${WD[dow]}</span></span><span class="m">${closed ? 'CLOSED' : MONF[d.getMonth()]}</span></button>`;
};
let html = S.date < today ? `<button type="button" class="more" data-d="${today}">‹ Today</button>${chip(S.date)}` : '';
for (let i = 0; i < count; i++)
html += chip(addDays(today, i));
const keep = strip.scrollLeft;
strip.innerHTML = html + '<button type="button" class="more" data-more="1" aria-label="Pick a date">📅</button>';
$$('button', strip).forEach(b => b.addEventListener('click', () => {
if (b.dataset.more)
return pickDate();
if (b.dataset.d !== S.date) {
S.date = b.dataset.d;
renderDateStrip();
loadDay(true);
}
}));
const sel = $('.sel', strip);
strip.scrollLeft = sel && (sel.offsetLeft < keep || sel.offsetLeft + sel.offsetWidth > keep + strip.clientWidth) ? Math.max(0, sel.offsetLeft - strip.clientWidth * 0.2) : keep;
const t = $('#dayTitle');
if (t)
t.textContent = titleD(S.date);
}
function openFind() {
openSheet(`${head('Find customer')}<input class="inp" id="cfQ" type="search" placeholder="Name, last 4 digits or phone" autocomplete="off" aria-label="Name, last 4 digits or phone"><div id="cfRes"></div>`, (sh) => {
const q = $('#cfQ', sh), res = $('#cfRes', sh);
let tm = 0, seq = 0;
setTimeout(() => q.focus(), 120);
const draw = (rows) => {
res.innerHTML = rows.length ? rows.map((c, i) => `<div class="cf-card"><h4>${esc(c.name || 'No name')} <small class="muted">··${esc(c.last4)}</small></h4><p class="cf-l">${c.visits} visit${c.visits === 1 ? '' : 's'}${c.note ? ` · 📝 <span data-raw>${esc(c.note)}</span>` : ''}</p>
${c.up.length ? c.up.map(u => `<button type="button" class="btn small cf-up" data-cfa="${u.id}" data-cfd="${u.date}">📅 ${esc(shortDate(u.date))} ${esc(tlabel(u.start))} · ${esc(u.tech)} · ${esc(u.svc)}${u.status === 'arrived' ? ' · checked in' : ''}</button>`).join('') : '<p class="cf-l muted">No upcoming appointment.</p>'}
<p class="cf-l">${c.last ? `Last time: <b>${esc(c.last.svc || 'Not decided')}</b>${c.last.tech ? ' · ' + esc(c.last.tech) : ''} · ${esc(shortDate(c.last.date))}` : '<span class="muted">No earlier visit.</span>'}</p>
<div class="row"><button type="button" class="btn small primary" data-cfb="${i}">📅 Book</button>${c.phone && !IS_MGR ? `<button type="button" class="btn small" data-cfp="${esc(c.phone)}">Customer profile</button>` : ''}</div></div>`).join('') : (q.value.trim().length >= 2 ? '<p class="muted" style="margin-top:12px">No customer found.</p>' : '');
$$('[data-cfa]', res).forEach(b => b.addEventListener('click', async () => { closeSheet(); S.date = b.dataset.cfd; renderDateStrip(); await loadDay(true); const d = await ensureDay(S.date); const a = d.appts.find(x => x.id === +b.dataset.cfa); if (a)
openMenu(a); }));
$$('[data-cfp]', res).forEach(b => b.addEventListener('click', () => { closeSheet(); openCustomer(b.dataset.cfp); }));
$$('[data-cfb]', res).forEach(b => b.addEventListener('click', () => {
const c = rows[+b.dataset.cfb];
closeSheet();
openBookSheet({ next: true, date: S.today || localToday(), phone: c.phone ? c.phone.replace(/\D/g, '').slice(-10) : '', name: c.name, staff: c.last ? c.last.staff : 0, services: c.last ? c.last.services : [] });
}));
};
q.addEventListener('input', () => {
clearTimeout(tm);
tm = setTimeout(async () => {
const v = q.value.trim(), my = ++seq;
if (v.length < 2)
return draw([]);
try {
const r = await api('cust_find', null, { q: v });
if (my === seq)
draw(r.rows);
}
catch (e) {
res.innerHTML = `<p class="err">${esc(e.message)}</p>`;
}
}, 250);
});
});
}
document.addEventListener('click', (e) => { if (e.target.closest('#apFind'))
openFind(); });
function pickDate() { const p = $('#datePick'); p.value = S.date; if (p.showPicker) {
try {
p.showPicker();
return;
}
catch (e) { }
} p.click(); }
$('#datePick').addEventListener('change', (e) => { if (e.target.value) {
S.date = e.target.value;
renderDateStrip();
loadDay(true);
} });
$('#dayTitle')?.addEventListener('click', pickDate);
$('#dateStrip').addEventListener('wheel', (e) => { if (Math.abs(e.deltaY) > Math.abs(e.deltaX)) {
e.currentTarget.scrollLeft += e.deltaY;
e.preventDefault();
} }, { passive: false });
async function loadDay(scroll) {
const my = S.daySeq = (S.daySeq || 0) + 1;
try {
const d = await api('day', null, { date: S.date });
if (my !== S.daySeq)
return;
if (d.ver && ADMIN_VER && d.ver !== ADMIN_VER && $('#sheet').hidden) {
let k = '';
try {
k = sessionStorage.getItem('adReload') || '';
}
catch (e) { }
if (k !== d.ver) {
try {
sessionStorage.setItem('adReload', d.ver);
}
catch (e) { }
location.reload();
return;
}
}
S.day = d;
S.today = d.today;
S.nowBase = { min: d.now, at: Date.now() };
const sn = $('#salonName');
if (sn) {
sn.textContent = $('.ns-only, .has-book') ? String(d.salon || '').trim() : String(d.salon || '').replace(/\s+/g, '');
delete sn.dataset.full;
fitName();
}
setRvBadge(d.rvDue);
if (typeof setRp === 'function')
setRp(d.rp);
setBdBadge(d.bdDue);
setStopBadge(d.stopNew);
setRfBadge(d.rfDue);
document.title = d.salon;
if (S.tab === 'appts') {
renderDateStrip();
renderGrid(scroll);
}
}
catch (e) {
oops(e);
}
}
async function ensureDay(date) {
if (S.day && S.day.date === date)
return S.day;
const d = await api('day', null, { date });
if (date === S.date)
S.day = d;
return d;
}
function laneLayout(list) {
list.sort((a, b) => a.start - b.start || b.duration - a.duration || a.id - b.id);
const lanes = [];
let group = [], groupEnd = -1;
const groups = [];
for (const a of list) {
if (a.start >= groupEnd) {
group = [];
groups.push(group);
lanes.length = 0;
groupEnd = -1;
}
let lane = lanes.findIndex(end => end <= a.start);
if (lane < 0) {
lane = lanes.length;
lanes.push(0);
}
lanes[lane] = a.start + a.duration;
a._lane = lane;
group.push(a);
groupEnd = Math.max(groupEnd, a.start + a.duration);
group._n = Math.max(group._n || 0, lanes.length);
}
for (const g of groups)
for (const a of g)
a._n = g._n;
}
function dayLanes(list) {
list.sort((a, b) => a.start - b.start || a.id - b.id);
const ends = [];
for (const a of list) {
let l = ends.findIndex(e => e <= a.start);
if (l < 0) {
l = ends.length;
ends.push(0);
}
ends[l] = a.start + a.duration;
a._lane = l;
}
const n = Math.max(1, ends.length);
for (const a of list)
a._n = n;
return n;
}
const PAL = [['#D4F5E4', '#0F5132', '#2FA36B'], ['#FBDDE8', '#7A1E45', '#D9538A'], ['#E6DDFB', '#3F2A7A', '#8466D6'], ['#FFF1C2', '#6B4E00', '#D9A400'],
['#FFE0CC', '#7A3410', '#E07B3C'], ['#CFF3F0', '#0B5750', '#1FA39A'], ['#D8ECFF', '#0B3F73', '#3C8DDB'], ['#E7EDCC', '#414D12', '#8A9A2E'],
['#FFD9D6', '#7A1F1A', '#E0625A'], ['#DCE1FF', '#25307A', '#5B6BE0'], ['#F4DDF7', '#5E1F66', '#B657C4'], ['#F1E6D6', '#5A4122', '#B08A57']];
const PAL_NONE = ['#E3E8EF', '#334155', '#7A8AA3'];
const OFK = { referral: 'k-ref', refcredit: 'k-rc', winback: 'k-wb', birthday: 'k-bd', reward: 'k-rw' };
const offPills = (a) => (a.offers || []).map(o => `<span class="ofp ${OFK[o.kind] || ''}" data-full="${esc(o.label)}" data-short="${esc(o.short)}">${esc(o.label)}</span>`).join('');
const offRow = (a) => (a.offers || []).length ? `<div class="ofps">${offPills(a)}</div>` : '';
const askSt = (a, d) => { const st = (((d || S.day) && (d || S.day).turnBar && (d || S.day).turnBar.auto) || {})[a.id]; return st && (st.kind === 'ask' || st.kind === 'hold') ? st : null; };
const afterTxt = (st) => `⏳ after ${String(st.name).toUpperCase()}${st.svc ? ` (${st.svc})` : ''}`;
const askTxt = (st) => st.kind === 'hold' ? `⏳ Chờ ${String(st.name).toUpperCase()} ~${st.answer || 5} phút · Waiting for ${String(st.name).toUpperCase()}` : `⏳ Asking ${String(st.name).toUpperCase()} – busy ${st.busy} min`;
const askPill = (a) => { const st = askSt(a); return st ? `<span class="ofp k-ask" data-full="${esc(askTxt(st))}" data-short="${esc('⏳ ' + String(st.name).split(' ').pop().toUpperCase() + (st.kind === 'hold' ? ' ~' + (st.answer || 5) + "'" : ' ?'))}">${esc(askTxt(st))}</span>` : ''; };
const pcOf = (a) => (a.pc >= 0 ? PAL[a.pc % PAL.length] : null) || PAL_NONE;
const NS_COLORS = ['#1E6FD9', '#D32F2F', '#7B1FA2', '#2E7D32', '#CA4700', '#008476', '#D81B60', '#283593', '#795548', '#827717', '#455A64'];
function nsColors(lists) { lists.forEach(l => l.forEach(a => { a._c = a.pc >= 0 ? NS_COLORS[a.pc % NS_COLORS.length] : '#555'; })); }
const svcLines = (a, byId) => {
const L = a.services.map(id => {
const x = byId[id];
if (!x)
return null;
const dz = a.design && x.design;
return { full: x.name + (dz ? ' + Design' : ''), short: (x.short || x.name) + (dz ? ' +D' : ''), main: x.main !== false };
}).filter(Boolean);
const m = L.filter(x => x.main), sm = L.filter(x => !x.main);
if (!m.length || !sm.length)
return L;
m[0] = { full: m[0].full + sm.map(x => ' + ' + x.full).join(''), short: m[0].short + sm.map(x => ' + ' + x.short).join('') };
return m;
};
const svHTML = (svc) => Array.isArray(svc) ? svc.map(x => `<span class="sv" data-full="${esc(x.full)}" data-short="${esc(x.short)}">${esc(x.full)}</span>`).join('') : (svc ? `<span class="sv">${esc(svc)}</span>` : '');
const nsStatus = (a) => [a.source === 'online' ? 'ONLINE' : '', a.status === 'booked' ? (a.confirm === 'yes' ? 'Confirmed ✓' : a.unconfirmed ? 'NOT CONFIRMED' : '') : ''].filter(Boolean).join(' · ');
const nsText = (a, svc, badges) => {
const st = nsStatus(a);
return `<span class="nstx">${badges ? `<span class="badges">${badges}</span>` : ''}<span class="nm">${esc(a.name)}</span>${svHTML(svc)}${st ? `<span class="on st${a.unconfirmed && a.status === 'booked' ? ' unc' : ''}">${esc(st)}</span>` : ''}${offPills(a)}${askPill(a)}${a.note ? `<span class="nt">${esc(a.note)}</span>` : ''}</span>`;
};
const nsSlots = (a, svc, badges) => nsText(a, svc, badges) + Array.from({ length: Math.max(1, Math.round(a.duration / 15)) }, (_, i) => `<span class="slot${i ? ' blank' : ''}"></span>`).join('');
const nsLane = (a, svc, badges) => nsText(a, svc, badges);
const nsMore = (root) => $$('.appt', root).forEach(el => {
const s = $('.nstx', el);
if (!s)
return;
const over = () => s.scrollHeight > el.clientHeight + 2;
if (!over())
return;
const sv = $$('.sv', s), drop = [...$$('.nt, .ofp', s).reverse(), ...$$('.st', s), ...sv.slice(1).reverse()];
let n = 0;
for (const x of drop) {
if (!over())
break;
x.hidden = true;
if (x.classList.contains('sv'))
n++;
}
if (n) {
const m = document.createElement('span');
m.className = 'sv more';
m.textContent = '+' + n;
sv[0].after(m);
}
});
const salonNow = () => S.nowBase ? S.nowBase.min + (Date.now() - S.nowBase.at) / 60000 : -1;
function markPast() {
const d = S.day, g = S.geo, grid = $('#grid');
if (!d || !g || !grid || S.tab !== 'appts')
return;
const pastDay = d.date < d.today, today = d.date === d.today, now = salonNow();
$$('.cell', grid).forEach(c => c.classList.toggle('past', pastDay || (today && +c.dataset.m + 15 <= now)));
$$('.cell[data-m], .times [data-m]', grid).forEach(c => { const m = +c.dataset.m; c.classList.toggle('nowq', today && m <= now && now < m + 15); });
const nl = $('.nowline', grid);
if (nl) {
const on = today && now >= g.gStart && now <= g.gEnd;
nl.hidden = !on;
if (on)
nl.style.top = (gheadH() + (now - g.gStart) / 15 * g.rowH) + 'px';
}
}
const gheadH = () => $('#grid .ghead')?.offsetHeight || 44;
function renderGrid(scroll) {
if (S.apDrag) {
S.apDragLater = true;
return;
}
if (!$('#apptPeek.pk-act'))
hidePeek();
const d = S.day, grid = $('#grid');
const bar = $('#closedBar');
if (bar)
bar.hidden = true;
const open = d.hours?.open ?? 540, close = d.hours?.close ?? 1140;
let gStart = Math.floor(open / 60) * 60, gEnd = Math.ceil(close / 60) * 60;
for (const a of d.appts) {
gStart = Math.min(gStart, Math.floor(a.start / 60) * 60);
gEnd = Math.max(gEnd, Math.ceil((a.start + a.duration) / 60) * 60);
}
const rows = (gEnd - gStart) / 15;
const rowH = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--row-h')) || 44;
const known = new Set(d.staff.map(s => s.id));
const anyone = d.appts.filter(a => !known.has(a.staff)).map(a => ({ ...a }));
const cols = [...(anyone.length ? [{ id: 0, lane: 0, name: 'ANYONE' }] : []), ...d.staff.map(s => ({ id: s.id, name: s.name }))];
const svcById = Object.fromEntries(d.services.map(s => [s.id, s]));
const nowRef = d.date === d.today ? d.now : (d.date < d.today ? 99999 : -1);
let h = `<div class="ghead"><div class="corner"></div>${cols.map(c => `<div class="sname"><span>${esc(c.name)}</span></div>`).join('')}</div><div class="gbody"><div class="times">`;
for (let r = 0; r < rows; r++) {
const m = gStart + r * 15;
h += m % 60 === 0 ? `<div class="hr" data-m="${m}">${((Math.floor(m / 60) % 12) || 12)}${IS_DESK ? `:00${m >= 720 ? 'PM' : 'AM'}` : `<small>${m >= 720 ? 'PM' : 'AM'}</small>` /* (hair 04/11, anh Logan "cột tên không thẳng hàng") like nails 2.99.505 – LỆNH 504: '10' + small 'AM', fits the 58px time column so the names line up */}</div>` : `<div data-m="${m}">${m % 60}</div>`;
}
h += '</div>';
const offIds = new Set((d.off || []).map(o => o.id));
const isOff = (c, m) => !d.hours || m < d.hours.open || m + 15 > d.hours.close || (c.id && offIds.has(c.id));
const lists = cols.map(c => {
const list = c.id ? d.appts.filter(a => a.staff === c.id).map(a => ({ ...a })) : anyone;
if (c.id)
laneLayout(list);
else
c.dayLanes = dayLanes(list);
c.lanes = list.reduce((n, a) => Math.max(n, a._n || 1), 1);
return list;
});
nsColors(lists);
cols.forEach((c, ci) => {
const laned = !c.id && c.dayLanes > 1;
h += `<div class="col${laned ? ' lanes' : ''}" data-ci="${ci}"${laned ? ` style="--lanes:${c.dayLanes}"` : ''}>`;
for (let r = 0; r < rows; r++) {
const m = gStart + r * 15;
h += `<div class="cell q${m % 60 === 0 ? 0 : 1}${isOff(c, m) ? ' off' : ''}" data-m="${m}"></div>`;
}
for (const a of lists[ci]) {
const top = (a.start - gStart) / 15 * rowH, ht = a.duration / 15 * rowH - 1, w = 100 / a._n, left = w * a._lane;
const svc = svcLabel(a, d.services);
const late = a.status === 'booked' && nowRef >= a.start + 10;
const cls = ['appt', a.status, late ? 'late' : '', a.unconfirmed ? 'unconf' : '', a.confirm === 'yes' ? 'conf' : '', a.undecided ? 'undecided' : '', laned ? 'lane' : '', a.duration <= 30 ? 'short' : ''].join(' ');
const badges = [a.test ? '<i class="b tst" title="Test number – not counted anywhere">TEST</i>' : '', a.isNew ? '<i class="b new" title="New online booking"></i>' : '', a.groupSize > 1 ? `<i class="b grp" title="Group">👤<b>${a.groupSize}</b></i>` : '', a.linked ? '<i class="b lnk" title="Same customer – 2 techs (linked)">🔗</i>' : '',
a.undecided ? '<i class="b und" title="Not decided – choose the service">?</i>' : '',
a.status === 'paid' ? (a.before ? '<i class="b paid" title="Done – paid before Checkout">✓</i>' : '<i class="b paid">$</i>') : '', a.confirm === 'yes' && a.status === 'booked' ? '<i class="b ok">✓</i>' : '',
a.unconfirmed ? '<i class="b warn">?</i>' : '', a.resched && a.status === 'booked' ? '<i class="b" title="Rescheduled by customer">🔁</i>' : '',
a.fast ? '<i class="b fast" title="Done much faster than usual">⚠</i>' : '', a.deposit > 0 ? '<i class="b dep" title="Deposit paid">💳</i>' : ''].join('');
h += `<button type="button" class="${cls}" data-id="${a.id}" style="top:${top}px;height:${ht}px;left:${left}%;width:${w}%;--ns-c:${a._c}">
${(laned ? nsLane : nsSlots)(a, a.undecided ? [{ full: 'Not decided · ' + udDur(a.duration), short: 'Not decided' }] : svcLines(a, svcById), badges)}${d.checkoutOn && a.status === 'arrived' && (d.date < d.today || (d.date === d.today && d.now > a.start + a.duration + 120)) ? '<span class="nco" title="Checked in but not checked out (2+ hours after the end)">Not checked out</span>' : ''}${!d.checkoutOn && (a.status === 'arrived' || a.status === 'booked') && d.date < d.today ? '<span class="nco bco" title="Before Settings → Checkout, tax & payments → Start using Checkout on: not checked out on the web (kept as it was)">Before Checkout</span>' : ''}${a.status === 'booked' && a.noshowAuto === 3 ? '<span class="nco nrv" title="Not checked in by closing time – open it: Check in / No-show / leave it">Needs review</span>' : ''}${(() => {
const st = a.status === 'arrived' && !a.started && d.turnBar && d.turnBar.autoOn ? (d.turnBar.auto || {})[a.id] : null;
return !st ? '' : st.kind === 'after' ? `<span class="nco bco">${esc(afterTxt(st))}</span>` : st.kind === 'nocan' ? `<span class="nco nrv">${esc(st.why)}</span>` : st.kind === 'wait' ? `<span class="nco bco">${st.allBusy ? 'Waiting – all techs busy · next ' + esc(st.name) : 'Waiting for ' + esc(st.name)} (~${st.min} min)</span>` : st.kind === 'offer' ? `<span class="nco bco">🔔 ${esc(st.name)} – waiting for Accept</span>` : st.kind === 'req' ? `<span class="nco bco">⏳ Waiting for ${esc(String(st.name).toUpperCase())}</span>` : '';
})()}</button>`;
}
h += '</div>';
});
h += '</div>';
if (!cols.length)
h += '<div class="empty-cols">No techs working this day. Add techs in Settings, or tap Book to put a client under ANYONE.</div>';
if (d.date === d.today)
h += '<div class="nowline" hidden></div>';
h += '<div class="rowsel" id="rowSel" hidden></div>';
grid.innerHTML = h;
S.geo = { gStart, gEnd, rowH, cols };
fitCols();
nsMore(grid);
stickNames();
markPast();
clearInterval(S.pastT);
S.pastT = setInterval(markPast, 30000);
$$('.cell', grid).forEach(el => el.addEventListener('click', () => {
const ci = +el.parentElement.dataset.ci;
openWizard({ date: S.date, start: +el.dataset.m, staff: cols[ci].id, fromCell: true });
}));
$$('.appt', grid).forEach(el => {
el.addEventListener('click', () => {
if (S.justDragged)
return;
const id = +el.dataset.id, now = Date.now(), key = 'a' + id;
if (S.lastTap && S.lastTap.key === key && now - S.lastTap.t < 450) {
S.lastTap = null;
hidePeek();
const a = d.appts.find(x => x.id === id);
if (a)
openByState(a);
return;
}
S.lastTap = { key, t: now };
$$('.picked', grid).forEach(x => x.classList.remove('picked'));
$('#rowSel').hidden = true;
el.classList.add('picked');
const a = d.appts.find(x => x.id === id);
if (a)
showPeek(el, a, d);
});
enableDrag(el);
});
if (scroll !== false) {
const target = d.date === d.today ? d.now - 60 : open;
$('#gridWrap').scrollTop = Math.max(0, (target - gStart) / 15 * rowH);
}
}
function stickNames() {
const wrap = $('#gridWrap'), grid = $('#grid');
if (!wrap || !grid)
return;
const y = wrap.scrollTop;
$$('.appt', grid).forEach(el => {
const t = el.offsetTop, h = el.offsetHeight, tx = el.querySelector('.nstx');
if (!tx)
return;
const off = y > t + 1 && h > 44 ? Math.min(y - t, h - 40) : 0;
if (off > 0) {
tx.style.transform = `translateY(${off}px)`;
el.classList.add('stk');
}
else if (el.classList.contains('stk')) {
tx.style.transform = '';
el.classList.remove('stk');
}
});
}
{
let rq = 0;
document.addEventListener('scroll', (e) => { if (e.target && e.target.id === 'gridWrap' && !rq)
rq = requestAnimationFrame(() => { rq = 0; stickNames(); }); }, true);
}
function fitCols() {
const grid = $('#grid'), wrap = $('#gridWrap'), g = S.geo;
if (!grid || !wrap || !g)
return;
const tw = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--time-w')) || 70;
const avail = wrap.clientWidth - tw, n = Math.max(1, g.cols.length);
const perScreen = innerWidth < 600 ? 6 : Math.max(6, Math.floor(avail / 96));
const cw = Math.floor(avail / Math.min(n, perScreen)), heads = $$('.ghead .sname', grid), cols = $$('.col', grid);
grid.style.setProperty('--col-w', cw + 'px');
let total = tw;
const laneW = Math.max(56, Math.min(cw, 90));
g.cols.forEach((c, i) => {
const w = Math.max(cw, (c.lanes || 1) * (!c.id && c.dayLanes > 1 ? laneW : 48));
total += w;
[heads[i], cols[i]].forEach(el => { if (el)
el.style.flexBasis = w > cw ? w + 'px' : ''; });
});
grid.style.width = Math.max(total, tw + cw) + 'px';
$$('.ghead .sname span', grid).forEach(s => {
s.style.fontSize = '';
let fs = parseFloat(getComputedStyle(s).fontSize);
while (s.offsetWidth > s.parentElement.clientWidth - 4 && fs > 10) {
fs -= 1;
s.style.fontSize = fs + 'px';
}
});
}
window.addEventListener('resize', () => { fitCols(); fitName(); });
try {
let rw = 0;
new ResizeObserver((en) => { const w = Math.round(en[0].contentRect.width); if (w && w !== rw) {
rw = w;
fitName();
} }).observe($('.ns-head'));
}
catch (e) { }
function fitName() {
const h = $('#salonName'), hd = $('.ns-head'), u = $('#btnUser');
if (!h || !hd)
return;
if (hd.classList.contains('has-book') && !(u && !u.hidden)) {
const full = h.dataset.full || h.textContent.trim();
h.dataset.full = full;
h.title = full;
h.textContent = full;
h.style.fontSize = '';
const shrink = (min) => { let fs = parseFloat(getComputedStyle(h).fontSize); while (h.scrollWidth > h.clientWidth + 1 && fs > min) {
fs -= 0.5;
h.style.fontSize = fs + 'px';
} return h.scrollWidth <= h.clientWidth + 1; };
if (shrink(14))
return;
const short = full.replace(/\s*(&|AND)\s+SPA\s*$/i, '').trim();
if (short && short !== full) {
h.textContent = short;
h.style.fontSize = '';
if (shrink(13))
return;
}
shrink(11);
return;
}
if (hd.classList.contains('ns-only')) {
h.style.fontSize = '';
return;
}
hd.classList.remove('ns-notitle');
h.style.fontSize = '';
let fs = parseFloat(getComputedStyle(h).fontSize);
while (h.scrollWidth > h.clientWidth + 1 && fs > (document.getElementById('btnRefer') ? 8 : 11)) {
fs -= 0.5;
h.style.fontSize = fs + 'px';
}
if (u && !u.hidden && (fs < 13 || h.scrollWidth > h.clientWidth + 1 || u.scrollWidth > u.clientWidth + 1))
hd.classList.add('ns-notitle');
}
function showPeek(el, a, d) {
hidePeek();
const tech = a.staff ? (d.staff.find(s => s.id === a.staff)?.name || '') : 'ANYONE';
const svc = svcLabel(a, d.services) || (a.undecided ? '❓ Not decided · ' + udDur(a.duration) : '');
const box = document.createElement('div');
box.id = 'apptPeek';
box.className = 'appt-peek';
box.setAttribute('role', 'status');
box.innerHTML = `<b class="pk-n">${esc(a.name)}${a.groupSize > 1 ? ` <span class="pk-g">👤${a.groupSize}</span>` : ''}</b>${svc ? `<span class="pk-s">${esc(svc)}</span>` : ''}
<span class="pk-t">${tlabel(a.start)} – ${tlabel(a.start + a.duration)} · ${esc(tech)}</span>${a.note ? `<span class="pk-o">📝 ${esc(a.note)}</span>` : ''}${offRow(a)}`;
const acts = a.status === 'arrived' && !IS_MGR;
if (acts) {
box.classList.add('pk-act');
box.insertAdjacentHTML('beforeend', '<span class="pk-acts"><button type="button" class="pk-b" data-pk="menu">☰ Menu</button><button type="button" class="pk-b pk-left" data-pk="left">🚶 Khách bỏ về</button></span>');
box.addEventListener('click', (e) => {
const b = e.target.closest('[data-pk]');
if (!b)
return;
e.stopPropagation();
hidePeek();
const left = b.dataset.pk === 'left';
S.apLeft = left ? a.id : 0;
openMenu(a);
});
}
document.body.appendChild(box);
const r = el.getBoundingClientRect(), bw = box.offsetWidth, bh = box.offsetHeight, gap = 6;
let top = r.top - bh - gap;
if (top < 8)
top = Math.min(innerHeight - bh - 8, r.bottom + gap);
const left = Math.max(8, Math.min(innerWidth - bw - 8, r.left + r.width / 2 - bw / 2));
Object.assign(box.style, { top: Math.max(8, top) + 'px', left: left + 'px' });
S.peekT = setTimeout(hidePeek, acts ? 9000 : 6000);
}
function hidePeek() { clearTimeout(S.peekT); const b = $('#apptPeek'); if (b)
b.remove(); }
document.addEventListener('pointerdown', (e) => { if (!e.target.closest || !e.target.closest('.appt, #apptPeek'))
hidePeek(); }, true);
document.addEventListener('scroll', hidePeek, true);
function lightCol(ci) {
$$('#grid .col.drop-on, #grid .ghead .sname.drop-on').forEach(x => x.classList.remove('drop-on'));
if (ci < 0)
return;
const c = $$('#grid .col')[ci], n = $$('#grid .ghead .sname')[ci];
if (c)
c.classList.add('drop-on');
if (n)
n.classList.add('drop-on');
}
const HOLD_MS = 1000;
function enableDrag(el) {
let timer = null, sx = 0, sy = 0, drag = null, touched = false;
const pt = (e) => (e.touches && e.touches.length ? e.touches[0] : e.changedTouches ? e.changedTouches[0] : e);
const start = (e) => { if (e.button > 0)
return; const p = pt(e); sx = p.clientX; sy = p.clientY; clearTimeout(timer); timer = setTimeout(() => begin(p), HOLD_MS); };
const cancelPress = () => { clearTimeout(timer); timer = null; };
const begin = (p) => {
timer = null;
hidePeek();
const a = S.day.appts.find(x => x.id === +el.dataset.id);
if (!a || (a.status === 'paid' && !(window.CalMove && CalMove.can())))
return;
const grid = $('#grid'), r = el.getBoundingClientRect(), gr = grid.getBoundingClientRect();
const ghost = el.cloneNode(true);
ghost.classList.add('ghost');
ghost.removeAttribute('data-id');
Object.assign(ghost.style, { left: (r.left - gr.left) + 'px', top: (r.top - gr.top) + 'px', width: $('.col').offsetWidth + 'px', height: r.height + 'px' });
grid.appendChild(ghost);
el.classList.add('lifted');
const tag = document.createElement('span');
tag.className = 'dragtime';
ghost.appendChild(tag);
drag = { a, ghost, tag, offY: p.clientY - r.top, start: a.start, staff: a.staff, raf: 0, last: { clientX: p.clientX, clientY: p.clientY }, col: -1 };
S.apDrag = true;
document.body.classList.add('ap-dragging');
{
const gw = $('#gridWrap'), x = gw.scrollLeft, y = gw.scrollTop;
gw.style.overflow = 'hidden';
gw.scrollLeft = x;
gw.scrollTop = y;
}
if (navigator.vibrate)
navigator.vibrate(12);
move(p);
};
const EDGE = 40, VMAX = 24;
const speed = (d) => d >= EDGE ? 0 : Math.max(2, Math.round(VMAX * (1 - Math.max(0, d) / EDGE)));
const edges = (p) => {
const gw = $('#gridWrap');
if (!gw)
return [0, 0];
const w = gw.getBoundingClientRect(), vv = window.visualViewport;
const vw = vv ? vv.width : window.innerWidth, vh = vv ? vv.height : window.innerHeight;
const timeW = ($('.times') || {}).offsetWidth || 0, headH = ($('.ghead') || {}).offsetHeight || 0;
const L = Math.max(w.left, 0) + timeW, R = Math.min(w.right, vw), T = Math.max(w.top, 0) + headH, Bm = Math.min(w.bottom, vh);
let vx = 0, vy = 0;
if (p.clientX > R - EDGE && gw.scrollLeft + gw.clientWidth < gw.scrollWidth - 1)
vx = speed(R - p.clientX);
else if (p.clientX < L + EDGE && gw.scrollLeft > 0)
vx = -speed(p.clientX - L);
if (p.clientY > Bm - EDGE && gw.scrollTop + gw.clientHeight < gw.scrollHeight - 1)
vy = speed(Bm - p.clientY);
else if (p.clientY < T + EDGE && gw.scrollTop > 0)
vy = -speed(p.clientY - T);
return [vx, vy];
};
const tick = () => {
if (!drag)
return;
drag.raf = 0;
const [vx, vy] = edges(drag.last);
if (!vx && !vy)
return;
const gw = $('#gridWrap');
gw.scrollLeft += vx;
gw.scrollTop += vy;
place(drag.last);
drag.raf = requestAnimationFrame(tick);
};
const move = (p) => {
if (!drag)
return;
drag.last = { clientX: p.clientX, clientY: p.clientY };
place(drag.last);
if (!drag.raf)
drag.raf = requestAnimationFrame(tick);
};
const place = (p) => {
const g = S.geo, gr = $('#grid').getBoundingClientRect();
const timeW = $('.times').offsetWidth, headH = $('.ghead').offsetHeight, colEls = $$('#grid .col');
let col = colEls.findIndex(c => { const q = c.getBoundingClientRect(); return p.clientX < q.right; });
if (col < 0)
col = colEls.length - 1;
col = Math.max(0, Math.min(g.cols.length - 1, col));
let m = g.gStart + Math.round(((p.clientY - drag.offY) - gr.top - headH) / g.rowH) * 15;
m = Math.max(g.gStart, Math.min(g.gEnd - 15, m));
drag.start = m;
drag.staff = g.cols[col].id;
const cr = colEls[col] ? colEls[col].getBoundingClientRect() : null;
drag.ghost.style.left = (cr ? cr.left - gr.left : timeW) + 'px';
if (cr)
drag.ghost.style.width = cr.width + 'px';
drag.ghost.style.top = (headH + (m - g.gStart) / 15 * g.rowH) + 'px';
drag.tag.textContent = tlabel(m) + ' · ' + g.cols[col].name;
if (col !== drag.col) {
lightCol(-1);
drag.col = col;
lightCol(col);
}
};
const end = async () => {
cancelPress();
if (!drag)
return;
const { a, ghost, start: ns, staff: nst } = drag;
if (drag.raf)
cancelAnimationFrame(drag.raf);
drag = null;
ghost.remove();
el.classList.remove('lifted');
lightCol(-1);
S.apDrag = false;
document.body.classList.remove('ap-dragging');
{
const gw = $('#gridWrap'), x = gw.scrollLeft, y = gw.scrollTop;
gw.style.overflow = '';
gw.scrollLeft = x;
gw.scrollTop = y;
}
const later = S.apDragLater;
S.apDragLater = false;
if (later && ns === a.start && nst === a.staff)
loadDay(false);
S.justDragged = true;
setTimeout(() => { S.justDragged = false; }, 350);
if (ns === a.start && nst === a.staff)
return;
if (a.status === 'paid')
return window.CalMove ? CalMove.paid(a, ns, nst) : loadDay(false);
await moveAppt(a, ns, nst);
};
el.addEventListener('touchstart', (e) => { touched = true; start(e); }, { passive: true });
el.addEventListener('touchmove', (e) => { if (drag) {
e.preventDefault();
move(pt(e));
return;
} const p = pt(e); if (Math.hypot(p.clientX - sx, p.clientY - sy) > 8)
cancelPress(); }, { passive: false });
el.addEventListener('touchend', end);
el.addEventListener('touchcancel', end);
el.addEventListener('contextmenu', (e) => e.preventDefault());
el.addEventListener('mousedown', (e) => {
if (touched)
return;
start(e);
const mm = (ev) => { if (drag)
move(ev);
else if (Math.hypot(ev.clientX - sx, ev.clientY - sy) > 6)
cancelPress(); };
const mu = () => { document.removeEventListener('mousemove', mm); document.removeEventListener('mouseup', mu); end(); };
document.addEventListener('mousemove', mm);
document.addEventListener('mouseup', mu);
});
}
function apptPayload(a, over) {
return Object.assign({ id: a.id, date: a.date, start: a.start, staff: a.staff, services: a.services, design: a.design ? 1 : 0, duration: a.duration, name: a.name, phone: a.phone, note: a.note }, over || {});
}
async function moveAppt(a, start, staff, force, silent, both) {
try {
const r = await api('save_appt', apptPayload(a, { start, staff, force: !!force, linked_too: !!both }));
if (r.conflict) {
openSheet(`${head('Double booking?')}<p>${esc(r.message)}</p><div class="actions"><button type="button" class="btn primary" id="mvYes">Move anyway</button><button type="button" class="btn" id="mvNo">Keep old time</button></div>`, (sh) => {
$('#mvYes', sh).addEventListener('click', () => { closeSheet(); moveAppt(a, start, staff, true, false, !!both); });
$('#mvNo', sh).addEventListener('click', closeSheet);
});
return;
}
const staffName = staff ? (S.day.staff.find(s => s.id === staff)?.name || '') : 'ANYONE';
await loadDay(false);
if (silent)
return;
toast(`${a.name} → ${tlabel(start)} · ${staffName}`, 5000, { label: 'Undo', run: () => moveAppt({ ...a, start }, a.start, a.staff, true, true, !!both) });
if (r.text)
offerText(r.text, 'Text the new time?', null, true);
}
catch (e) {
oops(e);
loadDay(false);
}
}
