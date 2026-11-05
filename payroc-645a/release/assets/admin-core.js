/* (2.99.11) the version this file came with (its ?v=) – compared with the server's on every refresh */
const ADMIN_VER = (() => { try { const own = new URL(document.currentScript.src).searchParams.get('v') || ''; if (!/^m[0-9a-z]+$/.test(own)) return own;
  /* (2.99.413) since 2.99.404 this file's ?v= is its own file time (av()), never the APP_VERSION the server sends (X-NF-Ver) → every page reloaded once at the
     first "safe" moment – even on the sign-in code step. The running version = look.js's ?v= (still APP_VERSION). */
  const s = document.querySelector('script[src*="look.js?v="]'); return s ? new URL(s.src, location.href).searchParams.get('v') || '' : ''; } catch (e) { return ''; } })();
/* Salon Manager – owner app (no libraries). */
'use strict';

/* (2.99.139) screens loaded only when opened (owner pages: Settings, Reports & Payroll, Customers; Front desk). A call before the file is here
   loads it once (cached with ?v=) and then runs the real function. */
const LAZY_BASE = (() => { try { return new URL('admin/', document.currentScript.src).href; } catch (e) { return '../assets/admin/'; } })();
const LAZY_P = {};
const LAZY_FILES = { settings: ['settings', 'settings-salon', 'settings-texts', 'turn-early', 'settings-pay', 'turn-half', 'turn-easy', 'setup-link', 'turn-ex', 'nf-only', 'dejavoo-hq' /* (2.99.638b) */, 'payroc-hq' /* (2.99.645a) */, 'push-tech', 'settings-promo', 'settings-staff', 'settings-apps', 'settings-asend', 'settings-colors'], reports: ['reports', 'reports-pay', 'pay-text'] }; // (2.99.206 – order 407) a screen in several files (≤ ~60 KB each), loaded in this order
/* (2.99.214 – order 418) a screen's own CSS (assets/admin-lazy-<screen>.css, tools/css-split418.py) comes with its JavaScript: placed right after
   admin-checkout.css (before the dark layer / admin-popups.css – the same order as before), the screen opens when both are loaded */
const LAZY_CSS = { settings: 'admin-lazy-settings', reports: 'admin-lazy-reports', customers: 'admin-lazy-customers' };
function lazyCss(m) {
  const n = LAZY_CSS[m]; if (!n || document.querySelector(`link[data-lazycss="${n}"]`)) return null;
  const l = document.createElement('link'); l.rel = 'stylesheet'; l.setAttribute('data-lazycss', n); l.href = new URL('../' + n + '.css?v=' + encodeURIComponent(ADMIN_VER), LAZY_BASE).href;
  const pos = document.querySelector('link[data-dkcss]') || document.querySelector('link[href*="admin-popups"]');
  if (pos && pos.parentNode) pos.parentNode.insertBefore(l, pos); else document.head.appendChild(l);
  return l;
}
function lazyMod(m) {
  if (!LAZY_P[m]) LAZY_P[m] = new Promise((ok, no) => { const fs = LAZY_FILES[m] || [m]; let n = 0, bad = false;
    const css = lazyCss(m); const want = fs.length + (css ? 1 : 0); if (css) { css.onload = () => { if (++n === want && !bad) ok(); }; css.onerror = () => { if (++n === want && !bad) ok(); }; } // a CSS that fails: the screen still opens
    fs.forEach((f) => { const s = document.createElement('script'); s.src = LAZY_BASE + f + '.js?v=' + encodeURIComponent(ADMIN_VER); s.async = false;
      s.onload = () => { if (++n === want && !bad) ok(); }; s.onerror = () => { if (bad) return; bad = true; delete LAZY_P[m]; no(new Error('Could not load this screen – check the internet and try again.')); }; document.head.appendChild(s); }); });
  return LAZY_P[m];
}
const lazyCall = (m, name, stub, args) => lazyMod(m).then(() => { const f = window[name]; if (typeof f !== 'function' || f === stub) throw new Error('Screen ' + m + ' did not load (' + name + ')'); return f(...args); });
function customerSearch(...a) { return lazyCall('customers', 'customerSearch', customerSearch, a); }
function dkBoot(...a) { return lazyCall('desk', 'dkBoot', dkBoot, a); }
function dkClosed(...a) { return lazyCall('desk', 'dkClosed', dkClosed, a); }
function dkLock(...a) { return lazyCall('desk', 'dkLock', dkLock, a); }
function dkReloadList(...a) { return lazyCall('desk', 'dkReloadList', dkReloadList, a); }
function dupBox(...a) { return lazyCall('customers', 'dupBox', dupBox, a); }
function openCustomer(...a) { return lazyCall('customers', 'openCustomer', openCustomer, a); }
function openImport(...a) { return lazyCall('customers', 'openImport', openImport, a); }
function openPayTech(...a) { return lazyCall('reports', 'openPayTech', openPayTech, a); }
function payslipsHTML(...a) { return lazyCall('reports', 'payslipsHTML', payslipsHTML, a); }
function renderHistory(...a) { return lazyCall('reports', 'renderHistory', renderHistory, a); }
function renderSettings(...a) { // Home (owner + manager) is drawn without loading the Settings screens – the same as renderSettings() does for Home
  if (!S.setSec && (S.home !== 'settings' || IS_MGR)) { S.setSec = null; S.home = null; const p = $('#p-settings'); p.innerHTML = homeHTML(); bindHs(p); return Promise.resolve(); }
  return lazyCall('settings', 'renderSettings', renderSettings, a); }
function showApptLog(...a) { return lazyCall('settings', 'showApptLog', showApptLog, a); }


/* 2.40 keyboard: it goes away by itself when the typing is done – a full phone number (10 digits), a full gift card code (12, then "Use"),
   Return / ✓ / Done on a number box, or a tap on an empty spot of the screen. Only blur(): nothing typed is ever lost. */
(() => {
  const typing = (a) => a && (a.tagName === 'TEXTAREA' || (a.tagName === 'INPUT' && !/^(checkbox|radio|button|submit|range|color|file)$/.test(a.type)));
  let tapAt = 0;
  window.kbTapAt = () => tapAt;
  document.addEventListener('pointerdown', (e) => {
    const a = document.activeElement; if (!typing(a)) return;
    if (e.target !== a) tapAt = Date.now(); // a tap somewhere else while typing (the box loses the keyboard because of the tap, not ✓ / Done)
    if (e.target.closest('input,textarea,select,button,a,label,[role="button"],[contenteditable],.seg,.pay-chips,.svc-chips')) return;
    a.blur(); // an empty spot: keyboard away
  }, true);
  document.addEventListener('focusin', (e) => { const el = e.target; if (el.tagName === 'INPUT' && (el.type === 'number' || el.inputMode === 'decimal') && !el.hasAttribute('enterkeyhint')) el.setAttribute('enterkeyhint', 'done'); });
  document.addEventListener('keydown', (e) => {
    const el = e.target;
    if (e.key === 'Enter' && el.tagName === 'INPUT' && (el.type === 'number' || el.inputMode === 'decimal')) { e.preventDefault(); el.blur(); }
  }, true);
  document.addEventListener('input', (e) => {
    const el = e.target; if (el.tagName !== 'INPUT') return;
    if (el.type === 'tel') { const d = el.value.replace(/\D/g, ''); if (d.length === 10 || (d.length === 11 && d[0] === '1')) setTimeout(() => { if (document.activeElement === el) el.blur(); }, 30); }
    if (el.hasAttribute('data-code12') && el.value.replace(/[^A-Za-z0-9]/g, '').length === 12) {
      setTimeout(() => { el.blur(); const go = el.closest('.linkbox')?.querySelector('button:last-of-type'); if (go) go.click(); }, 30); // full code: look it up (the last button: Use / Find – not 📷 Scan)
    }
  }, true);
})();

const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const money = (n) => '$' + (Math.round((+n || 0) * 100) / 100).toFixed(2);
const pad = (n) => String(n).padStart(2, '0');
const MON = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
const MONF = ['JANUARY','FEBRUARY','MARCH','APRIL','MAY','JUNE','JULY','AUGUST','SEPTEMBER','OCTOBER','NOVEMBER','DECEMBER'];
const WD = ['SUN','MON','TUE','WED','THU','FRI','SAT'];
const WDL = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
const DURS = [[15,'15 Min'],[30,'30 Min'],[45,'45 Min'],[60,'1 Hour'],[75,'1 Hour 15'],[90,'1 Hour 30'],[105,'1 Hour 45'],[120,'2 Hour'],[150,'2 Hour 30'],[180,'3 Hour'],[300,'5 Hour']];

const S = { csrf: null, date: null, today: null, day: null, tab: 'appts', lastEvent: 0, lastTap: null, thread: null };
/* The same app runs the manager page (/manager/): Appointments only – no money, settings, customer list, Messages or deleting. */
const IS_MGR = document.documentElement.dataset.app === 'manager';
/** (2.99.425 – anh Logan 26/10 17:19) English OR Vietnamese – never both on one screen: the owner's language choice (Settings → Language). */
const LV = (en, vi) => ((window.I18N && window.I18N.lang() === 'vi') ? vi : en);
/* (2.99.89) the Front desk iPad (/desk/?k=…): Checkout · Clock in / out · Sell gift card – the person at the desk types their PIN each time */
const IS_DESK = document.documentElement.dataset.app === 'desk';
const DESK_K = IS_DESK ? (document.documentElement.dataset.k || '') : '';
/* (2.99.311 – lệnh 19/10 13:43) INSIDE THE NAILFLOW APP: say so on EVERY request (X-NF-App) and set the app cookie at once – BEFORE boot()'s first call.
   Before, only native.js set the cookie, AFTER boot() had already asked 'me': when the phone's web view had lost its cookies the server took the owner
   for a browser (12-hour idle limit, no app key given at sign-in) → "Owner sign in" again. X-NF-Dev = this phone's own random id (its app key is
   replaced only by a new sign-in on the SAME phone – a 2nd iPhone no longer removes the first one's key). */
const NF_APP = (() => { try { return !!(window.Capacitor && Capacitor.isNativePlatform && Capacitor.isNativePlatform()); } catch (e) { return false; } })();
const NF_DEV = (() => { if (!NF_APP) return ''; try { let d = localStorage.getItem('nfDev'); if (!/^[a-f0-9]{16}$/.test(d || '')) { d = [...crypto.getRandomValues(new Uint8Array(8))].map(b => b.toString(16).padStart(2, '0')).join(''); localStorage.setItem('nfDev', d); } return d; } catch (e) { return ''; } })();
if (NF_APP) { try { document.cookie = 'nfapp=1; path=/; max-age=34560000; samesite=lax' + (location.protocol === 'https:' ? '; secure' : ''); } catch (e) {} }
/* The manager page's private link (?k=…, when the owner made one): kept in the address – so Add to Home Screen keeps it – and remembered here. */
const MGR_K = (() => { if (!IS_MGR) return ''; const k = new URLSearchParams(location.search).get('k') || ''; try { if (k) localStorage.setItem('mgrK', k); return k || localStorage.getItem('mgrK') || ''; } catch (e) { return k; } })();
/** Background refreshes (not a person using the app): a manager is logged out after 12 hours without using it. */
const auto = (fn) => { S.auto = true; try { return fn(); } finally { S.auto = false; } };

