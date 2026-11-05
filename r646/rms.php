<?php
/* diag (05/11): fresh link of a call's recording via Telnyx, then the loudness per second of each channel (no audio leaves the server). php rms.php <call id> */
chdir('/home/uyurpyzubx0m/public_html'); require 'inc/core.php'; require_once 'inc/calls.php'; require_once 'inc/calls-tx.php';
$id = (int)($argv[1] ?? 0); $c = q('SELECT rec_sid, file FROM calls WHERE id = ?', [$id])->fetch(); if (!$c) exit("no call\n");
$r = tx_api('GET', '/recordings/' . rawurlencode((string)$c['rec_sid'])); $d = $r['data'] ?? []; echo 'rec: ', ($d['status'] ?? '?'), ' ', ($d['duration_millis'] ?? '?'), " ms, channels ", ($d['channels'] ?? '?'), "\n";
$u = (string)($d['download_urls']['wav'] ?? ''); if ($u === '') exit("no wav link\n");
$t = tempnam('/tmp', 'r180'); $ch = curl_init($u); $fh = fopen($t, 'w'); curl_setopt_array($ch, [CURLOPT_FILE => $fh, CURLOPT_TIMEOUT => 30]); curl_exec($ch); curl_close($ch); fclose($fh);
$b = file_get_contents($t); @unlink($t); if (substr($b, 0, 4) !== 'RIFF') exit("not wav\n");
$p = 12; $fmt = null; $data = '';
while ($p + 8 <= strlen($b)) { $id4 = substr($b, $p, 4); $sz = unpack('V', substr($b, $p + 4, 4))[1]; if ($id4 === 'fmt ') $fmt = unpack('vfmt/vch/Vrate/Vbr/vba/vbits', substr($b, $p + 8, 16)); if ($id4 === 'data') { $data = substr($b, $p + 8, $sz); break; } $p += 8 + $sz + ($sz % 2); }
echo 'fmt: ', json_encode($fmt), "\n"; if (!$fmt || $fmt['bits'] !== 16) exit("not pcm16 (fmt " . ($fmt['fmt'] ?? '?') . ")\n");
$ch = $fmt['ch']; $rate = $fmt['rate']; $n = intdiv(strlen($data), 2 * $ch); $s = unpack('v*', $data);
for ($k = 0; $k < $ch; $k++) { $line = ''; for ($sec = 0; $sec * $rate < $n; $sec++) { $sum = 0; $m = 0; for ($i = $sec * $rate; $i < min($n, ($sec + 1) * $rate); $i += 8) { $v = $s[$i * $ch + $k + 1]; if ($v > 32767) $v -= 65536; $sum += $v * $v; $m++; }
    $db = $m ? 20 * log10(max(1, sqrt($sum / $m)) / 32768) : -99; $line .= $db > -35 ? '#' : ($db > -50 ? '+' : '.'); } echo "ch$k: $line\n"; }
echo "(1 char = 1 s: # loud, + quiet sound, . silence)\n";
