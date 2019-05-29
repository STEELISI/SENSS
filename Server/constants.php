<?php
require_once 'db.php';
$sql="SELECT as_name,controller_url from CONSTANTS";
$result = $conn1->query($sql);
if ($result->num_rows > 0) {
        while ($row = $result->fetch_assoc()) {
                        //const SENSS_AS = $row["as_name"];
                        //const CONTROLLER_BASE_URL=$row["controller_url"];
                        define('SENSS_AS',$row["as_name"]);
                        define('CONTROLLER_BASE_URL',$row["controller_url"]);
        }
}
define('SWITCH_DPID', 91487349082);