/* ---------- dates, times, phones ---------- */
const parseD = (s) => { const [y, m, d] = s.split('-').map(Number); return new Date(y, m - 1, d); };
const fmtD = (d) => d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate());
const addDays = (s, n) => { const d = parseD(s); d.setDate(d.getDate() + n); return fmtD(d); };
const titleD = (s) => { const d = parseD(s); return MON[d.getMonth()] + '-' + pad(d.getDate()) + '-' + String(d.getFullYear()).slice(2); };
const longD = (s) => { const d = parseD(s); return WDL[d.getDay()] + ', ' + MON[d.getMonth()] + ' ' + d.getDate(); };
const tlabel = (m) => { const h = Math.floor(m / 60), mm = m % 60; return ((h % 12) || 12) + ':' + pad(mm) + (h >= 12 ? ' PM' : ' AM'); };
const localToday = () => { try { return new Date().toLocaleString('sv-SE', { timeZone: 'America/Chicago' }).slice(0, 10); } catch (e) { return fmtD(new Date()); } }; // (2.99.100) the salon's day (Chicago), not the phone's
const digits = (p) => { let d = String(p || '').replace(/\D/g, ''); if (d.length === 11 && d[0] === '1') d = d.slice(1); return d; };
const prettyPhone = (p) => { const d = digits(p); return d.length === 10 ? `(${d.slice(0, 3)}) ${d.slice(3, 6)}-${d.slice(6)}` : (p || ''); };
const bdayLabel = (b) => { if (!b) return ""; const [m, d] = b.split("-").map(Number); return d ? MON[m - 1] + " " + d : ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"][m - 1] + " (day not given)"; }; // (2.64) month only: "March"

/* (2.99.282 – order 495) A new version on the server (APP_VERSION ≠ the one running here): the NailFlow app (iPhone / Android), AN Desk and Safari load it
   by themselves at a SAFE moment – the app opened again (back from the background) or back on the main screen (a sheet closed) – never while Checkout,
   a popup or the tip screen is open, never while typing; AN Desk only on its lock (PIN) screen. Once per version (no reload loop). Nobody closes the app. */
const NFV = { srv: '' };
function nfVerSeen(v) { if (v && ADMIN_VER && v !== ADMIN_VER) { NFV.srv = v; setTimeout(nfMaybeReload, 300); } }
function nfSafe() {
  if (document.visibilityState !== 'visible') return false;
  const sh = document.getElementById('sheet'); if (sh && !sh.hidden) return false; // Checkout / a sheet is open
  if (document.querySelector('.gs-ov, .ck-svc, .ck-pop, [role="dialog"]:not([hidden]), body.tip-open, body.gs-open')) return false;
  const a = document.activeElement; if (a && a !== document.body && a.matches && a.matches('input, textarea, select, [contenteditable="true"]')) return false; // typing
  if (typeof IS_DESK !== 'undefined' && IS_DESK && typeof DK !== 'undefined' && DK.who) return false; // AN Desk: only when locked
  return true;
}
function nfMaybeReload() {
  if (!NFV.srv || NFV.srv === ADMIN_VER || !nfSafe()) return;
  let k = ''; try { k = sessionStorage.getItem('nfReload') || ''; } catch (e) {} if (k === NFV.srv) return;
  try { sessionStorage.setItem('nfReload', NFV.srv); sessionStorage.setItem('nfBackTab', JSON.stringify({ t: S.tab || '', at: Date.now() })); } catch (e) {} location.reload(); /* (2.99.530) remember the page: the new version opens on it again (not Appointments) */
}
async function nfVerCheck() { try { const r = await fetch('../api.php?action=nf_ver&t=' + Date.now(), { cache: 'no-store', credentials: 'same-origin' }); const d = await r.json(); nfVerSeen(String(d.v || '')); } catch (e) {} }
document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible') nfVerCheck(); }); // the app opened again
window.addEventListener('pageshow', (e) => { if (e.persisted) nfVerCheck(); }); // Safari back-forward cache
document.addEventListener('focusout', () => { if (NFV.srv) setTimeout(nfMaybeReload, 1500); }); // done typing on the main screen
setInterval(() => { if (NFV.srv) nfMaybeReload(); else if (document.visibilityState === 'visible') nfVerCheck(); }, 300000); // AN Desk left open all day: every 5 min

/* ---------- API ---------- */
/** (2.99.501 – LỆNH 477e GẤP, anh Logan 30/10) one request failed (cancelled by the phone, a moment of Wi-Fi…): the red 'No internet' bar shows ONLY when the
 *  phone says offline, or a tiny ping (chg.php: no login, no database) gets no answer twice (4 s each, 1.5 s apart). A ping that answers = the internet is there → no bar. */
function netCheck() {
  if (!window.NetBar) return; if (navigator.onLine === false) { NetBar.fail(); return; } if (netCheck.busy) return; netCheck.busy = true;
  const ping = () => { const ac = typeof AbortController !== 'undefined' ? new AbortController() : null, t = ac ? setTimeout(() => ac.abort(), 4000) : 0;
    return fetch('../chg.php?ping=1&t=' + Date.now(), { credentials: 'omit', cache: 'no-store', signal: ac ? ac.signal : undefined }).finally(() => clearTimeout(t)); };
  ping().catch(() => new Promise(r => setTimeout(r, 1500)).then(ping)).then(() => NetBar.ok(), () => NetBar.fail()).finally(() => { netCheck.busy = false; });
}
async function api(action, body, params, keepalive) { // keepalive: still sent when the Messages app opens right after
  const qs = new URLSearchParams({ action, ...(params || {}) });
  const opt = { method: body ? 'POST' : 'GET', headers: {}, credentials: 'same-origin', keepalive: !!keepalive, cache: 'no-cache' }; // (2.99.201 – order 401) never an old answer from the phone's cache (always asks; a 304 still saves the bytes)
  if (body instanceof FormData) opt.body = body; // pictures: sent as files (the server refuses a JSON body over 1 MB)
  else if (body) { opt.headers['Content-Type'] = 'application/json'; opt.body = JSON.stringify(body); }
  if (S.csrf) opt.headers['X-CSRF'] = S.csrf;
  if (IS_MGR) opt.headers['X-Role'] = 'manager'; // the owner opening this page sees exactly what a manager sees
  if (IS_DESK) { opt.headers['X-Desk'] = DESK_K; opt.headers['X-Lang'] = DK.lang; } // (2.99.89) only the person who typed the PIN, only Checkout / gift cards
  if (S.auto) opt.headers['X-Auto'] = '1';
  if (NF_APP) { opt.headers['X-NF-App'] = '1'; if (NF_DEV) opt.headers['X-NF-Dev'] = NF_DEV; } // (2.99.311) the NailFlow app – even when its cookie is lost
  let res, data;
  // (2.99.95) no internet: never a silent wait – after 30 s (not for big jobs) it stops and says clearly it was NOT saved; the red bar shows
  const ac = !keepalive && typeof AbortController !== 'undefined' && !/backup|import|export|yearend|report|logo|gallery|photo/i.test(action) ? new AbortController() : null;
  const tmo = ac ? setTimeout(() => ac.abort(), 30000) : 0; if (ac) opt.signal = ac.signal;
  try { res = await fetch('../api.php?' + qs, opt); } catch (e) { clearTimeout(tmo); netCheck(); /* (2.99.501 – LỆNH 477e) the red bar only when the internet is really gone (was: on any failed request) */
    const net = (m) => Object.assign(new Error(m), { net: true }); // (2.99.241 – order 439) no answer from the server: a "texted" mark is tried again later
    if (body && e && e.name === 'AbortError') throw net('May not have saved – check before entering again (no answer in 30 seconds).'); // (2.99.100) sent, no answer: it may have saved
    if (body && navigator.onLine !== false) throw net('May not have saved – check before entering again (the connection was lost).'); // (2.99.100) it may have reached the server
    throw net(body ? 'NOT saved – no internet. Write it on paper and enter it when the internet is back.' : 'No internet – check the Wi-Fi and try again.'); }
  clearTimeout(tmo); if (window.NetBar) NetBar.ok();
  try { const sv = res.headers.get('X-NF-Ver'); if (sv) nfVerSeen(sv); } catch (e) {} // (2.99.282 – order 495)
  try { data = await res.json(); } catch (e) { throw Object.assign(new Error('The server had a problem (' + res.status + '). Wait a moment and try again.'), { net: true }); } // (2.99.69) a server problem is not "no internet""
  if (IS_DESK && res.status === 401 && action !== 'desk_unlock' && action !== 'ck_clock') { dkLock(); throw new Error(data.error || 'Please type your PIN again.'); } // (2.99.89) 2 minutes without a tap: locked
  if (res.status === 401 && !IS_DESK && action !== 'login' && action !== 'mgr_login' && action !== 'login_2fa') { showLogin(); throw Object.assign(new Error('Please log in.'), { net: true }); } // (2.99.413) a wrong sign-in code: stay on the code step (its message says why)
  if (res.status === 428 && data.need2fa && body && !(body instanceof FormData)) { // (2.99.257 – order 466) asked again even on a trusted device: the Authenticator code, then the same request
    const c = await ask2fa(data.error); if (!c) throw new Error('Not done – the Authenticator code is needed.'); return api(action, Object.assign({}, body, { code2fa: c }), params, keepalive); }
  if (!res.ok || data.error) throw new Error(data.error || ('Error ' + res.status));
  if (data && data.asNow === 'android' && !IS_MGR && !IS_DESK) setTimeout(() => toast('📲 Sending by Android…', 3000, null, true), 60); /* (2.99.225) Android: only a small line (2.99.305: the iPhone "📲 Send now" box removed) */ // (2.99.204 – order 402)
  if (data && (data.auto || data.asNow) && action !== 'autosend_kick') setTimeout(() => api('autosend_kick', {}).catch(() => {}), 4000); // (2.99.210 – order 414) a text waits for Auto send: ask once more – the email goes even if the host cut the work after the answer
  if (action === 'day' && data && data.turnBar && window.TVO && !IS_DESK && data.date === data.today) { try { TVO.fromBar(IS_MGR || !data.turnBar.voice ? data.turnBar : { ...data.turnBar, voice: { ...data.turnBar.voice, desk: data.turnBar.voice.owner === true } } /* (2.99.465 – LỆNH 465) the owner's admin reads only with Settings → Turn → 🔊 Read tech calls aloud on this admin (OFF by default) */, { canAccept: true, api: (a, b) => api(a, b), done: () => { try { if (typeof refreshCurrent === 'function') refreshCurrent(); } catch (e) {} } }); } catch (e) {} } // (2.99.256 – order 467) the desk reads out + "Accept for LOGAN"
  return data;
}
/** (2.45) A phone number to tap: 📋 Copy · 📞 Call · 💬 Text (press and hold = Copy); copies 10 digits. */
const phL = (p) => window.PhoneUI ? PhoneUI.link(p) : esc(prettyPhone(p));
if (window.PhoneUI) PhoneUI.setup({ text: IS_MGR || IS_DESK ? null : (p) => { try { closeSheet(); } catch (e) {} openText({ phone: p }); } }); // managers: Copy + Call (texting a number is owner only)
function toast(msg, ms = 2800, action, low) {
  const t = $('#toast'); t.textContent = msg; t.hidden = false; t.classList.toggle('low', !!low); // low: at the bottom (2.50 "✓ Sent to …")
  if (action) {
    const b = document.createElement('button'); b.type = 'button'; b.className = 'toast-act'; b.textContent = action.label;
    b.addEventListener('click', () => { t.hidden = true; action.run(); }); t.appendChild(b);
  }
  clearTimeout(toast._t); toast._t = setTimeout(() => { t.hidden = true; }, ms);
}
const oops = (e) => toast(e.message || String(e), 4500);

let actx = null;
function beep() {
  try {
    actx = actx || new (window.AudioContext || window.webkitAudioContext)();
    [0, 0.16].forEach((t, i) => {
      const o = actx.createOscillator(), g = actx.createGain(); o.frequency.value = i ? 1320 : 990;
      g.gain.setValueAtTime(0.18, actx.currentTime + t); g.gain.exponentialRampToValueAtTime(0.001, actx.currentTime + t + 0.3);
      o.connect(g).connect(actx.destination); o.start(actx.currentTime + t); o.stop(actx.currentTime + t + 0.3);
    });
  } catch (e) {}
}
document.addEventListener('touchstart', () => { try { actx = actx || new (window.AudioContext || window.webkitAudioContext)(); actx.resume(); } catch (e) {} }, { once: true, passive: true });

/** (2.99.257 – order 466) A small box: "6-digit code from the Authenticator app" → the code ('' = cancelled). Never kept anywhere. */
function ask2fa(msg) {
  return new Promise((done) => { const ov = document.createElement('div'); ov.className = 'ask2fa';
    ov.innerHTML = `<form class="ask2fa-in" novalidate><b>🔐 ${esc(msg || 'Type the 6-digit code from the Authenticator app.')}</b><input inputmode="numeric" autocomplete="one-time-code" maxlength="11" placeholder="123456" aria-label="Authenticator code"><div class="row"><button type="button" class="btn" data-x>Cancel</button><button type="submit" class="btn primary">OK</button></div></form>`;
    document.body.appendChild(ov); const ip = ov.querySelector('input'); setTimeout(() => ip.focus(), 50);
    const end = (v) => { ov.remove(); done(v); };
    ov.querySelector('[data-x]').addEventListener('click', () => end(''));
    ov.querySelector('form').addEventListener('submit', (e) => { e.preventDefault(); const v = ip.value.replace(/\s+/g, ''); if (v.length >= 6) end(v); }); });
}
/* ---------- login ---------- */
/** The 2nd step of the owner sign-in (Authenticator code) – after the password, or after the one owner link (…/app/, 2.99.224). */
function loginCodeStep(days) { const box = $('#loginCodeBox'); if (!box) return; box.hidden = false;
  const r = (days && typeof days === 'object') ? days : null; if (r) days = r.trustDays || 0; else if (days === true) days = 0; /* (2.99.396) the code by text: the answer of login / app_login */
  const sms = !!(r && r.via === 'sms'), lbl = $('#loginCodeLbl'), hint = $('#loginCodeHint'), sb = $('#loginSms'); S.codeSms = sms; // (2.99.413)
  if (lbl) lbl.textContent = sms ? LV(`6-digit code texted to ${r.sms || 'the owner cell'}`, `Mã 6 số đã nhắn tới ${r.sms || 'số chủ tiệm'}`) : LV('6-digit code from the Authenticator app', 'Mã 6 số từ app Authenticator');
  if (hint) { hint.hidden = sms && !r.smsErr; hint.textContent = sms ? (r.smsErr || '') : 'Lost the phone? Type one of your recovery codes.'; }
  if (sb) { sb.hidden = !(r && r.sms); sb.textContent = sms ? LV('📲 Text a new code', '📲 Gửi lại mã') : LV('📲 Text me a code instead', '📲 Gửi mã qua tin nhắn'); }
  const tr = $('#loginTrust'); if (tr) { tr.hidden = !(days > 0); const t = tr.querySelector('span'); if (t && days) t.textContent = `Trust this device – no code here for ${days} days · Tin máy này`; } /* (2.99.257 – order 466) */ $('#loginPass').closest('form').querySelector('[for=loginPass]').hidden = true; $('#loginPass').hidden = true; $('#loginPass').required = false; setTimeout(() => $('#loginCode').focus(), 50); }
function showLogin() {
  if (IS_MGR) { stopTimers(); closeSheet(); return showMgrLogin(); }
  // (2.99.317 – lệnh 541) inside the NailFlow app the owner never sees this old "password only" page: back to the app's own screen (/app/ – the salons kept on
  // this phone → Face ID, or email + password + Authenticator); ?out=1 = do not jump straight back in here. A browser (computer, AN Desk) keeps this page.
  if (NF_APP && !window.__nfCode) { const hub = (document.body && document.body.dataset.hub) || '/app/'; location.replace(hub + (hub.includes('?') ? '&' : '?') + 'role=owner&out=' + (window.__nfOut ? '1' : '2')); return; } // out=1 logged out (stays off), out=2 the session ended (this time only)
  if (NF_APP && window.__nfCode) { const h = $('#loginForm h2'); if (h) h.textContent = 'NailFlow · Mã xác minh'; const f = $('#loginForgot'); if (f) f.hidden = true; } // (2.99.318 – 541) the app's sign-in, step 2 only
  $('#login').hidden = false; setTimeout(() => $('#loginPass').focus(), 50);
}
$('#loginForm')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const err = $('#loginErr'); err.hidden = true; err.classList.remove('ok');
  try {
    const box = $('#loginCodeBox'), step2 = box && !box.hidden; // 2-step sign-in: the password first, then the Authenticator code
    const r = step2 ? await api('login_2fa', { code: $('#loginCode').value, trust: !!($('#loginTrustCb') && $('#loginTrustCb').checked && !$('#loginTrust').hidden) }) : await api('login', { password: $('#loginPass').value });
    if (r.need2fa) return loginCodeStep(r);
    if (r.appTok && window.NFNative && NFNative.keep) await NFNative.keep(r.appTok, 'admin'); // (2.99.259 – order 469) in the app: stay signed in
    S.csrf = r.csrf; $('#loginPass').value = ''; if (box) { box.hidden = true; $('#loginCode').value = ''; $('#loginPass').hidden = false; $('#loginPass').required = true; $('[for=loginPass]').hidden = false; } $('#login').hidden = true; boot();
  } catch (x) { err.textContent = S.codeSms && /^Wrong code/.test(x.message) ? 'Wrong code. Type the 6 digits we texted. · Sai mã.' : x.message; err.hidden = false; // (2.99.413) the code by text: never "Authenticator"
    if (/password again/i.test(x.message)) { const bx = $('#loginCodeBox'); if (bx) { bx.hidden = true; $('#loginCode').value = ''; } $('#loginPass').hidden = false; $('#loginPass').required = true; const lb = $('[for=loginPass]'); if (lb) lb.hidden = false; setTimeout(() => $('#loginPass').focus(), 50); } } // (2.99.421) the 10 minutes ran out: back to the password step
});
/* (2.99.120) a manager session in this browser (e.g. the Pushover "Open the day report" link opened in Safari): log the manager out here and
   log in as the owner on the same page – the address (?tab=day&date=…) stays, so after the owner's log-in that day's report opens */
$('#loginMgrOut')?.addEventListener('click', async (e) => { const b = e.currentTarget; b.disabled = true;
  try { await api('mgr_logout', {}); $('#loginMgr').hidden = true; b.hidden = true; const err = $('#loginErr'); err.textContent = 'Manager logged out. Type the owner password.'; err.classList.add('ok'); err.hidden = false; setTimeout(() => $('#loginPass').focus(), 50); }
  catch (x) { toast(x.message, 5000); }
  b.disabled = false; });
/* (2.99.276 – order 487) "Forgot password?": nothing is sent – only NailFlow's support number (NailFlow makes a one-time link in AN HQ) */
$('#loginSms')?.addEventListener('click', async (e) => { const b = e.currentTarget, err = $('#loginErr'); err.hidden = true; b.disabled = true;
  try { const r = await api('login_sms', {}); err.textContent = LV('Code texted to ' + (r.to || 'the owner cell'), 'Đã nhắn mã tới ' + (r.to || 'số chủ tiệm')); err.classList.add('ok'); const l = $('#loginCodeLbl'); if (l) l.textContent = LV(`6-digit code (Authenticator or texted to ${r.to || 'the owner cell'})`, `Mã 6 số (Authenticator hoặc tin nhắn tới ${r.to || 'số chủ tiệm'})`); setTimeout(() => $('#loginCode').focus(), 50); }
  catch (x) { err.textContent = x.message; err.classList.remove('ok'); }
  err.hidden = false; setTimeout(() => { b.disabled = false; }, 30000); });
/* (2.99.276 – order 487) "Forgot password?": nothing is sent – only NailFlow's support number (NailFlow makes a one-time link in AN HQ) */
$('#loginForgot')?.addEventListener('click', async (e) => { const b = e.currentTarget, err = $('#loginErr'); err.hidden = true; b.disabled = true;
  try { const r = await api('admin_forgot', {}); err.textContent = LV('Contact NailFlow to reset your password: ', 'Liên hệ NailFlow để đặt lại mật khẩu: ') + (r.contact || '(515) 672-7879'); err.classList.add('ok'); }
  catch (x) { err.textContent = x.message; err.classList.remove('ok'); }
  err.hidden = false; b.disabled = false; });
