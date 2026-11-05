<?php
$T = getenv('T'); define('SITE_ROOT', $T . '/main'); putenv('HQ_DATA=' . $T . '/hq');
@mkdir($T . '/main/inc', 0777, true);
require '/home/claude/int648/inc/hq.php';
$R = []; $ok = function ($n, $c, $i = '') use (&$R) { $R[] = (bool)$c; echo ($c ? '✓ ' : '✗ ') . $n . ($c ? '' : '  → ' . json_encode($i)) . "\n"; };
file_put_contents($T . '/hq/hq.json', json_encode(['salons' => [['id' => 's2', 'root' => $T . '/s2']]]));
$p = new PDO('sqlite:' . $T . '/s2.sqlite');
$p->exec("CREATE TABLE IF NOT EXISTS calls (id INTEGER PRIMARY KEY, kind TEXT, dur_sec INT, created_at TEXT)");
$r = hq_ai('s2'); $ok('1 defaults: 100 min, $50, $0.50, not free, off', $r['plan'] == ['incl' => 100, 'usd' => 50.0, 'over' => 0.5, 'free' => false] && $r['on'] === false && $r['months'][0]['total'] == 50.0, $r);
$m = date('Y-m') . '-03 10:00:00';
foreach ([61, 600, 3000, 3000, 59] as $d) $p->prepare("INSERT INTO calls (kind, dur_sec, created_at) VALUES ('agent', ?, ?)")->execute([$d, $m]);
$p->prepare("INSERT INTO calls (kind, dur_sec, created_at) VALUES ('call', 9999, ?)")->execute([$m]); /* not AI */
$p->prepare("INSERT INTO calls (kind, dur_sec, created_at) VALUES ('agent', 600, ?)")->execute([date('Y-m', strtotime(date('Y-m-01') . ' -1 month')) . '-20 10:00:00']);
$r = hq_ai('s2'); $t = $r['months'][0];
$ok('2 minutes rounded up per call, only AI calls: 2+10+50+50+1 = 113', $t['minutes'] === 113 && $t['calls'] === 5, $t);
$ok('3 13 over x $0.50 = $6.50, total $56.50', $t['over'] === 13 && $t['overUsd'] == 6.5 && $t['total'] == 56.5, $t);
$ok('4 last month separate: 10 min, $50', $r['months'][1]['minutes'] === 10 && $r['months'][1]['total'] == 50.0, $r['months'][1]);
$r = hq_ai('s2', ['on' => true, 'incl' => '200', 'usd' => '80', 'over' => '0.75']);
$ok('5 HQ saves on + new numbers; under 200 min = $80', $r['on'] && $r['plan']['incl'] === 200 && $r['months'][0]['total'] == 80.0, $r);
$s = $p->query("SELECT v FROM settings WHERE k = 'call_agent_ok'")->fetchColumn(); $ok('6 salon setting call_agent_ok = 1', $s === '1', $s);
$r = hq_ai('s2', ['free' => true]); $ok('7 Free: bill $0', $r['plan']['free'] && $r['months'][0]['total'] == 0.0, $r);
try { hq_ai('s2', ['over' => '-1']); $ok('8 bad number refused', false); } catch (RuntimeException $e) { $ok('8 bad number refused', true); }
try { hq_ai('s2', ['incl' => 'abc']); $ok('8b text refused', false); } catch (RuntimeException $e) { $ok('8b text refused', true); }
$r = hq_ai('s2', ['on' => false]); $s = $p->query("SELECT v FROM settings WHERE k = 'call_agent_ok'")->fetchColumn(); $ok('9 off -> call_agent_ok 0', !$r['on'] && $s === '0', $s);
$log = json_encode(hq_load()['log'] ?? []); $ok('10 HQ log has AI call rows', substr_count($log, 'AI call') >= 3, $log);
$aud = json_encode($p->query("SELECT * FROM audit_log WHERE target LIKE 'AI call%'")->fetchAll()); $ok('11 salon audit has it', strlen($aud) > 10, $aud);
$c = hq_card(['id' => 's2', 'root' => $T . '/s2']); $ok('12 card has the AI line', isset($c['ai']) && $c['ai']['min'] === 113 && $c['ai']['on'] === false, $c['ai'] ?? $c);
$p->exec('DROP TABLE calls'); $r = hq_ai('s2'); $ok('13 a salon with no calls table: 0 minutes, no error', $r['months'][0]['minutes'] === 0, $r);
echo '== ' . array_sum($R) . ' / ' . count($R) . " PASS\n";
