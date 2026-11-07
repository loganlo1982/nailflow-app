<?php
/* READ-ONLY dry run of the REAL AI reading of customer texts (the live keys on the server) – nothing is booked, texted, pushed or saved.
   For each item: the SAME text-message AI read as inc/textbook.php tb_try (cl_ai + its ai_extra NOTE, then cl_ai_after + cl_weekday_fix; several texts → tb_latest),
   and for items with "turns" also the phone switchboard AI (calls-talk.php cl_talk_ai, a synthetic $st['log']).
   tb_eval is NEVER called (it texts / pushes / books): its pure checks are copied below (missing, tech said, cl_ivr_fit, cl_ivr_offer) → "would".
   No side effects: (1) DB session READ ONLY + one READ ONLY transaction, ROLLBACK at the end (any write throws); (2) every texting / push / phone API base
   pointed to a dead local port (SMSGATE_BASE, NF_TX_BASE, NF_SW_BASE, FCM_BASE, FCM_OAUTH); (3) no sending function is called; (4) autosend / messages /
   appointments max ids + the tb_ai_n counter printed before / after. The tool's own AI calls are NOT counted in tb_ai_n (that would be a write).
   SALON_ID=<site> php aidry.php <items.json> [--talk]     items = [{"id":…, "text":"…", "phone":"+1…"?}, {"id":…, "turns":["…", "…"] }] (≤ 60, 1 s between AI calls)
   --talk = cl_talk_ai for the single-text items too. A turn may be {"who":"salon","text":"…"} (a switchboard line; the text AI reads only the customer's ones). */
declare(strict_types=1);
const AIDRY_MAX = 60;
const AIDRY_DEAD = 'http://127.0.0.1:9'; /* the discard port: connection refused at once */
const AIDRY_PHONE = '+15550100199';      /* a fictional 555-01xx number: no customer file, no upcoming appointment */
$site = (string)getenv('SALON_ID'); if (!preg_match('/^[a-z0-9]+$/', $site)) { fwrite(STDERR, "SALON_ID?\n"); exit(1); }
$file = ''; $talkAll = false; foreach (array_slice($argv, 1) as $a) { if ($a === '--talk') $talkAll = true; elseif ($file === '') $file = $a; }
$items = $file !== '' && is_file($file) ? json_decode((string)file_get_contents($file), true) : null;
if (!is_array($items) || !array_is_list($items)) { fwrite(STDERR, "usage: SALON_ID=<site> php aidry.php <items.json> [--talk]\n"); exit(1); }
if (count($items) > AIDRY_MAX) { fwrite(STDERR, 'max ' . AIDRY_MAX . ' items per run (got ' . count($items) . ")\n"); exit(1); }

/* (2) kill switch for anything that could text / push / call: set BEFORE any app code is loaded */
foreach (['SMSGATE_BASE', 'NF_TX_BASE', 'NF_SW_BASE', 'FCM_BASE', 'FCM_OAUTH'] as $e) { putenv("$e=" . AIDRY_DEAD); $_ENV[$e] = AIDRY_DEAD; }
define('AIDRY_READ_ONLY', 1);

require "/home/uyurpyzubx0m/app/sites/$site/current/inc/core.php";
settings();
/* the same files as call_in.php cl_job_lib() / cron/tx-mp3.php (plain functions only: api.php returns at once with NF_API_LIB) */
if (!defined('NF_API_LIB')) define('NF_API_LIB', 1);
foreach (['/inc/backup.php', '/inc/import.php', '/inc/totp.php', '/inc/rebook.php', '/inc/gallery.php', '/inc/birthday.php', '/inc/paypal.php', '/inc/review.php', '/inc/giftcards.php',
    '/inc/outbox.php', '/inc/logo.php', '/inc/reports.php', '/inc/checkout.php', '/inc/payroll.php', '/inc/export.php', '/inc/yearend.php', '/inc/referral.php', '/inc/promolinks.php',
    '/inc/turnq.php', '/inc/apptoffers.php', '/inc/rewards.php', '/inc/api/_auth.php', '/inc/api/_menu.php', '/inc/api/_texts.php', '/inc/api/_kiosk.php', '/inc/api/_out.php'] as $f) require_once APP_ROOT . $f;
require_once APP_ROOT . '/api.php'; require_once APP_ROOT . '/inc/calls-job.php'; require_once APP_ROOT . '/inc/replies.php'; require_once APP_ROOT . '/inc/textbook.php';

/* (1) the database: READ ONLY session + READ ONLY transaction (MySQL / MariaDB: any INSERT / UPDATE / DELETE throws), rolled back at the end */
if (is_sqlite()) { q('PRAGMA query_only = ON'); q('BEGIN'); }
else { q('SET SESSION TRANSACTION READ ONLY'); q('START TRANSACTION READ ONLY'); }

