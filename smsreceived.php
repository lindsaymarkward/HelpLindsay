<?php
/**
 * created by phpstorm.
 * user: sci-lmw1
 * date: 21/12/2015
 * time: 1:59 pm
 */

//echo "<pre>";
//echo "test";
//print_r($_post);
//echo "</pre>";
//echo "plain:";
//echo $_request['data'];
//phpinfo();

$contents = file_get_contents("php://input");
$file = fopen("messages.txt", "a");
fwrite($file, $contents . "\n");
fclose($file);


