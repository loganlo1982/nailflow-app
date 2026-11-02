<?php
/* LAMWEB sim631 (LENH-631) - REAL model conversations with the Telnyx assistant's OWN prompt + tools (tx_instructions / tx_tools / tx_model),
   on a COPY of the app. Telnyx chat completions only: NO call, NO SMS, NO database change (the tools answer here, fake). The key is read by tx_key() and never printed.
   Run (server, on the copy with fix631):  php sim631.php <app dir>          -> sim631-ket-qua.txt next to this script */
declare(strict_types=1);
$A = rtrim($argv[1] ?? '', '/'); if ($A === '' || !is_file("$A/inc/core.php")) { fwrite(STDERR, "usage: php sim631.php <app dir>\n"); exit(2); }
require "$A/inc/core.php"; settings(); require_once "$A/inc/calls.php"; require_once "$A/inc/calls-agent.php"; require_once "$A/inc/calls-tx.php";
$OUT = __DIR__ . '/sim631-ket-qua.txt'; file_put_contents($OUT, '');
function say(string $s): void { global $OUT; echo $s, "\n"; file_put_contents($OUT, $s . "\n", FILE_APPEND); }
if (tx_key() === '') { say('STOP: Telnyx key not set on this copy (Settings -> Calls -> Telnyx)'); exit(3); }
$g = cl_agent_data('');
$sys = strtr(tx_instructions(), ['{{now}}' => $g['now'], '{{days}}' => implode("\n", $g['days']), '{{menu}}' => implode("\n", $g['menu']), '{{techs}}' => implode("\n", $g['techs']), '{{caller_name}}' => 'none', '{{upcoming}}' => 'none']);
$tools = []; foreach (tx_tools() as $t) { if (($t['type'] ?? '') === 'webhook') $tools[] = ['type' => 'function', 'function' => ['name' => $t['webhook']['name'], 'description' => $t['webhook']['description'], 'parameters' => $t['webhook']['body_parameters']]];
    elseif (($t['type'] ?? '') === 'hangup') $tools[] = ['type' => 'function', 'function' => ['name' => 'end_call', 'description' => (string)($t['hangup']['description'] ?? 'Hang up.'), 'parameters' => ['type' => 'object', 'properties' => (object)[]]]]; }
