# 2.99.647 test (from 646): the AI part of a Telnyx call is recorded and kept (tx_cli_airec). Fake Telnyx /v2 on 127.0.0.1:18990, local SQLite copy, nothing real.
import subprocess, json, os, sys, time, shutil, threading, http.server
A0 = os.path.abspath(sys.argv[1]); K = '/home/claude/kit638h/s'; T5 = K + '/T586'; D = '/home/claude/t646/run647'; FP = 18990
shutil.rmtree(D, ignore_errors=True); os.makedirs(D + '/calls'); A = D + '/app'; shutil.copytree(A0, A, symlinks=True); DB = D + '/db.sqlite'
shutil.copy(K + '/tdb/base.sqlite', DB)
R = []
def ok(n, c, i=''): R.append(bool(c)); print(('✓ ' if c else '✗ ') + n + ('' if c else '   → ' + str(i)[:400]))
ENV = {**os.environ, 'TZ': 'America/Chicago', 'NF_SHARED_DIR': T5 + '/shared', 'NF_CALLS_DIR': D + '/calls', 'NF_TX_BASE': 'http://127.0.0.1:%d/v2' % FP}
def sh(*a): return subprocess.run(a, capture_output=True, text=True, env=ENV)
seed = sh('php', T5 + '/seed.php', A, DB, '18991'); assert seed.returncode == 0, seed.stderr
MP3 = b'ID3\x03\x00\x00\x00\x00\x00\x0a' + b'\xff\xfb\x90\x00' * 400
hits = []
class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _j(self, c, o): b = json.dumps(o).encode(); self.send_response(c); self.send_header('Content-Type', 'application/json'); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        hits.append('GET ' + self.path)
        if self.path.startswith('/v2/recordings?'):
            if 'CA-NOREC' in self.path: return self._j(200, {'data': []})
            return self._j(200, {'data': [{'id': 'rec-ai-1', 'status': 'completed', 'duration_millis': 30000, 'call_control_id': 'CA-AI-1',
                'download_urls': {'mp3': 'http://127.0.0.1:%d/files/rec-ai-1.mp3' % FP, 'wav': ''}}]})
        if self.path == '/files/rec-ai-1.mp3':
            if 'Authorization' not in self.headers: self.send_response(403); self.end_headers(); return
            self.send_response(200); self.send_header('Content-Type', 'audio/mpeg'); self.end_headers(); self.wfile.write(MP3); return
        self.send_response(404); self.end_headers()
    def do_DELETE(self): hits.append('DELETE ' + self.path); self.send_response(204); self.end_headers()
srv = http.server.ThreadingHTTPServer(('127.0.0.1', FP), H); threading.Thread(target=srv.serve_forever, daemon=True).start()
def php(code):
    r = sh('php', '-r', 'require "%s/inc/core.php"; settings(); require_once "%s/inc/calls.php"; require_once "%s/inc/calls-tx.php"; tx_table(); %s' % (A, A, A, code)); return (r.stdout + r.stderr).strip()
def sql(q): r = sh('php', T5 + '/db.php', DB, q); return json.loads(r.stdout or '[]')
print(php('require_once "%s/inc/android.php"; set_setting("tx_key", ad_enc("KEYTEST_0000000000000000")); set_setting("tx_schema", "1"); echo tx_key() !== "" ? "key ok" : "no key";' % A))
t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - 600))
for sid in ['CA-AI-1', 'CA-NOREC']:
    php("q(\"INSERT INTO calls (call_sid, from_phone, to_phone, kind, started_at, status, created_at, purge_at, prov) VALUES ('%s', '+15155550142', '+15155136667', 'agent', '%s', 'done', '%s', '2099-01-01', 'tx')\");" % (sid, t, t))
php("q(\"INSERT INTO calls (call_sid, from_phone, to_phone, kind, started_at, status, created_at, purge_at, prov) VALUES ('CA-NEW', '+15155550143', '+15155136667', 'agent', '%s', 'done', '%s', '2099-01-01', 'tx')\");" % (time.strftime('%Y-%m-%d %H:%M:%S'), time.strftime('%Y-%m-%d %H:%M:%S')))
out = php('tx_cli_airec(); echo "ran";')
ok('1 the cron runs without error', out.endswith('ran'), out)
r1 = sql("SELECT file, rec_sid FROM calls WHERE call_sid = 'CA-AI-1'")[0]
ok('2 AI call: the MP3 is kept (file set, .mp3, rec_sid)', r1['file'] and r1['file'].endswith('.mp3') and r1['rec_sid'] == 'rec-ai-1', r1)
p = D + '/calls/' + (r1['file'] or 'x')
ok('3 the file is the real recording, owner-only (0600)', os.path.isfile(p) and open(p, 'rb').read() == MP3 and oct(os.stat(p).st_mode)[-3:] == '600', p)
ok('4 the download used the key only after 403, Telnyx copy deleted', any(h == 'DELETE /v2/recordings/rec-ai-1' for h in hits), hits)
r2 = sql("SELECT file FROM calls WHERE call_sid = 'CA-NOREC'")[0]
ok('5 no recording on Telnyx yet -> nothing kept, tried again later', not r2['file'] and '"' in php('echo setting("tx_airec_try");'), r2)
ok('6 a call of the last 2 minutes is not asked yet', not any('CA-NEW' in h for h in hits), hits)
n = len(hits); php('tx_cli_airec();')
ok('7 at most once a minute (a second run at once asks nothing)', len(hits) == n, hits[n:])
php('set_setting("tx_airec_at", "0");'); [php('set_setting("tx_airec_at", "0"); tx_cli_airec();') for _ in range(7)]
asks = [h for h in hits if 'CA-NOREC' in h]
ok('8 (647) no finished recording yet is NOT a used try: asked every run (1+7), kept for later', len(asks) == 8 and '[8,0]' in php('echo setting("tx_airec_try");').replace(' ', ''), (len(asks), php('echo setting("tx_airec_try");')))
ok('9 the call that already has its file is not asked again', len([h for h in hits if 'CA-AI-1' in h]) == 1, hits)
t2 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - 300))
for k in range(4): php("q(\"INSERT INTO calls (call_sid, from_phone, to_phone, kind, started_at, status, created_at, purge_at, prov) VALUES ('CA-NOREC%d', '+15155550142', '+15155136667', 'agent', '%s', 'done', '%s', '2099-01-01', 'tx')\");" % (k, t2, t2))
php("q(\"INSERT INTO calls (call_sid, from_phone, to_phone, kind, started_at, status, created_at, purge_at, prov) VALUES ('CA-AI-1', '+15155550144', '+15155136667', 'agent', '%s', 'done', '%s', '2099-01-01', 'tx')\");" % (t, t))
[php('set_setting("tx_airec_at", "0"); tx_cli_airec();') for _ in range(4)]
r9 = sql("SELECT file FROM calls WHERE call_sid = 'CA-AI-1' ORDER BY id DESC LIMIT 1")[0]
ok('9b (647) 5 calls with no recording yet do not block a newer-asked call: it is saved within 4 runs', r9['file'], (r9, php('echo setting("tx_airec_try");')))
body = open(A + '/inc/calls-tx.php').read(); import re as _re; body = (_re.search(r"'recording_settings' => \[[^\]]*\]", body) or [''])[0].replace("'", '"').replace(' => ', ':').replace(', ', ',')
ok('10 the assistant asks Telnyx to record (dual MP3)', '"enabled":true' in body and 'dual' in body and 'mp3' in body, body)
print('PASS %d/%d' % (sum(R), len(R))); srv.shutdown(); sys.exit(0 if all(R) else 1)
