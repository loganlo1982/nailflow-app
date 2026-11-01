#!/usr/bin/env python3
# CHAT 01/11 12:30 - ROOT CAUSE "slow to show in the calendar" with the AI agent number: call_in.php (cXML, yesterday) answers then runs cl_job($id)
#  RIGHT AWAY; call_agent.php 'rec' (SWML) only queues the call -> waits for the next cron minute (up to ~60 s). Fix: 'rec' answers '{}', closes the
#  connection, then reads the answered call right away (kind 'call' only; voicemails keep the cron + text-back wait). cl_job locks the row: no double work with the cron.
import sys, os, shutil, time, subprocess, hashlib
R = sys.argv[1].rstrip('/'); go = len(sys.argv) > 2 and sys.argv[2] == 'go'
P = '/home/uyurpyzubx0m/public_html/call_agent.php'
OLD = "    case 'rec': cl_table(); cl_agent_rec($in); echo '{}'; exit;"
NEW = ("    case 'rec': cl_table(); cl_agent_rec($in); // (CHAT 01/11 606f) answer, then read the answered call NOW like call_in.php (not at the next cron minute)\n"
       "        ignore_user_abort(true); @set_time_limit(280); header('Content-Type: application/json'); header('Content-Length: 2'); header('Connection: close'); echo '{}';\n"
       "        while (ob_get_level() > 0) @ob_end_flush(); @flush(); if (function_exists('litespeed_finish_request')) litespeed_finish_request(); elseif (function_exists('fastcgi_finish_request')) fastcgi_finish_request();\n"
       "        $rs = mb_substr((string)($_GET['sid'] ?? ($in['call_id'] ?? '')), 0, 64);\n"
       "        $rr = $rs !== '' ? q(\"SELECT id FROM calls WHERE call_sid = ? AND status = 'queued' AND kind = 'call'\", [$rs])->fetch() : null;\n"
       "        if ($rr) { try { ag_lib(); cl_job((int)$rr['id']); } catch (Throwable $e) { error_log('606f job #' . $rr['id'] . ': ' . $e->getMessage()); } }\n"
       "        exit;")
fs = [R + '/call_agent.php', P]
for f in fs:
    t = open(f, encoding='utf-8').read(); print(f, hashlib.sha256(t.encode()).hexdigest()[:8], 'anchor', t.count(OLD))
    if t.count(OLD) != 1: sys.exit('ANCHOR FAIL')
if not go: print('check only'); sys.exit()
od = os.path.expanduser('~/app/old'); os.makedirs(od, exist_ok=True); st = time.strftime('%m%d%H%M')
for i, f in enumerate(fs):
    b = od + '/call_agent.php.' + ('rel' if i == 0 else 'pub') + '.pre-606f-' + st; shutil.copy2(f, b)
    n = open(f, encoding='utf-8').read().replace(OLD, NEW); open(f, 'w', encoding='utf-8').write(n)
    r = subprocess.run(['php', '-l', f], capture_output=True, text=True)
    if r.returncode: shutil.copy2(b, f); sys.exit('PHP FAIL - put back ' + f + r.stdout + r.stderr)
    print('OK', f, hashlib.sha256(n.encode()).hexdigest()[:8], 'backup', b)