/* Manager login (/manager/): tap your name, type your PIN. */
async function showMgrLogin() {
  /* (2.99.343 – lệnh 576) the NailFlow app opened again (or the session ended): this phone's manager key signs the manager back in (Face ID first when
     the salon's "Lock the app with Face ID" is on – native.js); no key / not accepted → the names + PIN below, as before */
  if (NF_APP && !S.mgrTried && window.NFNative && NFNative.resume) { S.mgrTried = true; if (await NFNative.resume('mgr')) return boot(); }
  $('#login').hidden = false;
  const oa = $('#mgrOpenApp'); if (oa && !NF_APP && /iPhone|iPad|iPod|Android/.test(navigator.userAgent)) { oa.href = 'nailflow://open?u=' + encodeURIComponent(location.href); oa.hidden = false; oa.style.display = 'block'; } // (2.99.343 – lệnh 576) a phone browser: open this page in the NailFlow app
  let r; try { r = await api('mgr_names', null, MGR_K ? { k: MGR_K } : null); } catch (e) { r = { managers: [], salon: '', err: e.message }; }
  if (r.salon) $('#loginSalon').textContent = r.salon;
  const box = $('#mgrNames'), form = $('#mgrForm');
  $('#mgrNone').hidden = r.managers.length > 0; form.hidden = true;
  if (r.err) $('#mgrNone').textContent = r.err;
  box.innerHTML = r.managers.map(m => `<button type="button" data-id="${m.id}" data-len="${m.pinLen || 0}">${esc(m.name)}</button>`).join('');
  $$('button', box).forEach(b => b.addEventListener('click', () => {
    S.mgrPick = +b.dataset.id; S.mgrLen = +b.dataset.len || 0; $$('button', box).forEach(x => x.classList.toggle('on', x === b));
    form.hidden = false; $('#mgrErr').hidden = true; setTimeout(() => $('#mgrPin').focus(), 50);
  }));
  if (r.managers.length === 1) $('button', box).click();
}
$('#mgrForm')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const err = $('#mgrErr'); err.hidden = true;
  try {
    const r = await api('mgr_login', { id: S.mgrPick, pin: $('#mgrPin').value, k: MGR_K });
    if (r.appTok && window.NFNative && NFNative.keep) await NFNative.keep(r.appTok, 'mgr:' + S.mgrPick); S.mgrTried = false; // (2.99.343 – lệnh 576) in the app: stays signed in on this phone
    S.csrf = r.csrf; $('#mgrPin').value = ''; $('#login').hidden = true; boot();
  } catch (x) { err.textContent = x.message; err.hidden = false; $('#mgrPin').select(); }
});
$('#mgrPin')?.addEventListener('input', (e) => { const el = e.target; // all the digits of the PIN: keyboard away and log in
  if (S.mgrLen && el.value.replace(/\D/g, '').length === S.mgrLen) { el.blur(); $('#mgrForm').requestSubmit(); } });
$$('#login [data-lang]').forEach(b => b.addEventListener('click', () => I18.set(b.dataset.lang, true))); // chosen before logging in: saved to them at login

/* ---------- bottom sheet ---------- */
/* (2.89) The sheet is one element for every screen: the listeners a screen puts on it are taken off when the next screen opens or the sheet closes
   (before: a closed Book still answered taps – "No, that's all" of the old 1-person booking jumped to "Enter customer phone number"). */
/* (2.99.170 – order 359) The tech's round photo – or the first letter on the tech's own color (each tech a different color). Owner / manager / AN Desk only. */
/* (2.99.171 – order 360) 1 tech = 1 own color (Staff → Color; same table as STAFF_PAL in inc/core/staff-services.php):
   [dark – border, name, initial circle · light – card in Light · dark-mode card · dark-mode name]. toneVars(tone) → --tav --tavl --tavn --tavt. */
const TECH_PAL = [['#1A56B0', '#D5E3F9', '#173361', '#BACCE7'], ['#A51E14', '#F9D7D5', '#511C1F', '#E4BCB8'], ['#6B21A8', '#E9D5F9', '#391D5D', '#D3BCE5'], ['#924300', '#F9E5D5', '#492B17', '#DEC7B2'],
  ['#00655F', '#D5F9F7', '#0C3A3F', '#B2D1CF'], ['#A3125E', '#F9D5E8', '#50173E', '#E3B8CF'], ['#1A6B33', '#D5F9E0', '#173C2C', '#BAD3C2'], ['#3730A3', '#D8D6F8', '#23235B', '#C3C1E3'],
  ['#6B4423', '#F7E5D7', '#392C25', '#D3C7BD'], ['#475569', '#DEE5F0', '#293343', '#C8CCD2'], ['#0B6380', '#D5F0F9', '#10394C', '#B6D0D9'], ['#6A5300', '#F9F1D5', '#383217', '#D2CBB2']];
const techPal = (tone) => TECH_PAL.find(p => p[0].toLowerCase() === String(tone || '').toLowerCase()) || ['#4B5563', '#E5E7EB', '#2A3140', '#D1D5DB'];
const toneVars = (tone, k) => { const p = techPal(tone); k = k || ''; return `--tav${k}:${p[0]};--tavl${k}:${p[1]};--tavn${k}:${p[2]};--tavt${k}:${p[3]}`; };
function techAv(s, cls) { s = s || {}; const n = String(s.name || '').trim(), i = n ? n[0].toUpperCase() : '?';
  return `<span class="tav${cls ? ' ' + cls : ''}" style="${toneVars(s.tone)}" title="${esc(n)}" aria-hidden="true"><b>${esc(i)}</b>${s.photo ? `<img src="../${esc(s.photo)}" alt="" decoding="async" onerror="this.remove()">` : ''}</span>`; }
let sheetAC = null;
/* (2.93) Book (admin): a short spoken line for each step – English, the device's own voice, no hand. "🔊 Sound on / 🔇 Sound off" next to ✕,
   remembered on this device. A new line (or any tap in the Book window) stops the one being said; nothing anywhere else in admin talks. */
const BKV = { on: (() => { try { return localStorage.getItem('bookVoiceA') !== 'off'; } catch (e) { return true; } })(), voice: null, live: false };
const bkVoice = () => { try { const v = speechSynthesis.getVoices().filter(x => /^en[-_]US/i.test(x.lang)); return v.find(x => /premium|enhanced/i.test(x.name)) || v.find(x => /^(Samantha|Ava|Allison|Google US)/i.test(x.name)) || v[0] || null; } catch (e) { return null; } };
function bkHush() { try { if (window.speechSynthesis && (speechSynthesis.speaking || speechSynthesis.pending)) speechSynthesis.cancel(); } catch (e) {} }
function bkSay(t) {
  if (!BKV.on || !BKV.live || !t || !('speechSynthesis' in window)) return;
  try { speechSynthesis.cancel(); const u = new SpeechSynthesisUtterance(t); u.lang = 'en-US'; BKV.voice = BKV.voice || bkVoice(); if (BKV.voice) u.voice = BKV.voice; u.rate = 1.02; speechSynthesis.speak(u); } catch (e) {}
}
/* (2.95) Book (admin): the guide hand of the customers' page (hand.js) – it goes to the next thing to tap after every tap. "👆 Guide on / off" next to Sound. */
const BKG = { on: (() => { try { return localStorage.getItem('bookGuideA') !== 'off'; } catch (e) { return true; } })(), t: null, fr: 0, sweep: 0, loaded: false };
function bkHandEl() { let h = $('#aHand'); if (h) return h;
  document.body.insertAdjacentHTML('beforeend', '<div class="g-hand" id="aHand" hidden aria-hidden="true"><span class="g-ring"></span><svg class="g-fin" viewBox="0 0 40 48"><path d="M15 4c2.2 0 4 1.8 4 4v13l1.6-.5c1.7-.5 3.4.4 4 2l.3.9 1.4-.4c1.7-.4 3.4.5 3.9 2.1l.3.9 1.2-.3c1.8-.4 3.6.7 4 2.5l.7 3.3c.9 4.2-.2 8.6-3 11.9L32 45H14.5l-8.8-11.2c-1-1.3-.9-3.2.3-4.3 1.3-1.2 3.3-1.2 4.5.1L11 30V8c0-2.2 1.8-4 4-4z" fill="#3472B9" stroke="#fff" stroke-width="2.4" stroke-linejoin="round"/></svg></div>');
  if (!BKG.loaded) { BKG.loaded = true; const me = document.querySelector('script[src*="admin.js"]'), x = document.createElement('script'); x.src = (me && me.src ? me.src : '../assets/admin.js').replace(/admin\.js/, 'hand.js'); x.onload = () => bkGuide(); document.head.appendChild(x); }
  return $('#aHand'); }
/** What to tap next in the Book window (null = nothing). */
function bkNext() {
  const sh = $('#sheet'), vis = (el) => el && el.getClientRects().length && getComputedStyle(el).visibility !== 'hidden';
  const tp = $('#tpBg'); if (tp) return $('[data-ask="one"]', tp) || $('.tp-any', tp);
  if (!sh || sh.hidden) return null;
  if ($('.wiz0', sh)) return $('[data-p]', sh);
  if ($('.bk1', sh)) { const vr = $('.vrow', sh); if (vr) return $('.vbtn[data-vdone]', vr) && $('.vbtn.on', vr) ? $('.vbtn[data-vdone]', vr) : $('.vbtn:not(.done)', vr); // (2.96) the open question first
    const aq = $('.addq [data-addno]', sh); if (vis(aq)) return aq;
    const pb = $('.pbox', sh); if (pb && BKG.more) return $('.schip:not(.on)', pb) || $('.schip', pb); // "+ Add more": back to that person's services
    if (pb && !$('.schip.on', pb)) return $('.schip', pb);
    const need = $('.tline.need', sh) || $('.pt-line.need [data-ptpick]', sh); if (need && vis(need)) return need;
    return $('#wNext', sh); }
  const ph = $('#wPhone', sh); if (ph) return digits(ph.value).length === 10 ? $('#wNext', sh) : ph;
  const nm = $('#wName', sh); if (nm) return nm.value.trim() ? $('#wSave', sh) : nm;
  return null;
}
function bkPlace() { BKG.fr = 0; const h = $('#aHand'); if (!h || !window.GHand) return;
  const t = BKG.t; if (!BKG.on || !BKV.live || !t || !t.isConnected || !t.getClientRects().length) { GHand.off(h); return; }
  const r = t.getBoundingClientRect(), box = t.closest('#tpBg .tp-box') || $('#sheet'), br = box.getBoundingClientRect(), foot = $('#sheet .sheet-foot'), fl = foot && !foot.contains(t) && !t.closest('#tpBg') ? foot.getBoundingClientRect().top : br.bottom;
  const cy = (r.top + r.bottom) / 2; const ps = !t.closest('#tpBg') && $('#sheet .pbox .pb-stick.stuck'), top0 = ps ? ps.getBoundingClientRect().bottom : br.top;
  if (cy < top0 + 4 || cy > fl - 4) { GHand.off(h); bkJump(cy < top0 + 4 ? 'up' : 'down', top0, fl); return; } // (2.98) scrolled away: the hand waits, a "↑ Tap here" / "↓ Tap here" shows the way
  bkJump(null);
  const TX = []; const tw = document.createTreeWalker(t, NodeFilter.SHOW_TEXT); let n; while ((n = tw.nextNode())) { if (!n.nodeValue.trim()) continue; const rg = document.createRange(); rg.selectNodeContents(n); for (const q of rg.getClientRects()) if (q.width > 1) TX.push(q); }
  const clean = (x, y) => !TX.some(q => !(x + 39 < q.left || x - 1 > q.right || y + 47 < q.top || y - 8 > q.bottom)); // the finger never on the words
  const P = [[r.right - 30, r.top + r.height * 0.45], [r.right - 20, r.bottom - 14], [r.left + 8, r.bottom - 14], [r.left + r.width / 2, r.bottom - 10], [r.right - 30, r.bottom - 6]];
  const p = P.find(([x, y]) => clean(x, y) && x + 39 < innerWidth) || P[1]; GHand.to(h, Math.max(2, Math.min(innerWidth - 42, p[0])), Math.min(innerHeight - 48, p[1]));
}
/* (2.98) the open question is off the screen (the user scrolled or tapped a group tab): a small "↑ Tap here" / "↓ Tap here" – the page is never pulled back by itself */
function bkJump(dir, top0, bot) { let j = $('#aJump');
  if (!dir || !BKG.on || !BKV.live) { if (j) j.hidden = true; return; }
  if (!j) { document.body.insertAdjacentHTML('beforeend', '<button type="button" class="bk-jump" id="aJump" hidden></button>'); j = $('#aJump');
    j.addEventListener('click', () => { const t = BKG.t; j.hidden = true; if (t && t.isConnected) { t.scrollIntoView({ block: 'center', behavior: 'smooth' }); setTimeout(bkPlace, 500); } }); }
  j.textContent = (dir === 'up' ? '↑' : '↓') + ' Tap here'; j.style.bottom = Math.round(innerHeight - bot + 10) + 'px'; j.hidden = false; } // just above Back / Next, on the right: it covers no title
function bkGuide(scroll) { const h = BKG.on && BKV.live ? bkHandEl() : $('#aHand'); if (!h) return; clearTimeout(BKG.sweep);
  if (!BKG.on || !BKV.live) { if (window.GHand) GHand.off(h); bkJump(null); return; }
  const t = bkNext(); BKG.t = t;
  if (t && scroll !== false) { const sc = t.closest('#sheet'); if (sc && !t.closest('.sheet-foot')) { const r = t.getBoundingClientRect(), sr = sc.getBoundingClientRect(), ft = $('.sheet-foot', sc), bot = ft ? ft.getBoundingClientRect().top : sr.bottom;
      if (r.top < sr.top + 60 || r.bottom > bot - 10) t.scrollIntoView({ block: 'center', behavior: 'smooth' }); } }
  bkPlace(); setTimeout(bkPlace, 450);
  const vr = t && t.classList.contains('vbtn') && !t.classList.contains('done') ? t.closest('.vrow') : null; // (2.96) Full set → Fill: the hand runs over the choices, back to the first
  if (vr) { const L = $$('.vbtn:not(.done)', vr); let i = 1; const nx = () => { if (!vr.isConnected || !L.includes(BKG.t)) return; BKG.t = i < L.length ? L[i++] : L[0]; bkPlace(); if (BKG.t !== L[0]) BKG.sweep = setTimeout(nx, 800); };
    if (L.length > 1) BKG.sweep = setTimeout(nx, 1100); }
  const tp = $('#tpBg'); if (tp && t && t.classList.contains('tp-any')) { const L = $$('.tp-t:not([disabled])', tp).slice(0, 4); let i = 0; // the pop-up: ANYONE, then a quick look over the techs, back to ANYONE
    const nx = () => { if (!tp.isConnected || BKG.t !== t && !L.includes(BKG.t)) return; BKG.t = i < L.length ? L[i++] : t; bkPlace(); if (BKG.t !== t) BKG.sweep = setTimeout(nx, 700); };
    BKG.sweep = setTimeout(nx, 1600); }
}
const bkGuideSoon = (ms = 300, scroll = true) => { clearTimeout(BKG.soonT); BKG.soonT = setTimeout(() => bkGuide(scroll), ms); };
document.addEventListener('click', (e) => { if (!BKV.live || !e.target.closest('#sheet, #tpBg') || e.target.closest('#bkSnd, #bkGd')) return;
  if (e.target.closest('[data-addmore]')) BKG.more = true; else if (e.target.closest('[data-sb], [data-same], [data-addno], [data-p], [data-edit]')) BKG.more = false;
  /* (2.98) only a tap that makes a new step (a service, Full set / Fill, No that's all, a tech, Next…) may scroll the page to the next question; a group tab, Change, a box… never */
  bkGuideSoon(380, !!e.target.closest('.schip, .vbtn, [data-addno], [data-addmore], [data-same], [data-p], [data-edit], [data-ptpick], [data-ptone], .tline, #wNext, #wBack, #tpBg button')); }, true);
new MutationObserver((ms) => { if (BKV.live && BKG.on && ms.some(m => [...m.addedNodes, ...m.removedNodes].some(n => n.id === 'tpBg'))) bkGuideSoon(250); }).observe(document.body, { childList: true }); // a pick-a-tech window opened / closed
document.addEventListener('input', (e) => { if (BKV.live && e.target.closest('#sheet')) bkGuideSoon(250, false); }, true);
document.addEventListener('scroll', () => { if (BKV.live && !BKG.fr) BKG.fr = requestAnimationFrame(bkPlace); }, { capture: true, passive: true });
addEventListener('resize', () => { if (BKV.live) bkPlace(); });
function bkSnd() { const sh = $('#sheet'), x = sh && $('.x', sh); if (!x || $('#bkSnd', sh)) return;
  x.insertAdjacentHTML('beforebegin', `<button type="button" class="bk-snd" id="bkGd" aria-pressed="${BKG.on}" aria-label="${BKG.on ? 'Guide on – tap to turn off' : 'Guide off – tap to turn on'}">👆</button>`);
  $('#bkGd', sh).addEventListener('click', (e) => { e.stopPropagation(); BKG.on = !BKG.on; try { localStorage.setItem('bookGuideA', BKG.on ? 'on' : 'off'); } catch (x2) {}
    const b = e.currentTarget; b.textContent = '👆'; b.setAttribute('aria-pressed', String(BKG.on)); b.setAttribute('aria-label', BKG.on ? 'Guide on – tap to turn off' : 'Guide off – tap to turn on'); bkGuide(); });
  x.insertAdjacentHTML('beforebegin', `<button type="button" class="bk-snd" id="bkSnd" aria-pressed="${BKV.on}" aria-label="${BKV.on ? 'Sound on – tap to turn off' : 'Sound off – tap to turn on'}">${BKV.on ? '🔊' : '🔇'}</button>`);
  $('#bkSnd', sh).addEventListener('click', (e) => { e.stopPropagation(); BKV.on = !BKV.on; try { localStorage.setItem('bookVoiceA', BKV.on ? 'on' : 'off'); } catch (x2) {}
    if (!BKV.on) bkHush(); const b = e.currentTarget; b.textContent = BKV.on ? '🔊' : '🔇'; b.setAttribute('aria-pressed', String(BKV.on)); b.setAttribute('aria-label', BKV.on ? 'Sound on – tap to turn off' : 'Sound off – tap to turn on'); }); }
