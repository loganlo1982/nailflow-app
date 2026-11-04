#!/usr/bin/env python3
# fix639v (CHAT, anh Logan 04/11 00:05 "doi ngon ngu ... anh muon de tren NailFlowApp"): Home, above "NailFlowApp / Support / Log out":
# English | Tiếng Việt (the same set_lang as Settings → Language – bindLang). Settings keeps its own row. 2 files: admin-core.js, desk-easy.css.
# python3 fix639v.py <release dir>   (kiem)   /   ... go
import sys, os, shutil, time
a = sys.argv[1:]; go = bool(a) and a[-1] == 'go'
if go: a = a[:-1]
if not a: sys.exit('usage: python3 fix639v.py <release dir> [go]')
R = a[0].rstrip('/')
LANG = ('<div class="hm-lang" data-raw role="group" aria-label="Language / Ngôn ngữ">${[[\'en\', \'English\'], [\'vi\', \'Tiếng Việt\']].map(([k, l]) => '
        '`<button type="button" data-lang="${k}" class="${window.I18N && I18N.lang && I18N.lang() === k ? \'on\' : \'\'}">${l}</button>`).join(\'\')}</div>')
P = [('assets/admin-core.js', 'id="hmInfo"><b>NailFlowApp</b>', 'id="hmInfo">' + LANG + '<b>NailFlowApp</b>'),
     ('assets/admin-core.js', "function bindHs(root) { $('#hmOut', root)?.addEventListener('click', (e) => ownerLogOut(e.currentTarget));",
      "function bindHs(root) { $('#hmOut', root)?.addEventListener('click', (e) => ownerLogOut(e.currentTarget)); if (typeof bindLang === 'function') bindLang($('#hmInfo', root) || document.createElement('div')); /* (639v) */")]
CSS = ('\n/* (639v – anh Logan 04/11 00:05) Home: English | Tiếng Việt above NailFlowApp */\n'
       '.hm-info .hm-lang{display:flex;width:max-content;max-width:100%;margin-left:auto;margin-right:auto;gap:4px;background:rgba(255,255,255,.18);border-radius:999px;padding:3px;margin-top:0;margin-bottom:8px}\n'
       '.hm-info .hm-lang button{min-height:40px;padding:0 16px;border:0;border-radius:999px;background:transparent;color:#fff;font:inherit;font-size:15px;font-weight:700;text-shadow:none}\n'
       '.hm-info .hm-lang button.on{background:#fff;color:#1F3B8A}\n')
CF = 'assets/desk-easy.css'
files = {}
for f, o, n in P:
    files.setdefault(f, open(os.path.join(R, f), encoding='utf-8').read())
    print(f, 'anchors', files[f].count(o))
    if files[f].count(o) != 1: print('STOP – nothing changed'); sys.exit(1)
cs = open(os.path.join(R, CF), encoding='utf-8').read()
if 'hm-lang' in cs or 'hm-lang' in files['assets/admin-core.js']: print('DA CO 639v – STOP'); sys.exit(1)
if not go: print('check OK – run again with: go'); sys.exit(0)
os.makedirs(os.path.expanduser('~/app/old'), exist_ok=True); t = time.strftime('%m%d%H%M')
for f in list(files) + [CF]: shutil.copy2(os.path.join(R, f), os.path.expanduser('~/app/old/' + f.replace('/', '__') + '.pre-639v-' + t))
s = files['assets/admin-core.js']
for f, o, n in P: s = s.replace(o, n)
open(os.path.join(R, 'assets/admin-core.js'), 'w', encoding='utf-8').write(s)
open(os.path.join(R, CF), 'w', encoding='utf-8').write(cs.rstrip('\n') + '\n' + CSS)
print('OK 639v – JS/CSS: no restart, reload the pages')
