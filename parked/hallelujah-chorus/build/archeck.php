<?php
// Runs the app's ArrangementCheck on one template file, reading the app's code only (no artisan, no link).
// usage: php archeck.php /path/to/template.json
require '/Users/hillel/Code/stackapella/server/vendor/autoload.php';
$t = json_decode(file_get_contents($argv[1]), true);
$found = (new App\Support\Templates\ArrangementCheck())->check($t);
echo count($found['hard']), " hard, ", count($found['advice']), " advice\n";
foreach ($found['hard'] as $l) echo "HARD $l\n";
$kinds = [];
foreach ($found['advice'] as $l) { $k = strstr($l, ':', true) ?: 'other'; $kinds[$k] = ($kinds[$k] ?? 0) + 1; }
print_r($kinds);
foreach ($found['advice'] as $l) echo "  $l\n";