document.addEventListener('pointerdown', (e) => { if (BKV.live && !e.target.closest('#bkSnd') && e.target.closest('#sheet, #tpBg')) bkHush(); }, true); // a tap: the line being said stops
function openSheet(html, mount) {
  const sh = $('#sheet');
  if (sheetAC) sheetAC.abort(); const ac = sheetAC = new AbortController(); S.sheetAsk = null; // (2.99.97) a new sheet: no "Discard?" unless it sets one
  const pg = !!S.pageMode; sh.classList.toggle('as-page', pg); sh.classList.remove('pos', 'pos-rc', 'ckA', 'ck-padopen'); delete sh.dataset.ckt; // (2.99.92) the POS look only where it is set again // (2.99.71) opened from Home: a full page with "‹ Home" on top, no pop-up on top of a pop-up
  sh.innerHTML = (pg ? '<div class="page-top"><button type="button" class="homeback" data-homeback>‹ Home</button></div>' : '<div class="grab"></div>') + html;
  sh.hidden = false; dockSync(); /* (2.99.473) a page from Home: no dock */ $('#sheetBg').hidden = pg; { const tb = $('#tabbar'); sh.style.bottom = pg && tb && tb.getClientRects().length ? Math.max(0, innerHeight - tb.getBoundingClientRect().top) + 'px' : ''; } /* the page ends above the bottom menu */ sh.scrollTop = 0; sh.style.transform = ''; sh.dataset.t0 = String(Date.now()); // (2.62) see the click guard below
  $$('.x', sh).forEach(b => b.addEventListener('click', closeSheet));
  $$('[data-homeback]', sh).forEach(b => b.addEventListener('click', goHome));
  if (mount) { sh.addEventListener = (t, f, o) => EventTarget.prototype.addEventListener.call(sh, t, f, typeof o === 'object' && o ? { ...o, signal: ac.signal } : { capture: !!o, signal: ac.signal });
    try { mount(sh); } finally { delete sh.addEventListener; } }
}
/* (2.62) iPhone keyboard: the sheet shrinks to the part of the screen above the keyboard, so the buttons stuck at its bottom stay in sight;
   the box being typed in scrolls into view. */
if (window.visualViewport) {
  const vv = window.visualViewport;
  const fit = () => { const sh = $('#sheet'); if (!sh || sh.hidden || innerWidth >= 700) { if (sh) { sh.style.height = ''; sh.style.top = ''; } return; }
    const kb = innerHeight - vv.height > 80; sh.style.top = kb ? vv.offsetTop + 'px' : ''; sh.style.height = kb ? vv.height + 'px' : ''; };
  vv.addEventListener('resize', fit); vv.addEventListener('scroll', fit);
  document.addEventListener('focusin', (e) => { const el = e.target; if (!el.closest || !el.closest('#sheet') || !/^(INPUT|TEXTAREA|SELECT)$/.test(el.tagName)) return;
    setTimeout(() => { fit(); el.scrollIntoView({ block: 'center', behavior: 'smooth' }); }, 300); });
}
/* (2.62) the tap that opened a sheet must not also press the button that appears under the finger (iPhone "ghost click") */
$('#sheet').addEventListener('click', (e) => { if (Date.now() - +($('#sheet').dataset.t0 || 0) < 350) { e.stopPropagation(); e.preventDefault(); } }, true);
function closeSheet() { setTimeout(() => { if (typeof dockSync === 'function') dockSync(); }, 0); /* (2.99.473) after it closed */ S.sheetAsk = null; BKV.live = false; bkHush(); bkJump(null); { const h = $('#aHand'); if (h && window.GHand) GHand.off(h); } if (sheetAC) { sheetAC.abort(); sheetAC = null; } clearTimeout(autoA); $('#tpBg')?.remove(); $('#sheet').style.height = ''; $('#sheet').style.top = ''; $('#sheet').hidden = true; $('#sheetBg').hidden = true; $('#sheet').innerHTML = ''; $('#sheet').classList.remove('as-page'); $('#sheet').style.bottom = ''; S.pageMode = false; if (FR && FR.pend) setTimeout(() => { if (FR.pend && frFree()) { FR.pend = false; frReload(); } }, 400); /* (2.99.200) no new call to chg.php: the change is already known */ if (IS_DESK) dkClosed(); setTimeout(nfMaybeReload, 600); } // (2.99.282) back on the main screen: a waiting new version loads now (2.99.84) a change came while it was open: show it now
/* (2.99.97) Closing by the gray part, Escape or dragging the top down: a sheet with something unsaved (Book) asks first (S.sheetAsk). */
function askClose() { if (typeof S.sheetAsk === 'function' && S.sheetAsk()) return; closeSheet(); }
$('#sheetBg').addEventListener('click', askClose);
document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !$('#sheet').hidden) askClose(); });
const head = (title, sub) => `<div class="sheet-head"><div><h3>${esc(title)}</h3>${sub ? `<p class="sub">${sub}</p>` : ''}</div><button class="x" type="button" aria-label="Close">×</button></div>`;
/** Just the × in the corner (compact sheets: New appointment from the schedule, Edit). */
const xOnly = () => '<div class="sheet-x"><button class="x" type="button" aria-label="Close">×</button></div>';
/** "Oct 2 · 11:30 AM · Change": day and time kept out of the way; Change shows the Date / Start boxes. */
const whenLine = (date, start, id) => `<p class="when-line" id="${id}">${esc(MON[parseD(date).getMonth()] + ' ' + parseD(date).getDate())} · ${tlabel(start)} · <button type="button" class="linkbtn" data-when>Change</button></p>`;
(() => { // drag the sheet down to close
  const sh = $('#sheet'); let y0 = null, dy = 0;
  // (2.99.97) only a drag that STARTS on the top of the sheet (grab bar / progress / title – the top 80 px), never on a wheel, a list that
  // scrolls, a button, a box to type in, the keypad, a signature or a photo crop (scrolling inside a sheet never closes it)
  const NO = 'input,select,textarea,button,a,label,canvas,.b3-wheel,.b3-col,.svc-chips,.durs,.msel,.crop-wrap,.keypad,.sig,[data-nodrag]';
  const scrolls = (el) => { for (let x = el; x && x !== sh; x = x.parentElement) { const cs = getComputedStyle(x); if ((x.scrollHeight > x.clientHeight + 1 && /(auto|scroll)/.test(cs.overflowY)) || (x.scrollWidth > x.clientWidth + 1 && /(auto|scroll)/.test(cs.overflowX))) return true; } return false; };
  sh.addEventListener('touchstart', (e) => {
    const t = e.touches[0], top = sh.getBoundingClientRect().top;
    y0 = (!sh.classList.contains('as-page') && sh.scrollTop <= 0 && e.touches.length === 1 && t.clientY - top <= 80 && !e.target.closest(NO) && !scrolls(e.target)) ? t.clientY : null; dy = 0;
  }, { passive: true });
  sh.addEventListener('touchmove', (e) => {
    if (y0 === null) return; dy = e.touches[0].clientY - y0;
    if (dy > 0 && sh.scrollTop <= 0) { sh.style.transition = 'none'; sh.style.transform = `translateY(${dy}px)`; }
    else if (dy < 0) { y0 = null; sh.style.transform = ''; }
  }, { passive: true });
  sh.addEventListener('touchend', () => { if (y0 === null) return; y0 = null; sh.style.transition = ''; sh.style.transform = ''; if (dy > 120) askClose(); });
  sh.addEventListener('touchcancel', () => { y0 = null; sh.style.transition = ''; sh.style.transform = ''; });
})();
/** (2.99.272 – order 482) The services this tech is NOT ticked for (Settings → Nail techs → services; none ticked = all) – the desk is asked first. */
function skillMiss(sid, ids) { const D = S.day || {}, st = (D.staff || []).find(s => s.id === +sid); if (!st || !st.skills || !st.skills.length) return [];
  return (ids || []).map(Number).filter(id => id > 0 && !st.skills.includes(id)).map(id => ((D.services || []).find(x => x.id === id) || {}).name || '').filter(Boolean); }
/** (2.99.273 – order 483 mục 11) this tech's booked customer the new one would run into ("11:00"), '' = none: menu minutes + 5 min before the booked time. */
function bookedClash(sid, mins, skipId) { const D = S.day || {}; if (!D.appts || (D.date && D.date !== (S.today || localToday()))) return ''; const t = new Date(), now = t.getHours() * 60 + t.getMinutes();
  const nx = D.appts.filter(x => x.staff === +sid && x.id !== skipId && !x.walkin && !x.started && ['booked', 'arrived'].includes(x.status) && x.start >= now - 15).sort((x, y) => x.start - y.start)[0];
  return nx && nx.start < now + Math.max(1, mins || 30) + 5 ? tlabel(nx.start) : ''; }
function skillAsk(box, sid, ids, go, mins, skipId) { const m = skillMiss(sid, ids), bk = mins === undefined ? '' : bookedClash(sid, mins, skipId); if ((!m.length && !bk) || !box) return go(); const D = S.day || {}, n = ((D.staff || []).find(s => s.id === +sid) || {}).name || '';
  const why = [m.length ? LV(`is not ticked for ${m.join(', ')}`, `chưa được tick làm ${m.join(', ')}`) : '', bk ? LV(`has a booking at ${bk} – this customer would run into it`, `có khách hẹn ${bk} – khách này sẽ lấn giờ hẹn`) : ''].filter(Boolean).join(' · ');
  box.hidden = false; confirmIn(box, LV(`${n} ${why} – give to ${n} anyway?`, `${n} ${why} – vẫn giao?`), LV('Give anyway', 'Vẫn giao'), go); }
function confirmIn(box, text, yesLabel, onYes, danger, noLabel) {
  box.innerHTML = `<div class="confirm"><p>${esc(text)}</p><div class="row"><button type="button" class="btn small ${danger ? 'redfill' : 'primary'}" data-yes>${esc(yesLabel)}</button><button type="button" class="btn small" data-no>${esc(noLabel || 'Go back')}</button></div></div>`;
  $('[data-yes]', box).addEventListener('click', async (e) => { const b = e.currentTarget; if (b.disabled) return; b.disabled = true; // (2.99.92) never sent twice
    try { await onYes(e); } finally { if (b.isConnected) b.disabled = false; } });
  $('[data-no]', box).addEventListener('click', () => { box.innerHTML = ''; });
  box.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
}
(() => {
  const MONEY = /amt|amount|price|cash|tip|total|pay|money|disc|\$/i;
  const fix = () => {
    $$('input[type="number"]:not([inputmode])').forEach(i => { const k = [i.id, i.name, i.getAttribute('aria-label'), i.placeholder].join(' ');
      i.inputMode = MONEY.test(k) || String(i.step).includes('.') || i.step === 'any' ? 'decimal' : 'numeric'; });
    $$('input[type="tel"]:not([inputmode])').forEach(i => { i.inputMode = 'tel'; });
    $$('table:not(.tc-no)').forEach(t => {
      const r0 = t.tHead?.rows[0] || t.rows[0]; const hs = r0 ? [...r0.cells] : [];
      if (hs.length < 4 || hs.some(c => c.tagName !== 'TH' || c.colSpan > 1)) { t.classList.add('tc-no'); return; }
      const L = hs.map(c => c.textContent.trim()); t.classList.add('tcards'); r0.classList.add('tc-h');
      [...t.rows].forEach(r => { if (r === r0 || r.dataset.tc) return; r.dataset.tc = '1'; let i = 0; [...r.cells].forEach(c => { if (L[i] && i) c.dataset.label = L[i]; i += c.colSpan; }); });
    });
  };
  let q = 0; new MutationObserver(() => { if (!q) q = requestAnimationFrame(() => { q = 0; fix(); }); }).observe(document.body, { childList: true, subtree: true });
})();

