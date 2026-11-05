<?php
/* diag (05/11): what was said on a call's recording (the salon's own speech-to-text key; the audio never leaves the server except to it). SALON_ID=an php stt180.php <call id> */
chdir('/home/uyurpyzubx0m/public_html'); require 'inc/core.php'; require_once 'inc/calls.php'; require_once 'inc/calls-tx.php';
$id = (int)($argv[1] ?? 0); $c = q('SELECT rec_sid FROM calls WHERE id = ?', [$id])->fetch(); if (!$c) exit("no call\n");
$d = tx_api('GET', '/recordings/' . rawurlencode((string)$c['rec_sid']))['data'] ?? []; $u = (string)($d['download_urls']['mp3'] ?? ''); if ($u === '') exit("no mp3 link\n");
$t = tempnam('/tmp', 'r180') . '.mp3'; $ch = curl_init($u); $fh = fopen($t, 'w'); curl_setopt_array($ch, [CURLOPT_FILE => $fh, CURLOPT_TIMEOUT => 30]); curl_exec($ch); curl_close($ch); fclose($fh);
$k = trim((string)(cl_stt_get()['key'] ?? '')); if ($k === '') { @unlink($t); exit("no stt key\n"); }
$ch = curl_init('https://api.openai.com/v1/audio/transcriptions');
curl_setopt_array($ch, [CURLOPT_POST => true, CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 120, CURLOPT_HTTPHEADER => ['Authorization: Bearer ' . $k],
    CURLOPT_POSTFIELDS => ['file' => new CURLFile($t, 'audio/mpeg', 'call.mp3'), 'model' => 'whisper-1', 'response_format' => 'verbose_json']]);
$raw = curl_exec($ch); $code = (int)curl_getinfo($ch, CURLINFO_HTTP_CODE); curl_close($ch); @unlink($t);
if ($code !== 200) exit("stt http $code\n"); $j = json_decode((string)$raw, true);
foreach ((array)($j['segments'] ?? []) as $s) printf("%5.1f-%5.1f %s\n", $s['start'], $s['end'], trim((string)$s['text']));
