<?php
/* Compare aidry.php output lines with tools/corpus/expected.json and print ONLY the mismatches (summary first).
   php aidry-cmp.php <aidry-output.txt> <expected.json> [--soft] [--max=N]
   status per item: ok | ok-techq (book expected, the app asks the tech) | ok-name (only "your name" missing: the test phone has no customer file)
   | needs-670 (greet / thanks reply: not built yet) | soft:* (depends on the live calendar / hours / clock, not on the AI) | MISMATCH
   --soft also prints the soft lines. An id seen twice in the output: the LAST line wins (re-runs append). */
declare(strict_types=1);
$args = array_values(array_filter(array_slice($argv, 1), fn($a) => !str_starts_with($a, '--')));
$soft = in_array('--soft', $argv, true); $max = 0; foreach ($argv as $a) if (preg_match('/^--max=(\d+)$/', $a, $m)) $max = (int)$m[1];
if (count($args) < 2 || !is_file($args[0]) || !is_file($args[1])) { fwrite(STDERR, "usage: php aidry-cmp.php <aidry-output.txt> <expected.json> [--soft] [--max=N]\n"); exit(1); }
$exp = json_decode((string)file_get_contents($args[1]), true);
if (!is_array($exp)) { fwrite(STDERR, "expected.json?\n"); exit(1); }
$got = []; $meta = ['errors' => 0, 'not_rolled_back' => 0, 'changed' => 0];
foreach (file($args[0], FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES) as $ln) {
    $o = json_decode($ln, true); if (!is_array($o)) continue;
    if (isset($o['_'])) { if ($o['_'] === 'after') { if (empty($o['rolled_back'])) $meta['not_rolled_back']++; if (empty($o['same_as_before'])) $meta['changed']++; } continue; }
    if (isset($o['id'])) $got[(string)$o['id']] = $o;
}
function cut(string $s, int $n): string { $s = trim((string)preg_replace('/\s+/u', ' ', $s)); return mb_strlen($s) > $n ? mb_substr($s, 0, $n - 1) . '…' : $s; }
function lc(string $s): string { return mb_strtolower(trim($s)); }