/* ---------- tabs ---------- */
const HOME_TAB_ICON = '<svg viewBox="0 0 32 32" aria-hidden="true"><rect x="5" y="5" width="9.5" height="9.5" rx="2.6" fill="none" stroke="currentColor" stroke-width="2.3"/><rect x="17.5" y="5" width="9.5" height="9.5" rx="2.6" fill="none" stroke="currentColor" stroke-width="2.3"/><rect x="5" y="17.5" width="9.5" height="9.5" rx="2.6" fill="none" stroke="currentColor" stroke-width="2.3"/><rect x="17.5" y="17.5" width="9.5" height="9.5" rx="2.6" fill="none" stroke="currentColor" stroke-width="2.3"/></svg>';
/* (2.99.71) The manager page gets a Home button too (its own icons only); the "‹ Home" bar sits above the pages. */
(() => {
  const tb = $('#tabbar'); if (!tb) return;
  if (IS_MGR && !$('#p-settings')) { const sec = document.createElement('section'); sec.className = 'panel page'; sec.id = 'p-settings'; sec.hidden = true; tb.parentNode.insertBefore(sec, tb);
    const b = document.createElement('button'); b.type = 'button'; b.dataset.tab = 'settings'; b.innerHTML = HOME_TAB_ICON + '<span>Home</span>'; tb.insertBefore(b, $('#btnMe') || null); }
  const first = $('.panel'); if (first && !$('#homeBar')) { const d = document.createElement('div'); d.id = 'homeBar'; d.className = 'home-bar'; d.hidden = true;
    d.innerHTML = '<button type="button" class="homeback">‹ Home</button>'; first.parentNode.insertBefore(d, first); d.firstChild.addEventListener('click', () => goHome()); }
  { const hd = $('.ns-head'), h1 = $('#salonName'); // (2.99.72) "+ Book" top left, in the row of the salon name (the name is never covered, the schedule not pushed down)
    if (hd && h1 && !$('#btnBookTop')) { const bb = document.createElement('button'); bb.type = 'button'; bb.id = 'btnBookTop'; bb.className = 'ns-book'; bb.innerHTML = '<span aria-hidden="true">+</span> Book';
      bb.addEventListener('click', () => openBook()); const L = document.createElement('span'); L.className = 'ns-side ns-bk'; L.appendChild(bb);
      if (IS_MGR) { $('#btnBook')?.remove(); const us = $('#btnUser')?.closest('.ns-side'); hd.classList.add('has-book', 'mgr-book'); hd.insertBefore(L, hd.firstChild); if (us) hd.appendChild(us); }
      else { hd.classList.add('has-book'); hd.insertBefore(L, h1); const R2 = document.createElement('span'); R2.className = 'ns-side ns-bk-sp'; R2.setAttribute('aria-hidden', 'true'); R2.innerHTML = '<span class="ns-book">+ Book</span>'; hd.appendChild(R2); } } }
  const hb = tb.querySelector('[data-tab="settings"]'); if (hb && !hb.dataset.home) { hb.dataset.home = '1'; const dot = hb.querySelector('.tab-dot'); hb.innerHTML = (dot ? dot.outerHTML : '') + HOME_TAB_ICON + '<span>Home</span>'; }
  /* (2.99.467 – LỆNH 467, anh Logan 19:24) the owner's bottom bar: the glossy pictures of the video task too (the line drawing stays if a picture cannot load) */
  /* (2.99.468 – LỆNH 468) the owner's Log out: small, at the left of the bottom bar next to Check-in (the same ownerOut() as the old Home button – in the app: Face ID next time) */
  /* (2.99.506 – LỆNH 503, anh Logan 30/10) Log out LEFT the dock: small 'Log out' at the bottom of Home + the last row of Settings (ownerLogOut below) */
  if (false && !IS_MGR && !IS_DESK && !$('#tabOut')) { const ob = document.createElement('button'); ob.type = 'button'; ob.id = 'tabOut'; ob.className = 'tab-out'; ob.setAttribute('aria-label', 'Log out');
    ob.innerHTML = '<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M13 6.5H8.5a2 2 0 0 0-2 2v15a2 2 0 0 0 2 2H13" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/><path d="M14.5 16H26M21.5 11l5 5-5 5" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg><span>' + LV('Log out', 'Thoát') + '</span>';
    ob.addEventListener('click', async () => { ob.disabled = true; try { await ownerOut(); S.csrf = null; try { if (window.NFNative && NFNative.loggedOut) NFNative.loggedOut(); } catch (e) {} if (typeof showLogin === 'function') showLogin(); else location.reload(); } finally { ob.disabled = false; } });
    tb.insertBefore(ob, tb.firstChild); }
  /* (2.99.490 – LỆNH 489, anh Logan 30/10) the owner's '+ Book' moved into the dock, between Receipts and Home (the date row with Find / + Book is gone) – it books for Anyone like the old button */
  if (false && !IS_MGR && !IS_DESK && !$('#tabBook')) { /* (2.99.512) Book left the dock  it is at the top right of Appointments */ const bk = document.createElement('button'); bk.type = 'button'; bk.id = 'tabBook'; bk.className = 'tab-book'; bk.setAttribute('aria-label', LV('Book', 'Đặt hẹn'));
    bk.innerHTML = '<svg viewBox="0 0 32 32" aria-hidden="true"><rect x="5" y="7" width="22" height="20" rx="3" fill="none" stroke="currentColor" stroke-width="2.4"/><path d="M5 12.5h22M11 4.5v5M21 4.5v5M16 15.5v8M12 19.5h8" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/></svg><span>' + LV('Book', 'Đặt hẹn') + '</span>';
    bk.addEventListener('click', () => { if (typeof openBook === 'function') openBook(); });
    const home = tb.querySelector('[data-tab="settings"]'); tb.insertBefore(bk, home || null); }
  /* (2.99.512  CHAT, anh Logan 30/10 00:57) the owner's dock: Messages (the Home Messages picture + unread count) in Book's place, between Receipts and Home */
if (!IS_MGR && !IS_DESK && !$('#tabMsg')) { const bm = document.createElement('button'); bm.type = 'button'; bm.id = 'tabMsg'; bm.className = 'tab-msg'; bm.setAttribute('aria-label', LV('Messages', 'Tin nhắn'));
bm.innerHTML = '<img class="tab-img" alt="" decoding="async" src="../assets/home-ic/reminder.webp?v=516"><svg viewBox="0 0 32 32" aria-hidden="true"><path d="M6 7h20a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H14l-6 5v-5H6a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2z" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linejoin="round"/></svg><span>' + LV('Messages', 'Tin nhắn') + '</span><i class="tab-badge" id="tabMsgBdg" hidden></i>';
{ const im = bm.querySelector('img'); im.addEventListener('load', () => bm.classList.add('has-ti'), { once: true }); im.addEventListener('error', () => im.remove(), { once: true }); }
bm.addEventListener('click', () => { if (S.pageMode && !$('#sheet').hidden) closeSheet(); S.fromHome = false; S.thread = null; M.view = 'send'; setTab('messages'); bm.classList.add('on'); });
const home2 = tb.querySelector('[data-tab="settings"]'); tb.insertBefore(bm, home2 || null); }
{ const ab = tb.querySelector('[data-tab="appts"]'); if (ab && !IS_MGR && !IS_DESK) { ab.dataset.short = LV('Appts', 'Lịch hẹn'); const sp = ab.querySelector('span'); if (sp) sp.dataset.short = ab.dataset.short; } } /* (2.99.470 – LỆNH 469 f) the big Home dock: a shorter name so 5 buttons fit one row */
  if (!IS_MGR && !IS_DESK) { document.body.classList.add('own-dock'); const hx = tb.querySelector('[data-tab="history"]'); if (hx) hx.hidden = true; } /* (2.99.538 - anh Logan 30/10 17:38) the owner's dock like the iPhone: 4 icons (Check-in, Appointments, Messages, Home) - Receipts is on Home -> Daily */
	if (!IS_MGR && !IS_DESK) for (const [t, f] of [['checkin', 'tab-checkin'], ['appts', 'tab-appts'], ['history', 'tab-history'], ['settings', 'tab-home']]) { const b = tb.querySelector(`[data-tab="${t}"]`); if (!b || b.querySelector('.tab-img')) continue;
    const im = document.createElement('img'); im.className = 'tab-img'; im.alt = ''; im.decoding = 'async'; im.src = '../assets/home-ic/' + f + '.webp?v=516'; im.addEventListener('load', () => b.classList.add('has-ti'), { once: true }); im.addEventListener('error', () => im.remove(), { once: true }); const sv = b.querySelector('svg'); b.insertBefore(im, sv || b.firstChild); }
})();
/* (2.99.473 – LỆNH 469 d, anh Logan 29/10) like the iPhone: a page opened from a Home icon (it has the red '‹ Home') has NO dock;
   the 4 pages of the dock itself (Check-in, Appointments, Receipts, Home) opened from the dock keep it. The owner only. */
function dockSync() { const pg = !!S.pageMode && !$('#sheet').hidden; const sec = S.tab === 'settings' && !!S.setSec && !!S.secFromHome;
  document.body.classList.toggle('no-dock', !IS_MGR && !IS_DESK && ((S.fromHome && S.tab !== 'settings') || sec || pg || S.tab !== 'settings' || S.home === 'settings' || !!S.setSec)); } /* (2.99.561 - LENH 561, anh Logan 30/10 22:58) like the iPhone: the owner's dock ONLY on Home - every page opened (Messages, Appointments, Check-in, Settings...) uses the whole screen */
function setTab(tab) {
  if (tab !== 'messages' && document.body.classList.contains('ib-chat')) { document.body.classList.remove('ib-chat'); const pm = $('#p-messages'); if (pm) pm.style.height = ''; } // (2.99.328 – lệnh 555) leaving a chat
  S.tab = tab; if (window.Talk) Talk.tab(tab); // (2.99.165) 🎙 talk to the iPad: on the Check-in tab
  $$('#tabbar button').forEach(b => b.classList.toggle('on', b.dataset.tab === tab));
  $$('.panel').forEach(p => { p.hidden = p.id !== 'p-' + tab; });
  document.body.classList.toggle('on-settings', tab === 'settings' && !IS_MGR); // (2.99.65) Settings: no salon name on top, the icons start at the top
  if (tab === 'settings') S.fromHome = false;
  { const hb = $('#homeBar'); if (hb) { hb.hidden = !((S.fromHome || (!IS_MGR && !IS_DESK)) && tab !== 'settings' && !(!IS_MGR && !IS_DESK && (tab === 'appts' || tab === 'checkin'))); if (tab !== 'messages') { $$('.msg-seg', hb).forEach(x => x.remove()); hb.classList.remove('hb-seg'); } } } /* (2.99.471) the Messages buttons leave the top row with Messages */ // (2.99.71) "‹ Home" above a page opened from Home
  dockSync(); /* (2.99.473) */
  if (tab === 'history' && !S.fromHome && !IS_MGR && !IS_DESK && typeof H !== 'undefined' && !['receipts', 'history'].includes(H.view)) H.view = 'receipts'; /* (2.99.528) the dock's Receipts always opens Receipts (not the Payroll last opened from Home) */
if (tab === 'appts' && typeof chgSched === 'function' && !IS_DESK && S.csrf && !FR.busy) chgSched(1500); // (2.99.201 – order 401) Appointments: start waiting on chg.php now
  ({ appts: () => loadDay(), checkin: renderCheckin, checkout: renderCheckout, turns: () => renderTurns(), today: () => renderToday(), messages: renderMessages, settings: renderSettings, history: renderHistory })[tab]();
}
$$('#tabbar button[data-tab]').forEach(b => b.addEventListener('click', () => {
  if (false && b.dataset.tab === 'checkout' && S.qOwner && !IS_DESK) return qdOn(); // (25/10 Logan: no sign-in step to come back) owner's Checkout stays in the admin // (2.99.322 – lệnh 539 mục 11) the owner's Checkout = the AN Desk Checkout (checkout mode), the admin needs the owner password again
  if (b.dataset.tab === 'messages' && S.tab === 'messages') { S.thread = null; M.view = 'send'; } // tap Messages again: back to To send
  if (S.pageMode && !$('#sheet').hidden) closeSheet(); // (2.99.71) a list opened as a page from Home goes away
  S.fromHome = false;
  if (b.dataset.tab === 'settings') { S.home = null; S.setSec = null; S.secFromHome = false; } // (2.99.71) the Home button: always the Home icons
  setTab(b.dataset.tab);
}));
const openReminder = () => { S.thread = null; M.view = 'send'; setTab('messages'); }; // texts to send
$('#btnReminder')?.addEventListener('click', openReminder);
/* (2.99.63) Book · Reminder · Review · Birthday · Refer: an iPhone-style icon grid at the top of Settings (the top bar keeps only the salon name);
   red badges like iOS (hidden at 0, "99+" above 99); a small red dot on the Settings tab while any list has something to send */
const HS = { msg: 0, rv: 0, bd: 0, rf: 0, stop: 0, ap: 0 }; // (2.99.333 – lệnh 563) ap: bookings not seen yet (Appointments) // (2.99.124) stop: Home → Auto STOP (not on the app icon)
const HS_SVG = {
  checkout: '<rect x="4" y="8" width="24" height="16.5" rx="2.5" fill="none" stroke="#fff" stroke-width="2.4"/><path d="M4 13h24" stroke="#fff" stroke-width="3"/><path d="M8.5 20h6" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/>',
  checkin: '<rect x="6.5" y="5" width="15" height="21" rx="2" fill="none" stroke="#fff" stroke-width="2.4"/><path d="M10 11h8M10 15.5h8M10 20h4" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/><circle cx="22.5" cy="22.5" r="5" fill="none" stroke="#fff" stroke-width="2.4"/><path d="M22.5 20.3v2.4l1.6 1.1" stroke="#fff" stroke-width="2" fill="none" stroke-linecap="round"/>',
  appts: '<rect x="5" y="7.5" width="22" height="19" rx="2.5" fill="none" stroke="#fff" stroke-width="2.4"/><path d="M5 12.5h22M11 5v5M21 5v5" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/><path d="M10 17.5h3M15 17.5h3M20 17.5h2M10 21.5h3M15 21.5h3" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/>',
  history: '<path d="M8 5h16v22.5l-2.7-1.8-2.6 1.8-2.7-1.8-2.7 1.8-2.6-1.8L8 27.5z" fill="none" stroke="#fff" stroke-width="2.4" stroke-linejoin="round"/><path d="M12 11h8M12 15.5h8M12 20h5" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/>',
  book: '<path d="M7 9.5h18v15.5H7z" fill="none" stroke="#fff" stroke-width="2.4" stroke-linejoin="round"/><path d="M7 14h18M12 6.5v5M20 6.5v5M16 17v6M13 20h6" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/>',
  reminder: '<path d="M6 9.5c0-1.7 1.3-3 3-3h14c1.7 0 3 1.3 3 3v9c0 1.7-1.3 3-3 3h-8l-5.5 4v-4H9c-1.7 0-3-1.3-3-3z" fill="none" stroke="#fff" stroke-width="2.4" stroke-linejoin="round"/><path d="M11 12.5h10M11 16.5h6" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/>',
  review: '<path d="M16 5.5l3.2 6.6 7.2 1-5.2 5.1 1.2 7.2L16 22l-6.4 3.4 1.2-7.2-5.2-5.1 7.2-1z" fill="none" stroke="#fff" stroke-width="2.4" stroke-linejoin="round"/>',
  bday: '<path d="M7 26h18v-8.5c0-1.4-1.1-2.5-2.5-2.5h-13C8.1 15 7 16.1 7 17.5z" fill="none" stroke="#fff" stroke-width="2.4" stroke-linejoin="round"/><path d="M7 20.5c2 1.6 3.6 1.6 5.3 0s3.4-1.6 5.3 0 3.4 1.6 5.4 0M11 15v-3M16 15v-3M21 15v-3" stroke="#fff" stroke-width="2.4" stroke-linecap="round" fill="none"/><path d="M11 8.5l-.01.01M16 8.5l-.01.01M21 8.5l-.01.01" stroke="#fff" stroke-width="3.4" stroke-linecap="round"/>',
  refer: '<path d="M6.5 13h19v4.5h-19zM8 17.5h16V26H8z" fill="none" stroke="#fff" stroke-width="2.4" stroke-linejoin="round"/><path d="M16 13v13M16 13c-1.5-4.5-6.5-5.5-6.5-2.5 0 2 3.5 2.5 6.5 2.5zm0 0c1.5-4.5 6.5-5.5 6.5-2.5 0 2-3.5 2.5-6.5 2.5z" fill="none" stroke="#fff" stroke-width="2.4" stroke-linejoin="round"/>',
};
/* (2.99.71) HOME – the owner's main screen, like the iPhone home screen: only icons, 4 a row, small gray group titles.
   Each icon opens its own page with "‹ Home" on top (lists that were pop-ups open as a full page – never one pop-up on another).
   A manager sees only the icons of what a manager may do. */
