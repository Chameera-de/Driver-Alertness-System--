<?php
if(isset($_GET["uSpeed"]))
{
    echo "I am in";
    $s_val = $_GET["uSpeed"];
    $sl_val = $_GET["speedLimit"]; 
    $r_val = $_GET["road"]; 


    $myObj = array('uSpeed' => $s_val, 'speedLimit' => $sl_val, 'road' => $r_val);
    $json = json_encode($myObj,JSON_PRETTY_PRINT);
    
    file_put_contents("inputs.txt", $json);

}
else{
  
    $f =  file_get_contents("inputs.txt");
    echo ($f);
}


?>