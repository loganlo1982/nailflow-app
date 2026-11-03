<?php
/* LAMWEB LENH-633 (anh Logan 02/11 19:29): Love Nails = a NEW salon on the shared code, https://lovenails.nailflowapp.com
   SALON_ID lovenails · its OWN database · its OWN config (0600, outside the web) · its own sessions / data / uploads · the SAME release as AN (links, rel_point).
   Never reads / writes American Nails' config, database or files. Never deletes anything. No owner password (admin/setup.php via AN HQ later).
   Nothing is sent: sms off, auto send off, Android off, birthday / review off, NO cron job (sites.php 'cron' => []) until anh Logan turns them on.
   Run (CHAT, on the server, as the cPanel user):
     php install633.php <app dir> [go] [--mysql] [--web <docroot>] [--host <host>]
       <app dir> = /home/uyurpyzubx0m/app   (has sites.php, releases/, sites/an/current)
       default database = SQLite file <app>/sites/lovenails/data/lovenails.sqlite (no password anywhere)
       --mysql = a MySQL database CHAT made in cPanel first: env NF_LN_DB_NAME, NF_LN_DB_USER, NF_LN_DB_PASS (+ NF_LN_DB_HOST, default localhost);
                 the password goes ONLY into the 0600 config, never printed.
   Without "go": checks only, changes nothing. */
declare(strict_types=1);
$argv0 = $argv; array_shift($argv0); $opt = ['mysql' => false, 'web' => '/home/uyurpyzubx0m/public_html/lovenails', 'host' => 'lovenails.nailflowapp.com']; $pos = [];
for ($i = 0; $i < count($argv0); $i++) { $a = $argv0[$i];
    if ($a === '--mysql') $opt['mysql'] = true; elseif ($a === '--web') $opt['web'] = rtrim((string)$argv0[++$i], '/'); elseif ($a === '--host') $opt['host'] = strtolower((string)$argv0[++$i]); else $pos[] = $a; }
$B = rtrim((string)($pos[0] ?? ''), '/'); $GO = ($pos[1] ?? '') === 'go'; $ID = 'lovenails'; $WEB = $opt['web']; $HOST = $opt['host'];
$stop = []; $say = function (string $s) { echo $s, "\n"; };
if ($B === '' || !is_file("$B/sites.php")) { fwrite(STDERR, "usage: php install633.php <app dir with sites.php> [go] [--mysql]\n"); exit(2); }
$map = (static function ($f) { return require $f; })("$B/sites.php"); if (!is_array($map)) $stop[] = 'sites.php is not a list';
$say('== LENH-633 install Love Nails · ' . date('Y-m-d H:i T') . ' · ' . ($GO ? 'GO' : 'CHECK ONLY'));
$say('sites.php: ' . implode(', ', array_map(fn($k, $s) => $k . ' (' . implode(' ', (array)($s['hosts'] ?? [])) . '; cron ' . implode(' ', (array)($s['cron'] ?? [])) . ')', array_keys((array)$map), (array)$map)));
if (isset($map[$ID])) $stop[] = "sites.php already has '$ID'";
foreach ((array)$map as $k => $s) foreach ((array)($s['hosts'] ?? []) as $h) if (strtolower((string)$h) === $HOST) $stop[] = "host $HOST is already salon '$k'";
foreach ((array)$map as $k => $s) if (rtrim((string)($s['web'] ?? ''), '/') === $WEB) $stop[] = "web folder $WEB is already salon '$k'";
if (file_exists("$B/sites/$ID")) $stop[] = "$B/sites/$ID already exists";
$an = $map['an'] ?? (array_values(array_filter((array)$map, fn($s) => !empty($s['main'])))[0] ?? null);
$anId = isset($map['an']) ? 'an' : (string)array_search($an, (array)$map, true);
$cur = $anId !== '' ? @readlink("$B/sites/$anId/current") : false; $V = $cur ? basename((string)$cur) : '';
$say("version: the main salon ($anId) uses " . ($V ?: '?'));
if ($V === '' || !is_file("$B/releases/$V/inc/core.php") || !is_file("$B/releases/$V/inc/release.php")) $stop[] = "release of the main salon not found ($V)";
if (!is_dir($WEB)) $stop[] = "web folder $WEB does not exist (make the subdomain in cPanel first)";
else { $have = array_values(array_diff(scandir($WEB) ?: [], ['.', '..', 'cgi-bin', '.well-known']));
    $say("web folder $WEB: " . ($have ? implode(' ', $have) : 'empty (cgi-bin only)'));
    if ($have) $stop[] = "web folder $WEB is not empty: " . implode(' ', array_slice($have, 0, 8)) . ' – nothing is changed or deleted, CHAT decides'; }