Object.assign(HS_SVG, {
  hq: '<path d="M6 27V9.5L16 5l10 4.5V27" fill="none" stroke="#fff" stroke-width="2.3" stroke-linejoin="round"/><path d="M11 13h3M18 13h3M11 18h3M18 18h3M14 27v-5h4v5" stroke="#fff" stroke-width="2.3" stroke-linecap="round" fill="none"/>', // (2.99.274) 🏢 AN HQ
  sendrc: '<path d="M8 4.5h16v23l-2.7-1.8-2.6 1.8-2.7-1.8-2.7 1.8-2.6-1.8L8 27.5z" fill="none" stroke="#fff" stroke-width="2.3" stroke-linejoin="round"/><path d="M12 10.5h8M12 15h8M12 19.5h5" stroke="#fff" stroke-width="2.3" stroke-linecap="round"/>', // (2.99.141) 🧾 Send receipt
  giftcard: '<rect x="5" y="10.5" width="22" height="15.5" rx="2.5" fill="none" stroke="#fff" stroke-width="2.4"/><path d="M5 15.5h22M16 10.5v15.5" stroke="#fff" stroke-width="2.4"/><path d="M16 10.5c-1.6-4.2-6.6-4.8-6.6-2 0 1.8 3.4 2 6.6 2zm0 0c1.6-4.2 6.6-4.8 6.6-2 0 1.8-3.4 2-6.6 2z" fill="none" stroke="#fff" stroke-width="2.2" stroke-linejoin="round"/>',
  closeday: '<rect x="6" y="5" width="20" height="23" rx="2.5" fill="none" stroke="#fff" stroke-width="2.4"/><path d="M11 11h10M11 15.5h10" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/><path d="M11.5 21.5l3 3 6-6.5" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>',
  report: '<rect x="5" y="4" width="22" height="24" rx="3" fill="none" stroke="#fff" stroke-width="2.4"/><path d="M10 22v-4M16 22v-8M22 22v-11" stroke="#fff" stroke-width="2.8" stroke-linecap="round"/>', // (2.99.147)
  payroll: '<rect x="4" y="9" width="24" height="15" rx="2.5" fill="none" stroke="#fff" stroke-width="2.4"/><circle cx="16" cy="16.5" r="3.6" fill="none" stroke="#fff" stroke-width="2.4"/><path d="M8.5 13v.01M23.5 20v.01" stroke="#fff" stroke-width="3" stroke-linecap="round"/>',
  winback: '<path d="M8 13a9 9 0 1 1 1.5 9.5" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/><path d="M7.5 7.5V13h5.5" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/><path d="M16 21s-4-2.5-4-5.6a2.2 2.2 0 0 1 4-1.3 2.2 2.2 0 0 1 4 1.3c0 3.1-4 5.6-4 5.6z" fill="#fff"/>',
  customers: '<circle cx="12.5" cy="12" r="4.2" fill="none" stroke="#fff" stroke-width="2.4"/><path d="M4.5 25.5c0-4.2 3.6-6.5 8-6.5s8 2.3 8 6.5" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/><path d="M20.5 7.8a4.2 4.2 0 0 1 0 8.4M23.5 19.3c2.4.8 4 2.8 4 6.2" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/>',
  turnview: '<rect x="4.5" y="6.5" width="23" height="20" rx="2.5" fill="none" stroke="#fff" stroke-width="2.3"/><path d="M4.5 11.5h23M11 11.5v15M17.5 11.5v15" stroke="#fff" stroke-width="2"/><path d="M7 16h2M13.5 16h2M20 20h4" stroke="#fff" stroke-width="2.6" stroke-linecap="round"/>', // (2.99.362 – lệnh 604)
  turn: '<path d="M6 16a10 10 0 0 1 17.3-6.8M26 6v5h-5M26 16a10 10 0 0 1-17.3 6.8M6 26v-5h5" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>',
  staff: '<circle cx="16" cy="11" r="5" fill="none" stroke="#fff" stroke-width="2.4"/><path d="M6.5 27c0-5.2 4.3-8 9.5-8s9.5 2.8 9.5 8" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/>',
  reports: '<path d="M7 26V16M13 26V8M19 26v-7M25 26V12M4.5 26.5h23" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round"/>',
  y1099: '<path d="M8 4.5h11l5 5v18H8z" fill="none" stroke="#fff" stroke-width="2.4" stroke-linejoin="round"/><path d="M19 4.5v5h5" fill="none" stroke="#fff" stroke-width="2.2" stroke-linejoin="round"/><text x="16" y="22.5" text-anchor="middle" font-family="-apple-system,BlinkMacSystemFont,Arial,sans-serif" font-size="7.6" font-weight="800" fill="#fff">1099</text>',
  settings: '<circle cx="16" cy="16" r="4.2" fill="none" stroke="#fff" stroke-width="2.4"/><path d="M16 4.5l2 .3.7 2.7 2.1 1.2 2.7-.8 1.4 1.4-.8 2.7 1.2 2.1 2.7.7.3 2-.3 2-2.7.7-1.2 2.1.8 2.7-1.4 1.4-2.7-.8-2.1 1.2-.7 2.7-2 .3-2-.3-.7-2.7-2.1-1.2-2.7.8-1.4-1.4.8-2.7-1.2-2.1-2.7-.7-.3-2 .3-2 2.7-.7 1.2-2.1-.8-2.7 1.4-1.4 2.7.8 2.1-1.2.7-2.7z" fill="none" stroke="#fff" stroke-width="2.2" stroke-linejoin="round"/>',
});
HS_SVG.sellgift = HS_SVG.giftcard; // (2.99.443) 🎁 Sell gift card: the Gift card drawing
const HOME = [ // [group title, [[key, label, color, badge]]]
  ['Daily', [['checkout', 'Checkout', '#16A085'], ['sendrc', 'Send receipt', '#0A84FF', 'rq'], ['checkin', 'Check-in', '#5856D6'], ['appts', 'Appointments', '#E5533D', 'ap'], ['book', 'Book', '#2F6FE0']]],
  ['Money', [['co', 'Checkout', '#16A085'] /* (25/10/2026 – 2.99.410) Checkout left the bottom bar and Daily left Home: the owner's Checkout is here */, ['report', 'Report today', '#5E5CE6'], ['giftcard', 'Gift history', '#2E9E4F'], ['closeday', 'Close day', '#0A84FF'], ['payroll', 'Payroll', '#34A853'], ['sellgift', 'Sell gift card', '#2E9E4F'] /* (2.99.443 – CHAT 05:03, anh Logan 00:01) at the END: the same Sell gift card as Receipts */]], // (2.99.145) HOME GỌN (SO-LUAT 07/10): setup pages only in Settings (replaces 2.99.118)
  ['Customers', [['reminder', 'Reminder', '#F08A24', 'msg'], ['review', 'Review', '#E8A800', 'rv'], ['bday', 'Birthday', '#E4497F', 'bd'], ['refer', 'Refer', '#2E9E4F', 'rf'],
    ['winback', 'Win-back', '#FF6B3D'], ['customers', 'Customers', '#30B0C7'], ['s-ash', 'Auto STOP', '#8E2DE2', 'stop'], ['s-asend', 'Auto send', '#0A84FF']]], // Auto STOP moved here (its red number stays)
  ['Techs', [['turn', 'Turn', '#16A085'], ['turnview', 'Turn view', '#0E7C86'], ['staff', 'Staff', '#AF52DE'], ['reports', 'Reports', '#FF9500'], ['y1099', '1099', '#636366']]],
  // (25/10/2026 – anh Logan) every Settings page as an icon on Home too (the ones Home already has – Customers, Win-back, Gift card, Staff, Auto STOP, Auto send – not twice); color = its Settings icon
  ['Salon', [['s-salon', 'Salon info'], ['s-apps', 'Install apps'], ['s-hours', 'Hours'], ['s-services', 'Services'], ['s-turn', 'Turn rules'], ['s-rotation', 'Turn order'], ['s-receipt', 'Receipt'], ['s-look', 'Appearance' /* (2.99.503 – LỆNH 500 a) was 'Look' */]].map(([k, t]) => [k, t, null])],
  ['Booking & iPads', [['s-online', 'Online booking'], ['s-checkin', 'Check-in iPad'], ['s-desk', 'Front desk'], ['s-thanks', 'Thank-you'], ['s-gallery', 'Gallery'], ['s-colors', 'Polish colors'], ['s-bstats', 'Booking stats'], /* (2.99.524) Service time left Home */ ['s-bookprice', 'Prices online'] /* (2.99.489 – LỆNH 488 a) */].map(([k, t]) => [k, t, null])],
  ['Money setup', [['s-pay', 'Checkout & tax'], ['s-loyalty', 'Rewards'], ['s-offers', 'Offers'], ['s-referral', 'Referral setup']].map(([k, t]) => [k, t, null])],
  ['Texts & alerts', [['s-sms', 'Text messages'], ['s-smstpl', 'SMS templates'], ['s-notify', 'Notifications'], ['s-promo', 'Custom promo'], ['s-birthday', 'Birthday texts'], ['s-review', 'Google reviews']].map(([k, t]) => [k, t, null, k === 's-review' ? 'rv' : null])] /* (2.99.437 – CHAT 28/10 03:05) Google reviews: the red number = today's customers to ask */,
  ['Safety & records', [['s-backup', 'Backup'], ['s-activity', 'Activity log'], ['s-audit', 'Money log'], ['s-testmode', 'Test mode'], ['s-test', 'Test numbers'], ['s-account', 'Account']].map(([k, t]) => [k, t, null])],
  ['Settings', [['settings', 'Settings', '#8E8E93'], ['hq', 'AN HQ', '#101826']]], // (2.99.274 – order 486) 🏢 the owner only (American Nails, HQ allows it)
];
const HOME_MGR = ['checkout', 'sendrc', 'checkin', 'appts', 'book', 'closeday', 'turnview']; // (2.99.362 – lệnh 604) + Lịch theo turn // (2.99.141) + 🧾 Send receipt (managers may text receipts – SO-LUAT 07/10) // (2.99.137) + Check-in (SO-LUAT 07/10) // a manager: only what a manager may do (Close day: today only)
/** (2.99.499 – LỆNH 499 a, anh Logan 30/10) the owner's Home page 1 'Daily': shortcuts to the pages used every day (the same icons stay in their own groups). Keys 'd-…' = the icon without 'd-' (opens the same page). */
const OWN_DAILY = ['Daily', [['d-co', 'Checkout', '#16A085'], ['d-history', 'Receipts', '#6B7A90'] /* (2.99.538 - anh Logan 30/10 17:38) Receipts left the dock: here */, ['d-turn', 'Turn', '#16A085'], ['d-customers', 'Customers', '#30B0C7'], ['d-sellgift', 'Sell gift card', '#2E9E4F'], ['d-report', 'Report today', '#5E5CE6'], ['d-closeday', 'Close day', '#0A84FF'], ['d-payroll', 'Payroll', '#34A853'], ['d-reports', 'Reports', '#FF9500']]]; /* (2.99.521  CHAT, anh Logan 30/10 01:41 'Daily khng hp l') 8 = two full rows, in the order of the day: Checkout  Turn  Customers  Gift card / Report today  Close day  Payroll  Reports (1099 = once a year  Techs; Messages = the dock) */
const HS_APPS = HOME.flatMap(([, l]) => l).map(([k, t, c, f]) => [k, t, c, f || null]);
/* (2.99.467 – LỆNH 467) the owner's Home: the glossy iPhone-like pictures (made by the video task, Downloads\\LENH-ICON-HOME-467.txt) – the line drawing stays under it if a picture cannot load */
const HS_IMG = new Set(['history','bday','closeday','co','customers','giftcard','hq','payroll','refer','reminder','report','reports','review','s-account','s-activity','s-apps','s-asend','s-ash','s-audit','s-backup','s-birthday','s-bstats','s-checkin','s-colors','s-desk','s-gallery','s-hours','s-look','s-loyalty','s-notify','s-offers','s-online','s-pay','s-payroll','s-promo','s-receipt','s-referral','s-review','s-rotation','s-salon','s-services','s-sms','s-smstpl','s-svctime','s-test','s-testmode','s-thanks','s-turn','sellgift','settings','staff','turn','turnview','winback','y1099']);
const hsFmt = (n) => n > 99 ? '99+' : String(n);
/** (2.99.118) a Home icon's drawing: its own, or for a Settings page ("s-pay") the white line drawing of that Settings row (24-unit) */
const hsSvg = (k) => k === 'co' ? hsSvg('checkout') : k.startsWith('s-') ? `<svg viewBox="0 0 24 24" aria-hidden="true">${(SET_IC[k.slice(2)] || [, ''])[1]}</svg>` : `<svg viewBox="0 0 32 32" aria-hidden="true">${HS_SVG[k]}</svg>`;
const HOME_GC = { 'Daily': '#2F6FE0', 'Money': '#34A853', 'Customers': '#E4497F', 'Techs': '#AF52DE', 'Salon': '#1F4E8C', 'Booking & iPads': '#FF9500', 'Money setup': '#1E8E4E', 'Texts & alerts': '#30B0C7', 'Safety & records': '#636366', 'Settings': '#8E8E93' };
function homeHTML() {
  return `<h2 class="visually-hidden">Home</h2><div id="hmGs"></div><div id="hmRp">${typeof rpHTML === 'function' ? rpHTML() : ''}</div>${IS_MGR ? '' : '<div class="hm-pager" id="hmPager">' /* (2.99.467 – LỆNH 467, anh Logan 29/10) the owner's Home like the iPhone: ONE group = ONE screen, swipe sideways to the next group */}${(IS_MGR ? HOME : hmLayout([OWN_DAILY] /* (2.99.499 – LỆNH 499 a) page 1 */.concat(typeof showGroup === 'function' ? showGroup() : []) /* (2.99.478 – LỆNH 466) the show salon: page 'Demo' first */.concat(['Salon', 'Techs', 'Money', 'Customers'].map(g => HOME.find(([gt]) => gt === g)).filter(Boolean)).concat(HOME.filter(([gt]) => !['Salon', 'Techs', 'Money', 'Customers', 'Daily' /* (2.99.499) the manager's Daily – the owner has OWN_DAILY */].includes(gt)))) /* (2.99.477 – LỆNH 470) the owner's own order (hold + drag) */) /* (25/10/2026 anh Logan) the owner's Home: Salon on top, then Techs, Money, Customers, then the other Settings groups */.filter(([gt, list]) => IS_MGR || gt !== 'Settings' && (gt !== 'Daily' || list.some(([k]) => k.startsWith('d-')) /* (2.99.499) only the owner's own Daily */) /* (25/10/2026 anh Logan) no Settings group at the bottom: every Settings page has its own icon above */ /* (25/10/2026 anh Logan) the owner's Home: no Daily group – Checkout / Check-in / Appointments / Receipts are in the bottom menu, + Book on top */).map(([gt, list]) => { const l = list.filter(([k]) => (!IS_MGR || HOME_MGR.includes(k)) && (k !== 'hq' || (!IS_MGR && S.hqOpen)) && (k !== 's-asend' || S.asCan !== false) && (k !== 's-thanks' || S.main !== false) && (!['s-apps', 's-backup', 's-testmode', 's-test', 's-receipt' /* (2.99.479 – LỆNH 474b) Receipt: NailFlow support only */].includes(k) || !!S.support) /* (25/10/2026 anh Logan) Install apps, Backup, Test mode, Test numbers: hidden from the salon – only NailFlow support (opened from AN HQ) sees them */ && (k !== 's-svctime' || S.svcHas !== false)); const sec = !IS_MGR; return l.length ? `${sec ? `<section class="home-sec" data-g="${esc(gt)}" style="--gc:${HOME_GC[gt] || '#8E8E93'}">` : ''}<h3 class="home-gh">${esc(gt)}</h3>
    <div class="hs-grid home-grid" role="group" aria-label="${esc(gt)}">${l.map(([k, t, c, f]) => `<button type="button" class="hs-app" data-app="${k}"><span class="hs-ic" style="background:${c || ((typeof SET_IC !== 'undefined' && SET_IC[k.slice(2)]) || [])[0] || '#8E8E93'}">${hsSvg(k.replace(/^d-/, ''))}${!IS_MGR && HS_IMG.has(k.replace(/^d-/, '')) ? `<img class="hs-img" src="../assets/home-ic/${k.replace(/^d-/, '')}.webp?v=516" alt="" decoding="async">` : ''}${f && (!IS_MGR || f === 'rq') ? `<i class="hs-badge"${HS[f] ? '' : ' hidden'}>${hsFmt(HS[f])}</i>` : ''}</span><span class="hs-lb">${esc(k === 'reminder' && S.android ? 'Messages' : t)}</span></button>`).join('')}</div>${sec ? '</section>' : ''}` : ''; }).join('')}${IS_MGR ? '' : `</div><div class="hm-info" id="hmInfo"><div class="hm-lang" data-raw role="group" aria-label="Language / Ngôn ngữ">${[['en', 'English'], ['vi', 'Tiếng Việt']].map(([k, l]) => `<button type="button" data-lang="${k}" class="${window.I18N && I18N.lang && I18N.lang() === k ? 'on' : ''}">${l}</button>`).join('')}</div><b>NailFlowApp</b><br>Support: <a href="tel:+16016666677">(601) 666-6677</a><br><button type="button" class="hm-out" id="hmOut">${esc(LV('Log out', 'Thoát'))}</button></div>` /* (2.99.476 – LỆNH 473, anh Logan 30/10) the owner's Home, at the bottom: app + version, the support phone (this line only) */}${IS_MGR ? '' : '<div class="hm-dots" id="hmDots" role="tablist" aria-label="Home pages"></div>'}${'' /* (2.99.468 – LỆNH 468) the big red Log out left Home: it is the small "Log out" at the left of the bottom bar (owner) */}`; // (2.99.253 – order 458) Log out at the end of Home
}
/** (2.99.467 – LỆNH 467) Home pages (one group each): the dots under them (tap = that page), the page kept when Home is drawn again. Swiping = the browser's own scroll-snap. */
function hmPagerBind(root) {
  $$('img.hs-img', root).forEach(i => i.addEventListener('error', () => i.remove(), { once: true }));
  const pg = $('#hmPager', root), dots = $('#hmDots', root); if (!pg || !dots) return;
  const secs = $$('.home-sec', pg); if (secs.length < 2) { dots.hidden = true; return; }
  const step = () => pg.clientWidth + (parseFloat(getComputedStyle(pg).columnGap) || 0);
  dots.innerHTML = secs.map((s, i) => `<button type="button" class="hm-dot" role="tab" data-i="${i}" aria-label="${esc((s.querySelector('.home-gh') || {}).textContent || String(i + 1))}"></button>`).join('');
  const mark = () => { const i = Math.max(0, Math.min(secs.length - 1, Math.round(pg.scrollLeft / Math.max(1, step())))); S.hmPage = i;
    $$('.hm-dot', dots).forEach((d, k) => { d.classList.toggle('on', k === i); d.setAttribute('aria-selected', k === i ? 'true' : 'false'); }); };
  $$('.hm-dot', dots).forEach(d => d.addEventListener('click', () => pg.scrollTo({ left: +d.dataset.i * step(), behavior: 'smooth' })));
  pg.addEventListener('scroll', () => { clearTimeout(pg._t); pg._t = setTimeout(mark, 60); }, { passive: true });
  pg.addEventListener('keydown', (e) => { if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return; const i = (S.hmPage || 0) + (e.key === 'ArrowRight' ? 1 : -1); if (i < 0 || i >= secs.length) return; e.preventDefault(); pg.scrollTo({ left: i * step(), behavior: 'smooth' }); });
  const i0 = Math.min(S.hmPage || 0, secs.length - 1); pg.scrollLeft = i0 * step(); requestAnimationFrame(() => { pg.scrollLeft = i0 * step(); mark(); });
  hmArrBind(root, pg, dots, step, mark); /* (2.99.477 – LỆNH 470) */
}
/** (2.99.477 – LỆNH 470, anh Logan 30/10) the owner's Home groups in the salon's own order: S.homeLayout = {group: [icon keys]} (saved on the server – every device the same).
 *  An icon not in the layout yet (new) stays at the end of its own group; an icon moved to another group leaves its own; hidden icons (permissions) are still hidden later (homeHTML filter). */
