<?php
/* CHAT 625 – conversation test with the REAL model (Telnyx chat completions), NO call, NO SMS, NO booking (tools are faked here).
   SALON_ID=an php sim625.php <live app> <dir with the calls-agent.php to test> <label> [scenario]. Read-only on the live DB. Prints the transcript. */
$app = $argv[1]; $ag = $argv[2]; $mode = $argv[3] ?? 'test'; $only = $argv[4] ?? '';
chdir($app); require $app . '/inc/core.php'; settings(); require_once $ag . '/inc/calls-agent.php'; require_once $app . '/inc/calls-tx.php';
$g = cl_agent_data('');
$sys = str_replace(['{{now}}', '{{days}}', '{{menu}}', '{{techs}}', '{{caller_name}}', '{{upcoming}}'],
    [$g['now'], implode("\n", $g['days']), implode("\n", $g['menu']), implode("\n", $g['techs']), 'none', 'none'], tx_instructions());
$tools = [];
foreach ((array)cl_agent_ai('', '')['ai']['SWAIG']['functions'] as $f) { $n = (string)$f['function']; $pa = (array)$f['parameters']; if (!$pa['properties'] || $pa['properties'] === (object)[]) $pa['properties'] = (object)[];
    $tools[] = ['type' => 'function', 'function' => ['name' => $n === 'end_call' ? 'hangup' : $n, 'description' => (string)$f['description'], 'parameters' => $pa]]; }
$sat = date('Y-m-d', strtotime('next saturday'));
$S = [ /* name => [caller lines, tool answers by name (array = in order)] */
 'a_all_in_one' => [["Hi, I'd like a regular pedicure for me this Saturday at 2 PM. My name is Maria."], ['check_times' => ['OPEN Sat ' . $sat . ' 2:00 PM']]],
 'b_vague'      => [["Hi, can I make an appointment for a pedicure?"], []],
 'c_group'      => [["I need pedicures for me and my daughter this Saturday at 2."], ['check_times' => ['OPEN Sat ' . $sat . ' 2:00 PM']]],
 'd_hours'      => [["What time are you open today?"], []],
 'e_price'      => [["How much is a gel manicure?"], ['transfer_owner' => ['NO_ONE - say: "The salon will call you back shortly. Have a good day!" then hang up (hangup tool).']]],
 'f_no_time'    => [["Hi, this is Ann, I want a pedicure this Saturday at 2.", "No, neither of those work for me."],
                    ['check_times' => ['FULL – offer Sat ' . $sat . ' 1:15 PM or Sat ' . $sat . ' 3:30 PM'], 'add_note' => ['OK note saved'], 'transfer_owner' => ['NO_ONE - say: "The salon will call you back shortly. Have a good day!" then hang up (hangup tool).']]],
];
foreach ($S as $name => [$lines, $ans]) {
    if ($only !== '' && $only !== $name) continue;
    echo "===== [$mode] $name\n"; $msg = [['role' => 'system', 'content' => $sys], ['role' => 'assistant', 'content' => tx_greeting()]]; $used = [];
    foreach ($lines as $line) { echo "CALLER: $line\n"; $msg[] = ['role' => 'user', 'content' => $line];
        for ($k = 0; $k < 6; $k++) {
            try { $r = tx_api('POST', '/ai/openai/chat/completions', ['model' => tx_model(), 'messages' => $msg, 'tools' => $tools, 'temperature' => 0.3, 'max_tokens' => 300], 60); }
            catch (Throwable $e) { echo "!! API: ", mb_substr($e->getMessage(), 0, 300), "\n"; break 2; }
            $m = $r['choices'][0]['message'] ?? []; $tc = (array)($m['tool_calls'] ?? []);
            if (trim((string)($m['content'] ?? '')) !== '') echo "AI: ", trim((string)$m['content']), "\n";
            if (!$tc) { $msg[] = ['role' => 'assistant', 'content' => (string)($m['content'] ?? '')]; break; }
            $msg[] = ['role' => 'assistant', 'content' => (string)($m['content'] ?? ''), 'tool_calls' => $tc];
            foreach ($tc as $t) { $fn = $t['function']['name']; $i = $used[$fn] = ($used[$fn] ?? -1) + 1; $res = $ans[$fn][$i] ?? $ans[$fn][0] ?? ($fn === 'hangup' ? 'The call ends now.' : 'OK');
                echo "  TOOL ", $fn, " ", mb_substr((string)$t['function']['arguments'], 0, 160), " -> ", mb_substr($res, 0, 80), "\n";
                $msg[] = ['role' => 'tool', 'tool_call_id' => $t['id'], 'content' => $res]; if ($fn === 'hangup') break 3; }
        }
    }
}
