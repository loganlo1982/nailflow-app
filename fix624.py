#!/usr/bin/env python3
# LAMWEB 2.99.624 (619 – loi that tim thay o 618-B): SignalWire screening of the iPhone leg counted 10+ words as the voicemail -> the owner's long hello
#  ("Hello thank you for calling American Nails and Spa how can I help you") was HUNG UP and the caller sent to the voicemail / AI. Same rule as Telnyx 616 L1:
#  10+ words = voicemail only when there is no hello / salon word; the voicemail words (CL_VM_HEAR) still win. cXML (call_in.php) + SWML (call_agent.php).
#  CHANGED: inc/calls.php (CL_PERSON_HEAR + cl_screened_xml), inc/calls-agent.php (cl_agent_screen_swml). AN public_html: nothing (its call_*.php use these inc files).
# Run (in the app folder):  python3 fix624.py <app dir>  /  python3 fix624.py <app dir> go
import sys, os, shutil, time, hashlib, json, subprocess
R = sys.argv[1].rstrip('/'); go = len(sys.argv) > 2 and sys.argv[2] == 'go'
def sha(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
F = json.loads(r'''{"inc/calls.php": {"base": "cece0d0c", "new": "e22d99d1", "A": [["xml(array $p, string $parent): string {\n    $said = trim((string)($p['SpeechResult'] ?? '')); $vm = $said !== '' && (preg_match(CL_VM_HEAR, $said) || str_word_count($said) >= 10);\n    if ($parent !== '') try { cl_table()", "xml(array $p, string $parent): string {\n    $said = trim((string)($p['SpeechResult'] ?? '')); $vm = $said !== '' && (preg_match(CL_VM_HEAR, $said) || (str_word_count($said) >= 10 && !preg_match(CL_PERSON_HEAR, $said))); /* (2.99.624) a long hello from the owner is a person (as Telnyx 616 L1) */\n    if ($parent !== '') try { cl_table()"], ["angup/></Response>' : '<Response/>');\n}\nconst CL_VM_HEAR = '/(leave (me |us )?(a", "angup/></Response>' : '<Response/>');\n}\n/* (2.99.624) a person's first words on the iPhone leg: a long greeting with these is the owner, not the voicemail (the voicemail words above still win) */\nconst CL_PERSON_HEAR = '/\\\\b(hello|hi|hey|american|nails|salon|speaking|this is|yes|yeah)\\\\b/i';\nconst CL_VM_HEAR = '/(leave (me |us )?(a"]]}, "inc/calls-agent.php": {"base": "a0b1f1a1", "new": "b2377418", "A": [["' => 1, 'speech_language' => 'en-US']],\n        ['cond' => [['when' => '/' . $re . '/i.test(prompt_value) || (prompt_value || \"\").split(\" \").length >= 10', 'then' => [['hangup' => (object)[]]]]]],\n        ]]]; /* (CHAT 01/11 606v) NO `request` here - connect confirm allows only cond/switch/set/unset/hangup/play/prompt/record/... (SignalWire docs); a request broke the screening -> the iPhone voicemail was bridged (AN #70) */ // (2.99.606 - LENH 605B 10:06, AN #53 #54) a PERSON answered the iPhone: 'talked' now (the \"connected\" case of connect only runs after the bridge, often never)\n}\n/** The old free voicemail (not answer", "' => 1, 'speech_language' => 'en-US']],\n        ['cond' => [['when' => '/' . $re . '/i.test(prompt_value) || ((prompt_value || \"\").split(\" \").length >= 10 && !' . CL_PERSON_HEAR . '.test(prompt_value || \"\"))', 'then' => [['hangup' => (object)[]]]]]],\n        ]]]; /* (2.99.624) 10+ words = the voicemail only when no hello / salon words (the owner's long greeting stays connected) */ /* (CHAT 01/11 606v) NO `request` here - connect confirm allows only cond/switch/set/unset/hangup/play/prompt/record/... (SignalWire docs); a request broke the screening -> the iPhone voicemail was bridged (AN #70) */ // (2.99.606 - LENH 605B 10:06, AN #53 #54) a PERSON answered the iPhone: 'talked' now (the \"connected\" case of connect only runs after the bridge, often never)\n}\n/** The old free voicemail (not answer"]]}}''')
NEWF = json.loads(r'''{}''')
plan = []; bad = 0
for f, x in F.items():
    p = f'{R}/{f}'; s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in x['A']]
    al = '2.99.624' in s; print(f, 'sha', sha(s), '(LAMWEB base', x['base'] + ')', 'anchors', *n, 'already', al)
    if al or n != [1] * len(n): bad = 1; continue
    t = s
    for a, b in x['A']: t = t.replace(a, b)
    plan.append((f, p, t))
for f, t in NEWF.items():
    p = f'{R}/{f}'; ex = os.path.exists(p); print('NEW', f, 'exists' if ex else 'ok', sha(t))
    if ex: bad = 1
if bad: sys.exit('STOP: an anchor is not found exactly once, already patched, or a new file is already there - nothing changed')
if not go:
    for f, p, t in plan: print('NEW would be', f, sha(t))
    sys.exit('check only - run again with: go')
bk = os.path.expanduser('~/app/old'); os.makedirs(bk, exist_ok=True); st = time.strftime('%m%d%H%M'); done = []; made = []
def back(msg):
    for q, bb in done: shutil.copy2(bb, q)
    for q in made:
        try: os.remove(q)
        except OSError: pass
    sys.exit('ERROR ' + msg + ' - every file put back, new files removed')
def chk(p):
    c = ['php', '-l', p] if p.endswith('.php') else (['node', '--check', p] if p.endswith('.js') and shutil.which('node') else None)
    if not c: return
    r = subprocess.run(c, capture_output=True, text=True)
    if r.returncode: back('in ' + p + ': ' + (r.stdout + r.stderr)[:300])
for f, p, t in plan:
    b = f'{bk}/' + f.replace('/', '__') + f'.pre-624-{st}'; shutil.copy2(p, b); m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m); done.append((p, b)); chk(p)
    print('NEW', f, sha(t), 'backup', b)
for f, t in NEWF.items():
    p = f'{R}/{f}'
    open(p, 'w', encoding='utf-8').write(t); made.append(p)
    os.chmod(p, 0o644)
    chk(p); print('MADE', f, sha(t))
print('OK 2.99.624 (SignalWire: the owner\'s long hello is a person) - set APP_VERSION 2.99.624, restart php-fpm. Nothing in the AN public_html copies.')