$home = dirname($B);
foreach (["$home/lovenails", "$home/public_html/lovenails.nailflowapp.com"] as $old) if (file_exists($old)) $say("NOTE: $old exists (an older Love Nails copy?) – NOT touched; AN HQ's default list points Love Nails to $home/lovenails");
if ($opt['mysql']) { foreach (['NF_LN_DB_NAME', 'NF_LN_DB_USER', 'NF_LN_DB_PASS'] as $e) if ((string)getenv($e) === '') $stop[] = "--mysql: env $e not set";
    $dbn = (string)getenv('NF_LN_DB_NAME'); if ($dbn !== '' && $an && ($ac = @(static function ($f) { return require $f; })("$B/sites/$anId/config.php")) && is_array($ac) && ($ac['db_name'] ?? '') === $dbn) $stop[] = 'NF_LN_DB_NAME is the main salon\'s database – a NEW one is needed'; }
if ($stop) { foreach ($stop as $s) $say('STOP: ' . $s); $say('nothing changed'); exit(3); }
if (!$GO) { $say("OK to install: sites/$ID + config (" . ($opt['mysql'] ? 'MySQL ' . getenv('NF_LN_DB_NAME') : 'SQLite') . "), sites.php line ('cron' => []), links in $WEB -> sites/$ID/current -> releases/$V. Run again with: go"); exit(0); }

/* ---------- GO ---------- */
$made = []; $t = date('mdHi'); @mkdir("$B/old", 0700, true); $bak = "$B/old/sites.php.pre-633-$t"; copy("$B/sites.php", $bak); $say("backup $bak");
$undo = function (string $why) use (&$made, $B, $bak, $say) {
    copy($bak, "$B/sites.php"); foreach (array_reverse($made) as $p) { if (is_link($p) || is_file($p)) @unlink($p); elseif (is_dir($p)) @rmdir($p); }
    $say('ERROR ' . $why . ' – sites.php put back, everything made by this script removed (nothing else was touched)'); exit(4); };
