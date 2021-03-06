<?php

function check_blacklist($signature){
	require_once "constants.php";
	$sql = sprintf("SELECT * FROM BLACKLIST WHERE signature='%s'",$signature);
    	$result = $conn1->query($sql);
    	if ($result->num_rows > 0) {
		return true;
	}
	return false;
}
function get_count($as_name, $request_type)
{
	require_once "constants.php";
	$sql=sprintf("SELECT used_filter_requests, max_filter_requests, used_monitoring_requests, max_monitoring_requests, block_monitoring, block_filtering FROM THRESHOLDS WHERE as_name='%s'",$as_name);
    	$result = $conn1->query($sql);
    	if ($result->num_rows > 0) {
        	while ($row = $result->fetch_assoc()) {
			$used_filter_requests=$row["used_filter_requests"];
			$max_filter_requests=$row["max_filter_requests"];
			$used_monitoring_requests=$row["used_monitoring_requests"];
			$max_monitoring_requests=$row["max_monitoring_requests"];
			$block_monitoring=$row["block_monitoring"];
			$block_filtering=$row["block_filtering"];
        	}
    	}

	$sql="SELECT revoke_all FROM CONSTANTS";
    	$result = $conn1->query($sql);
    	if ($result->num_rows > 0) {
        	while ($row = $result->fetch_assoc()) {
			$revoke_all=$row["revoke_all"];
        	}
    	}

	if($request_type=="Add filter"){
		$used_filter_requests=$used_filter_requests+1;
	    	if ($used_filter_requests>$max_filter_requests){
			$excess_rules=true;
	    	}
    		else{
			$excess_rules=false;
    		}
		if ($block_filtering==1){
			$blocked=true;
		}
		else{
			$blocked=false;
		}
		if ($revoke_all==1){
			$revoked=true;
		}
		else{
			$revoked=false;
		}

	    	return array(
			"threshold"=>$max_filter_requests,
			"count"=>$used_filter_requests-1,
			"excess_rules"=>$excess_rules,
			"blocked"=>$blocked,
			"revoked"=>$revoked,
			"as_name"=>SENSS_AS
		);
	}
	if($request_type=="Add monitor"){
		$used_monitoring_requests=$used_monitoring_requests+1;
	    	if ($used_monitoring_requests>$max_monitoring_requests){
			$excess_rules=true;
	    	}
    		else{
			$excess_rules=false;
    		}
		if ($block_monitoring==1){
			$blocking=true;
		}
		else{
			$blocking=false;
		}
		if ($revoke_all==1){
			$revoked=true;
		}
		else{
			$revoked=false;
		}

	    	return array(
			"threshold"=>$max_monitoring_requests,
			"count"=>$used_monitoring_requests-1,
			"excess_rules"=>$excess_rules,
			"blocked"=>$blocked,
			"revoked"=>$revoked,
			"as_name"=>SENSS_AS
		);
	}
}



if (!isset($_GET['action'])) {
    	http_response_code(400);
    	return;
}