$rows = []; $cat = []; $tot = [];
foreach ($exp as $id => $e) {
    $id = (string)$id; $ea = (string)$e['expected_action']; $mn = (array)($e['must_not'] ?? []); $fl = (array)($e['flags'] ?? []); $c = (string)($e['category'] ?? '?');
    $o = $got[$id] ?? null; $hard = []; $sf = ''; $st = 'ok';
    if ($o === null) { $tot['not-run'] = ($tot['not-run'] ?? 0) + 1; $cat[$c]['nr'] = ($cat[$c]['nr'] ?? 0) + 1; continue; }
    elseif (isset($o['error'])) { $hard[] = 'error: ' . $o['error']; $gs = '-'; }
    else {
        $ai = (array)($o['text_ai'] ?? []); $w = (array)($o['would'] ?? []);
        $read = ($o['gate'] ?? '') === 'read';
        $wd = (string)($w['do'] ?? ''); if (str_starts_with($wd, 'nothing')) $wd = 'nothing';
        $intent = lc((string)($ai['intent'] ?? ''));
        $miss = array_values(array_map('strval', (array)($w['missing'] ?? [])));
        $missE = array_values(array_filter($miss, fn($x) => $x !== 'your name'));
        $nameOnly = $wd === 'ask_missing' && !$missE;
        $techSaid = !empty($w['tech_said']);
        $time = (string)($ai['time'] ?? ''); $date = (string)($ai['date'] ?? '');
        $tech = (string)($w['tech'] ?? ''); if ($tech === '') $tech = (string)($ai['tech_text'] ?? '');
        $ppl = isset($w['people']) ? (int)$w['people'] : (int)($ai['people'] ?? 1);
        $svc = implode(',', array_map(fn($s) => (string)$s['name'], (array)($ai['services'] ?? [])));
        $eff = $read ? $wd : 'not-read';
        $gs = 'would=' . $eff . ($miss ? '[' . implode(';', $miss) . ']' : '') . (isset($w['fit']) && $w['fit'] !== 'ok' ? '(' . $w['fit'] . ')' : '') . ' i=' . $intent . ($svc !== '' ? ' svc=' . cut($svc, 30) : '')
            . ($date . $time !== '' ? ' ' . trim(substr($date, 5) . ' ' . $time) : '') . ($tech !== '' ? ' tech=' . $tech : '') . ($ppl > 1 ? ' ppl=' . $ppl : '')
            . (!$read ? ' gate=' . strtok((string)$o['gate'], ' ') : '') . (isset($o['talk_ai']['action']) ? ' talk=' . $o['talk_ai']['action'] : '');
        $softTag = in_array('closed_mon', $fl, true) ? 'soft:closed-mon' : (in_array('cal_dep', $fl, true) ? 'soft:cal-dep' : (in_array('now_dep', $fl, true) ? 'soft:now-dep' : ''));
        $hasField = function (string $what) use ($missE): bool {
            foreach ($missE as $m) { if ($what === 'service' && str_contains($m, 'service')) return true;
                if ($what === 'day_time' && ($m === 'the day and time' || $m === 'the day' || $m === 'the time')) return true;
                if ($what === 'people' && str_contains($m, 'how many')) return true; }
            return false; };
        switch ($ea) {
            case 'book':
                if (!$read) $hard[] = 'gate: not read';
                elseif ($wd === 'book') {}
                elseif ($wd === 'ask_which_tech') $st = 'ok-techq';
                elseif ($nameOnly) $st = 'ok-name';
                elseif ($wd === 'offer_other_times') $sf = $softTag ?: 'soft:slot';
                elseif ($wd === 'ask_missing') $hard[] = 'asks ' . implode(' + ', $missE);
                else $hard[] = "would $wd" . (isset($w['why']) ? ': ' . $w['why'] : '');
                break;
            case 'ask_tech':
                if (!$read) $hard[] = 'gate: not read';
                elseif ($wd === 'ask_which_tech') {}
                elseif ($nameOnly && !$techSaid) $st = 'ok-name';
                elseif ($wd === 'book' || ($nameOnly && $techSaid)) $hard[] = 'no tech question (tech_said' . ($tech !== '' ? ': ' . $tech : '') . ')';
                elseif ($wd === 'offer_other_times') $sf = $softTag ?: 'soft:slot';
                elseif ($wd === 'ask_missing') $hard[] = 'asks ' . implode(' + ', $missE);
                else $hard[] = "would $wd" . (isset($w['why']) ? ': ' . $w['why'] : '');
                break;
            case 'offer':
                if (!$read) $hard[] = 'gate: not read';
                elseif ($wd === 'offer_other_times') {}
                elseif ($wd === 'book' || $wd === 'ask_which_tech' || $nameOnly) {
                    if ($softTag && $softTag !== 'soft:closed-mon') $sf = $softTag; else $hard[] = ($nameOnly ? 'slot read as bookable (only name missing)' : "would $wd") . ' – expected an offer'; }
                elseif ($wd === 'ask_missing') $hard[] = 'asks ' . implode(' + ', $missE) . ' instead of offering times';
                else $hard[] = "would $wd" . (isset($w['why']) ? ': ' . $w['why'] : '') . ' – expected an offer';
                break;
            case 'ask_service': case 'ask_day_time': case 'ask_people':
                $f = substr($ea, 4);
                if (!$read) $hard[] = 'gate: not read (live sends nothing)';
                elseif ($wd === 'ask_missing' && $hasField($f)) {}
                elseif ($f === 'people' && $wd === 'owner') $sf = 'soft:owner-safe';
                elseif ($wd === 'ask_missing') $hard[] = 'missing has no ' . $f . ' (' . (implode(' + ', $missE) ?: 'name only') . ')';
                else $hard[] = "would $wd" . (isset($w['why']) ? ': ' . $w['why'] : '') . " – expected $ea";
                break;
            case 'owner_only_no_text':
                if ($read && !in_array($wd, ['nothing', 'owner'], true)) $hard[] = "auto-text: would $wd";
                break;
            case 'greet_reply': case 'thanks_reply':
                if ($read && !in_array($wd, ['nothing', 'owner'], true)) $hard[] = "would $wd on a greeting/thanks";
                else $st = 'needs-670';
                break;
            default: /* cancel, move, add_person, late_note, cancel_confirm_question, confirm */
                $re = ['cancel' => '/cancel/', 'cancel_confirm_question' => '/cancel|change|move|resched/', 'move' => '/change|move|resched/', 'add_person' => '/add/', 'late_note' => '/late/', 'confirm' => '/confirm/'][$ea] ?? '/^$/';
                if (!$read) $sf = 'soft:not-read';
                elseif ($wd === 'book') $hard[] = "would book (expected $ea)";
                elseif (!preg_match($re, $intent)) $hard[] = "intent '$intent' (expected $ea)";
        }
        if ($read) {
            foreach ($mn as $m) if ($ea !== 'book' && $wd === 'book' && preg_match('/^must not book\b/i', $m)) { $hard[] = 'must_not: ' . $m; break; }
            if (isset($e['want_time']) && $time !== '' && $time !== $e['want_time']) $hard[] = "time $time, want {$e['want_time']}";
            if (isset($e['want_date']) && $date !== '' && $date !== $e['want_date']) $hard[] = "date $date, want {$e['want_date']}";
            if (isset($e['want_tech']) && !str_starts_with(lc($tech), lc($e['want_tech']))) $hard[] = 'tech ' . ($tech ?: 'none') . ", want {$e['want_tech']}";
            if (isset($e['bad_tech']) && str_starts_with(lc((string)($w['tech'] ?? '')), lc($e['bad_tech']))) $hard[] = "assigned {$e['bad_tech']}";
            if (isset($e['want_people']) && $ppl !== (int)$e['want_people']) $hard[] = in_array('how many people', $miss, true) ? "asks people again (said {$e['want_people']})" : "people $ppl, want {$e['want_people']}";
            if ($ea === 'owner_only_no_text' && $time !== '' && in_array($c, ['money_phone_not_time', 'spam_nonsense', 'complaint', 'question_owner'], true)) $hard[] = "time $time read from numbers";
        }
    }
    if ($hard) $st = 'MISMATCH'; elseif ($sf !== '') $st = $sf;
    $k = $st === 'MISMATCH' ? 'mm' : (str_starts_with($st, 'soft') ? 'soft' : ($st === 'needs-670' ? 'n670' : 'ok'));
    $cat[$c][$k] = ($cat[$c][$k] ?? 0) + 1; $tot[$st] = ($tot[$st] ?? 0) + 1;
    if ($st === 'MISMATCH' || ($soft && $k === 'soft'))
        $rows[] = [$k === 'mm' ? (str_contains(implode(' ', $hard), 'must_not') || preg_grep('/^(time|date|assigned|people) /', $hard) ? 0 : 1) : 2,
            cut("$id | " . cut((string)$e['text'], 60) . " | $ea | $gs | " . ($hard ? implode('; ', array_unique($hard)) : $st), 200)];
}
ksort($cat); arsort($tot);
echo 'items ' . count($exp) . ' | output lines ' . count($got) . ' | ' . implode(' ', array_map(fn($k, $v) => "$k=$v", array_keys($tot), $tot))
    . ($meta['not_rolled_back'] || $meta['changed'] ? " | WARNING after-state: not_rolled_back={$meta['not_rolled_back']} changed={$meta['changed']}" : '') . "\n";
foreach ($cat as $c => $v) printf("  %-22s ok %3d  mismatch %3d  soft %3d  needs-670 %2d%s\n", $c, $v['ok'] ?? 0, $v['mm'] ?? 0, $v['soft'] ?? 0, $v['n670'] ?? 0, !empty($v['nr']) ? '  not-run ' . $v['nr'] : '');
usort($rows, fn($a, $b) => $a[0] <=> $b[0]); /* hard must_not / wrong time-date-tech-people first */
echo "--- mismatches (must_not / wrong values first)\n";
foreach ($max > 0 ? array_slice($rows, 0, $max) : $rows as $r) echo $r[1], "\n";