$SD = "$B/sites/$ID";
foreach ([$SD, "$SD/data", "$SD/sessions"] as $d) { if (!@mkdir($d, 0700)) $undo("mkdir $d"); $made[] = $d; }
$cfg = ['site_url' => 'https://' . $HOST];
if ($opt['mysql']) $cfg += ['driver' => 'mysql', 'db_host' => (string)(getenv('NF_LN_DB_HOST') ?: 'localhost'), 'db_name' => (string)getenv('NF_LN_DB_NAME'), 'db_user' => (string)getenv('NF_LN_DB_USER'), 'db_pass' => (string)getenv('NF_LN_DB_PASS')];
else $cfg += ['driver' => 'sqlite', 'sqlite_path' => "$SD/data/lovenails.sqlite"];
$cf = "$SD/config.php"; $old = umask(0077); $ok = file_put_contents($cf, "<?php\n// LENH-633 Love Nails (own database) – made " . date('Y-m-d H:i') . "\nreturn " . var_export($cfg, true) . ";\n"); umask($old);
if ($ok === false) $undo('config'); chmod($cf, 0600); $made[] = $cf; $say("config $cf (0600, " . $cfg['driver'] . ')');
// sites.php: one more entry (text added before the closing bracket; checked by loading it back)
$src = (string)file_get_contents("$B/sites.php"); $line = "    '$ID' => ['hosts' => ['$HOST'], 'web' => '$WEB', 'cron' => [], 'main' => false], // LENH-633 " . date('Y-m-d') . " – cron off until anh Logan turns it on\n";
$pos2 = max((int)strrpos($src, '];'), 0); $pos3 = (int)strrpos($src, ');'); $at = max($pos2, $pos3);
if ($at <= 0) $undo('sites.php: no closing bracket found');
$before = rtrim(substr($src, 0, $at)); $new = $before . (str_ends_with($before, ',') || str_ends_with($before, '[') || str_ends_with($before, '(') ? '' : ',') . "\n" . $line . substr($src, $at);
file_put_contents("$B/sites.php.new-633", $new); $chk = shell_exec(escapeshellarg(PHP_BINARY) . ' -l ' . escapeshellarg("$B/sites.php.new-633") . ' 2>&1');
$m2 = str_contains((string)$chk, 'No syntax errors') ? (static function ($f) { return require $f; })("$B/sites.php.new-633") : null;
$want = $map; $want[$ID] = ['hosts' => [$HOST], 'web' => $WEB, 'cron' => [], 'main' => false];
if (!is_array($m2) || $m2 != $want) { @unlink("$B/sites.php.new-633"); $undo('sites.php check: the new list is not the old one + Love Nails'); }
rename("$B/sites.php.new-633", "$B/sites.php"); $say("sites.php: + $ID (cron off) – the other salons unchanged");
// the database: tables + Love Nails' own first settings (a child php process of the release, SALON_ID=lovenails)
$R = "$B/releases/$V";
$php = '$R = getenv("NF_REL"); require $R . "/inc/core.php"; require_once $R . "/inc/schema.php"; if (SITE_ID !== "lovenails") { fwrite(STDERR, "wrong salon " . SITE_ID); exit(5); }'
    . ' $dr = cfg()["driver"] ?? "mysql"; foreach (schema_sql($dr) as $sql) { try { db()->exec($sql); } catch (PDOException $e) { if (stripos($sql, "CREATE INDEX") === false) throw $e; } }'
    . ' settings(); ensure_schema();'
    . ' if ((int)q("SELECT COUNT(*) FROM appointments")->fetchColumn() || (int)q("SELECT COUNT(*) FROM customers")->fetchColumn()) { fwrite(STDERR, "the new database is not empty"); exit(6); }'
    . ' foreach (["salon_name" => "Love Nails", "timezone" => "America/Chicago", "sms_enabled" => "0", "as_on" => "0", "as_device" => "", "bday_on" => "0", "review_on" => "0", "ad_transport" => "", "call_on" => "0"] as $k => $v) set_setting($k, $v);'
    . ' echo json_encode(["salon" => setting("salon_name"), "schema" => setting("schema_version"), "staff" => (int)q("SELECT COUNT(*) FROM staff")->fetchColumn(), "services" => (int)q("SELECT COUNT(*) FROM services")->fetchColumn(), "customers" => 0]);';
$out = shell_exec('cd ' . escapeshellarg($R) . ' && SALON_ID=lovenails NF_REL=' . escapeshellarg($R) . ' ' . escapeshellarg(PHP_BINARY) . ' -r ' . escapeshellarg($php) . ' 2>&1');
$j = json_decode((string)$out, true); if (!is_array($j) || ($j['salon'] ?? '') !== 'Love Nails') $undo('database: ' . mb_substr(preg_replace('/pass\w*\s*=\s*\S+/i', 'pass=***', (string)$out), 0, 300));
if (!$opt['mysql']) $made[] = "$SD/data/lovenails.sqlite";
$say('database: ' . json_encode($j));
// the web folder: the SAME release links as every salon (rel_point of the release: current -> releases/<v>, one link per top-level name, .htaccess copied)
$php2 = '$R = getenv("NF_REL"); define("APP_ROOT", $R); require $R . "/inc/release.php"; echo json_encode(rel_point("lovenails", getenv("NF_VER"), "LENH-633 install"));';
$out2 = shell_exec('cd ' . escapeshellarg($R) . ' && SALON_ID=lovenails NF_REL=' . escapeshellarg($R) . ' NF_VER=' . escapeshellarg($V) . ' ' . escapeshellarg(PHP_BINARY) . ' -r ' . escapeshellarg($php2) . ' 2>&1');
$j2 = json_decode((string)$out2, true); if (!is_array($j2) || empty($j2['ok'])) $undo('links: ' . mb_substr((string)$out2, 0, 300));
$made[] = "$SD/current"; foreach (scandir($WEB) ?: [] as $e) if (is_link("$WEB/$e")) $made[] = "$WEB/$e";
if (!is_dir("$WEB/uploads")) { @mkdir("$WEB/uploads", 0755); $made[] = "$WEB/uploads"; }
$say('links: ' . json_encode($j2) . ' · ' . count(array_filter(scandir($WEB) ?: [], fn($e) => is_link("$WEB/$e"))) . ' links in ' . $WEB);
$say("OK Love Nails installed (version $V). Next: https://$HOST/ , /admin/setup.php (owner password through AN HQ setup link), SSL (AutoSSL), cron stays off.");