function aidry_state(): array {
    $o = []; foreach (['autosend', 'messages', 'appointments'] as $t) { try { $o[$t . '_max_id'] = (int)q("SELECT MAX(id) FROM $t")->fetchColumn(); } catch (Throwable $e) { $o[$t . '_max_id'] = 'n/a'; } }
    $n = json_decode((string)q("SELECT v FROM settings WHERE k = 'tb_ai_n'")->fetchColumn(), true);
    $o['tb_ai_n'] = is_array($n) ? $n : null; $o['tb_day_max'] = TB_DAY_MAX;
    foreach (['call_ai_cap', 'call_cap_day', 'tb_on'] as $k) $o[$k] = (string)q('SELECT v FROM settings WHERE k = ?', [$k])->fetchColumn();
    return $o;
}
function aidry_svc(array $ids): array { $ids = array_values(array_filter(array_map('intval', $ids))); return $ids ? array_map(fn($s) => ['id' => (int)$s['id'], 'name' => (string)$s['name']], services_by_ids($ids)) : []; }
function aidry_hm(int $m): string { return $m < 0 ? '' : sprintf('%02d:%02d', intdiv($m, 60), $m % 60); }
function aidry_fit(string $date, int $start, array $ppl): array {
    $fit = cl_ivr_fit($date, $start, $ppl); $o = ['fit' => $fit === '' ? 'ok' : $fit];
    if ($fit !== '') $o['offered'] = array_map(fn($x) => $x[0] . ' ' . aidry_hm((int)$x[1]), cl_ivr_offer($date, $start, $ppl));
    return $o;
}
/** tb_eval's decisions WITHOUT its tb_send / tb_push / tb_book / tb_state_set (2.99.669 textbook.php): what it WOULD do. */
function aidry_would(string $p, array $j, array $c, array $st): array {
    $file = customer_by_phone($p);
    $name = mb_strtoupper(trim(mb_substr((string)preg_replace('/\s+/u', ' ', (string)($j['customer_name'] ?? '')), 0, 55)));
    if ($name === '' && $file && trim((string)$file['name']) !== '') $name = mb_strtoupper(trim((string)$file['name']));
    if (!empty($j['tech_last'])) {
        $lt = (int)q("SELECT staff_id FROM appointments WHERE phone = ? AND kind = 'appt' AND status IN ('arrived', 'paid') AND staff_id > 0 ORDER BY appt_date DESC, start_min DESC LIMIT 1", [$p])->fetchColumn();
        if (!$lt || !q('SELECT 1 FROM staff WHERE id = ? AND active = 1', [$lt])->fetchColumn()) return ['do' => 'owner', 'why' => 'same tech as last time: none found'];
        $j['tech_id'] = $lt; $j['tech_text'] = ''; }
    $tt = trim((string)($j['tech_text'] ?? ''));
    $pplAsk = false; $pp = max((int)($j['people'] ?? 1), count(array_filter((array)($j['party'] ?? []), 'is_array')));
    if ($pp > 2 && empty($st['add']) && tb_ppl_said((string)$c['text_c'], !empty($st['pplq'])) !== $pp) { $j['people'] = 1; $j['party'] = []; $j['same_services'] = false; $pplAsk = true; }
    $b = cl_ivr_jppl($c, $j); $n = count($b['ppl']);
    $base = ['people' => $n, 'tech_id' => (int)$b['tech'], 'tech' => $b['tech'] ? staff_name((int)$b['tech']) : '', 'ppl' => array_map(fn($x) => ['sids' => $x['sids'], 'dur' => $x['dur'], 'staff' => $x['staff']], $b['ppl'])];
    if ($tt !== '' && !$b['tech'] && !preg_match('/^(any|anyone|anybody|any tech|no|none|no preference|whoever)$/iu', $tt)) return ['do' => 'owner', 'why' => 'tech name not at this salon: ' . $tt] + $base;
    if ($n > CL_GROUP_MAX || ($n > 1 && !$b['ok'])) return ['do' => 'owner', 'why' => 'several people, not clear who gets what'] + $base;
    $cf = $j['confidence'] ?? null; $conf = is_numeric($cf) ? (float)$cf : 1.0; if ($conf > 1 && $conf <= 100) $conf /= 100;
    if ($conf < 0.5) return ['do' => 'owner', 'why' => 'confidence < 0.5'] + $base;
    $date = valid_date((string)($j['date'] ?? '')) ? (string)$j['date'] : '';
    $start = preg_match('/^(\d{1,2}):(\d{2})$/', (string)($j['time'] ?? ''), $m) && (int)$m[1] < 24 && (int)$m[2] < 60 ? (int)$m[1] * 60 + (int)$m[2] : -1;
    if ($date !== '' && $date > date('Y-m-d', strtotime('+90 days'))) return ['do' => 'owner', 'why' => 'date > 90 days'] + $base;
    if ($date !== '' && empty($st['add']) && array_filter(rp_upcoming($p), fn($a) => $a['appt_date'] === $date)) return ['do' => 'owner', 'why' => 'already has an appointment that day'] + $base;
    $svcOk = $b['ok'] && empty($j['svc_unsaid']);
    $techSaid = !empty($st['techq']) || $b['tech'] || cl_ivr_techsaid($j) || cl_talk_anyone((string)$c['text_c']);
    $miss = []; if (!$svcOk) $miss[] = $n > 1 ? 'the service for each person' : 'the service';
    if ($date === '' && $start < 0) $miss[] = 'the day and time'; elseif ($date === '') $miss[] = 'the day'; elseif ($start < 0) $miss[] = 'the time';
    if ($name === '') $miss[] = 'your name';
    if ($pplAsk) $miss[] = 'how many people';
    $base += ['name' => $name, 'tech_said' => (bool)$techSaid, 'svc_ok' => (bool)$svcOk];
    if ($miss) return ['do' => 'ask_missing', 'missing' => $miss, 'also_asks_tech' => !$techSaid] + $base;
    $f = aidry_fit($date, $start, $b['ppl']);
    if ($f['fit'] !== 'ok') return ['do' => 'offer_other_times'] + $f + $base;
    if (!$techSaid) return ['do' => 'ask_which_tech'] + $f + $base;
    return ['do' => 'book'] + $f + $base;
}
function aidry_out(array $o): void { echo json_encode($o, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES), "\n"; }

