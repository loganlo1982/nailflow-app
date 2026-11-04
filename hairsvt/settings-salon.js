Object.assign(SET_PAGES, {
salon(b, s) {
const L = s.logo;
b.innerHTML = `<h3 style="margin-top:0">Logo</h3>
<div class="logo-row"><img class="logo-now" src="${esc(L.logo)}" alt="Logo" loading="lazy" decoding="async"><div>
<p class="hint" style="margin:0 0 8px">Shown on the booking page, the check-in iPad, customer pages, admin, the app icon and link previews.</p>
<div class="row"><label class="btn primary small" for="lgFile">⬆ Upload logo</label>
${L.canBack ? `<button type="button" class="btn small" id="lgBack"><img class="logo-prev-mini" src="${esc(L.prevLogo)}" alt="" loading="lazy" decoding="async">Use previous logo</button>` : ''}</div>
<input type="file" id="lgFile" class="visually-hidden" accept="image/png,image/jpeg"></div></div>
<h3>Salon details</h3>
<div class="field"><label for="sName">Salon name</label><input id="sName" value="${esc(s.salon_name)}"></div>
<div class="two"><div class="field"><label for="sPhone">Salon phone</label><input id="sPhone" type="tel" value="${esc(s.salon_phone)}"></div>
<div class="field"><label for="sTz">Time zone</label><select id="sTz">${tzList.map(z => `<option${z === s.timezone ? ' selected' : ''}>${z}</option>`).join('')}</select></div></div>
<div class="field"><label for="sAddr">Address</label><input id="sAddr" value="${esc(s.salon_address)}"></div>
<div class="field"><label for="sAppShort">App short name <small class="muted">(tên ngắn trên icon app)</small></label><input id="sAppShort" maxlength="12" placeholder="${esc(s.app_short_now || '')}" value="${esc(s.app_short || '')}">
<p class="hint" style="margin:4px 0 0">App names: <b>${esc((s.app_short || s.app_short_now || ''))} Admin · Manager · Tech · Desk</b>. Empty = the first letters of the salon name. Shown in the NailFlow app and on receipts / texts.</p></div>
<div class="field"><label for="sNoText">Desk / no-text numbers <small class="muted">(số bàn – không nhắn tin)</small></label><input id="sNoText" inputmode="tel" placeholder="other landlines, comma between" value="${esc(s.no_text_phones || '')}">
<p class="hint" style="margin:4px 0 0">📵 Never texted (Auto send, To send, Send now, receipts, reminders): the salon phone above${(s.no_text_list || []).length ? ' – now: <b>' + (s.no_text_list || []).map(esc).join(', ') + '</b>' : ''}. Your test numbers (Settings → Test numbers) are never blocked.</p></div>
<button type="button" class="btn primary block" id="sSave">Save</button>
`;
$('#sSave', b).addEventListener('click', async () => {
try {
await api('save_settings', { salon_name: $('#sName', b).value, salon_phone: $('#sPhone', b).value, salon_address: $('#sAddr', b).value, no_text_phones: $('#sNoText', b).value, app_short: $('#sAppShort', b).value, timezone: $('#sTz', b).value });
saved();
$('#salonName').textContent = $('#sName', b).value.replace(/\s+/g, '');
fitName();
S.day = null;
}
catch (e) {
oops(e);
}
});
$('#lgFile', b).addEventListener('change', (e) => { const f = e.target.files && e.target.files[0]; e.target.value = ''; if (f)
openLogoCrop(f); });
const back = $('#lgBack', b);
if (back)
back.addEventListener('click', async () => { try {
await api('logo_revert', {});
toast('Previous logo is back ✓');
renderSettings();
}
catch (x) {
oops(x);
} });
},
async testmode(b) {
let r;
try {
r = await api('test_mode_admin');
}
catch (e) {
b.innerHTML = `<p class="err">${esc(e.message)}</p>`;
return;
}
const t = r.info, tm = (x) => { const d = new Date(x.replace(' ', 'T')); return isNaN(d) ? '' : tlabel(d.getHours() * 60 + d.getMinutes()); };
b.innerHTML = t ? `<div class="tm-on-card"><p class="tm-big">🧪 TEST MODE is ON – ends ${esc(t.ends)}</p><p class="hint" style="margin:0">Started by ${esc(t.by)}${t.from ? ' at ' + esc(tm(t.from)) : ''}. Stops by itself at ${esc(t.ends)}.</p></div>
<div id="tmBox"></div><button type="button" class="btn red block" id="tmStop">⏹ Stop test</button>
<p class="hint">Stop test deletes the TEST visits, clock-ins and turns of the test, voids the TEST receipts / gift cards, and puts the real turn line back as it was (Money & security log).</p>`
: `<p class="hint" style="margin:0 0 8px">For 30, 60 or 120 minutes you can try everything on the real iPad and the techs’ real phones – also on a closed day or after hours:</p>
<ul class="hint tm-list"><li>The check-in iPad opens, but only for the test numbers (Settings → Test numbers).</li><li>Techs can clock in / out / Break / I'm back at any time.</li><li>Turns run for real: YOUR TURN (marked 🧪 TEST), Accept / Skip / 3 min, “how long?”, the 60-min alert.</li><li>Nothing goes into Payroll, Reports, Close day, Year-end, Rewards, Referral, Win-back or Review; no texts to customers.</li><li>An orange bar “🧪 TEST MODE – ends …” on the iPad, admin, AN Desk and AN Tech.</li><li>When it ends (Stop or time up) everything the test made is cleaned; the real turn line is as before.</li></ul>
${r.block ? `<p class="err" style="margin:6px 0">Can’t start now: ${esc(r.block)}</p>` : ''}
<div class="row tm-start" style="gap:8px">${[30, 60, 120].map(m => `<button type="button" class="btn primary" data-tm="${m}" ${r.block ? 'disabled' : ''} style="flex:1">▶ Start test · ${m} min</button>`).join('')}</div><div id="tmBox"></div>`;
$$('[data-tm]', b).forEach(x => x.addEventListener('click', async () => {
x.disabled = true;
try {
await api('test_mode_start', { min: +x.dataset.tm });
toast('🧪 Test mode ON');
}
catch (e) {
oops(e);
}
window.TestBar && TestBar.refresh();
renderSettings();
}));
$('#tmStop', b)?.addEventListener('click', () => confirmIn($('#tmBox', b), 'Stop the test now? Everything the test made is deleted / voided.', 'Stop test', async () => {
try {
const x = await api('test_mode_stop', {});
toast(`Test stopped – ${x.visits || 0} test visit(s), ${x.clocks || 0} clock-in(s) cleaned`);
}
catch (e) {
oops(e);
}
window.TestBar && TestBar.refresh();
renderSettings();
}, true));
},
test(b, s) {
const c = s.test_counts || { appts: 0, receipts: 0 };
b.innerHTML = `<p class="hint" style="margin:0 0 8px">These numbers work exactly like a real customer everywhere (check-in, online booking, Checkout, texts, turns, STOP). The only difference: their receipts are marked TEST – never counted in sales, Close day, Payroll, Year-end or reports.</p>
<div id="tpList"></div>
<button type="button" class="btn small" id="tpAdd" style="margin:4px 0 10px">+ Add a test number</button>
<button type="button" class="btn primary block" id="tpSave">Save test numbers</button>
<h3>🔗 Test booking link</h3>
<p class="hint">The booking page in TEST MODE: every time of every day (closed days, after hours, techs with online booking off), a test number filled in (only test numbers can book there), all TEST. Only for you – do not share it.</p>
${s.test_link ? `<div class="field"><div class="linkbox"><input class="inp" readonly id="tmLink" value="${esc(s.test_link)}" aria-label="Test booking link"><button type="button" class="btn small" data-copy="${esc(s.test_link)}">Copy</button><a class="btn small primary" href="${esc(s.test_link)}" target="_blank" rel="noopener">Open</a></div>
${s.test_link_text && s.test_link_phone ? `<a class="btn small" style="margin-top:6px" href="${esc(smsHref(s.test_link_phone, s.test_link_text))}">💬 Text it to ${esc(prettyPhone(s.test_link_phone))}</a>` : ''}
<p class="hint" style="margin:4px 0 0">Works until ${esc(s.test_link_until)} (24 hours).</p></div>`
: `<p class="err" style="margin:0 0 8px">The test link expired (${esc(s.test_link_until || '')}).</p><button type="button" class="btn primary block" id="tmNew">Tạo link mới</button>`}
<h3>🗑 Test data</h3>
<p class="hint" id="tcN">Now: ${c.appts} test appointment(s), ${c.receipts} test receipt(s).</p>
<div id="tcBox"></div>
<button type="button" class="btn red block" id="tcDel" ${c.appts + c.receipts ? '' : 'disabled'}>Delete all test data</button>`;
const list = (s.test_phones || []).slice();
if (!list.length)
list.push('');
const draw = () => {
$('#tpList', b).innerHTML = list.map((p, i) => `<div class="row tprow" style="gap:6px;margin-bottom:6px"><input type="tel" inputmode="tel" data-i="${i}" value="${esc(p)}" placeholder="(555) 010-0100" aria-label="Test number ${i + 1}" style="flex:1"><button type="button" class="btn small" data-rm="${i}" aria-label="Remove">✕</button></div>`).join('');
$$('[data-i]', b).forEach(x => x.addEventListener('input', () => { list[+x.dataset.i] = x.value; }));
$$('[data-rm]', b).forEach(x => x.addEventListener('click', () => { list.splice(+x.dataset.rm, 1); if (!list.length)
list.push(''); draw(); }));
};
draw();
const tn = $('#tmNew', b);
if (tn)
tn.addEventListener('click', async () => { try {
await api('test_link_new', {});
toast('New test link ✓ – works for 24 hours');
renderSettings();
}
catch (e) {
oops(e);
} });
$('#tpAdd', b).addEventListener('click', () => { if (list.length >= 20)
return toast('At most 20 test numbers'); list.push(''); draw(); $$('[data-i]', b).pop().focus(); });
$('#tpSave', b).addEventListener('click', async () => { try {
await api('save_settings', { test_phones: list.map(x => x.trim()).filter(Boolean) });
saved();
renderSettings();
}
catch (e) {
oops(e);
} });
$('#tcDel', b).addEventListener('click', () => confirmIn($('#tcBox', b), `Delete ${c.appts} test appointment(s) and ${c.receipts} test receipt(s) for good? Real customers are not touched.`, 'Delete test data', async () => {
try {
const r = await api('test_clear', { confirm: 'DELETE' });
toast(`Deleted ${r.appts} appointment(s), ${r.receipts} receipt(s)`);
renderSettings();
}
catch (e) {
oops(e);
}
}, true));
},
receipt(b, s) {
b.innerHTML = `<div class="field"><label for="rcLine">Service line name on receipts</label><input id="rcLine" maxlength="40" value="${esc(s.receipt_line)}"></div>
<p class="hint" style="margin:0 0 8px">Each tech gets one line: “${esc(s.receipt_line)} · TONY $100.00”. On the receipt screen, the printed receipt, the customer's receipt link and Receipts.</p>
<p class="hint" style="margin:0 0 8px">Only a word on receipts – it is not a service: never on the booking page, Book, Check-in or the service list.</p>
<button type="button" class="btn primary block" id="rcLineSave">Save</button>
<h3>🖨 Receipt paper (Print receipt)</h3>
<div class="seg" id="sPaper"><button type="button" data-paper="letter" class="${s.receipt_paper !== '80mm' ? 'on' : ''}">Letter paper</button><button type="button" data-paper="80mm" class="${s.receipt_paper === '80mm' ? 'on' : ''}">80 mm receipt printer</button></div>
<p class="hint">Letter: the receipt in the middle of one page, with the logo, easy to read. 80 mm: narrow, for a thermal receipt printer. One page, no margins. If the link or the date still prints at the top / bottom (a computer): in the print window turn off “Headers and footers”.</p>
<label class="check"><input type="checkbox" id="rcDeskPrint" ${s.desk_autoprint ? 'checked' : ''}><span><b>AN Desk: print the receipt by itself after paying</b> – the desk computer prints it right after Checkout (no need to tap 🖨 Print). Off: tap 🖨 Print.</span></label>
<p class="hint">To print with no print window on the desk computer: Windows → the SNBC printer = default printer; open AN Desk with an Edge shortcut that has <b>--kiosk-printing</b>.</p>`;
$('#rcDeskPrint', b).addEventListener('change', async (e) => { try {
await api('save_settings', { desk_autoprint: e.target.checked });
saved();
}
catch (x) {
e.target.checked = !e.target.checked;
oops(x);
} });
$$('[data-paper]', b).forEach(x => x.addEventListener('click', async () => { try {
await api('save_settings', { receipt_paper: x.dataset.paper });
$$('[data-paper]', b).forEach(y => y.classList.toggle('on', y === x));
saved();
}
catch (e) {
oops(e);
} }));
$('#rcLineSave', b).addEventListener('click', async () => { try {
await api('save_settings', { receipt_line: $('#rcLine', b).value });
saved();
renderSettings();
}
catch (e) {
oops(e);
} });
b.insertAdjacentHTML('beforeend', `<h3>📵 Paper walk-in sheet (no internet)</h3><p class="hint">Print a few and keep them at the desk. No internet: write each walk-in on it (time, name, tech, services, $, tip, how paid) and enter them when the internet is back.</p>
<button type="button" class="btn block" id="wsPrint">🖨 Print the paper walk-in sheet</button>`);
$('#wsPrint', b).addEventListener('click', printWalkinSheet);
},
hours(b, s) {
b.innerHTML = `<span class="lbl">Opening hours</span>
<div id="hrs" style="margin-top:6px">${[1, 2, 3, 4, 5, 6, 0].map(d => {
const h = s.hours[d] || { open: '09:00', close: '19:00' };
return `<div class="hours-row" data-d="${d}">
<b>${WD[d]}</b><input type="time" class="o" value="${h.open}" aria-label="${WDL[d]} open"><input type="time" class="c" value="${h.close}" aria-label="${WDL[d]} close">
<label><input type="checkbox" class="cl" ${h.closed ? 'checked' : ''}> Closed</label></div>`;
}).join('')}</div>
<button type="button" class="btn primary block" id="hSave" style="margin-top:6px">Save opening hours</button>
<h3>Closed dates</h3>
<p class="hint">Holidays or days off for the whole salon, on top of the weekly opening hours. Customers cannot book these days.</p>
<div class="list" id="cdList"></div>
<div class="two" style="margin-top:10px"><div class="field"><label for="cdFrom">From</label><input id="cdFrom" type="date"></div>
<div class="field"><label for="cdTo">To (optional)</label><input id="cdTo" type="date"></div></div>
<div class="field"><label for="cdNote">Reason (optional)</label><input id="cdNote" maxlength="60" placeholder="Thanksgiving"></div>
<button type="button" class="btn primary block" id="cdAdd">Add closed date</button>
<h3>Special day – its own hours</h3>
<p class="hint">A day the salon opens late or closes early (Christmas Eve 10–3…). Used everywhere: online booking, the iPad, the turn line, reminders. Closed all day: use Closed dates above.</p>
<div class="two"><div class="field"><label for="spFrom">Day</label><input id="spFrom" type="date"></div><div class="field"><label for="spTo">To (optional)</label><input id="spTo" type="date"></div></div>
<div class="two"><div class="field"><label for="spOpen">Open</label><input id="spOpen" type="time" value="10:00"></div><div class="field"><label for="spClose">Close</label><input id="spClose" type="time" value="15:00"></div></div>
<div class="field"><label for="spNote">Reason (optional)</label><input id="spNote" maxlength="60" placeholder="Christmas Eve"></div>
<button type="button" class="btn primary block" id="spAdd">Add special hours</button>`;
$('#hSave', b).addEventListener('click', async () => {
const hours = {};
$$('#hrs .hours-row', b).forEach(r => { hours[r.dataset.d] = { open: $('.o', r).value, close: $('.c', r).value, closed: $('.cl', r).checked }; });
try {
await api('save_settings', { hours });
saved();
S.day = null;
}
catch (e) {
oops(e);
}
});
const cdDay = (ds) => { const x = parseD(ds); return WD[x.getDay()] + ' ' + MON[x.getMonth()] + ' ' + x.getDate() + ', ' + x.getFullYear(); };
const drawClosed = (list) => {
$('#cdList', b).innerHTML = list.map(c => `<div class="item cd-item"><div class="main">
<div class="t1">${esc(c.from === c.to ? cdDay(c.from) : cdDay(c.from) + ' – ' + cdDay(c.to))}</div><div class="t2">${c.open ? `🕘 <b>Special hours ${esc(hmLabel(c.open))} – ${esc(hmLabel(c.close))}</b>${c.note ? ' · ' + esc(c.note) : ''}` : esc(c.note || 'Closed')}</div>
${c.appts.length ? `<div class="cdwarn"><b>⚠ ${c.appts.length} appointment${c.appts.length > 1 ? 's are' : ' is'} still booked ${c.open ? 'outside these hours' : 'on ' + (c.from === c.to ? 'this day' : 'these days')}.</b> They were not deleted. Please call these customers:
<ul>${c.appts.map(a => `<li>${esc(cdDay(a.date))} ${esc(a.time)} · ${esc(a.name)}${a.phone ? ' · ' + esc(a.phone) : ''} · ${esc(a.tech)}${a.services ? ' · ' + esc(a.services) : ''}</li>`).join('')}</ul>
<button type="button" class="btn small primary" data-cdtx="${esc(c.id)}">💬 Queue texts to ${c.appts.length} customer${c.appts.length > 1 ? 's' : ''}</button></div>` : ''}</div>
<button type="button" class="icon-btn" data-cdrm="${esc(c.id)}" aria-label="Remove this closed date">✕</button></div>`).join('') || '<div class="empty">No closed dates.</div>';
$$('[data-cdtx]', b).forEach(x => x.addEventListener('click', async () => {
x.disabled = true;
try {
const r = await api('closed_texts', { id: x.dataset.cdtx });
x.textContent = `✓ ${r.queued} text${r.queued === 1 ? '' : 's'} in Messages → To send`;
refreshBadge();
}
catch (e) {
oops(e);
x.disabled = false;
}
}));
$$('[data-cdrm]', b).forEach(x => x.addEventListener('click', async () => {
if (x.dataset.sure !== '1') {
x.dataset.sure = '1';
x.textContent = '?';
toast('Tap ✕ again to open the salon on these days');
return;
}
try {
const r = await api('closed_remove', { id: x.dataset.cdrm });
drawClosed(r.closed_dates);
S.day = null;
toast('Closed date removed');
}
catch (e) {
oops(e);
}
}));
};
drawClosed(s.closed_dates || []);
$('#spAdd', b).addEventListener('click', async () => {
const from = $('#spFrom', b).value, to = $('#spTo', b).value || from;
if (!from) {
toast('Choose the day first');
return;
}
try {
const r = await api('closed_add', { from, to, open: $('#spOpen', b).value, close: $('#spClose', b).value, note: $('#spNote', b).value });
drawClosed(r.closed_dates);
S.day = null;
$('#spFrom', b).value = $('#spTo', b).value = $('#spNote', b).value = '';
toast(r.appts.length ? `Special hours added. ⚠ ${r.appts.length} appointment${r.appts.length > 1 ? 's are' : ' is'} outside them – see the list.` : 'Special hours added', r.appts.length ? 6000 : 2800);
}
catch (e) {
oops(e);
}
});
$('#cdAdd', b).addEventListener('click', async () => {
const from = $('#cdFrom', b).value, to = $('#cdTo', b).value || from;
if (!from) {
toast('Choose the date first');
return;
}
try {
const r = await api('closed_add', { from, to, note: $('#cdNote', b).value });
drawClosed(r.closed_dates);
S.day = null;
$('#cdFrom', b).value = $('#cdTo', b).value = $('#cdNote', b).value = '';
toast(r.appts.length ? `Closed date added. ⚠ ${r.appts.length} appointment${r.appts.length > 1 ? 's are' : ' is'} still booked – see the list.` : 'Closed date added', r.appts.length ? 6000 : 2800);
}
catch (e) {
oops(e);
}
});
},
services(b, s) {
const mo = (x, k) => ((s.svc_more || {})[x.id] || {})[k] || '';
const mainDef = (x) => /^basic manicure$/i.test(String(x.name).trim()) || +x.price >= +(s.main_min ?? 30);
const mainOf = (x) => x._main !== undefined ? x._main : (s.svc_main && s.svc_main[x.id] !== undefined ? !!+s.svc_main[x.id] : mainDef(x));
const services = s.services.map(x => ({ ...x }));
const removedSvc = [];
b.innerHTML = `<p class="hint">Min = how long the service takes. Rebook = text the client to come back this many days after the visit (empty = off). Tip: a sample hair menu is in Settings → ✂️ Hair salon rules.</p>
<h3>Groups on the booking page, iPad and Book</h3>
<p class="hint">Customers see the services under these titles. ↑ changes the order (services: ↑ in the list below). Choose each service's group below; a service without a group shows under OTHER. Español = the title in Spanish.</p>
<div id="sgList"></div>
<div class="row"><button type="button" class="btn small" id="sgAdd">+ Add group</button></div>
<h3>Services</h3>
<div class="field" style="max-width:420px"><label for="svDef">Default service time (min) <span class="muted">(new services start with this; add-ons 0 = inside the main service)</span></label><input class="inp" id="svDef" type="number" min="0" step="5" value="${esc(String(s.svc_default_min ?? 60))}"></div>
<div class="field" style="max-width:420px"><label for="svMin">Main service from $ <span class="muted">(cheaper ones go with a main service, same tech – unless ticked below)</span></label><input class="inp" id="svMin" type="number" min="0" step="1" value="${esc(String(s.main_min ?? 30))}"></div>
<div id="svList"></div>
<div class="row"><button type="button" class="btn" id="svAdd">+ Add service</button><button type="button" class="btn primary" id="svSave">Save services</button></div>
<button type="button" class="linkbtn" id="svHist" style="margin-top:10px">🕘 Price history</button><div id="svHistBox"></div>`;
const groups = (s.svc_groups || []).map(g => ({ ...g, ids: [...(g.ids || [])] }));
const gOf = (x) => groups.findIndex(g => g.ids.includes(x.id) || (x._g !== undefined && g === groups[x._g]));
services.forEach(x => { x._g = groups.findIndex(g => g.ids.includes(x.id)); const inf = (s.svc_info || {})[x.id] || {}; x.desc = inf.d || ''; x.desc_es = inf.d_es || ''; x.addon = inf.addon || ''; x.full = inf.full || ''; x.full_es = inf.full_es || ''; x.fit = inf.fit || ''; x.fit_es = inf.fit_es || ''; });
const quickDef = (n) => { n = String(n || '').toUpperCase(); return ''; /* (hair 1) */ return n.includes('PEDI') ? 'Gel, Paraffin' : n.includes('MANI') && !n.includes('KID') ? 'Gel, Collagen Gloves' : /ACRYL|DIP|POWDER|GEL X/.test(n) ? 'French, Design' : ''; };
const drawGrp = () => {
$('#sgList', b).innerHTML = groups.map((g, i) => `<div class="edit-row sg-row"><input class="sg-ic" value="${esc(g.icon || '')}" data-g="icon" data-i="${i}" maxlength="4" aria-label="Icon">
<input class="nm" value="${esc(g.name)}" data-g="name" data-i="${i}" placeholder="Group name" aria-label="Group name" style="text-transform:uppercase">
<input value="${esc(g.name_es || '')}" data-g="name_es" data-i="${i}" placeholder="Español" aria-label="Spanish name">
<select data-gk="${i}" aria-label="Group kind" hidden style="display:none">${[['hand', 'Hands (Tay)'], ['foot', 'Feet (Chân)'], ['other', 'Other (Khác)']].map(([v, l]) => `<option value="${v}"${(g.kind || 'other') === v ? ' selected' : ''}>${l}</option>`).join('')}</select>
<label class="check sg-hide"><input type="checkbox" data-gh="${i}" ${g.hidden ? 'checked' : ''}><span>Hidden</span></label>
<button type="button" class="icon-btn" data-gup="${i}" aria-label="Move up">↑</button><button type="button" class="icon-btn del" data-grm="${i}" aria-label="Remove group">✕</button>
<input class="sg-note" value="${esc(g.note || '')}" data-g="note" data-i="${i}" placeholder="Small line under the title (optional)" aria-label="Line under the title">
<input class="sg-note" value="${esc(g.quick ?? quickDef(g.name))}" data-g="quick" data-i="${i}" placeholder="Quick add-ons, e.g. Toner, Deep conditioning" aria-label="Quick add-ons" title="Quick add-ons: buttons in &quot;Add another service?&quot; (add-on names, comma between)"></div>`).join('') || '<div class="empty">No groups – the services show in one list.</div>';
$$('#sgList input', b).forEach(inp => inp.addEventListener('input', () => { groups[+inp.dataset.i][inp.dataset.g] = inp.value; if (inp.dataset.g !== 'name_es')
drawSvcGrp(); }));
$$('#sgList [data-gh]', b).forEach(x => x.addEventListener('change', () => { groups[+x.dataset.gh].hidden = x.checked ? 1 : 0; }));
$$('#sgList [data-gk]', b).forEach(x => x.addEventListener('change', () => { groups[+x.dataset.gk].kind = x.value; }));
$$('#sgList [data-gup]', b).forEach(x => x.addEventListener('click', () => { const i = +x.dataset.gup; if (i > 0) {
services.forEach(v => { if (v._g === i)
v._g = i - 1;
else if (v._g === i - 1)
v._g = i; });
[groups[i - 1], groups[i]] = [groups[i], groups[i - 1]];
drawGrp();
drawSvcGrp();
} }));
$$('#sgList [data-grm]', b).forEach(x => x.addEventListener('click', () => { const i = +x.dataset.grm; services.forEach(v => { if (v._g === i)
v._g = -1;
else if (v._g > i)
v._g--; }); groups.splice(i, 1); drawGrp(); drawSvcGrp(); toast('Group removed – its services go to OTHER until you choose a group. Press "Save services".'); }));
};
const drawSvcGrp = () => $$('#svList [data-sg]', b).forEach(sel => { const x = services[+sel.dataset.sg]; sel.innerHTML = `<option value="-1">OTHER (no group)</option>` + groups.map((g, i) => `<option value="${i}"${x._g === i ? ' selected' : ''}>${esc(((g.icon || '') + ' ' + (g.name || '')).trim() || 'Group ' + (i + 1))}</option>`).join(''); if (x._g < 0)
sel.value = '-1'; });
const drawSvc = () => {
$('#svList', b).innerHTML = services.map((x, i) => `<div class="edit-row svc-row">
<input class="nm" value="${esc(x.name)}" data-f="name" data-i="${i}" aria-label="Service name" placeholder="Service name">
<span class="tools"><input type="color" value="${esc(x.color)}" data-f="color" data-i="${i}" aria-label="Color">
<button type="button" class="icon-btn" data-sup="${i}" aria-label="Move up">↑</button>
<button type="button" class="icon-btn del" data-rm="${i}" aria-label="Remove">✕</button></span>
<label class="mini">Min<input type="number" inputmode="numeric" min="0" step="5" value="${x.duration}" data-f="duration" data-i="${i}"></label>
<label class="mini">$<input type="number" inputmode="decimal" min="0" step="0.01" value="${x.price}" data-f="price" data-i="${i}"></label>
<label class="mini" hidden style="display:none">Turn<input type="number" inputmode="decimal" min="0" max="5" step="0.5" value="${x.turn ?? ''}" placeholder="auto" data-f="turn" data-i="${i}" aria-label="Turn value"></label>
<label class="mini">Rebook<input type="number" inputmode="numeric" min="0" max="365" step="1" value="${x.rebook || ''}" placeholder="off" data-f="rebook" data-i="${i}" aria-label="Rebook reminder after days"></label>
<label class="mini">Short<input value="${esc(x.short || '')}" data-f="short" data-i="${i}" maxlength="16" placeholder="auto" style="text-transform:uppercase" aria-label="Short name on the schedule"></label>
<label class="mini es">Español (check-in iPad)<input value="${esc(x.name_es || '')}" data-f="name_es" data-i="${i}" placeholder="optional – empty = English name" aria-label="Spanish name"></label>
<label class="check mini mn"><input type="checkbox" data-mn="${i}" ${mainOf(x) ? 'checked' : ''}><span>Counts as a main service <span class="muted">(its own nail tech; off = goes with the main service, same tech)</span></span></label>
<label class="mini grp">Group<select data-sg="${i}" aria-label="Group"></select></label>
<label class="mini ad">Extra (add-on)<select data-f="addon" data-i="${i}" aria-label="Add-on"><option value="">No – a main service</option><option value="hand"${x.addon === 'hand' ? ' selected' : ''}>Yes – with a hands service</option><option value="foot"${x.addon === 'foot' ? ' selected' : ''}>Yes – with a pedicure</option></select></label>
<label class="mini es">Short description (booking page, 1 line + ⓘ More)<input value="${esc(x.desc || '')}" data-f="desc" data-i="${i}" maxlength="300" placeholder="optional"></label>
<label class="mini es">Description in Español<input value="${esc(x.desc_es || '')}" data-f="desc_es" data-i="${i}" maxlength="300" placeholder="optional"></label>
<label class="mini es">Full description (ⓘ More on the booking page)<textarea rows="3" data-f="full" data-i="${i}" maxlength="3000" placeholder="${esc(mo(x, 'full') || 'optional')}">${esc(x.full || '')}</textarea></label>
<label class="mini es">Full description in Español<textarea rows="3" data-f="full_es" data-i="${i}" maxlength="3000" placeholder="${esc(mo(x, 'full_es') || 'optional')}">${esc(x.full_es || '')}</textarea></label>
<label class="mini es">Who it’s for (ⓘ More)<textarea rows="2" data-f="fit" data-i="${i}" maxlength="600" placeholder="${esc(mo(x, 'fit') || 'optional')}">${esc(x.fit || '')}</textarea></label>
<label class="mini es">Who it’s for – Español<textarea rows="2" data-f="fit_es" data-i="${i}" maxlength="600" placeholder="${esc(mo(x, 'fit_es') || 'optional')}">${esc(x.fit_es || '')}</textarea></label>
${mo(x, 'fit') || mo(x, 'full') ? '<p class="hint mini es" style="margin:0">' + 'Empty box = the starter text shown in grey. Your own words are never replaced.' + '</p>' : ''}
<label class="check mini-chk"><input type="checkbox" data-f="design" data-i="${i}" ${x.design ? 'checked' : ''}><span>Nail design option (1 h 30)</span></label></div>`).join('') || '<div class="empty">No services yet.</div>';
drawSvcGrp();
$$('#svList [data-sg]', b).forEach(sel => sel.addEventListener('change', () => { services[+sel.dataset.sg]._g = +sel.value; }));
$$('#svList textarea[data-f]', b).forEach(t => t.addEventListener('input', () => { services[+t.dataset.i][t.dataset.f] = t.value; }));
$$('#svList select[data-f]', b).forEach(sel => sel.addEventListener('change', () => { services[+sel.dataset.i][sel.dataset.f] = sel.value; }));
$$('#svList input', b).forEach(inp => inp.addEventListener(inp.type === 'checkbox' ? 'change' : 'input', () => { services[+inp.dataset.i][inp.dataset.f] = inp.type === 'checkbox' ? (inp.checked ? 1 : 0) : inp.value; }));
$$('#svList [data-sup]', b).forEach(x => x.addEventListener('click', () => { const i = +x.dataset.sup; if (i > 0) {
[services[i - 1], services[i]] = [services[i], services[i - 1]];
drawSvc();
} }));
$$('#svList [data-rm]', b).forEach(x => x.addEventListener('click', () => {
const i = +x.dataset.rm;
if (x.dataset.sure !== '1') {
x.dataset.sure = '1';
x.textContent = '?';
toast('Tap ✕ again to remove ' + (services[i].name || 'this service'));
return;
}
removedSvc.push(services[i]);
services.splice(i, 1);
drawSvc();
toast('Removed. Press "Save services" to keep this change.');
}));
};
drawGrp();
drawSvc();
$('#sgAdd', b).addEventListener('click', () => { groups.push({ name: '', name_es: '', icon: '', kind: 'other', ids: [] }); drawGrp(); drawSvcGrp(); const all = $$('#sgList .nm', b); all[all.length - 1].focus(); });
$$('#svList [data-mn]', b).forEach(x => x.addEventListener('change', () => { services[+x.dataset.mn]._main = x.checked; }));
$('#svAdd', b).addEventListener('click', () => { services.push({ _g: -1, id: 0, name: '', duration: +(s.svc_default_min ?? 60) || 60, price: 0, color: '#3472B9', turn: '', rebook: '', name_es: '', design: 0, short: '' }); drawSvc(); const all = $$('#svList .nm', b); all[all.length - 1].focus(); });
$('#svHist', b).addEventListener('click', async (e) => {
const bt = e.currentTarget;
bt.hidden = true;
const bx = $('#svHistBox', b);
bx.innerHTML = '<p class="muted">Loading…</p>';
try {
const r = await api('audit', null, { kind: 'price' });
bx.innerHTML = r.rows.length ? `<table class="rp-t"><tr><th>When</th><th>Service</th><th>Old → new</th><th>Who</th></tr>${r.rows.map(x => `<tr><td>${esc(shortDate(x.at.slice(0, 10)))} ${esc(x.at.slice(11, 16))}</td><td>${esc(x.target.replace(/^Service · /, ''))}</td><td>${esc(x.before)} → <b>${esc(x.after)}</b></td><td>${esc(x.who)}</td></tr>`).join('')}</table>` : '<p class="muted">No price changes yet (kept from 2.99.102 on).</p>';
}
catch (er) {
bx.innerHTML = `<p class="err">${esc(er.message)}</p>`;
}
});
$('#svSave', b).addEventListener('click', async () => {
try {
await api('save_services', { services: [...services, ...removedSvc.filter(x => x.id).map(x => ({ id: x.id, remove: true }))] });
{
const mm = { ...(s.svc_main || {}) };
services.forEach(x => { if (x.id && x._main !== undefined) {
if (x._main === mainDef(x))
delete mm[x.id];
else
mm[x.id] = x._main ? 1 : 0;
} });
const mv = +($('#svMin', b)?.value || 30);
await api('save_settings', { svc_main: mm, main_min: mv, svc_default_min: +($('#svDef', b)?.value ?? 60) });
}
const fresh = (await api('settings')).services || [];
const idOf = (x) => x.id || fresh.find(f => f.name.trim().toUpperCase() === String(x.name).trim().toUpperCase())?.id || 0;
const info = {};
services.forEach(x => { const id = idOf(x); if (id && (x.desc || x.desc_es || x.addon || x.full || x.full_es || x.fit || x.fit_es))
info[id] = { d: x.desc || '', d_es: x.desc_es || '', addon: x.addon || '', full: x.full || '', full_es: x.full_es || '', fit: x.fit || '', fit_es: x.fit_es || '' }; });
await api('save_svc_groups', { info, groups: groups.map((g, i) => ({ name: g.name, name_es: g.name_es, icon: g.icon, note: g.note || '', note_es: g.note_es || '', hidden: g.hidden ? 1 : 0, kind: g.kind || 'other', quick: g.quick ?? quickDef(g.name), ids: services.filter(x => x._g === i).map(idOf).filter(Boolean) })) });
saved();
S.day = null;
renderSettings();
}
catch (e) {
oops(e);
}
});
try { svTidy(b, { services, groups, s }); } catch (e) {}
},
techs(b, s) {
window.__skillCats = s.skillCats || [];
const offTxt = (t) => t.offDays.length ? 'Off ' + t.offDays.map(d => WD[d]).join(', ') : 'Works every day';
const skillTxt = (t) => {
if (t.skillAll || !t.skills.length)
return 'All services';
const C = (s.skillCats || []).filter(c => c.ids.length);
const on = C.filter(c => (t.skillCats || []).includes(c.key)).map(c => c.name.charAt(0) + c.name.slice(1).toLowerCase()), some = C.filter(c => !(t.skillCats || []).includes(c.key) && c.ids.some(i => (t.skillPick || []).includes(i))).length;
return on.length || some ? on.join(', ') + (some ? `${on.length ? ' + ' : ''}${some} kind${some > 1 ? 's' : ''} in part` : '') : 'No services';
};
b.innerHTML = `<div class="list" id="stList">${s.staff.map((t, i) => `<div class="item staff-row" data-id="${t.id}">
<button type="button" class="st-phbtn" data-phup="${t.id}" aria-label="${t.photo ? 'Change' : 'Upload'} photo of ${esc(t.name)}">${techAv(t, 'lg')}<span class="st-phcam">📷</span><small>${t.photo ? 'Change' : 'Upload photo'}</small></button><div class="main"><div class="t1">${esc(t.name)} ${t.pushN ? '' : `<button type="button" class="chip warn na-chip" data-alerthelp="${t.id}" style="border:0;font:inherit;font-size:12px;font-weight:700;line-height:1.4;min-height:0;cursor:pointer;vertical-align:middle" title="This tech’s phone gets no YOUR TURN notifications – tap: how to turn them on">🔕 no alerts ›</button> `}${t.hasPin ? '' : t.setupUntil ? '<span class="chip">invite sent</span>' : '<span class="chip warn">no PIN</span>'}${t.online ? '' : ' <span class="chip cancelled">online booking OFF</span>'}</div><div class="t2">${offTxt(t)} · ${skillTxt(t)}${t.online && Object.keys(t.onlineHours || {}).length ? ' · own online hours' : ''}${t.notify ? '' : ' · alerts off'}</div><div class="t2 ta-via">${t.pushN ? `📲 YOUR TURN: app notifications on ${t.pushN} phone${t.pushN === 1 ? '' : 's'}` : '🔔 YOUR TURN: the owner’s NailFlow app is told (tech has not turned on notifications)'}</div></div>
<div class="st-acts">${t.hasPin && !t.pushN ? `<button type="button" class="btn small icon-btn inv-btn setup-btn" data-setup="${t.id}" title="Opens Messages with a 48-hour link to AN Tech + how to turn on notifications (the PIN stays the same)">📲 Send setup link</button>` : ''}<button type="button" class="btn small icon-btn inv-btn" data-inv="${t.id}">${t.hasPin ? 'Reset PIN' : '📲 Send invite'}</button><span class="st-mv"><button type="button" class="icon-btn" data-up="${i}" aria-label="Move up">↑</button><button type="button" class="icon-btn" data-dn="${i}" aria-label="Move down">↓</button></span></div></div>`).join('') || '<div class="empty">No techs yet.</div>'}</div>
<div class="row" style="margin-top:8px"><button type="button" class="btn" id="stAdd">+ Add tech</button>${s.tech_invite ? '<button type="button" class="btn primary" id="stInvite">📲 Invite techs</button>' : ''}</div>
<p class="hint" style="margin-top:10px">Tap a tech to change days off, services, online booking or their PIN. ↑ ↓ changes the order of the columns.</p>
${linkBox('AN Tech – the tech page (each tech logs in with their own PIN, the same PIN as the iPad)', s.staff_url || (location.origin + location.pathname.replace(/admin\/.*$/, '') + 'tech/'))}
<h3>📞 Customer phone numbers on the tech page</h3>
<label class="check"><input type="checkbox" id="stPh" ${s.staff_phone_on ? 'checked' : ''}><span>Techs see the customer's number (📋 Copy · 📞 Call)</span></label>
<p class="hint">Off (default): techs never see customer phone numbers – private.</p>`;
$$('.staff-row', b).forEach(el => el.addEventListener('click', (e) => { if (e.target.closest('.icon-btn'))
return; openStaffEdit(s.staff.find(t => t.id === +el.dataset.id), s.services, s.hours, s.staff); }));
const reorder = async (i, j) => { const ids = s.staff.map(t => t.id); [ids[i], ids[j]] = [ids[j], ids[i]]; try {
await api('staff_order', { ids });
S.day = null;
renderSettings();
}
catch (e) {
oops(e);
} };
$$('[data-inv]', b).forEach(x => x.addEventListener('click', () => sendInvite(s.staff.find(t => t.id === +x.dataset.inv), x.closest('.staff-row'))));
$$('[data-setup]', b).forEach(x => x.addEventListener('click', () => sendSetupLink(s.staff.find(t => t.id === +x.dataset.setup))));
$$('[data-phup]', b).forEach(x => x.addEventListener('click', (e) => {
e.stopPropagation();
const t = s.staff.find(y => y.id === +x.dataset.phup);
if (!t)
return;
staffPhotoPick(t, (p) => { t.photo = p; x.innerHTML = techAv(t, 'lg') + '<span class="st-phcam">📷</span><small>' + (p ? 'Change' : 'Upload photo') + '</small>'; });
}));
$$('[data-alerthelp]', b).forEach(x => x.addEventListener('click', (e) => { e.stopPropagation(); alertHelp(s.staff.find(t => t.id === +x.dataset.alerthelp)); }));
$$('[data-up]', b).forEach(x => x.addEventListener('click', () => { const i = +x.dataset.up; if (i > 0)
reorder(i, i - 1); }));
$$('[data-dn]', b).forEach(x => x.addEventListener('click', () => { const i = +x.dataset.dn; if (i < s.staff.length - 1)
reorder(i, i + 1); }));
$('#stPh', b).addEventListener('change', async (e) => { try {
await api('save_settings', { staff_phone_on: e.target.checked });
saved();
}
catch (x) {
oops(x);
} });
$('#stAdd', b).addEventListener('click', () => openStaffEdit({ id: 0, name: '', offDays: [], skills: [], notify: 1, online: 1, hasPin: false, onlineHours: {} }, s.services, s.hours, s.staff));
$('#stInvite', b)?.addEventListener('click', () => techInvite(s.tech_invite, s.salon_name || ''));
},
customers(b, s) {
b.innerHTML = `<p class="hint">${s.customers} customer${s.customers === 1 ? '' : 's'}. Tap one to see their visits, birthday and notes (color, design, allergies…).</p>
<button type="button" class="btn small" id="cImport" style="margin:0 0 10px">📥 Import from old app</button>
<div id="cDups"></div>
<input class="inp" id="cq" type="search" placeholder="Search name or phone" autocomplete="off"><div class="list" id="cList" style="margin-top:10px"></div>`;
customerSearch(b);
$('#cImport', b).addEventListener('click', openImport);
dupBox($('#cDups', b), () => customerSearch(b));
},
online(b, s) {
b.innerHTML = `<label class="check"><input type="checkbox" id="sOnline" ${s.online_booking ? 'checked' : ''}><span>Customers can book online</span></label>
${linkBox('Booking link for customers', s.booking_url)}
<div class="two"><div class="field"><label for="sNotice">Online and managers: book at least … minutes ahead</label><input id="sNotice" type="number" inputmode="numeric" min="0" max="4320" step="15" value="${s.min_notice_min}"></div>
<div class="field"><label for="sDays">Book at most … days ahead</label><input id="sDays" type="number" inputmode="numeric" min="1" max="180" value="${s.booking_days}"></div></div>
<div class="field"><label for="sBuf">Clean-up time between two customers of the same tech (minutes)</label><input id="sBuf" type="number" inputmode="numeric" min="0" max="60" step="5" value="${s.buffer_min}"></div>
<p class="hint">Customers online see times from now + the minutes above (60 = at 10:05 the first time is 11:15); managers cannot book sooner either. Only you (admin) can book closer to the time. The check-in iPad (walk-ins) is not affected. The other rules here are for online booking only – you and your managers can book back to back.</p>
<div class="field"><label for="sMaxP">Most people in one online booking (the “6+” button)</label><input id="sMaxP" type="number" min="1" max="30" value="${s.max_group}"></div>
<p class="hint">A group bigger than the techs working that day can pick any open time and only “Anyone”; you arrange the techs here in admin. Which techs customers can pick: Nail techs → Online booking ON.</p>
<label class="check"><input type="checkbox" id="sAn" ${s.auto_next !== false ? 'checked' : ''}><span><b>Auto next step</b> – on the booking page: when a step is done, it goes on by itself after 1.5 s ("Next step… · Stay here"). Book now is always tapped.</span></label>
<label class="check"><input type="checkbox" id="sAnA" ${s.auto_next_admin !== false ? 'checked' : ''}><span><b>Auto next step in admin booking</b> – a tech chosen → the customer step (Book is always tapped)</span></label>
<label class="check"><input type="checkbox" id="sAskTm" ${s.book_ask_tm ? 'checked' : ''}><span><b>Ask ‘Same tech / Different tech’</b> – customers with 2+ services choose. Off: one box with the techs who do ALL their services (if any), otherwise a box for each service; “Any tech” is picked already</span></label>
<label class="check"><input type="checkbox" id="sShowPr" ${s.book_show_price ? 'checked' : ''}><span><b>Show prices and times on the booking page</b> – in the service list customers pick from (on by default; off: names only)</span></label>
<div class="field" id="sPrHidBox"><span class="lbl">When prices are hidden, the booking page shows</span><div class="seg" id="sPrHid"><button type="button" data-ph="call" class="${s.book_price_hidden !== 'from' ? 'on' : ''}">“Call for pricing”</button><button type="button" data-ph="from" class="${s.book_price_hidden === 'from' ? 'on' : ''}">“from $X” on each service</button></div></div>
<label class="check"><input type="checkbox" id="sSs" ${s.svc_search ? 'checked' : ''}><span><b>Show service search</b> – a "🔍 Find a service" box in Book (for a menu of more than 50 services)</span></label>
<label class="check"><input type="checkbox" id="sOhOn" ${s.online_hours_on ? 'checked' : ''}><span>Use each tech's online booking hours (set them in Nail techs → a tech). Off: every tech can be booked online during all opening hours.</span></label>
<div class="field"><label for="sPolicy">Cancellation policy (shown to customers)</label><textarea id="sPolicy">${esc(s.cancel_policy)}</textarea></div>
<div class="field"><label for="sFb">Facebook page of the salon (for Google)</label><input class="inp" id="sFb" type="url" inputmode="url" autocomplete="off" spellcheck="false" value="${esc(s.facebook_url || '')}" placeholder="https://www.facebook.com/…"></div>
<p class="hint" style="margin:-4px 0 10px">Google links the salon to this page. Empty = no Facebook link.</p>
<button type="button" class="btn primary block" id="oSave">Save</button>
<h3>🛡 New customers must confirm</h3>
<label class="check"><input type="checkbox" id="ncOn" ${s.noconfirm_on ? 'checked' : ''}><span>A NEW customer who books online gets a Confirm link in the confirmation text</span></label>
<label class="check"><input type="checkbox" id="ncAuto" ${s.nc_autocancel ? 'checked' : ''}${!s.sms_ready && !s.nc_autocancel ? ' disabled' : ''}><span><b>Auto-cancel unconfirmed</b> – off (recommended): the booking stays (yellow ? on the schedule) and you get a notification in the NailFlow app “… hasn't confirmed … – call?”. On: cancelled by itself and a “time released” text card.</span></label>
<p class="hint" style="color:var(--red);margin:-4px 0 10px 30px"><b>Khoá</b> – texts are sent by hand from the iPhone, so the customer never gets an automatic Confirm text.</p>
<div class="two"><div class="field"><label for="ncH">Confirm at the latest … hours before the time</label><input id="ncH" type="number" inputmode="numeric" min="1" max="48" value="${s.confirm_before_h}"></div>
<div class="field"><label for="ncW">Booked closer: … minutes after the text</label><input id="ncW" type="number" inputmode="numeric" min="5" max="240" value="${s.confirm_wait_min}"></div></div>
${tplP('ncTpl', 'Text when the time is released (Send / Skip card)', s.sms_release, '{name} {date} {time} {salon_phone}', 'release')}
<p class="hint">The confirmation card is on Messages → To send as soon as they book. The clock starts when the text is sent. Not confirmed in time: you get a NailFlow app notification to call them and the booking stays (it is cancelled only when YOU tap Cancel). With Auto-cancel on: cancelled by itself, a card to tell the customer, and released twice = Suspicious (must call to book). Returning customers (a visit, the old app, or booked by the salon) never need this.</p>
<button type="button" class="btn primary block" id="ncSave">Save</button>
<h3>⚠ Suspicious numbers (${s.suspects.length})</h3>
<div class="list">${s.suspects.map(c => `<div class="item"><div class="main"><div class="t1">${esc(c.name || '(no name)')}</div><div class="t2">${phL(c.phone)} · ${esc(logWhen(c.at))}</div></div><button type="button" class="btn small" data-uns="${esc(c.phone)}">Clear</button></div>`).join('') || '<div class="empty">None.</div>'}</div>`;
bindTpl(b);
$('#ncSave', b).addEventListener('click', async () => {
try {
await api('save_settings', { noconfirm_on: $('#ncOn', b).checked, nc_autocancel: $('#ncAuto', b).checked, confirm_before_h: +$('#ncH', b).value || 2, confirm_wait_min: +$('#ncW', b).value || 30, sms_release: $('#ncTpl', b).value });
saved();
renderSettings();
}
catch (e) {
oops(e);
}
});
$$('[data-uns]', b).forEach(x => x.addEventListener('click', async () => { try {
await api('customer_suspect', { phone: x.dataset.uns, on: false });
toast('Cleared');
renderSettings();
}
catch (e) {
oops(e);
} }));
$$('#sPrHid [data-ph]', b).forEach(x => x.addEventListener('click', () => $$('#sPrHid [data-ph]', b).forEach(y => y.classList.toggle('on', y === x))));
$('#oSave', b).addEventListener('click', async () => {
const mins = +$('#sNotice', b).value, days = +$('#sDays', b).value, buf = +$('#sBuf', b).value;
if (!(mins >= 0 && mins <= 4320))
return toast('Minutes ahead: 0 to 4320.');
if (!(days >= 1 && days <= 180))
return toast('Days ahead: 1 to 180.');
if (!(buf >= 0 && buf <= 60))
return toast('Clean-up time: 0 to 60 minutes.');
try {
await api('save_settings', { facebook_url: $('#sFb', b).value.trim(), book_show_price: $('#sShowPr', b).checked, book_ask_tm: $('#sAskTm', b).checked, book_price_hidden: $('#sPrHid .on', b)?.dataset.ph || 'call', auto_next: $('#sAn', b).checked, auto_next_admin: $('#sAnA', b).checked, svc_search: $('#sSs', b).checked, online_booking: $('#sOnline', b).checked, booking_days: Math.round(days), min_notice_min: Math.round(mins), buffer_min: Math.round(buf), max_group: +$('#sMaxP', b).value, cancel_policy: $('#sPolicy', b).value, online_hours_on: $('#sOhOn', b).checked });
saved();
S.day = null;
}
catch (e) {
oops(e);
}
});
},
look(b, s) {
const L = s.look || {}, rows = [['admin', 'Admin', 'this owner app'], ['manager', 'Manager', 'the manager page'], ['desk', 'AN Desk', 'the front desk computer']];
b.innerHTML = `<p class="hint">Light or dark for each page, on every device. Each device can still change only itself with the small 🌙 / ☀️ button at the top (hold it → “Use salon setting”).</p>
${rows.map(([k, t, d]) => `<div class="field lk-row"><label id="lkL-${k}"><b>${t}</b> <small class="muted">${d}</small></label><div class="seg" role="radiogroup" aria-labelledby="lkL-${k}" data-lkset="${k}">${[['dark', '🌙 Dark'], ['light', '☀️ Light'], ['auto', 'Auto']].map(([v, l]) => `<button type="button" role="radio" data-v="${v}" aria-checked="${(L[k] || 'dark') === v}" class="${(L[k] || 'dark') === v ? 'on' : ''}">${l}</button>`).join('')}</div></div>`).join('')}
<p class="hint" style="margin-top:4px">Auto = like the device (light by day, dark at night if the iPhone / computer is set to Auto). The customer pages, the check-in iPad, AN Tech and printing stay light.</p>
<button type="button" class="btn primary" id="lkSave">Save</button>`;
$$('[data-lkset]', b).forEach(g => g.addEventListener('click', (e) => { const x = e.target.closest('[data-v]'); if (!x)
return; $$('[data-v]', g).forEach(y => { y.classList.toggle('on', y === x); y.setAttribute('aria-checked', String(y === x)); }); }));
$('#lkSave', b).addEventListener('click', async () => {
const look = {};
$$('[data-lkset]', b).forEach(g => { look[g.dataset.lkset] = ($('[data-v].on', g) || {}).dataset?.v || 'dark'; });
try {
await api('save_settings', { look });
s.look = look;
if (window.LOOK)
LOOK.salon(look[IS_DESK ? 'desk' : IS_MGR ? 'manager' : 'admin']);
saved();
}
catch (e) {
oops(e);
}
});
},
desk(b, s) {
b.innerHTML = `<p class="hint">One iPad at the counter for <b>💳 Checkout · 🕐 Clock in / out · 🎁 Sell gift card</b> – no schedule, Settings, Reports, Customers, Payroll or Close day.
Each checkout and gift card sale asks for the PIN of the person at the desk (you, a manager, or a tech turned on in Settings → Nail techs → “Front desk”); the receipt says who checked out.
Locks itself after 2 minutes without a tap. Void, refund and tip changes stay here (owner).</p>
<p class="hint"><b>Put it on the iPad / tablet:</b> install the <b>NailFlow</b> app → 🖥 Front desk (AN Desk) → sign in once → “Set as front desk” (below). A Windows computer: open the link in its browser. Keep the link private: it has a secret code.</p>
${linkBox('Front desk link', s.desk_url, 'dkUrl')}
<button type="button" class="btn" id="dkNew">Change code (the old link stops working)</button>
<h3 class="set-h">🖥 Front desk devices · Máy quầy</h3>
<p class="hint">iPads / tablets set as <b>Front desk</b> in the NailFlow app: only AN Desk (Checkout · Check-in · Sell gift card · Receipts today · Messages, each person's PIN) – no admin, Settings, money reports or payroll. Leaving it on the device needs <b>your password</b>.
<br><i>Máy quầy: chỉ AN Desk, không vào admin. Thoát trên máy cần mật khẩu chủ. Gỡ = máy đó dừng ngay.</i></p>
<div id="qdList"><p class="muted">Loading…</p></div>
<button type="button" class="btn" id="qdSetHere">🖥 Set THIS device as the front desk · Đặt máy này làm Máy quầy</button>`;
const qdDraw = (l) => {
const w = $('#qdList', b);
if (!w)
return;
w.innerHTML = l.length ? l.map(d => `<div class="row qd-dev"><span><b>${esc(d.name)}</b><br><small class="muted">Set ${esc(d.at)} · last used ${esc(d.last)}</small></span><button type="button" class="btn small danger" data-qdel="${esc(d.id)}">Remove · Gỡ</button></div>`).join('')
: '<p class="muted">No front desk device yet · Chưa có máy quầy.</p>';
$$('[data-qdel]', w).forEach(x => x.addEventListener('click', async () => {
if (x.dataset.sure !== '1') {
x.dataset.sure = '1';
x.textContent = 'Tap again · Bấm lần nữa';
return;
}
try {
const r = await api('qd_dev_del', { id: x.dataset.qdel });
qdDraw(r.devices || []);
toast('Removed – that device stopped · Đã gỡ', 3000);
}
catch (y) {
oops(y);
}
}));
};
api('qd_dev_list').then(r => qdDraw(r.devices || [])).catch(y => { const w = $('#qdList', b); if (w)
w.innerHTML = `<p class="muted">${esc(y.message)}</p>`; });
$('#qdSetHere', b).addEventListener('click', () => qdSetup());
$('#dkNew', b).addEventListener('click', async (e) => {
const x = e.currentTarget;
if (x.dataset.sure !== '1') {
x.dataset.sure = '1';
x.textContent = 'Tap again to change the code';
return;
}
try {
const r = await api('desk_newkey', {});
$('#dkUrl', b).value = r.desk_url;
$('#dkUrlCopy', b).dataset.copy = r.desk_url;
x.dataset.sure = '';
x.textContent = 'Change code (the old link stops working)';
toast('New link made. Open it again on the iPad / computer.', 6000);
}
catch (y) {
oops(y);
}
});
},
checkin(b, s) {
b.innerHTML = `<p class="hint">Customers check themselves in on the front-desk iPad. Open this link on the check-in iPad (it is the customers' screen). Keep the link private: it has a secret code.</p>
${linkBox('Check-in link', s.checkin_url, 'ckUrl')}
<button type="button" class="btn" id="ckNew">Make a new link (the old one stops working)</button>
<label class="check" style="margin:12px 0 4px"><input type="checkbox" id="ckAny" ${s.ck_anytime !== false ? 'checked' : ''}><span><b>Check-in anytime (ignore business hours)</b> – customers can check in on the iPad / phone outside opening hours and on closed days. Off: only from 30 minutes before opening until closing. Voice and YOUR TURN stay quiet outside hours either way.</span></label>
<label class="check" style="margin:4px 0 4px"><input type="checkbox" id="ckUnsure" ${s.ck_unsure_btn ? 'checked' : ''}><span><b>Allow customers to skip / not sure</b> – the orange “Not sure? Ask your nail tech” card and the “Skip” button on the iPad’s service step. Off: every customer must pick at least 1 service (owner / manager can still book “Not decided”).</span></label>
<h3>“Not sure yet – Skip” customers</h3>
<p class="hint" style="margin:0 0 8px">They show in yellow as “❓ Not decided – ask tech”. Tap them to choose the service after asking; Start service needs a service.</p>
<div class="field"><label for="ckUd">Minutes held on the schedule until the tech chooses the service</label>
<div class="row"><input id="ckUd" type="number" inputmode="numeric" min="5" max="180" value="${s.ck_undecided_min || 30}" style="max-width:120px"><button type="button" class="btn primary" id="ckUdSave">Save</button></div></div>`;
$('#ckAny', b).addEventListener('change', async (e) => { try {
await api('save_settings', { ck_anytime: e.target.checked });
saved();
}
catch (x) {
e.target.checked = !e.target.checked;
oops(x);
} });
$('#ckUnsure', b).addEventListener('change', async (e) => { try {
await api('save_settings', { ck_unsure_btn: e.target.checked });
saved();
}
catch (x) {
e.target.checked = !e.target.checked;
oops(x);
} });
$('#ckUdSave', b).addEventListener('click', async () => {
try {
await api('save_settings', { ck_undecided_min: +$('#ckUd', b).value || 30 });
saved();
}
catch (e) {
oops(e);
}
});
$('#ckNew', b).addEventListener('click', async (e) => {
const x = e.currentTarget;
if (x.dataset.sure !== '1') {
x.dataset.sure = '1';
x.textContent = 'Tap again to make a new link';
return;
}
try {
const r = await api('checkin_newkey', {});
$('#ckUrl', b).value = r.checkin_url;
$('#ckUrlCopy', b).dataset.copy = r.checkin_url;
x.dataset.sure = '';
x.textContent = 'Make a new link (the old one stops working)';
toast('New link made. Open it again on the check-in iPad.', 6000);
}
catch (y) {
oops(y);
}
});
},
});
async function techInvite(url, salon) {
let svg = '';
try {
await loadScript('../assets/qrcode.min.js');
const q = qrcode(0, 'M');
q.addData(url);
q.make();
svg = q.createSvgTag({ cellSize: 6, margin: 2, scalable: true });
}
catch (e) { }
openSheet(`${head('📲 Invite techs', esc(salon))}
<div class="ti-qr" role="img" aria-label="QR – invite techs">${svg}</div>
<ol class="ti-steps"><li>The tech opens the NailFlow app (or the phone camera) → I'm a tech → Scan the salon's QR.</li>
<li>The phone remembers this salon – next time only the PIN.</li>
<li>A tech of 2 salons scans both QRs and chooses the salon when the app opens.</li></ol>
${linkBox('Invite link (text it to the tech)', url, 'tiLink')}
<div class="row"><button type="button" class="btn" id="tiCopy">📋 Copy link</button></div>
<p class="hint">Only for your techs: the link opens AN Tech of this salon – each tech still needs their own PIN.</p>`, (sh) => {
$('#tiCopy', sh).addEventListener('click', async () => { try {
await navigator.clipboard.writeText(url);
toast('Copied');
}
catch (e) {
const i = $('#tiLink', sh);
i.select();
} });
});
}


