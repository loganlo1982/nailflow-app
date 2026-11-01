<?php
// CHAT 01/11 16:55 (anh Logan: "tren web chi hien mau cua PLA, Auzona, iGel"): colors of other brands -> on = 0 (hidden, NOT deleted). Backup of the setting first.
declare(strict_types=1);
if (PHP_SAPI !== 'cli') exit;
require '/home/uyurpyzubx0m/app/sites/an/current/inc/core.php';
$raw = (string)setting('polish_colors'); $a = json_decode($raw, true); if (!is_array($a)) exit("bad json\n");
$keep = fn($b) => (bool)preg_match('/^(pla|auzona|igel)\b/i', trim((string)$b));
$n = 0; foreach ($a as &$c) { $on = $keep($c['brand'] ?? '') ? 1 : 0; if ((int)($c['on'] ?? 1) !== $on) $n++; $c['on'] = $on; } unset($c);
echo "would change $n of ", count($a), "\n";
if (($argv[1] ?? '') !== 'go') exit("check only\n");
@mkdir('/root/app/old', 0700, true); $b = '/root/app/old/setting-polish_colors.pre-brands-' . date('mdHi') . '.json'; file_put_contents($b, $raw); echo "backup $b\n";
set_setting('polish_colors', json_encode($a, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES));
$g = []; foreach (json_decode((string)setting('polish_colors'), true) as $c) { $k = ($c['brand'] ?? '?') . ' on=' . (int)$c['on']; $g[$k] = ($g[$k] ?? 0) + 1; } ksort($g); foreach ($g as $k => $v) echo "$k : $v\n";
