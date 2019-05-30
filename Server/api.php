<?php

if (!isset($_GET['action'])) {
    	http_response_code(400);
    	return;
}



function get_count()
{
	require_once "constants.php";
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

	case "update_threshold":
		require_once "db.php";
	    	$sql="SELECT as_name,request_type,COUNT(request_type) AS count_request_type,end_time from SERVER_LOGS WHERE  request_type='Add filter' OR (request_type='Add monitor' AND ".time()."<end_time) OR request_type='Remove filter' GROUP BY request_type";
	    	$result = $conn1->query($sql);
    		$add_filter=0;
	    	$remove_filter=0;
    		$monitoring_requests=0;
		$as_requests=array();
	    	if ($result->num_rows > 0) {
        		while ($row = $result->fetch_assoc()) {
				if(!isset($as_requests[$row["as_name"]])){
					$as_requests[$row["as_name"]]=array(
						"Add filter"=>0,
						"Remove filter"=>0,
						"Add monitor"=>0
					);
				}
                		if ($row["request_type"]=="Add filter"){
					$as_requests[$row["as_name"]]["Add filter"]=$row["count_request_type"];
	                	}
        	        	if ($row["request_type"]=="Remove filter"){
					$as_requests[$row["as_name"]]["Remove filter"]=$row["count_request_type"];
                		}
	                	if ($row["request_type"]=="Add monitor"){
        	                	$end_time=(int)$row["end_time"];
                	        	if (time()<$end_time){
						$as_requests[$row["as_name"]]["Add monitor"]=$row["count_request_type"];
	                        	}
        	        	}
        		}
	    	}
		foreach ($as_requests as $key => $value){
			$filtering_requests=$value["Add filter"]-$value["Remove filter"];
			$monitoring_requests=$value["Add monitor"];
			$sql=sprintf("INSERT INTO THRESHOLDS (as_name, used_filter_requests, max_filter_requests, used_monitoring_requests, max_monitoring_requests, fair_sharing, block_monitoring, block_filtering) VALUES('%s', %d, %d, %d, %d, %d, %d, %d) ON DUPLICATE KEY UPDATE used_filter_requests=%d, used_monitoring_requests=%d", $key,$filtering_requests, 1000, $monitoring_requests, 1000, 0, 0, 0, $filtering_requests,$monitoring_requests);
		    	$result = $conn1->query($sql);
			$conn1->commit();
		}
		$sql="SELECT * FROM THRESHOLDS";
		$result = $conn1->query($sql);
                if ($result->num_rows > 0) {
                        $return_array=array();
                        while ($row = $result->fetch_assoc()) {
				$temp=array("as_name"=>$row["as_name"],"used_filter_requests"=>$row["used_filter_requests"], "max_filter_requests"=>$row["max_filter_requests"], "used_monitoring_requests"=>$row["used_monitoring_requests"], "max_monitoring_requests"=>$row["max_monitoring_requests"], "fair_sharing"=>$row["fair_sharing"], "block_monitoring"=>$row["block_monitoring"], "block_filtering"=>$row["block_filtering"]);
				array_push($return_array,$temp);
                        }
                        echo json_encode(array(
                                "success" => true,
                                "data" => $return_array
                        ),true);
                        return;
		}
		echo json_encode(array(
                                "success" => true
		),true);
                return;


    	case "add_filter_alpha":
		require_once "client_auth.php";
		$client_info = client_auth(apache_request_headers());

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
		require_once "client_auth.php";
		$client_info = client_auth(apache_request_headers());

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
		require_once "client_auth.php";
		$client_info = client_auth(apache_request_headers());

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
		require_once "client_auth.php";
		$client_info = client_auth(apache_request_headers());

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
		require_once "client_auth.php";
		$client_info = client_auth(apache_request_headers());

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
		require_once "client_auth.php";
		$client_info = client_auth(apache_request_headers());

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
	                "success" => false
	        ),true);
        	return;

	case "edit_threshold":
		require_once "constants.php";
		$old_max_filter_requests=$_GET["old_max_filter_requests"];
		$old_max_monitoring_requests=$_GET["old_max_monitoring_requests"];
		$max_filter_requests=$_GET["max_filter_requests"];
		$max_monitoring_requests=$_GET["max_monitoring_requests"];
        	$as_name = $_GET['as_name'];
	        $sql = sprintf("UPDATE THRESHOLDS SET max_filter_requests=%d,max_monitoring_requests=%d WHERE as_name='%s'",$max_filter_requests, $max_monitoring_requests, $as_name);
        	$conn1->query($sql);
	        $conn1->commit();
        	return;

	case "block_unblock":
		require_once "constants.php";
		$type=$_GET["type"];
		$as_name=$_GET["as_name"];
		if ($type=="monitoring"){
	                $sql=sprintf("SELECT block_monitoring from THRESHOLDS where as_name='%s'",$as_name);
        	        $result = $conn1->query($sql);
                        while ($row = $result->fetch_assoc()) {
				$old_value=$row["block_monitoring"];
			}
			if ($old_value==0){
				$new_value=1;
			}
			if ($old_value==1){
				$new_value=0;
			}
	                $sql=sprintf("UPDATE THRESHOLDS SET block_monitoring=%d where as_name='%s'",$new_value,$as_name);
	        	$conn1->query($sql);
		        $conn1->commit();

			echo json_encode(array(
				"success" => true,
				"data" => array(
					"flip"=>$old_value
				)
			),true);
			return;
                }

		if ($type=="filtering"){
	                $sql=sprintf("SELECT block_filtering from THRESHOLDS where as_name='%s'",$as_name);
        	        $result = $conn1->query($sql);
                        while ($row = $result->fetch_assoc()) {
				$old_value=$row["block_filtering"];
			}
			if ($old_value==0){
				$new_value=1;
			}
			if ($old_value==1){
				$new_value=0;
			}
	                $sql=sprintf("UPDATE THRESHOLDS SET block_filtering=%d where as_name='%s'",$new_value,$as_name);
	        	$conn1->query($sql);
		        $conn1->commit();
			echo json_encode(array(
				"success" => true,
				"data" => array(
					"flip"=>$old_value
				)
			),true);
			return;
                }

		if ($type=="fair_sharing"){
	                $sql=sprintf("SELECT fair_sharing from THRESHOLDS where as_name='%s'",$as_name);
        	        $result = $conn1->query($sql);
                        while ($row = $result->fetch_assoc()) {
				$old_value=$row["fair_sharing"];
			}
			if ($old_value==0){
				$new_value=1;
			}
			if ($old_value==1){
				$new_value=0;
			}
	                $sql=sprintf("UPDATE THRESHOLDS SET fair_sharing=%d where as_name='%s'",$new_value,$as_name);
	        	$conn1->query($sql);
		        $conn1->commit();
			echo json_encode(array(
				"success" => true,
				"data" => array(
					"flip"=>$old_value
				)
			),true);
			return;
                }

    	default:
        	http_response_code(400);
        	return;
}