$before = aidry_state();
aidry_out(['_' => 'before', 'site' => $site, 'version' => defined('APP_VERSION') ? APP_VERSION : '', 'ai' => cai_on() ? 'claude ' . CL_AI_MODEL : (cl_stt_info()['set'] ? 'openai ' . CL_OAI_MODEL : 'NO KEY'),
    'talk_ai' => trim((string)(cl_stt_get()['key'] ?? '')) !== '' ? 'openai gpt-4o-mini' : 'NO KEY', 'nf_ai_url' => (string)getenv('NF_AI_URL'), 'nf_oai_url' => (string)getenv('NF_OAI_URL')] + $before);
$calls = 0; $pause = function () use (&$calls) { if ($calls++ > 0) sleep(1); };

try {
    foreach ($items as $k => $it) {
        $id = is_array($it) ? ($it['id'] ?? $k + 1) : $k + 1; $o = ['id' => $id];
        try {
            if (!is_array($it)) throw new RuntimeException('item is not an object');
            $p = norm_phone((string)($it['phone'] ?? AIDRY_PHONE)); if (strlen($p) !== 12) $p = AIDRY_PHONE;
            $turns = []; /* [['c'|'s', text], …] */
            if (isset($it['turns']) && is_array($it['turns'])) foreach ($it['turns'] as $t) {
                if (is_array($t)) { $who = strtolower((string)($t['who'] ?? $t[0] ?? 'c')); $tx = (string)($t['text'] ?? $t[1] ?? ''); $turns[] = [in_array($who, ['s', 'salon', 'switchboard'], true) ? 's' : 'c', $tx]; }
                else $turns[] = ['c', (string)$t]; }
            elseif (isset($it['text'])) $turns[] = ['c', (string)$it['text']];
            $turns = array_values(array_filter($turns, fn($x) => trim($x[1]) !== ''));
            $in = array_values(array_map(fn($x) => $x[1], array_filter($turns, fn($x) => $x[0] === 'c')));
            if (!$in) throw new RuntimeException('no customer text');
            $text = (string)end($in);
            /* what tb_try checks before the AI (no AI spent live when these say no) */
            $o['gate'] = tb_is_ack($text) ? 'ack (live: not read)' : (count($in) === 1 && !tb_looks($text) ? 'no booking words (live: not read unless in a conversation)' : 'read');
            /* --- the text AI, exactly as tb_try builds it --- */
            $words = count($in) > 1 ? implode("\n", array_map(fn($x, $i) => ($i === count($in) - 1 ? 'NEWEST text: ' : 'Earlier text: ') . $x, $in, array_keys($in))) : $text;
            $c = ['id' => 0, 'kind' => 'vm', 'from_phone' => $p, 'text_c' => $words, 'text_s' => '', 'ai_json' => '', 'call_sid' => ''];
            $c['ai_extra'] = "NOTE: this is NOT a phone call. The words above are the customer's TEXT MESSAGES (SMS) to the salon, oldest first (several texts = one request; a later text adds to or corrects an earlier one). Read them like a voicemail.\n"
                . "When the texts disagree, the NEWEST text wins for the day, the time, the service, the tech and the number of people (\"Sunday at 6\" then \"how about 1:30\" = Sunday 1:30, never 6). "
                . "people: only a count the customer clearly said (\"2 people\", \"me and my daughter\"); a number that may be something else (\"for 7 pedi\") is NOT people – then people = 1.\n";
            $pause(); $raw = cl_ai($c); $j = cl_weekday_fix($c, cl_ai_after($c, $raw));
            if (count($in) > 1) $j = tb_latest($j, $in);
            $sids = array_values(array_map('intval', (array)($j['service_ids'] ?? [])));
            $o['text_ai'] = ['intent' => (string)($j['intent'] ?? ''), 'service_ids' => $sids, 'services' => aidry_svc($sids), 'service_text' => (string)($j['service_text'] ?? ''),
                'svc_unsaid' => !empty($j['svc_unsaid']), 'date' => (string)($j['date'] ?? ''), 'time' => (string)($j['time'] ?? ''), 'tech_id' => (int)($j['tech_id'] ?? 0), 'tech_text' => (string)($j['tech_text'] ?? ''),
                'tech_last' => !empty($j['tech_last']), 'people' => (int)($j['people'] ?? 1), 'party' => (array)($j['party'] ?? []), 'name' => (string)($j['customer_name'] ?? ''),
                'missing' => (array)($j['missing'] ?? []), 'confidence' => $j['confidence'] ?? null, 'summary' => (string)($j['summary'] ?? '')]
                + (isset($j['date_fix']) ? ['date_fix' => $j['date_fix']] : []) + (($raw['date'] ?? '') !== ($j['date'] ?? '') || ($raw['time'] ?? '') !== ($j['time'] ?? '') ? ['ai_raw_when' => ($raw['date'] ?? '') . ' ' . ($raw['time'] ?? '')] : []);
            $o['would'] = strtolower(trim((string)($j['intent'] ?? ''))) !== 'book' ? ['do' => 'nothing (not a booking: Messages + normal push)'] : aidry_would($p, $j, $c, []);
            /* --- the switchboard AI (cl_talk_ai) on the same words --- */
            if (function_exists('cl_talk_ai') && (isset($it['turns']) || $talkAll)) {
                $pause(); $t = cl_talk_ai(['id' => 0, 'from_phone' => $p], ['log' => $turns], 20);
                if ($t === null) $o['talk_ai'] = null;
                else { $ps = array_values(array_filter((array)($t['persons'] ?? []), 'is_array')); $all = []; foreach ($ps as $x) $all = array_merge($all, array_map('intval', (array)($x['service_ids'] ?? [])));
                    $all = array_merge($all, array_map('intval', (array)($t['service_ids'] ?? [])));
                    $o['talk_ai'] = ['action' => (string)$t['action'], 'services' => aidry_svc(array_values(array_unique($all))), 'persons' => $ps, 'date' => (string)$t['date'], 'time' => (string)$t['time'],
                        'window' => trim($t['window_from'] . '–' . $t['window_to'], '–'), 'people' => (int)$t['people'], 'name' => (string)$t['name'], 'missing' => (array)$t['missing'], 'note' => (string)$t['note'], 'question_topic' => (string)$t['question_topic'], 'say' => (string)$t['say']];
                    $td = valid_date((string)$t['date']) ? (string)$t['date'] : ''; $tm = preg_match('/^(\d{1,2}):(\d{2})$/', (string)$t['time'], $mm) ? (int)$mm[1] * 60 + (int)$mm[2] : -1;
                    if ($t['action'] === 'book_new' && $td !== '' && $tm >= 0 && $ps) {
                        $tj = ['service_ids' => (array)($ps[0]['service_ids'] ?? []), 'service_text' => (string)($ps[0]['service_text'] ?? ''), 'tech_id' => (int)($ps[0]['tech_id'] ?? 0), 'people' => max(1, (int)$t['people'], count($ps)), 'party' => $ps, 'same_services' => false];
                        $tb = cl_ivr_jppl(['text_c' => implode(' ', $in)], $tj); $o['talk_ai']['check'] = ($tb['ok'] ? aidry_fit($td, $tm, $tb['ppl']) : ['fit' => 'service not clear']) + ['tech' => $tb['tech'] ? staff_name((int)$tb['tech']) : '']; } } }
        } catch (Throwable $e) { $o['error'] = get_class($e) . ': ' . $e->getMessage(); }
        aidry_out($o);
    }
} finally {
    q('ROLLBACK'); /* everything of this run is undone (nothing could be written anyway: READ ONLY) */
    $after = aidry_state(); /* read after the ROLLBACK (outside the snapshot): a real text / booking arriving meanwhile can move these – this tool never does */
    aidry_out(['_' => 'after', 'ai_calls' => $calls, 'rolled_back' => true, 'same_as_before' => $before === $after] + $after);
}
