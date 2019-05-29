<?php

if (!isset($_GET['action'])) {
    	http_response_code(400);
    	return;
}

//require_once "client_auth.php";
//$client_info = client_auth(apache_request_headers());


function get_count()
{
	//require_once "constants.php";
    	//$servername1 = "localhost";
	//$username1 = "root";
	//$password1 = "usc558l";
	//$dbname1 = "SENSS";
	//$conn1 = new mysqli($servername1, $username1, $password1, $dbname1);
	//if ($conn1->connect_error) {
    	//	die("Connection failed: " . $conn1->connect_error);
	//}
    	$sql="SELECT as_name,request_type,COUNT(request_type) AS count_request_type,end_time from SERVER_LOGS WHERE  request_type='Add filter' OR (request_type='Add monitor' AND ".time()."<end_time) OR request_type='Remove filter' GROUP BY request_type";
    	$result = $conn1->query($sql);
    	$add_filter=0;
    	$remove_filter=0;
    	$add_monitor=0;
    	if ($result->num_rows > 0) {
        	while ($row = $result->fetch_assoc()) {
                	if ($row["request_type"]=="Add filter"){
                        	$add_filter=$row["count_request_type"];
                	}
                	if ($row["request_type"]=="Remove filter"){
                        	$remove_filter=$row["count_request_type"];
                	}
                	if ($row["request_type"]=="Add monitor"){
                        	$end_time=(int)$row["end_time"];
                        	if (time()<$end_time){
                                	$add_monitor=$row["count_request_type"];
                        	}
                	}
        	}
    	}
    	$count=$add_filter-$remove_filter+$add_monitor;
    	$threshold=10;
    	$sql = sprintf("SELECT * FROM CLIENT_LOGS");
    	$result = $conn1->query($sql);
    	if ($result->num_rows > 0) {
        	while ($row = $result->fetch_assoc()) {
    			$threshold = $row['threshold'];
		}
    	}
    	$conn1->close();
    	if ($count>$threshold){
    		return array(
			"threshold"=>$threshold,
			"count"=>$count,
			"excess_rules"=>true,
			"as_name"=>SENSS_AS
		);
    	}
    	else{
    		return array(
			"threshold"=>$threshold,
			"count"=>$count,
			"excess_rules"=>false,
			"as_name"=>SENSS_AS
		);
    	}
}