/* (2.99.540 - anh Logan 30/10 18:44) OTHER salons: the setup / technical pages are hidden from the owner - they show only in a NailFlow support session (AN HQ -> Xin vao ho tro). American Nails: everything as before. */
var SUP_ONLY = new Set([/* (2.99.636 - LENH 636 LUAT CHUNG AN / MO, anh Logan 22:07): only the pages that are NailFlow's entirely (texting phone, Auto STOP, backups, test tools); the rest is the salon's own */ 'ash','asend','backup','testmode','test']);
function supHideSet(k) { return typeof S !== 'undefined' && !IS_MGR && !S.support && !S.anOwn && !!SUP_ONLY && SUP_ONLY.has(String(k)); } /* var + guard: safe even if called before this line runs */
function supHideHome(k) { k = String(k).replace(/^d-/, ''); return k.startsWith('s-') && supHideSet(k.slice(2)); }
function hmLayout(groups) {
	groups = groups.map(([gt, list]) => [gt, list.filter(it => !supHideHome(it[0]))]).filter(([, l]) => l.length); /* (2.99.540) */
  const L = S.homeLayout; if (!L || typeof L !== 'object') return groups;
  const def = {}; HOME.concat(groups).forEach(([, list]) => list.forEach(it => { if (!def[it[0]]) def[it[0]] = it; }));
  const placed = new Set(); Object.values(L).forEach(a => Array.isArray(a) && a.forEach(k => placed.add(k)));
  return groups.map(([gt, list]) => { const mine = Array.isArray(L[gt]) ? L[gt].map(k => def[k]).filter(Boolean).filter(it => !supHideHome(it[0])) : [];
    return [gt, mine.concat(list.filter(([k]) => !placed.has(k)))]; });
}
/** (2.99.477 – LỆNH 470) hold an icon ~0.6s → arrange: icons wiggle, a tap never opens; drag = move (in the page; held at the left/right edge ~0.5s = the next page);
 *  "Done" saves for the salon, "Reset to default" (asked first, inside the app) = the first order again. Swiping the pages without holding = as before. */
/* (2.99.529 - CHAT, anh Logan 30/10 02:23 'Daily and Money both have Close day - remove every icon that is twice') the owner's Home: an icon on Daily (or Messages, in the dock)
   is not shown again on the other pages; Money then only had Gift card -> Gift card joins Customers and the Money page goes; a page left empty is not shown. Managers: unchanged (hmLayout = owner only). */
(function () { const base = hmLayout; hmLayout = function (groups) { const out = base(groups); const daily = out.find(([gt]) => gt === 'Daily');
const dup = new Set(['reminder'].concat(daily ? daily[1].map(([k]) => k.replace(/^d-/, '')) : [])); let gift = null;
return out.map(([gt, l]) => { if (gt === 'Daily') return [gt, l]; return [gt, l.filter(it => { const k = String(it[0]).replace(/^d-/, ''); if (gt === 'Money' && k === 'giftcard' && !dup.has(k)) { gift = it; return false; } return !dup.has(k); })]; })
.map(([gt, l]) => gt === 'Customers' && gift && !l.some(x => x[0] === 'giftcard') ? [gt, l.concat([gift])] : [gt, l]).filter(([, l]) => l.length); }; })();
function hmArrBind(root, pg, dots, step, mark) {
  if (IS_MGR || IS_DESK) return; S.hmArr = false; document.body.classList.remove('hm-arranging');
  let press = null, drag = null;
  const pt = (e) => ({ x: e.clientX, y: e.clientY });
  const bar = () => {
    let b = $('#hmArrBar', root); if (b) return b;
    b = document.createElement('div'); b.id = 'hmArrBar'; b.className = 'hm-arr-bar';
    b.innerHTML = `<button type="button" class="hm-arr-reset">${esc(LV('Reset to default', 'Về mặc định'))}</button><div class="hm-arr-ask"></div>`; /* (2.99.488 – LỆNH 477d) no 'Done': a drop saves and leaves by itself */
    pg.parentNode.insertBefore(b, pg);
    b.addEventListener('pointerdown', () => clearTimeout(outT)); // (2.99.488) Reset to default being used: stay
    $('.hm-arr-reset', b).addEventListener('click', () => confirmIn($('.hm-arr-ask', b), LV('Put every Home icon back in its first place? (every phone of the salon)', 'Đưa tất cả icon Home về chỗ ban đầu? (mọi máy của tiệm)'), LV('Reset', 'Về mặc định'), reset, true, LV('Go back', 'Quay lại')));
    return b;
  };
  const enter = () => { if (S.hmArr) return; S.hmArr = true; pg.classList.add('hm-arr'); pg.style.overflowX = 'hidden'; pg.style.touchAction = 'none'; /* (2.99.501 – LỆNH 477e) the phone must not take the finger as a page swipe (pointercancel) */ document.body.classList.add('hm-arranging'); bar().hidden = false; try { navigator.vibrate && navigator.vibrate(12); } catch (e) {} };
  const leave = () => { clearTimeout(outT); S.hmArr = false; pg.classList.remove('hm-arr'); pg.style.overflowX = ''; pg.style.touchAction = ''; document.body.classList.remove('hm-arranging'); const b = $('#hmArrBar', root); if (b) b.remove(); };
  const now = () => { const o = {}; $$('.home-sec', pg).forEach(s => { o[s.dataset.g] = $$('.hs-app', s).map(b => b.dataset.app); }); return o; };
  // (2.99.483 – LỆNH 477b) each drop saves by itself; not saved (no internet…) → a small note, the order stays on this phone and the next drop saves it again
  let dirty = false, outT = 0; // (2.99.488 – LỆNH 477d) ~1.5 s after a drop with nothing else held / dragged → out of arranging
  // (2.99.501 – LỆNH 477e) drops in a row → ONE save ~0.6 s after the last drop; a save replaced by a newer one / cancelled → no message; the order is kept on screen at once
  let saveT = 0, seq = 0;
  function autosave() { dirty = true; S.homeLayout = now(); clearTimeout(saveT); saveT = setTimeout(saveNow, 600); }
  async function saveNow(again) { clearTimeout(saveT); const my = ++seq, lay = now(); S.homeLayout = lay;
    try { await api('save_settings', { home_layout: lay }); if (my === seq) dirty = false; }
    catch (err) { if (my !== seq || (err && err.name === 'AbortError')) return; if (!again && navigator.onLine !== false) { setTimeout(() => { if (my === seq && dirty) saveNow(true); }, 1000); return; } /* online: once more, quietly; offline: say so now */ toast(LV('Not saved – try again', 'Chưa lưu được – thử lại'), 2500, null, true); } }
  function done() { if (dirty) saveNow(); leave(); }
  async function reset() { try { await api('save_settings', { home_layout: null }); } catch (err) { toast((err && err.message) || LV('Not saved – try again', 'Chưa lưu được – thử lại')); return; }
    S.homeLayout = null; leave(); S.hmNoClick = Date.now() + 400; if (typeof goHome === 'function') goHome(); toast(LV('Home is back to default', 'Home đã về mặc định')); }
  // dragging: a copy follows the finger; the icon itself (faded) moves in the grids
  const startDrag = (btn, p) => { // (2.99.483 – LỆNH 477b) the copy = the icon tile itself, the SAME size as on Home (was the 512 picture), round corners, a shadow
    const ic = $('.hs-ic', btn) || btn, r = ic.getBoundingClientRect(), cs = getComputedStyle(ic); const ghost = ic.cloneNode(true); ghost.classList.add('hm-drag-ghost'); $$('.hs-badge', ghost).forEach(x => x.remove());
    Object.assign(ghost.style, { width: r.width + 'px', height: r.height + 'px', left: r.left + 'px', top: r.top + 'px', borderRadius: cs.borderRadius, backgroundColor: cs.backgroundColor, backgroundImage: cs.backgroundImage }); document.body.appendChild(ghost);
    btn.classList.add('hm-drag-src'); drag = { btn, ghost, moved: false, dx: p.x - r.left, dy: p.y - r.top, edge: 0, edgeT: 0, last: p, home: [btn.parentNode, btn.nextSibling], keys: allKeys() }; // (2.99.501 – LỆNH 477e) where it came from + every icon (a drop never loses one)
  };
  const allKeys = () => $$('.hs-app', pg).map(b => b.dataset.app).sort().join(',');
  const moveDrag = (p) => {
    const d = drag; d.moved = true; d.last = p; d.ghost.style.left = (p.x - d.dx) + 'px'; d.ghost.style.top = (p.y - d.dy) + 'px';
    const pr = pg.getBoundingClientRect(); const side = pg.scrollWidth <= pg.clientWidth + 2 ? 0 /* (2.99.500 – LỆNH 499 b) big screen: every group on one screen, no page to flip to */ : p.x < pr.left + 40 ? -1 : p.x > pr.right - 40 ? 1 : 0; /* (2.99.501 – LỆNH 477e) 28 → 40px: the left edge reached before the phone's own edge swipe */
    if (side !== d.edge) { d.edge = side; clearTimeout(d.edgeT); if (side) { const flip = () => { const i = (S.hmPage || 0) + side, n = $$('.home-sec', pg).length; if (i < 0 || i >= n) return;
      pg.scrollLeft = i * step(); S.hmPage = i; requestAnimationFrame(mark); /* (2.99.501 – LỆNH 477e) at once – a smooth scroll under the finger makes the phone cancel it */ d.edgeT = setTimeout(flip, 1100); }; d.edgeT = setTimeout(flip, 500); } }
    const el = document.elementFromPoint(p.x, p.y); if (!el || !pg.contains(el)) return;
    const over = el.closest('.hs-app'); const grid = el.closest('.home-grid') || (el.closest('.home-sec') && $('.home-grid', el.closest('.home-sec')));
    if (over && over !== d.btn) { const q = over.getBoundingClientRect(); const after = p.x > q.left + q.width / 2; over.parentNode.insertBefore(d.btn, after ? over.nextSibling : over); }
    else if (!over && grid && d.btn.parentNode !== grid) { const last = [...grid.children].pop(); if (!last || last.getBoundingClientRect().bottom < p.y || last.getBoundingClientRect().right < p.x || (last.getBoundingClientRect().bottom > p.y && last.getBoundingClientRect().top < p.y)) grid.appendChild(d.btn); }
  };
  /** (2.99.501 – LỆNH 477e GẤP) a drop NEVER loses an icon: dropped on the page now shown but no place yet (the page just flipped, the finger held still)
   *  → at the END of that page's group; dropped outside the icons' area (dots, dock, off the screen) → back where it was; then every icon counted –
   *  one missing / twice → the order before, nothing saved. */
  const settle = (d) => { const back = () => { const [par, nx] = d.home; if (par && par.isConnected) par.insertBefore(d.btn, nx && nx.parentNode === par ? nx : null); };
    const p = d.last, pr = pg.getBoundingClientRect(), inside = p && p.x >= 0 && p.x <= innerWidth && p.y >= pr.top && p.y <= pr.bottom; /* the edges beside the pages count as the page shown */
    if (!inside) back();
    else { const secs = $$('.home-sec', pg), inR = (r) => p.x >= r.left && p.x <= r.right && p.y >= r.top && p.y <= r.bottom; // the page shown / the frame under the finger – by their boxes
      const sec = pg.scrollWidth > pg.clientWidth + 2 ? secs[Math.max(0, Math.min(secs.length - 1, Math.round(pg.scrollLeft / Math.max(1, step()))))] : secs.find(x => inR(x.getBoundingClientRect()));
      const g = sec && $('.home-grid', sec);
      if (g) { const on = $$('.hs-app', g).find(b => b !== d.btn && inR(b.getBoundingClientRect()));
        if (on) { const q = on.getBoundingClientRect(); g.insertBefore(d.btn, p.x > q.left + q.width / 2 ? on.nextSibling : on); }
        else if (!g.contains(d.btn)) g.appendChild(d.btn); } }
    if (allKeys() !== d.keys) { back(); if (allKeys() !== d.keys) { S.hmNoClick = Date.now() + 400; if (typeof goHome === 'function') goHome(); return false; } }
    return true; };
  const endDrag = (drop) => { if (!drag) return; const moved = drag.moved; clearTimeout(drag.edgeT); drag.ghost.remove(); drag.btn.classList.remove('hm-drag-src'); const dd = drag; drag = null; if (moved && !settle(dd)) drop = false; S.hmNoClick = Date.now() + 350; setTimeout(mark, 450); if (drop && moved) { autosave(); clearTimeout(outT); outT = setTimeout(() => { if (!press && !drag && S.hmArr && !$('#hmArrBar .hm-arr-ask .confirm', root)) leave(); }, 1500); } };
  pg.addEventListener('click', (e) => { if (S.hmArr && !e.target.closest('.hs-app') && Date.now() > (S.hmNoClick || 0)) done(); }); // (2.99.483 – LỆNH 477b) a tap on an empty place = out (like the iPhone)
  pg.addEventListener('pointerdown', (e) => {
    const btn = e.target.closest('.hs-app'); if (!btn || (e.pointerType === 'mouse' && e.button !== 0)) return; clearTimeout(outT); // (2.99.488) holding / dragging another icon: keep arranging
    press = { id: e.pointerId, btn, p0: pt(e), held: S.hmArr, t: S.hmArr ? 0 : setTimeout(() => { if (!press) return; press.held = true; S.hmNoClick = Date.now() + 700; enter(); }, 600) };
  });
  if (hmArrBind.off) hmArrBind.off(); // Home drawn again: the old page's listeners go
  const move = (e) => {
    if (!press || e.pointerId !== press.id || !pg.isConnected) return; const p = pt(e), far = Math.hypot(p.x - press.p0.x, p.y - press.p0.y);
    if (!press.held) { if (far > 10) { clearTimeout(press.t); press = null; } return; } // moved before 0.6s = an ordinary swipe
    if (!drag && far > 6) startDrag(press.btn, press.p0);
    if (drag) { e.preventDefault(); moveDrag(p); }
  };
  const up = (e) => { if (!press || e.pointerId !== press.id) return; clearTimeout(press.t);
    press = null; endDrag(true); }; // (2.99.501 – LỆNH 477e) pointercancel (the phone took the touch) = a DROP where the finger was – never 'cancelled, icon gone'
  // the finger holding an icon: no page scroll under it – on the whole window (the finger may leave the pager)
  const tMove = (e) => { if (press && press.held) e.preventDefault(); };
  window.addEventListener('touchmove', tMove, { passive: false });
  window.addEventListener('pointermove', move, { passive: false }); window.addEventListener('pointerup', up); window.addEventListener('pointercancel', up);
  hmArrBind.off = () => { window.removeEventListener('pointermove', move); window.removeEventListener('pointerup', up); window.removeEventListener('pointercancel', up); window.removeEventListener('touchmove', tMove); endDrag(); };
  // the finger holding an icon: the page must not scroll under it (the phone's own scroll would take the touch)
  pg.addEventListener('touchmove', (e) => { if (press && press.held) e.preventDefault(); }, { passive: false });
  pg.addEventListener('contextmenu', (e) => { if (e.target.closest('.hs-app')) e.preventDefault(); });
  pg.addEventListener('dragstart', (e) => e.preventDefault());
}
/** (2.99.259 – order 469) Log out: in the app, its key is dropped too (the password + the code next time). */
async function ownerOut() { let t = null; window.__nfOut = 1; try { if (window.NFNative && NFNative.pushOff) await NFNative.pushOff(); /* (2.99.262) the app token goes too */
    // (2.99.317 – lệnh 541) in the app: the salon stays on this phone – the next sign-in is the salon's box + Face ID (the key is kept, Face ID first); elsewhere: gone as before
    if (window.NFNative && NFNative.bioNext) await NFNative.bioNext('admin'); else if (window.NFNative && NFNative.tok) { t = await NFNative.tok('admin'); await NFNative.forget('admin'); } } catch (e) {} try { await api('logout', { appTok: t ? t.tok : '' }); } catch (e) {} }
