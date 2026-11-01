#!/usr/bin/env python3
# CHAT 01/11 17:50 - ROOT CAUSE (AN #70, anh Logan bam nut do -> khach vao VOICEMAIL iPhone thay vi tong dai AI):
#  605B (2.99.606) added a `request` (a=talked) to the connect `confirm` SWML. SignalWire's docs: confirm allows ONLY cond, switch, set, unset, hangup, play,
#  prompt, record, record_call, stop_record_call, tap, stop_tap, stream, stop_stream, transcribe, transcribe_stop, send_digits, send_sms, denoise, stop_denoise,
#  user_event - NOT request. The screening no longer worked (no a=talked at screen time in the access log since 10:38) -> the iPhone voicemail got bridged.
#  Fix: the screening = prompt + cond hangup only (as 591). 'talked' still comes from connect's result case "connected", and cl_agent_rec reads status 'ring' too (CHAT 7a14fad8).
import sys, os, shutil, time, subprocess, hashlib
R = sys.argv[1].rstrip('/'); go = 'go' in sys.argv[2:]
fs = [R + '/inc/calls-agent.php']
A = "        ['request' => ['url' => cl_agent_url('talked', '&sid=' . rawurlencode((string)($_GET['sid'] ?? ''))), 'method' => 'POST']]]]];"
B = "        ]]]; /* (CHAT 01/11 606v) NO `request` here - connect confirm allows only cond/switch/set/unset/hangup/play/prompt/record/... (SignalWire docs); a request broke the screening -> the iPhone voicemail was bridged (AN #70) */"
for f in fs:
    t = open(f, encoding='utf-8').read(); print(f, hashlib.sha256(t.encode()).hexdigest()[:8], 'anchor', t.count(A))
    if t.count(A) != 1: sys.exit('ANCHOR FAIL')
if not go: print('check only'); sys.exit()
od = os.path.expanduser('~/app/old'); os.makedirs(od, exist_ok=True); st = time.strftime('%m%d%H%M')
for f in fs:
    b = od + '/inc__calls-agent.php.pre-606v-' + st; shutil.copy2(f, b)
    n = open(f, encoding='utf-8').read().replace(A, B); open(f, 'w', encoding='utf-8').write(n)
    r = subprocess.run(['php', '-l', f], capture_output=True, text=True)
    if r.returncode: shutil.copy2(b, f); sys.exit('PHP FAIL - put back ' + r.stdout + r.stderr)
    print('OK', f, hashlib.sha256(n.encode()).hexdigest()[:8], 'backup', b)
