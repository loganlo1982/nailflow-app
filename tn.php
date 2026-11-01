<?php
declare(strict_types=1);
if (PHP_SAPI !== 'cli') exit;
require '/home/uyurpyzubx0m/app/sites/an/current/inc/core.php'; require_once '/home/uyurpyzubx0m/app/sites/an/current/inc/calls-job.php';
$rf = new ReflectionFunction('cl_ivr_text'); echo 'cl_ivr_text ', $rf->getFileName(), ':', $rf->getStartLine(), "\n";
$src = file($rf->getFileName()); echo implode('', array_slice($src, $rf->getStartLine() - 1, 3));
foreach (["I want to cancel my appointments, 2 of them.", "Cancel both please", "cancel just one of them", "the second one", "Cancel all of us", "cancelar ambos", "cancel Test"] as $s) {
  $tw = ' ' . cl_norm($s) . ' ';
  $all = !preg_match('/ (one of|just one|only one|uno de|solo uno) /', $tw) && preg_match('/ (both|all|everyone|everybody|whole|all of (us|them)|(two|2|three|3|four|4|five|5) of (us|them)|ambos|todos|todas) /', $tw);
  $sec = preg_match('/ (second|2nd|segundo|segunda) /', $tw);
  echo str_pad($s, 45), ' norm[', trim($tw), '] all=', (int)$all, ' second=', $sec, "\n";
}