say('== sim631 ' . date('Y-m-d H:i T') . ' · model ' . tx_model() . ' · prompt md5 ' . substr(md5(tx_instructions()), 0, 8) . ' · ' . count($tools) . ' tools · version ' . APP_VERSION);
/* the fake caller: answers what the AI asks */
function caller(string $ai, array &$s): string {
    $l = strtolower($ai);
    if (preg_match('/\bgel\b/', $l) && preg_match('/\bdip\b/', $l) && preg_match('/acrylic|regular/', $l)) { $s['asked']++; return $s['type']; }
    if (str_contains($l, 'same for everyone') || str_contains($l, 'same for all') || str_contains($l, 'everyone the same') || preg_match('/all (three|3)[^.?]*\b(gel|dip|same)/', $l)) { $s['same_q']++; return $s['same']; }
    if (preg_match('/\bname/', $l) && !str_contains($l, $s['nameword'])) return $s['names'];
    if (str_contains($l, 'bye') || str_contains($l, 'all set')) return 'Thanks, bye!';
    return 'Yes, that\'s right.';
}
function chat(array $msgs, array $tools): array {
    for ($k = 0; $k < 4; $k++) { /* CHAT 631: an empty answer (API hiccup) -> ask again, up to 4 times */
        $r = tx_api('POST', '/ai/openai/chat/completions', ['model' => tx_model(), 'messages' => $msgs, 'tools' => $tools, 'temperature' => 0.3, 'max_tokens' => 600], 60);
        $m = (array)($r['choices'][0]['message'] ?? []);
        if (trim((string)($m['content'] ?? '')) !== '' || !empty($m['tool_calls'])) return $m;
        sleep(2);
    }
    return $m;
}
function run(string $id, string $first, array $s, array $sys_tools): array {
    [$sys, $tools] = $sys_tools; $s += ['asked' => 0, 'same_q' => 0, 'book' => null, 'asked_before_book' => 0, 'log' => []];
    $m = [['role' => 'system', 'content' => $sys], ['role' => 'assistant', 'content' => tx_greeting()], ['role' => 'user', 'content' => $first]]; $s['log'][] = 'C: ' . $first;
    for ($i = 0; $i < 14; $i++) {
        try { $r = chat($m, $tools); } catch (Throwable $e) { $s['log'][] = 'ERR ' . mb_substr($e->getMessage(), 0, 200); break; }
        $tc = (array)($r['tool_calls'] ?? []); $txt = trim((string)($r['content'] ?? ''));
        $m[] = array_filter(['role' => 'assistant', 'content' => $txt !== '' ? $txt : null, 'tool_calls' => $tc ?: null], fn($v) => $v !== null);
        if ($txt !== '') $s['log'][] = 'AI: ' . $txt;
        if ($tc) { $end = false;
            foreach ($tc as $t) { $fn = (string)($t['function']['name'] ?? ''); $args = json_decode((string)($t['function']['arguments'] ?? '{}'), true) ?: [];
                $s['log'][] = 'TOOL ' . $fn . ' ' . json_encode($args, JSON_UNESCAPED_UNICODE);
                $res = match ($fn) { 'check_times' => 'OPEN ' . ($args['date'] ?? '') . ' ' . ($args['time'] ?? ''), 'book' => 'BOOKED id 9001 ' . ($args['date'] ?? '') . ' ' . ($args['time'] ?? '') . " – Tell them they're all set and get a text in a minute.",
                    'find_appointments' => 'none', 'add_note' => 'NOTED – it goes on the appointment when booked (pass it as note to book).', 'transfer_owner' => 'Transferring the caller to the salon now.', 'end_call' => 'The call ends now.', default => 'OK' };
                if ($fn === 'book' && $s['book'] === null) { $s['book'] = $args; $s['asked_before_book'] = $s['asked']; }
                if ($fn === 'end_call' || $fn === 'transfer_owner') $end = true;
                $m[] = ['role' => 'tool', 'tool_call_id' => (string)($t['id'] ?? ''), 'content' => $res]; }
            if ($end) break; continue; }
        if ($txt === '') break;
        if ($s['book'] !== null && preg_match('/bye|see you/i', $txt)) break;
        $u = caller($txt, $s); $m[] = ['role' => 'user', 'content' => $u]; $s['log'][] = 'C: ' . $u;
    }
    return $s;
}
$ST = [$sys, $tools]; $R = [];
function ok(string $n, bool $c, array $s): void { global $R; $R[] = $c; say(($c ? '✓ ' : '✗ ') . $n); foreach ($s['log'] as $l) say('     ' . mb_substr($l, 0, 400)); }
$types = function (?array $b): array { if (!$b) return []; $t = [strtolower((string)($b['mani_type'] ?? ''))]; foreach ((array)($b['persons'] ?? []) as $p) $t[] = strtolower((string)($p['mani_type'] ?? '')); return array_values(array_filter($t, fn($x) => $x !== '' && $x !== 'none')); };
$s = run('A', "Hi, I'd like to book a manicure this Friday at 2 PM. My name is Sofia.", ['type' => 'Dip, please.', 'same' => 'Yes.', 'names' => 'Sofia.', 'nameword' => 'sofia'], $ST);
ok('A "manicure Friday at 2" (chua noi loai) -> AI HOI loai TRUOC khi book -> "dip" -> book mani_type dip', $s['asked_before_book'] >= 1 && in_array('dip', $types($s['book']), true), $s);
$s = run('B', "Hi, can I get a gel manicure tomorrow at 3? This is Kim.", ['type' => 'Gel.', 'same' => 'Yes.', 'names' => 'Kim.', 'nameword' => 'kim'], $ST);
ok('B "gel manicure" (da noi loai) -> KHONG hoi lai -> book mani_type gel', $s['book'] !== null && $s['asked'] === 0 && array_intersect(['gel', 'gel_real'], $types($s['book'])), $s);
$s = run('C', "Hi, I want to book manicures for 3 people this Saturday at 1. I'm Ana.", ['type' => 'Gel.', 'same' => 'Yes, same for everyone.', 'names' => 'Ana, Lily and Rosa.', 'nameword' => 'lily'], $ST);
ok('C nhom 3 nguoi -> hoi loai (+ "Same for everyone?") -> gel -> book 3 nguoi gel', $s['asked_before_book'] >= 1 && count((array)($s['book']['persons'] ?? [])) === 3 && array_intersect(['gel', 'gel_real'], $types($s['book'])), $s);
$s = run('D', "I'd like a manicure Friday at 2. Name's Jen.", ['type' => "I'm not sure, I'll decide there.", 'same' => 'Yes.', 'names' => 'Jen.', 'nameword' => 'jen'], $ST);
ok('D "not sure / I\'ll decide there" -> book ban co ban (unsure / plain / none), hoi loai CHI 1 lan', $s['book'] !== null && $s['asked'] === 1 && !array_intersect(['gel', 'gel_real', 'dip', 'acrylic', 'gel_fake', 'regular'], $types($s['book'])), $s);
$s = run('E', "Can I book a pedicure this Friday at 2? I'm Mia.", ['type' => 'Regular.', 'same' => 'Yes.', 'names' => 'Mia.', 'nameword' => 'mia'], $ST);
ok('E pedicure -> KHONG hoi loai (nhu cu) -> book', $s['book'] !== null && $s['asked'] === 0, $s);
$s = run('F', "Hi, manicures for my friends and me, 3 of us, this Saturday at 1. I'm Ana.", ['type' => 'Not the same - Ana wants gel, Lily dip, and Rosa acrylic.', 'same' => 'No - Ana gel, Lily dip, Rosa acrylic.', 'names' => 'Ana, Lily and Rosa.', 'nameword' => 'lily'], $ST);
$pt = array_map(fn($p) => strtolower((string)($p['mani_type'] ?? '')), (array)($s['book']['persons'] ?? []));
ok('F nhom KHAC loai (gel / dip / acrylic) -> persons[].mani_type tung nguoi', count($pt) === 3 && in_array('dip', $pt, true) && in_array('acrylic', $pt, true), $s);
say('PASS ' . array_sum($R) . '/' . count($R));