$action = $_GET['action'];
switch ($action) {
	case "check":
		if (!$client_info) {
		    	http_response_code(400);
		    	return;
		}
		require_once "constants.php";
		$get_count_array=get_count();
		echo json_encode($get_count_array,true);
		break;

    	case "add_filter_alpha":
		if (!$client_info) {
		    	http_response_code(400);
		    	return;
		}
		require_once "constants.php";
		$get_count_array=get_count();
		if($get_count_array['excess_rules']){
            		echo json_encode(array(
                    		"success" => false,
                    		"error" => 500,
		    		"as_name" => $get_count_array['as_name'],
                    		"details" => "Not sufficient rules",
		    		"threshold" => $get_count_array['threshold'],
		    		"count" => $get_count_array['count']
                	),true);
	    		break;
		}
		require_once "filter.php";
        	$response=add_filter_all($client_info);
		if (!$response["success"]){
			echo json_encode(array(
				"success" => false,
				"error" => 500,
				"as_name" => $response["as_name"],
				"details" => $response["details"],
				"threshold" => $get_count_array["threshold"],
				"count" => $get_count_array["count"]
			),true);
			break;
		}
		http_response_code(200);
		echo json_encode(array(
			"success" => true,
			"as_name" => $response["as_name"],
			"threshold" => $get_count_array["threshold"],
			"count" => $get_count_array["count"]
		),true);
       	 	break;

    	case "add_filter":
		if (!$client_info) {
		    	http_response_code(400);
		    	return;
		}
		require_once "constants.php";
		$get_count_array=get_count();
		if($get_count_array['excess_rules']){
            		echo json_encode(array(
                		"success" => false,
                    		"error" => 500,
		    		"as_name" =>$get_count_array['as_name'],
                    		"details" => "Not sufficient rules",
		    		"threshold" => $get_count_array['threshold'],
		    		"count" => $get_count_array['count']
                	),true);
	   		 break;
		}

        	if (!isset($_GET['monitor_id'])) {
            		echo json_encode(array(
                    		"success" => false,
                    		"error" => 400,
		    		"as_name" => $response["as_name"],
		    		"details" => "monitor_id not present",
		    		"threshold" => $get_count_array["threshold"],
		    		"count" => $get_count_array["count"]
                		)
            		);
            		return;
        	}

        	require_once "filter.php";
        	$response=add_filter($client_info, (int)$_GET['monitor_id']);
		if (!$response["success"]){
			echo json_encode(array(
				"success" => false,
				"error" => 500,
				"as_name" => $response["as_name"],
				"details" => $response["details"],
				"threshold" => $get_count_array["threshold"],
				"count" => $get_count_array["count"]
				),true);
			break;
		}
		http_response_code(200);
		echo json_encode(array(
			"success" => true,
			"as_name" => $response["as_name"],
			"threshold" => $get_count_array["threshold"],
			"count" => $get_count_array["count"]
			),true);
        	break;

    	case "remove_filter":
		if (!$client_info) {
		    	http_response_code(400);
		    	return;
		}
		require_once "constants.php";
        	if (!isset($_GET['monitor_id'])) {
            		echo json_encode(array(
                   		"success" => false,
                    		"error" => 400,
		    		"as_name" => $response["as_name"],
		    		"details" => "monitor_id not present"
                		)
            		);
            		return;
        	}
        	require_once "filter.php";
        	$response=remove_filter($client_info, (int)$_GET['monitor_id']);
		if (!$response["success"]){
			echo json_encode(array(
				"success" => false,
				"error" => 500,
				"as_name" => $response["as_name"],
				"details" => $response["details"]
				),true);
			break;
		}
		http_response_code(200);
		echo json_encode(array(
			"success" => true,
			"as_name" => $response["as_name"]
		),true);

        	http_response_code(200);
        	break;

    	case "add_monitor":
		if (!$client_info) {
		    	http_response_code(400);
		    	return;
		}
		require_once "constants.php";
		$get_count_array=get_count();
		if($get_count_array['excess_rules']){
            		echo json_encode(array(
                    		"success" => false,
                    		"error" => "Not sufficient rules",
		    		"threshold" => $get_count_array['threshold'],
		    		"count" => $get_count_array['count']
                		)
            		);
	    		break;
		}
        	require_once "monitor.php";
        	$response = add_monitor($client_info, file_get_contents("php://input"));
        	http_response_code(200);
        	$response['threshold']=$get_count_array['threshold'];
		$response['count']=$get_count_array['count'];
        	echo json_encode($response, true);
        	break;

    	case "remove_monitor":
		if (!$client_info) {
		    	http_response_code(400);
		    	return;
		}
		require_once "constants.php";
        	require_once "monitor.php";
        	if (!isset($_GET['monitor_id'])) {
            		echo json_encode(array(
                    		"success" => false,
                    		"error" => 400,
		    		"details" => "No monitor_id"
                	),true
            		);
            		return;
        	}
        	$responses=remove_monitor($client_info, (int)$_GET['monitor_id']);
        	http_response_code(200);
		if ($responses["success"]){
			echo json_encode(array(
				"success" => true,
				"as_name" => SENSS_AS
			),true);
		}
        	break;

    	case "get_monitor":
		if (!$client_info) {
		    	http_response_code(400);
		    	return;
		}
		require_once "constants.php";
        	if (!isset($_GET['monitor_id'])) {
            		echo json_encode(array(
                    		"success" => false,
                    		"error" => 400
                	)
            		);
            		return;
        	}
        	require_once "monitor.php";
        	$data = get_monitor($client_info, (int)$_GET['monitor_id']);
        	http_response_code(200);
        	echo json_encode($data, true);
        	return;

    	case "get_server_logs":
        	require_once "get_server_logs.php";
        	$data = get_server_logs();
        	http_response_code(200);
        	echo json_encode($data, true);
        	return;


	case "config_constants":
		require_once "constants.php";
	        $input = file_get_contents("php://input");
	        $input = json_decode($input, true);
	        $sql = sprintf("INSERT INTO CONSTANTS (as_name, controller_url, rule_capacity) VALUES ('%s', '%s', %d)", $input['as_name'], $input['controller_url'], $input['rule_capacity']);
        	$conn1->query($sql);
	        $conn1->commit();
        	return;

	case "remove_controller":
	        if (!isset($_GET['as_name']) && !isset($_GET['controller_url'])) {
        	        http_response_code(400);
                	return;
	        }
		require_once "constants.php";
        	$as_name = $_GET['as_name'];
	        $controller_url = $_GET['controller_url'];
	        $sql = sprintf("DELETE FROM CONSTANTS WHERE as_name='%s' AND controller_url='%s'",$as_name,$controller_url);
        	$conn1->query($sql);
	        $conn1->commit();
        	return;

	case "edit_controller":
	        if (!isset($_GET['as_name']) && !isset($_GET['controller_url'])) {
        	        http_response_code(400);
                	return;
	        }
		require_once "constants.php";
        	$old_as_name = $_GET['old_as_name'];
	        $old_controller_url = $_GET['old_controller_url'];
		$old_rule_capacity = $_GET['old_rule_capacity'];
        	$as_name = $_GET['as_name'];
	        $controller_url = $_GET['controller_url'];
		$rule_capacity = $_GET['rule_capacity'];


	        $sql = sprintf("UPDATE CONSTANTS SET as_name='%s',controller_url='%s',rule_capacity='%d' WHERE as_name='%s' AND controller_url='%s'",$as_name, $controller_url, $rule_capacity,  $old_as_name,$old_controller_url);
        	$conn1->query($sql);
	        $conn1->commit();
        	return;


	case "get_constants":
		require_once "constants.php";
                $sql="SELECT as_name,controller_url,rule_capacity from CONSTANTS";
                $result = $conn1->query($sql);
                if ($result->num_rows > 0) {
                        $return_array=array();
                        while ($row = $result->fetch_assoc()) {
				$temp=array("as_name"=>$row["as_name"],"controller_url"=>$row["controller_url"], "rule_capacity"=>$row["rule_capacity"]);
				array_push($return_array,$temp);
                        }
                        echo json_encode(array(
                                "success" => true,
                                "data" => $return_array
                        ),true);
                        return;
                }
        	echo json_encode(array(
	                "success" => false,
        	        "error" => 400
	        ),true);
        	return;

    	default:
        	http_response_code(400);
        	return;
}