$action = $_GET['action'];
switch ($action) {
	case "checking":
		require_once "client_auth.php";
		$signature = return_client_signature();
		$valid_signature=check_blacklist($signature["signature"]);
		if (!$valid_signature){
			http_response_code(400);
			return;
		}
	case "revoke_all":
		require_once "client_auth.php";
		$signature = return_client_signature();
		require_once "constants.php";
		$sql=sprintf("INSERT INTO BLACKLIST (signature) VALUES('%s')", $signature);
    		$result = $conn1->query($sql);
		db.commit();

	case "update_threshold":
		require_once "db.php";
	    	$sql="SELECT as_name,request_type,COUNT(request_type) AS count_request_type,end_time from SERVER_LOGS WHERE  request_type='Add filter' OR (request_type='Add monitor' AND ".time()."<end_time) OR request_type='Remove filter' GROUP BY as_name,request_type";
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
			//plsmark222
	                $sql=sprintf("SELECT rule_capacity from CONSTANTS");
        	        $result = $conn1->query($sql);
                        while ($row = $result->fetch_assoc()) {
				$max_capacity=$row["rule_capacity"];
			}

				$sql="SELECT COUNT(DISTINCT as_name) AS count FROM SERVER_LOGS";

        		        $result = $conn1->query($sql);
                	        while ($row = $result->fetch_assoc()) {
					$total_clients=$row["count"];
				}

				$new_max_capacity=$max_capacity/(2*$total_clients);


			$sql=sprintf("INSERT INTO THRESHOLDS (as_name, used_filter_requests, max_filter_requests, used_monitoring_requests, max_monitoring_requests, block_monitoring, block_filtering, fair_sharing) VALUES('%s', %d, %d, %d, %d, %d, %d, %d) ON DUPLICATE KEY UPDATE used_filter_requests=%d, used_monitoring_requests=%d", $key,$filtering_requests, $new_max_capacity, $monitoring_requests, $new_max_capacity, 0, 0, 0, $filtering_requests,$monitoring_requests);
		    	$result = $conn1->query($sql);
			$conn1->commit();
		}
		$sql="SELECT * FROM THRESHOLDS";
		$result = $conn1->query($sql);
                if ($result->num_rows > 0) {
                        $return_array=array();
                        while ($row = $result->fetch_assoc()) {
				$temp=array("as_name"=>$row["as_name"],"used_filter_requests"=>$row["used_filter_requests"], "max_filter_requests"=>$row["max_filter_requests"], "used_monitoring_requests"=>$row["used_monitoring_requests"], "max_monitoring_requests"=>$row["max_monitoring_requests"], "block_monitoring"=>$row["block_monitoring"], "block_filtering"=>$row["block_filtering"]);
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

	//Not sure if I use this anymore
    	case "add_filter_alpha":
		require_once "client_auth.php";
		$client_info = client_auth(apache_request_headers());
		$signature = return_client_signature();
		$valid_signature=check_blacklist($signature["signature"]);
		if (!$valid_signature){
			http_response_code(400);
			return;
		}


		if (!$client_info) {
		    	http_response_code(400);
		    	return;
		}
		require_once "constants.php";
		$request_type="Add filter";
		$get_count_array=get_count($client_info["as_name"],$request_type);
		if($get_count_array['excess_rules']){
            		echo json_encode(array(
                    		"success" => false,
                    		"error" => 500,
		    		"as_name" => $get_count_array['as_name'],
                    		"details" => "Not sufficient rules",
		    		"threshold" => $get_count_array['threshold'],
		    		"count" => $get_count_array['count']
                	),true);
	    		return;
		}
		if($get_count_array['blocked']){
            		echo json_encode(array(
                    		"success" => false,
                    		"error" => 500,
		    		"as_name" => $get_count_array['as_name'],
                    		"details" => "Blocked"
                	),true);
	    		break;
		}
		if($get_count_array['revoked']){
            		echo json_encode(array(
                    		"success" => false,
                    		"error" => 500,
		    		"as_name" => $get_count_array['as_name'],
                    		"details" => "All access revoked"
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
		$signature = return_client_signature();
		$valid_signature=check_blacklist($signature["signature"]);
		if (!$valid_signature){
			http_response_code(400);
			return;
		}

		if (!$client_info) {
		    	http_response_code(400);
		    	return;
		}
		require_once "constants.php";

		$request_type="Add filter";
		$get_count_array=get_count($client_info["as_name"],$request_type);
		if($get_count_array['excess_rules']){
            		echo json_encode(array(
                    		"success" => false,
                    		"error" => 500,
		    		"as_name" => $get_count_array['as_name'],
                    		"details" => "Not sufficient rules",
		    		"threshold" => $get_count_array['threshold'],
		    		"count" => $get_count_array['count']
                	),true);
	    		return;
		}
		if($get_count_array['blocked']){
            		echo json_encode(array(
                    		"success" => false,
                    		"error" => 500,
		    		"as_name" => $get_count_array['as_name'],
                    		"details" => "Blocked"
                	),true);
	    		break;
		}
		if($get_count_array['revoked']){
            		echo json_encode(array(
                    		"success" => false,
                    		"error" => 500,
		    		"as_name" => $get_count_array['as_name'],
                    		"details" => "All access revoked"
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
		$signature = return_client_signature();
		$valid_signature=check_blacklist($signature["signature"]);
		if (!$valid_signature){
			http_response_code(400);
			return;
		}


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
		$signature = return_client_signature();
		$valid_signature=check_blacklist($signature["signature"]);
		if (!$valid_signature){
			http_response_code(400);
			return;
		}


		if (!$client_info) {
		    	http_response_code(400);
		    	return;
		}
		require_once "constants.php";
		$request_type="Add monitor";
		$get_count_array=get_count($client_info["as_name"],$request_type);
		if($get_count_array['excess_rules']){
            		echo json_encode(array(
                    		"success" => false,
                    		"error" => 500,
		    		"as_name" => $get_count_array['as_name'],
                    		"details" => "Not sufficient rules",
		    		"threshold" => $get_count_array['threshold'],
		    		"count" => $get_count_array['count']
                	),true);
	    		return;
		}
		if($get_count_array['blocked']){
            		echo json_encode(array(
                    		"success" => false,
                    		"error" => 500,
		    		"as_name" => $get_count_array['as_name'],
                    		"details" => "Blocked"
                	),true);
	    		break;
		}
		if($get_count_array['revoked']){
            		echo json_encode(array(
                    		"success" => false,
                    		"error" => 500,
		    		"as_name" => $get_count_array['as_name'],
                    		"details" => "All access revoked"
                	),true);
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
		$signature = return_client_signature();
		$valid_signature=check_blacklist($signature["signature"]);
		if (!$valid_signature){
			http_response_code(400);
			return;
		}


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
		$signature = return_client_signature();
		$valid_signature=check_blacklist($signature["signature"]);
		if (!$valid_signature){
			http_response_code(400);
			return;
		}


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
	        $sql = sprintf("INSERT INTO CONSTANTS (as_name, controller_url, rule_capacity, fair_sharing, revoke_all) VALUES ('%s', '%s', %d, %d, 0)", $input['as_name'], $input['controller_url'], $input['rule_capacity'], $input["fair_sharing"]);
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




		//check if there are enough rules
		
				$sql="SELECT COUNT(*) AS count FROM THRESHOLDS";
        		        $result = $conn1->query($sql);
                	        while ($row = $result->fetch_assoc()) {
					$total_clients=$row["count"];
				}


				$sql="SELECT used_filter_requests, used_monitoring_requests FROM THRESHOLDS";
        		        $result = $conn1->query($sql);
				$max_request=0;
                	        while ($row = $result->fetch_assoc()) {
					if($row["used_filter_requests"]>$max_request){
						$max_request=$row["used_filter_requests"];
					}
					if($row["used_monitoring_requests"]>$max_request){
						$max_request=$row["used_monitoring_requests"];
					}
				}
				$current_capacity=$rule_capacity/(2*$total_clients);
				//$max_capacity=$rule_capacity-$nf_filter_requests-$nf_monitoring_requests;

		if($current_capacity<$max_request){
                        echo json_encode(array(
                                "success" => false,
                                "reason" => "Not enough rules to support active rules"
                        ),true);
                        return;
		}

	        $sql = sprintf("UPDATE CONSTANTS SET as_name='%s',controller_url='%s',rule_capacity='%d' WHERE as_name='%s' AND controller_url='%s'",$as_name, $controller_url, $rule_capacity,  $old_as_name,$old_controller_url);
        	$conn1->query($sql);
	        $conn1->commit();

	                $sql=sprintf("SELECT rule_capacity from CONSTANTS");
        	        $result = $conn1->query($sql);
                        while ($row = $result->fetch_assoc()) {
				$max_capacity=$row["rule_capacity"];
			}

				$sql="SELECT COUNT(*) AS count FROM THRESHOLDS where fair_sharing=0";
        		        $result = $conn1->query($sql);
                	        while ($row = $result->fetch_assoc()) {
					$total_clients=$row["count"];
				}


				$sql="SELECT max_filter_requests, max_monitoring_requests FROM THRESHOLDS WHERE fair_sharing=1";
        		        $result = $conn1->query($sql);
				$nf_filter_requests=0;
				$nf_monitoring_requests=0;
                	        while ($row = $result->fetch_assoc()) {
					$nf_filter_requests=$nf_filter_requests+$row["max_filter_requests"];
					$nf_monitoring_requests=$nf_monitoring_requests+$row["max_monitoring_requests"];
				}

				$max_capacity=$max_capacity-$nf_filter_requests-$nf_monitoring_requests;

				$sql="SELECT as_name FROM THRESHOLDS where fair_sharing=0";
        		        $result = $conn1->query($sql);
                	        while ($row = $result->fetch_assoc()) {
					$as_name=$row["as_name"];
					$new_max_requests=$max_capacity/(2*$total_clients);
				        $sql = sprintf("UPDATE THRESHOLDS SET max_filter_requests=%d,max_monitoring_requests=%d WHERE as_name='%s'",$new_max_requests, $new_max_requests, $as_name);
        				$conn1->query($sql);
		        		$conn1->commit();
				}

                        echo json_encode(array(
                                "success" => true
                        ),true);
                        return;


	case "get_constants":
		require_once "constants.php";
                $sql="SELECT as_name,controller_url,rule_capacity,revoke_all from CONSTANTS";
                $result = $conn1->query($sql);
                if ($result->num_rows > 0) {
                        $return_array=array();
                        while ($row = $result->fetch_assoc()) {
				$temp=array("as_name"=>$row["as_name"],"controller_url"=>$row["controller_url"], "rule_capacity"=>$row["rule_capacity"], "revoke_all"=>$row["revoke_all"]);
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



	                $sql=sprintf("SELECT rule_capacity from CONSTANTS");
        	        $result = $conn1->query($sql);
                        while ($row = $result->fetch_assoc()) {
				$max_capacity=$row["rule_capacity"];
			}

				$sql="SELECT used_filter_requests, used_monitoring_requests FROM THRESHOLDS";
        		        $result = $conn1->query($sql);
				$active_requests=0;
                	        while ($row = $result->fetch_assoc()) {
						$active_requests=$active_requests+$row["used_filter_requests"]+$row["used_monitoring_requests"];
				}

		//Monitoring
		$monitoring_check=$max_capacity-$active_requests-$max_monitoring_requests;
		$message="";
		$message_flag=false;
		if ($monitoring_check<0){
			$message=$message."Maximum monitoring rules cannot be greater than available rule capacity.<br />";
			$message_flag=true;
		}
		//Filtering
		$filtering_check=$max_capacity-$active_requests-$max_filter_requests;
		if ($filtering_check<0){
			$message=$message."Maximum filtering rules cannot be greater than available rule capacity.";
			$message_flag=true;
		}
		if($message_flag==true){
                        echo json_encode(array(
                                "success" => false,
                                "reason" => $message
                        ),true);
                        return;
		}

	        $sql = sprintf("UPDATE THRESHOLDS SET max_filter_requests=%d,max_monitoring_requests=%d,fair_sharing=1 WHERE as_name='%s'",$max_filter_requests, $max_monitoring_requests, $as_name);
        	$conn1->query($sql);
	        $conn1->commit();


	                $sql=sprintf("SELECT rule_capacity from CONSTANTS");
        	        $result = $conn1->query($sql);
                        while ($row = $result->fetch_assoc()) {
				$max_capacity=$row["rule_capacity"];
			}

				$sql="SELECT max_filter_requests, max_monitoring_requests FROM THRESHOLDS WHERE fair_sharing=1";
        		        $result = $conn1->query($sql);
				$nf_filter_requests=0;
				$nf_monitoring_requests=0;
                	        while ($row = $result->fetch_assoc()) {
					$nf_filter_requests=$nf_filter_requests+$row["max_filter_requests"];
					$nf_monitoring_requests=$nf_monitoring_requests+$row["max_monitoring_requests"];
				}

				$max_capacity=$max_capacity-$nf_filter_requests-$nf_monitoring_requests;
				$sql="SELECT COUNT(*) AS count FROM THRESHOLDS WHERE fair_sharing=0";
        		        $result = $conn1->query($sql);
                	        while ($row = $result->fetch_assoc()) {
					$total_clients=$row["count"];
				}

				$sql="SELECT as_name FROM THRESHOLDS WHERE fair_sharing=0";
        		        $result = $conn1->query($sql);
                	        while ($row = $result->fetch_assoc()) {
					$as_name=$row["as_name"];
					$new_max_requests=$max_capacity/(2*$total_clients);
				        $sql = sprintf("UPDATE THRESHOLDS SET max_filter_requests=%d,max_monitoring_requests=%d WHERE as_name='%s'",$new_max_requests, $new_max_requests, $as_name);
        				$conn1->query($sql);
		        		$conn1->commit();
				}

                        echo json_encode(array(
                                "success" => true
                        ),true);
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

	case "apply_fair_sharing":
		require_once "constants.php";
		$as_name=$_GET["as_name"];
	                $sql=sprintf("SELECT rule_capacity from CONSTANTS where as_name='%s'",$as_name);
        	        $result = $conn1->query($sql);
                        while ($row = $result->fetch_assoc()) {
				$max_capacity=$row["rule_capacity"];
			}

				$sql="SELECT COUNT(*) AS count FROM THRESHOLDS";
        		        $result = $conn1->query($sql);
                	        while ($row = $result->fetch_assoc()) {
					$total_clients=$row["count"];
				}

				$sql="SELECT as_name FROM THRESHOLDS";
        		        $result = $conn1->query($sql);
                	        while ($row = $result->fetch_assoc()) {
					$as_name=$row["as_name"];
					$new_max_requests=$max_capacity/(2*$total_clients);
				        $sql = sprintf("UPDATE THRESHOLDS SET max_filter_requests=%d,max_monitoring_requests=%d,fair_sharing=0 WHERE as_name='%s'",$new_max_requests, $new_max_requests, $as_name);
        				$conn1->query($sql);
		        		$conn1->commit();
				}

			echo json_encode(array(
				"success" => true,
				"data" => array(
					"fair_sharing_value"=>$new_max_requests
				)
			),true);


			return;

	case "revoke_unrevoke":
		require_once "constants.php";
		$type=$_GET["type"];
		if($type=="revoke"){
	                $sql=sprintf("UPDATE CONSTANTS SET revoke_all=1");
        	        $conn1->query($sql);
			$conn1->commit();
		}
		if($type=="unrevoke"){
	                $sql=sprintf("UPDATE CONSTANTS SET revoke_all=0");
        	        $conn1->query($sql);
			$conn1->commit();
		}
		return;

	case "upload_cert":
		$type=$_GET['cert_type'];
		echo "Here is the list ".$type;
		if($type=="new"){
			$target_dir = "/var/www/html/Server/cert/";
			$target_file = $target_dir . basename($_FILES["file"]["name"]);
			$file_name = $_POST["file_name"];
			//$target_file = $target_dir . basename($_FILES["file"]["name"]);
			$target_file = $target_dir . $file_name;
			echo $target_file;
			if(move_uploaded_file($_FILES["file"]["tmp_name"], $target_file)){
				echo "Uploaded successfully";
			}
			else{
				echo "Upload failed ".$_POST["file_name"];
			}
		}
		return;


    	default:
        	http_response_code(400);
        	return;
}