/* (hair 04/11, anh Logan: "làm lại như của nails") copied from nails 2.99.485 – LỆNH 475d (anh Logan 30/10) Settings → Services: short and clear, adding a service easy – THE LOOK ONLY. Every field, the turn / price / rebook / group / Español /
   Hands-Feet / order data and the SAME saves (save_services + save_settings + save_svc_groups – the old "Save services" button, hidden, is what saves) stay as they were.
   On top: a big "+ Add service". The list by GROUP (emoji + name as the title, never cut): each service one row – name · price · minutes; tap → a box with ALL its boxes
   (the old row itself, moved into the box) + Save (this service) + Delete (asked inside the app). "+" at the end of a group = a new service in that group.
   Groups (emoji, name, Español, Hands/Feet/Other, line, quick add-ons, Hidden, ↑, ✕) and the 2 general boxes: under "Edit groups" (closed until tapped). Order: "Sort" → ↑ on each row. */
function svTidy(b, ctx) {
  const { services, groups } = ctx; if (b.dataset.svTidy) return; b.dataset.svTidy = '1'; b.classList.add('sv-tidy');
  const L = (en, vi) => (typeof LV === 'function' ? LV(en, vi) : en), svList = $('#svList', b), save = $('#svSave', b), add = $('#svAdd', b);
  // the old page parts: the hints / the groups / the general boxes go into "Edit groups"; the old list + buttons stay (hidden) – they do the work
  const hints = $$(':scope > p.hint', b), h3 = $$(':scope > h3', b);
  const gbox = document.createElement('div'); gbox.className = 'sv-gbox'; gbox.id = 'svGroups'; gbox.hidden = true;
  const gbtn = document.createElement('button'); gbtn.type = 'button'; gbtn.className = 'btn block sv-gbtn'; gbtn.textContent = '⚙️ ' + L('Edit groups', 'Sửa nhóm');
  const top = document.createElement('div'); top.className = 'sv-top';
  top.innerHTML = `<button type="button" class="btn primary block sv-addbig">+ ${esc(L('Add service', 'Thêm dịch vụ'))}</button>
    <div class="sv-tools"><button type="button" class="btn small" id="svSort">↕ ${esc(L('Sort', 'Sắp xếp'))}</button><button type="button" class="tr-tip sv-i" aria-expanded="false">ⓘ ${esc(L('How turns / rebook work', 'Turn / Rebook là gì'))}</button></div>
    <p class="hint sv-ihint" hidden></p><div id="svView"></div><div class="sv-sortbar" hidden><button type="button" class="btn primary block" id="svSortSave">${esc(L('Save the order', 'Lưu thứ tự'))}</button></div>`;
  b.prepend(top); top.after(gbtn); gbtn.after(gbox);
  if (hints[0]) { $('.sv-ihint', top).textContent = hints[0].textContent; hints[0].remove(); }
  $('.sv-i', top).addEventListener('click', (e) => { const p = $('.sv-ihint', top); p.hidden = !p.hidden; e.currentTarget.setAttribute('aria-expanded', p.hidden ? 'false' : 'true'); });
  [h3[0], hints[1], $('#sgList', b), $('#sgAdd', b)?.closest('.row'), $('#svDef', b)?.closest('.field'), $('#svMin', b)?.closest('.field')].filter(Boolean).forEach(x => gbox.appendChild(x));
  if (hints[1]) { const t = document.createElement('button'); t.type = 'button'; t.className = 'tr-tip'; t.textContent = 'ⓘ ' + L('More', 'Giải thích'); hints[1].hidden = true; hints[1].before(t); t.addEventListener('click', () => { hints[1].hidden = !hints[1].hidden; }); }
  const gsave = document.createElement('button'); gsave.type = 'button'; gsave.className = 'btn primary block'; gsave.textContent = L('Save groups', 'Lưu nhóm'); gbox.appendChild(gsave); gsave.addEventListener('click', () => save.click());
  gbtn.addEventListener('click', () => { gbox.hidden = !gbox.hidden; gbtn.classList.toggle('on', !gbox.hidden); });
  if (h3[1]) h3[1].hidden = true; svList.hidden = true; save.closest('.row').hidden = true;
  // the list, by group
  const money2 = (v) => '$' + (Math.round((+v || 0) * 100) / 100).toFixed(2).replace(/\.00$/, '');
  let sorting = false;
  const draw = () => {
    const order = groups.map((g, gi) => [gi, g]).concat([[-1, { name: L('OTHER', 'KHÁC'), icon: '' }]]);
    $('#svView', top).innerHTML = order.map(([gi, g]) => { const list = services.map((x, i) => [x, i]).filter(([x]) => (x._g ?? -1) === gi); if (gi === -1 && !list.length) return '';
      return `<section class="sv-grp"><h4 class="sv-gt">${esc(((g.icon || '') + ' ' + (g.name || L('Group', 'Nhóm'))).trim())}${g.hidden ? ` <small class="sv-hid">${esc(L('hidden', 'ẩn'))}</small>` : ''}</h4>
        <div class="sv-rows">${list.map(([x, i]) => `<div class="sv-r" data-i="${i}">${sorting ? `<button type="button" class="icon-btn sv-up" data-up="${i}" aria-label="${esc(L('Move up', 'Lên'))}">↑</button>` : ''}<button type="button" class="sv-open" data-open="${i}"><span class="sv-n">${esc(x.name || L('(no name)', '(chưa có tên)'))}${x.active === 0 || x.hidden ? ` <small class="sv-hid">${esc(L('hidden', 'ẩn'))}</small>` : ''}</span><span class="sv-p">${esc(money2(x.price))}</span><span class="sv-m">${esc(String(+x.duration || 0))} ${esc(L('min', 'ph'))}</span><span class="sv-go" aria-hidden="true">›</span></button></div>`).join('')}
        <button type="button" class="sv-plus" data-addg="${gi}">+ ${esc(L('Add to this group', 'Thêm vào nhóm này'))}</button></div></section>`; }).join('') || `<p class="empty">${esc(L('No services yet.', 'Chưa có dịch vụ.'))}</p>`;
    $$('[data-open]', top).forEach(x => x.addEventListener('click', () => edit(+x.dataset.open)));
    $$('[data-addg]', top).forEach(x => x.addEventListener('click', () => addNew(+x.dataset.addg)));
    $$('[data-up]', top).forEach(x => x.addEventListener('click', () => { const r = $(`#svList [data-sup="${x.dataset.up}"]`, b); if (r) { r.click(); draw(); $('.sv-sortbar', top).hidden = false; } }));
  };
  // one service in a box: the old row itself goes in (every box + its listeners); Save = the old Save; closing without Save = nothing kept
  const edit = (i, isNew) => {
    const row = $(`#svList .svc-row:nth-child(${i + 1})`, b) || $$('#svList .svc-row', b)[i]; if (!row) return; const home = document.createComment('svrow'); row.before(home);
    let done = false;
    openSheet(`${head((isNew ? L('New service', 'Dịch vụ mới') : (services[i].name || L('Service', 'Dịch vụ'))))}<div class="sv-edit"></div>
      <div class="sv-foot"><button type="button" class="btn primary block" id="svOne">${esc(L('Save', 'Lưu'))}</button>${isNew ? '' : `<button type="button" class="btn red block" id="svDel">${esc(L('Delete this service', 'Xoá dịch vụ này'))}</button>`}<div id="svAsk"></div></div>`, (sh) => {
      $('.sv-edit', sh).appendChild(row); $('.icon-btn[data-sup]', row)?.setAttribute('hidden', ''); $('.icon-btn[data-rm]', row)?.setAttribute('hidden', '');
      const back = () => { if (home.parentNode) home.replaceWith(row); };
      $('#svOne', sh).addEventListener('click', () => { if (!String(services[i].name || '').trim()) { toast(L('Enter the service name', 'Nhập tên dịch vụ')); return; } done = true; back(); closeSheet(); save.click(); });
      $('#svDel', sh)?.addEventListener('click', () => confirmIn($('#svAsk', sh), L(`Delete ${services[i].name}? Customers can no longer book it.`, `Xoá ${services[i].name}? Khách không đặt được nữa.`), L('Delete', 'Xoá'), async () => {
        done = true; back(); closeSheet(); const rm = $(`#svList [data-rm="${i}"]`, b); if (rm) { rm.click(); $(`#svList [data-rm="${i}"]`, b)?.click(); } save.click(); }, true, L('Go back', 'Quay lại')));
      const shEl = $('#sheet'); const mo = new MutationObserver(() => { if (!shEl.hidden) return; mo.disconnect(); if (!done) { back(); renderSettings(); } }); mo.observe(shEl, { attributes: true, attributeFilter: ['hidden'] });
      const nm = $('input.nm', row); if (isNew && nm) setTimeout(() => nm.focus(), 50);
    });
  };
  const addNew = (gi) => { add.click(); const i = services.length - 1; if (gi >= 0) { services[i]._g = gi; const sel = $(`#svList [data-sg="${i}"]`, b); if (sel) sel.value = String(gi); } edit(i, true); };
  $('.sv-addbig', top).addEventListener('click', () => addNew(-1));
  $('#svSort', top).addEventListener('click', (e) => { sorting = !sorting; e.currentTarget.classList.toggle('on', sorting); draw(); });
  $('#svSortSave', top).addEventListener('click', () => save.click());
  gbox.addEventListener('input', () => draw()); gbox.addEventListener('click', (e) => { if (e.target.closest('[data-gup], [data-grm], #sgAdd')) setTimeout(draw, 0); });
  draw();
}
