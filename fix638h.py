#!/usr/bin/env python3
# fix638h.py - LENH-638h (Dejavoo answers 03/11): PaymentType UserChoice; Status busy = P5 still on it (no 2nd sale, unsure re-checked);
# partial kept apart; "Fix service prices" cannot lower a P5 receipt (use Refund). Base: LIVE after 639a.
# Run:  python3 fix638h.py <release dir>   (kiem)   /   ... go
import sys, os, shutil, time, hashlib, json, subprocess
args = [a for a in sys.argv[1:]]
if not args: sys.exit('usage: python3 fix638h.py <release dir> [go]')
go = args[-1] == 'go'
if go: args = args[:-1]
R = args[0].rstrip('/'); XP = [os.path.abspath(a) for a in args[1:]]
def sha(t): return hashlib.sha256(t.encode('utf-8')).hexdigest()[:8]
F = json.loads(r"""{"inc/dejavoo.php": {"base": "91145a39", "new": "4e24ea47", "A": [["const DV_PAY_TYPE = 'Card';   // the P5 asks credit / debit itself (docs: Credit | Debit | ... | Card)", "const DV_PAY_TYPE = 'UserChoice'; /* (2.99.638h - Dejavoo mtellez 03/11 20:16: 'Card' is not used in the US, \"UserChoice\" is the correct value = the customer picks credit / debit on the P5.\n   Sale / Status / Void / Return / TipAdjust all send this SAME value - Status must match the original sale) */"], ["        if ($s['status'] === 'not_found') return $r + ['paid' => false, 'retry_ok' => true, 'checked' => true];\n", "        if ($s['status'] === 'not_found') return $r + ['paid' => false, 'retry_ok' => true, 'checked' => true];\n        if ($s['status'] === 'busy') return $r + ['paid' => false, 'retry_ok' => false, 'checked' => true, 'unsure' => true, 'busy' => true]; /* (2.99.638h, Dejavoo q6: SPIn is synchronous - Status while the sale is still open = busy) the P5 is still on this payment: not a failure */\n"]]}, "inc/dejavoo-pay.php": {"base": "60a6c76b", "new": "b898f50d", "A": [["        if (($r['st'] ?? '') === 'wait') { // a request that never finished (closed tab, server restart): ask the P5 first", "        if (in_array($r['st'] ?? '', ['wait', 'unsure'], true)) { // a request that never finished (closed tab, server restart) - (2.99.638h) or ended unsure (busy / no answer): ask the P5 first, never a 2nd sale"], ["    dv_pend_put($ref, ['st' => !empty($s['unsure']) ? 'unsure' : 'failed', 'why' => $s['status']]);\n", "    dv_pend_put($ref, ['st' => $s['status'] === 'partial' ? 'partial' : (!empty($s['unsure']) ? 'unsure' : 'failed'), 'why' => $s['status']]); /* (2.99.638h) partial: never asked again as \"paid\" - it is voided on the P5 */\n    if (!empty($s['busy'])) fail('The P5 is still busy with this payment (the customer may still be paying). Wait until the P5 is done, then tap Pay again \u2013 it is checked first, never charged twice.', 409); /* (2.99.638h) */\n"]]}, "inc/checkout-edit.php": {"base": "d4ea05c4", "new": "39efc00f", "A": [["        if ((float)$r['refund'] > 0.004) fail(TV('This receipt already has a refund \u2013 refund the difference instead (Refund).', 'Ho\u00e1 \u0111\u01a1n \u0111\u00e3 c\u00f3 refund \u2013 ho\u00e0n ph\u1ea7n ch\u00eanh l\u1ec7ch b\u1eb1ng Refund.')); // (2.99.639a QA-0012) the line prices never change on a refund: lowering again refunded twice\n", "        if ((float)$r['refund'] > 0.004) fail(TV('This receipt already has a refund \u2013 refund the difference instead (Refund).', 'Ho\u00e1 \u0111\u01a1n \u0111\u00e3 c\u00f3 refund \u2013 ho\u00e0n ph\u1ea7n ch\u00eanh l\u1ec7ch b\u1eb1ng Refund.')); // (2.99.639a QA-0012) the line prices never change on a refund: lowering again refunded twice\n        require_once __DIR__ . '/dejavoo-back.php'; if (dv_receipt_p5($r)) fail(TV('This receipt was paid on the P5 \u2013 give the difference back with Refund (the P5 gives it back on the card).', 'Ho\u00e1 \u0111\u01a1n tr\u1ea3 b\u1eb1ng m\u00e1y P5 \u2013 ho\u00e0n ph\u1ea7n ch\u00eanh l\u1ec7ch b\u1eb1ng Refund (m\u00e1y P5 t\u1ef1 tr\u1ea3 v\u1ec1 th\u1ebb).'), 409); /* (2.99.638h e) a lower price here never reached the P5 */\n"]]}}""")
plan = []; bad = 0
for f, x in F.items():
    p = f'{R}/{f}'
    if not os.path.isfile(p): print(f, 'MISSING'); bad = 1; continue
    s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in x['A']]
    al = '638h' in s; print(f, 'sha', sha(s), '(LAMWEB base', x['base'] + ')', 'anchors', *n, 'already', al)
    if al or n != [1] * len(n): bad = 1; continue
    t = s
    for a, b in x['A']: t = t.replace(a, b)
    plan.append((f, p, t))
XA = json.loads(r"""[]""")
if XA and not XP: print('NOTE: this package also patches the web api.php copies (Love Nails ~/lovenails/api.php, ...) - give their paths after the release dir'); bad = 1
for p in XP:
    s = open(p, encoding='utf-8').read(); n = [s.count(a) for a, _ in XA]; al = '638h' in s; print(p, 'sha', sha(s), 'anchors', *n, 'already', al)
    if al or n != [1] * len(n): bad = 1; continue
    t = s
    for a, b in XA: t = t.replace(a, b)
    plan.append((p, p, t))
NEWF = json.loads(r"""{}""")
for f, t in NEWF.items():
    p = f'{R}/{f}'; ex = os.path.exists(p); print('NEW FILE', f, 'exists' if ex else 'ok', sha(t))
    if ex: bad = 1
if bad: sys.exit('STOP: an anchor is not found exactly once, already patched, or a new file is already there - nothing changed')
if not go:
    for f, p, t in plan: print('NEW would be', f, sha(t))
    sys.exit('check only - run again with: go')
bk = os.path.expanduser('~/app/old'); os.makedirs(bk, exist_ok=True); st = time.strftime('%m%d%H%M'); done = []
made = []
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
    b = f'{bk}/' + f.strip('/').replace('/', '__') + f'.pre-638h-{st}'; shutil.copy2(p, b); m = os.stat(p).st_mode; open(p, 'w', encoding='utf-8').write(t); os.chmod(p, m); done.append((p, b)); chk(p)
    print('NEW', f, sha(t), 'backup', b)
for f, t in NEWF.items():
    p = f'{R}/{f}'; open(p, 'w', encoding='utf-8').write(t); made.append(p); os.chmod(p, 0o644); chk(p); print('MADE', f, sha(t))
print('OK 638h: UserChoice + P5 busy/unsure safe + no lower price on P5 receipts')