/** (2.99.506 – LỆNH 503) the owner's Log out (Home bottom, Settings last row): the same as the dock's old button – in the app Face ID next time. */
async function ownerLogOut(b) { if (b) b.disabled = true; try { await ownerOut(); S.csrf = null; try { if (window.NFNative && NFNative.loggedOut) NFNative.loggedOut(); } catch (e) {} if (typeof showLogin === 'function') showLogin(); else location.reload(); } finally { if (b) b.disabled = false; } }
function bindHs(root) { $('#hmOut', root)?.addEventListener('click', (e) => ownerLogOut(e.currentTarget)); if (typeof bindLang === 'function') bindLang($('#hmInfo', root) || document.createElement('div')); /* (639v) */
  hmPagerBind(root); /* (2.99.467 – LỆNH 467) */ if (typeof gsLoad === 'function') gsLoad(root); /* (2.99.218 – order 419) Getting started */ $$('.hs-app', root).forEach(b => b.addEventListener('click', () => { if (S.hmArr || Date.now() < (S.hmNoClick || 0)) return; /* (2.99.477 – LỆNH 470) arranging: a tap never opens */ homeGo(b.dataset.app); })); if (typeof rpBind === 'function') rpBind($('#hmRp', root)); }
/** An icon on Home: its page (bottom-menu pages and Receipts tabs straight away, lists as a full page, Settings pages with ‹ Home). */
function homeGo(k) {
  if (k === 'guide' && S.showapp) return openGuide(); if (k === 'showreset' && S.showapp) return showReset(); // (2.99.478 – LỆNH 466) the show salon only
  if (k.startsWith('d-')) k = k.slice(2); // (2.99.499 – LỆNH 499 a) Daily shortcut = the icon itself
  if (k === 'co') k = 'checkout'; // (2.99.410) Money → Checkout (owner)
  if (IS_MGR && !HOME_MGR.includes(k)) return;
  const tab = (t) => { S.fromHome = true; setTab(t); };
  const hist = (v) => { H.view = v; tab('history'); };
  const sec = (x) => { S.home = 'sec'; S.setSec = x; S.secFromHome = true; $('#p-settings').scrollTop = 0; renderSettings(); };
  const page = (fn) => { S.pageMode = true; Promise.resolve(fn()).catch(oops); };
  if (k.startsWith('s-')) return sec(k.slice(2)); // (2.99.118) a Settings page straight from Home ("‹ Home" goes back)
  if (k === 'hq') { if (IS_MGR || !S.hqOpen) return; api('hq_open', {}).then(r => { location.href = r.url; }).catch(oops); return; } // (2.99.274 – order 486) one-time pass into AN HQ
  switch (k) {
    case 'checkout': return tab(k); // (25/10 Logan) owner's Checkout from Home = admin Checkout, Home back without password (was qdOn checkout mode) // (2.99.322 – lệnh 539 mục 11)
    case 'checkin': case 'appts': return tab(k);
    case 'book': return page(openBook);
    case 'sendrc': return page(openSendReceipts); // (2.99.141)
    case 'history': return hist('receipts');
    case 'giftcard': return sec('gift');
    case 'sellgift': return openGiftSell(); // (2.99.443) the Sell gift card window Receipts opens (the same flow)
    case 'closeday': return IS_MGR ? page(() => openCloseDay(S.today || localToday())) : hist('close');
    case 'report': return hist('today'); // (2.99.147) Report today (owner)
    case 'payroll': return hist('payroll');
    case 'reports': return hist('reports');
    case 'y1099': return hist('yearend');
    case 'reminder': S.thread = null; M.view = 'send'; return tab('messages');
    case 'review': return page(openReviewToday);
    case 'bday': return page(openBdayList);
    case 'refer': return page(openReferList);
    case 'winback': return sec('winback');
    case 'customers': return sec('customers');
    case 'staff': return sec('techs');
    case 'turn': return tab('turns');
    case 'turnview': return page(openTurnView); // (2.99.362 – lệnh 604)
    case 'settings': S.home = 'settings'; S.setSec = null; S.secFromHome = false; $('#p-settings').scrollTop = 0; return renderSettings();
  }
}
/** Back to the Home icons (from any page opened from Home). */
function goHome() { if (S.pageMode || !$('#sheet').hidden) closeSheet(); S.fromHome = false; S.home = null; S.setSec = null; S.secFromHome = false; setTab('settings'); }
function hsSync() {
  HS_APPS.forEach(([k, , , f]) => { if (!f) return; document.querySelectorAll(`.hs-app[data-app="${k}"] .hs-badge, .hs-app[data-app="d-${k}"] .hs-badge`).forEach(b => { b.hidden = !HS[f]; b.textContent = hsFmt(HS[f]); }); }); // (2.99.499) + the Daily shortcut
  { const mb = $('#tabMsgBdg'); if (mb) { mb.hidden = !HS.msg; mb.textContent = hsFmt(HS.msg); } } /* (2.99.512) the dock's Messages */ const d = $('#setDot'); if (d) d.hidden = IS_MGR ? !HS.rq : !(HS.msg || HS.rv || HS.bd || HS.rf || HS.rq || HS.ap);
}
/* (2.99.32) "⭐ Review": today's check-ins – the owner asks for a Google review from his own iPhone (the web sends nothing) */
const setRvBadge = (n) => { if (typeof n !== 'number') return; S.rvDue = n; HS.rv = n; hsSync(); };
$('#btnReview')?.addEventListener('click', () => openReviewToday());
/* (2.99.33) "🎂": birthdays in the next 21 days – the owner texts the salon's birthday template from his own iPhone (the web sends nothing) */
const setBdBadge = (n) => { if (typeof n !== 'number') return; S.bdDue = n; HS.bd = n; hsSync(); };
$('#btnBday')?.addEventListener('click', () => openBdayList());
/* (2.99.43) "Refer": customers who came 2–3 days ago, not asked to refer a friend in 90 days – Text opens Messages with the Referral template (the web sends nothing) */
const setRfBadge = (n) => { if (typeof n !== 'number') return; S.rfDue = n; HS.rf = n; hsSync(); };
const setRqBadge = (n) => { if (typeof n !== 'number' || IS_DESK) return; S.rqN = n; HS.rq = n; hsSync(); if (typeof showBadge === 'function') showBadge(); }; // (2.99.141) 🧾 Send receipt waiting
const setStopBadge = (n) => { if (typeof n !== 'number' || IS_MGR || IS_DESK) return; S.stopNew = n; HS.stop = n; hsSync(); showBadge(); }; // (2.99.124) Home → Auto STOP: new STOP + Check STOP cards; (2.99.125) also added to the app icon
$('#btnRefer')?.addEventListener('click', () => openReferList());
/* (2.99.122) "STOP" by hand: the customer replied STOP to the owner's iPhone (the web cannot see it) – the same save as Win-back STOP
   (winback_stop → opted_out = 1). Small gray button on Birthday / Refer / Review rows; asks once; the customer leaves the list. Owner only. */
const STOPPED = new Set();
const stopBtnH = (c) => !IS_MGR && !S.qa && c.phone && !c.stop ? `<button type="button" class="rvt-stop" data-stopph="${esc(c.phone)}">STOP</button><button type="button" class="rvt-stop rvt-wrong" data-stopph="${esc(c.phone)}" data-why="wrong">Wrong #</button>` : ''; // (2.99.144) + Wrong # (wrong number: the same as STOP)

/** (2.99.317 – lệnh 542) a page that could not load never stays on "Loading…": the reason + "↻ Try again". */
function loadFail(el, e, again) {
  if (!el) return; const vi = (typeof I18 === 'object' && I18.lang && I18.lang() === 'vi'); const m = (e && e.message) || String(e || '');
  el.innerHTML = `<div class="card load-fail"><p class="err" style="margin-top:0">⚠ ${vi ? 'Không tải được trang này' : 'This page could not load'}${m ? ': ' + esc(m) : ''}</p><button type="button" class="btn small" data-again>↻ ${vi ? 'Thử lại' : 'Try again'}</button></div>`;
  const b = el.querySelector('[data-again]'); if (b && typeof again === 'function') b.addEventListener('click', () => { el.innerHTML = '<p class="muted">Loading…</p>'; again(); });
}

/* (2.99.322 – lệnh 539 mục 11) Checkout mode: the owner taps Checkout → this login gets AN Desk rights only (the server refuses every admin action)
   and the AN Desk Checkout opens (cards, PIN, 🔒 Lock, Sell gift card, Receipts today, Messages, EN/VI). "👑 Admin" there + the owner password = back. */
async function qdOn() {
  try { const r = await api('qd_on', {}); location.replace(r.url); } catch (e) { oops(e); }
}
async function qdGo() {
  try { const r = await api('qd_state'); if (r.qmode && r.url) return location.replace(r.url); } catch (e) {}
  showLogin();
}
/* (2.99.322 – lệnh 539 mục 2) SET THIS DEVICE AS THE FRONT DESK (the owner, once): the device gets its own AN Desk code, the owner is signed out here
   (no owner session left on it) and from now on the app opens AN Desk only. Leaving it: the owner password (on the device), or Remove in Settings. */
function qdSetup() {
  const nm = /iPad|Macintosh/.test(navigator.userAgent) ? LV('Front desk iPad', 'iPad quầy') : LV('Front desk', 'Máy quầy');
  openSheet(`<h2>🖥 ${LV('Front desk', 'Máy quầy')}</h2>
    <p class="hint">This device will open <b>only AN Desk</b> (Checkout, Check-in, gift cards, receipts today, messages – each person's PIN). You will be <b>signed out</b> here.
      Leaving front desk mode needs your password.${LV('', '<br><i>Máy này sẽ chỉ mở AN Desk. Anh sẽ được đăng xuất trên máy này. Muốn thoát phải nhập mật khẩu chủ.</i>')}</p>
    <label class="fld"><span>${LV('Device name', 'Tên máy')}</span><input class="inp" id="qdName" maxlength="40" value="${esc(nm)}"></label>
    <p class="hint">Extra lock (optional): iPad → Settings → Accessibility → <b>Guided Access</b> on, then triple-click the side button in the app. Android → Settings → Security → <b>App pinning</b>.
      ${LV('', '<br><i>Khoá thêm (tuỳ chọn): iPad bật Guided Access (Trợ năng → Truy cập được hướng dẫn) rồi bấm 3 lần nút nguồn trong app. Android: Bảo mật → Ghim ứng dụng.</i>')}</p>
    <div class="row gap"><button type="button" class="btn" id="qdNo">${LV('Cancel', 'Huỷ')}</button><button type="button" class="btn primary" id="qdYes">🖥 ${LV('Set as front desk', 'Đặt làm Máy quầy')}</button></div>`);
  $('#qdNo').addEventListener('click', closeSheet);
  $('#qdYes').addEventListener('click', async (e) => { e.currentTarget.disabled = true;
    try {
      const r = await api('qd_dev_add', { name: $('#qdName').value });
      const full = new URL(r.url, location.href).href, hub = S.hub || '';
      try { localStorage.setItem('nfQd', full); if (hub) localStorage.setItem('nfQdHub', hub); } catch (x) {}
      let tok = ''; try { tok = window.NFNative && NFNative.tok ? (await NFNative.tok('admin')) || '' : ''; } catch (x) {}
      try { await api('logout', { appTok: tok, pushEp: (window.NFNative && NFNative.pushEp ? await NFNative.pushEp().catch(() => '') : '') }); } catch (x) {}
      try { if (window.NFNative && NFNative.forget) await NFNative.forget('admin'); } catch (x) {}
      location.replace(hub ? hub + (hub.includes('?') ? '&' : '?') + 'desk=' + encodeURIComponent(full) : full);
    } catch (y) { e.currentTarget.disabled = false; oops(y); } });
}
/* (2.99.561 - LENH 561, anh Logan 30/10 22:58) the owner: no dock in the pages (dockSync above), so every page has the red '‹ Home' at the top, still while scrolling:
   Messages = the '‹ Home' row (with To send / Sent / Inbox); Appointments = '‹ Home' at the left of the day strip (Book stays at the right); Check-in = '‹ Home' in the title row.
   Swipe from the LEFT EDGE (start <= 24 px, drag > 80 px to the right) = Home, like the iPhone. Managers / front desk: unchanged. */
(function () {
  if (IS_MGR || IS_DESK) return;
  const own = () => !IS_MGR && !IS_DESK;
  const mk = () => { const b = document.createElement('button'); b.type = 'button'; b.className = 'homeback own-hb'; b.textContent = '‹ Home'; b.addEventListener('click', () => goHome()); return b; };
  function apHome() { const p = $('#p-appts'), strip = $('#dateStrip'); if (!p || !strip || !own()) return;
    let w = $('#apHomeIc'); if (!w) { w = document.createElement('div'); w.id = 'apHomeIc'; w.className = 'ap-home-ic'; w.appendChild(mk()); p.insertBefore(w, strip); p.classList.add('has-home-ic'); }
    w.style.top = strip.offsetTop + 'px'; w.style.height = strip.offsetHeight + 'px'; }
  function ckHome() { const p = $('#p-checkin'); if (!p || !own()) return; const h = p.firstElementChild;
    if (!h || h.tagName !== 'H2' || h.querySelector('.own-hb')) return; h.classList.add('own-h'); const b = mk(); h.insertBefore(b, h.firstChild);
    const t = document.createElement('span'); t.className = 'own-ht'; while (b.nextSibling) t.appendChild(b.nextSibling); h.appendChild(t);
    const off = (parseFloat(getComputedStyle(p).paddingTop) || 0) + (parseFloat(getComputedStyle(h).marginTop) || 0); h.style.top = off + 'px'; h.style.clipPath = `inset(-${off}px -100vmax 0)`; } /* sticks where it is: no jump when scrolling */
  const watch = (sel, fn) => { const el = $(sel); if (!el) return; new MutationObserver(fn).observe(el, { childList: true, subtree: sel === '#p-appts' }); fn(); };
  watch('#p-appts', () => apHome()); watch('#p-checkin', () => ckHome()); addEventListener('resize', () => apHome());
  watch('#p-settings', () => dockSync()); /* the Settings list (Home -> Settings) is drawn without setTab: no dock there either */
  /* the left-edge swipe: only where the '‹ Home' button would do the same (a page, or a page-sheet opened from Home; never over a pop-up like Book / Checkout) */
  let sw = null;
  const can = () => { if (!own() || !S.csrf || document.body.classList.contains('ib-chat') || document.body.classList.contains('hm-arranging')) return false;
    const sh = $('#sheet'); if (sh && !sh.hidden) return !!(S.pageMode && sh.querySelector('[data-homeback]'));
    return S.tab !== 'settings' || S.home === 'settings' || !!S.setSec; };
  const hscroll = (el) => { for (let e = el; e && e !== document.body; e = e.parentElement) { if (e.scrollWidth > e.clientWidth + 2 && e.scrollLeft > 0 && /(auto|scroll)/.test(getComputedStyle(e).overflowX)) return true; } return false; };
  document.addEventListener('touchstart', (e) => { sw = null; if (e.touches.length !== 1) return; const t = e.touches[0];
    if (t.clientX > 24 || !can() || hscroll(e.target)) return; sw = { x: t.clientX, y: t.clientY, ok: true }; }, { passive: true });
  document.addEventListener('touchmove', (e) => { if (!sw) return; const t = e.touches[0], dx = t.clientX - sw.x, dy = Math.abs(t.clientY - sw.y);
    if (dy > 40 && dy > dx) sw.ok = false; sw.dx = dx; sw.dy = dy; }, { passive: true });
  document.addEventListener('touchend', () => { const s = sw; sw = null; if (s && s.ok && s.dx > 80 && s.dy < s.dx * 0.7 && can()) goHome(); }, { passive: true });
  document.addEventListener('touchcancel', () => { sw = null; }, { passive: true });
})();
