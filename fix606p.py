#!/usr/bin/env python3
# CHAT 01/11 16:45 (anh Logan: "lich hien hoi lau") - inc/calls-job.php: the 2 channels (caller / salon) go to speech-to-text AT THE SAME TIME
#  (curl_multi) instead of one after the other -> ~2-3 s faster. Same model, same key, same errors (throws -> the job retries as before).
# python3 fix606p.py <release dir> [go]
import sys, os, shutil, time, subprocess, hashlib
R = sys.argv[1].rstrip('/'); go = 'go' in sys.argv[2:]
f = R + '/inc/calls-job.php'
A1 = "$tc = cl_stt($parts[0], $hint); $ts = isset($parts[1]) ? cl_stt($parts[1], $hint) : '';"
B1 = "if (isset($parts[1])) [$tc, $ts] = cl_stt2([$parts[0], $parts[1]], $hint); else { $tc = cl_stt($parts[0], $hint); $ts = ''; } /* (CHAT 01/11 606p) both channels at once */"
A2 = "\n/* ---------- 4. the AI reads what was said"
B2 = r'''
/** (CHAT 01/11 606p) the caller's and the salon's channel read AT THE SAME TIME (curl_multi) - same request as cl_stt(), ~2-3 s faster. */
function cl_stt2(array $wavs, string $hint): array {
$out = []; $need = false; foreach ($wavs as $i => $w) { $out[$i] = ''; if (strlen($w) >= 2000) $need = true; }
if (!$need) return $out;
$k = trim((string)(cl_stt_get()['key'] ?? '')); if ($k === '') throw new RuntimeException('No speech-to-text key');
$url = (string)getenv('NF_STT_URL'); if ($url === '') $url = 'https://api.openai.com/v1/audio/transcriptions';
$mh = curl_multi_init(); $hs = []; $tmps = [];
foreach ($wavs as $i => $w) {
if (strlen($w) < 2000) continue;
$tmp = tempnam(sys_get_temp_dir(), 'nfc'); file_put_contents($tmp, $w); $tmps[] = $tmp;
$ch = curl_init($url);
curl_setopt_array($ch, [CURLOPT_POST => true, CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 120, CURLOPT_CONNECTTIMEOUT => 10, CURLOPT_HTTPHEADER => ['Authorization: Bearer ' . $k],
CURLOPT_POSTFIELDS => ['file' => new CURLFile($tmp, 'audio/wav', 'call.wav'), 'model' => cl_stt_model(), 'response_format' => 'json', 'prompt' => $hint]]);
curl_multi_add_handle($mh, $ch); $hs[$i] = $ch;
}
do { $st = curl_multi_exec($mh, $run); if ($run) curl_multi_select($mh, 1.0); } while ($run && $st === CURLM_OK);
$err = '';
foreach ($hs as $i => $ch) {
$raw = curl_multi_getcontent($ch); $code = (int)curl_getinfo($ch, CURLINFO_HTTP_CODE); curl_multi_remove_handle($mh, $ch); curl_close($ch);
if ($raw === null || $raw === '' || $code !== 200) { $err = 'Speech-to-text http ' . $code; continue; }
$j = json_decode((string)$raw, true); if (!is_array($j)) { $err = 'Speech-to-text answer not JSON'; continue; }
$out[$i] = trim((string)($j['text'] ?? ''));
}
curl_multi_close($mh); foreach ($tmps as $t) @unlink($t);
if ($err !== '') throw new RuntimeException($err);
return $out;
}
''' + A2
t = open(f, encoding='utf-8').read(); print(f, hashlib.sha256(t.encode()).hexdigest()[:8], 'anchors', t.count(A1), t.count(A2), 'already', 'cl_stt2' in t)
if t.count(A1) != 1 or t.count(A2) != 1 or 'cl_stt2' in t: sys.exit('ANCHOR FAIL')
n = t.replace(A1, B1).replace(A2, B2, 1)
print('new sha', hashlib.sha256(n.encode()).hexdigest()[:8])
if not go: print('check only'); sys.exit()
od = os.path.expanduser('~/app/old'); os.makedirs(od, exist_ok=True)
b = od + '/inc__calls-job.php.pre-606p-' + time.strftime('%m%d%H%M'); shutil.copy2(f, b)
open(f, 'w', encoding='utf-8').write(n)
r = subprocess.run(['php', '-l', f], capture_output=True, text=True)
if r.returncode: shutil.copy2(b, f); sys.exit('PHP FAIL - put back ' + r.stdout + r.stderr)
print('OK backup', b)
