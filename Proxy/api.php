<?php
function generate_request_headers() {
    ///var/www/html/SENSS/UI_client_server/Client/cert
    $clientcert = file_get_contents('/var/www/html/SENSS/UI_client_server/Client/cert/clientcert.pem');
    $clientcert = base64_encode($clientcert);
    return array(
        "Content-Type: application/json",
        "X-Client-Cert: " . $clientcert
    );
}

function makeRandomString($bits = 256) {
    $bytes = ceil($bits / 8);
    $return = '';
    for ($i = 0; $i < $bytes; $i++) {
        $return .= chr(mt_rand(0, 255));
    }
    return $return;
}



$action = $_GET['action'];
//$action="get_nonce";
switch ($action) {
    case "get_nonce":
	require_once "client_auth.php";
	$client_info = client_auth(apache_request_headers());
	if (!$client_info) {
        	http_response_code(400);
	        return;
	}

	$id = $_SERVER['HTTP_CLIENT_IP'] ? $_SERVER['HTTP_CLIENT_IP'] : ($_SERVER['HTTP_X_FORWARDED_FOR'] ? $_SERVER['HTTP_X_FORWARDED_FOR'] : $_SERVER['REMOTE_ADDR']);
	$nonce = hash('sha512', makeRandomString());
	$servername = "localhost";
	$username = "root";
	$password = "usc558l";
	$dbname = "SENSS_PROXY";
	$conn = new mysqli($servername, $username, $password, $dbname);
	if ($conn->connect_error) {
	    die("Connection failed: " . $conn->connect_error);
	}
	$sql = "SELECT id FROM NONCES WHERE ip = '" . $id . "'";
	$result = $conn->query($sql);
	if ($result->num_rows == 0) {
		$sql = sprintf("INSERT INTO NONCES (ip,nonce) VALUES ('%s','%s')",$id,$nonce);
	        $conn->query($sql);
        	$conn->commit();
	}
	else{
		$key=$result->fetch_assoc()["id"];
		$sql = sprintf("UPDATE NONCES SET nonce='%s' WHERE id='%s'",$nonce,$key);
	        $conn->query($sql);
        	$conn->commit();
	}
	echo $nonce;
	return;


    case "upload_cert":
        $type=$_GET['cert_type'];
        echo "Here is the list ".$type;
        if($type=="new"){
                $target_dir = "/var/www/html/Proxy/cert/";
                $target_file = $target_dir . basename($_FILES["file"]["name"]);
                $file_name = $_POST["file_name"];
                //$target_file = $target_dir . basename($_FILES["file"]["name"]);
                $target_file = $target_dir . $file_name;
                if(move_uploaded_file($_FILES["file"]["tmp_name"], $target_file)){
                        echo "Uploaded successfully";
                }
                else{
                        echo "Upload failed ".$_POST["file_name"];
                }
        }
        if($type=="replace"){
                $target_dir = "/var/www/html/Proxy/cert/";
                $target_file = $target_dir . basename($_FILES["file"]["name"]);
                $old_target_file = $target_dir . $_POST["old_file_name"];
                $file_name = $_POST["file_name"];
                $target_file = $target_dir . $file_name;
                echo "Here to check ".$old_target_file." ".file_exists($old_target_file);
                if (file_exists($old_target_file)==1){
                        unlink($old_target_file);
                }
                if(move_uploaded_file($_FILES["file"]["tmp_name"], $target_file)){
                        echo "Uploaded successfully";
                }
                else{
                        echo "Upload failed ".$_FILES["file_name"];
                }
        }

        if($type=="rename"){
                $target_dir = "/var/www/html/Proxy/cert/";
                $target_file = $target_dir . basename($_FILES["file"]["name"]);
                $old_target_file = $target_dir . $_POST["old_file_name"];
                $file_name = $_POST["file_name"];
                $target_file = $target_dir . $file_name;
                if (file_exists($old_target_file)==1){
                        rename( $old_target_file, $target_file);
                }
        }
	return;
    case "add_topo":
        $input = file_get_contents("php://input");
        $input = json_decode($input, true);
        require_once "db_conf.php";
        $sql = sprintf("INSERT INTO PROXY_INFO (as_name) VALUES ('%s')", $input['as_name']);
        $conn->query($sql);
        $conn->commit();
        return;

    case "get_setup_logs":
        require_once "db_conf.php";
                $sql="SELECT as_name from PROXY_INFO";
                $result = $conn->query($sql);
                if ($result->num_rows > 0) {
                        $return_array=array();
                        while ($row = $result->fetch_assoc()) {
                                array_push($return_array,$row);
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


    case "remove_node":
        $as_name = $_GET['as_name'];
        require_once "db_conf.php";
        $sql = sprintf("DELETE FROM PROXY_INFO WHERE  as_name='%s'",$as_name);
        $conn->query($sql);
        $conn->commit();
        $target_file = "/var/www/html/Proxy/cert/".$as_name."_cert.pem";
        unlink($target_file);
        return;

    case "edit_node":
        $old_as_name = $_GET['old_as_name'];
        $as_name = $_GET['as_name'];
        require_once "db_conf.php";
        $sql = sprintf("UPDATE PROXY_INFO SET as_name='%s' WHERE as_name='%s'",$as_name, $old_as_name);
        $conn->query($sql);
        $conn->commit();
        return;

    case "proxy_info":
	require_once "client_auth.php";
	$client_info = client_auth(apache_request_headers());
	if (!$client_info) {
        	http_response_code(400);
	        return;
	}

	$id = $_SERVER['HTTP_CLIENT_IP'] ? $_SERVER['HTTP_CLIENT_IP'] : ($_SERVER['HTTP_X_FORWARDED_FOR'] ? $_SERVER['HTTP_X_FORWARDED_FOR'] : $_SERVER['REMOTE_ADDR']);
	$servername = "localhost";
	$username = "root";
	$password = "usc558l";
	$dbname = "SENSS_PROXY";
	$conn = new mysqli($servername, $username, $password, $dbname);
	if ($conn->connect_error) {
	    die("Connection failed: " . $conn->connect_error);
	}
	$sql = "SELECT nonce FROM NONCES WHERE ip = '" . $id . "'";
	$result = $conn->query($sql);
	$nonce=$result->fetch_assoc()["nonce"];
	$sql = sprintf("DELETE FROM NONCES WHERE nonce='%s'",$nonce);
	$conn->query($sql);
	$conn->commit();
	$content=json_decode(file_get_contents("php://input"),true);
	$cnonce=$content["cnonce"];
	$hash=$content["hash"];
	$content=$content["data"];
	$testHash = hash('sha512',$nonce . $cnonce . json_encode($content,true));
	echo "\n";
	echo $hash."\n";
	echo $testHash."\n";
	if ($testHash==$hash){
		echo "Verification complete";
		return;
	}
	return;
        http_response_code(200);
	$content=json_decode(file_get_contents("php://input"),true);
	//$content=array(
	//	"hpc052"=>1
	//);
	$return_array=array();
	$content=$content["data"];
	foreach($content as $as_name=>$monitor_id){
			$monitor_id=(string) $monitor_id;
			require_once "db_conf.php";
    			$sql = "SELECT server_url FROM AS_URLS WHERE as_name = '" . $as_name . "'";
    			$result = $conn->query($sql);
    			if ($result->num_rows == 0) {
       	 			http_response_code(400);
    		    		return;
    			}
    			$senss_server_url = $result->fetch_assoc()["server_url"];
			array_push($return_array,$senss_server_url);
			$url = $senss_server_url . "?action=add_filter&monitor_id=" . $monitor_id."&as_name=".$as_name;
    			$options = array(
        			'http' => array(
            				'method' => 'GET',
 	          			'header' => generate_request_headers()
        			)
    			);
    			$context = stream_context_create($options);
    			$response = file_get_contents($url, false, $context);
    			$response = json_decode($response,true);
    			$httpcode = http_response_code();
   	 		http_response_code($httpcode);
    			if(!$response["success"]){
       	 			echo json_encode(array(
                			"as_name" => $response["as_name"],
                			"error" => $response["error"],
                			"threshold" => $response["threshold"],
                			"count" =>$response["count"],
                			"details" => $response["details"]
        			),true);
				return;
    			}
    			echo json_encode(array(
                		"success" => true,
                		"as_name" => $response["as_name"],
                		"threshold" => $response["threshold"],
                		"count" => $response["count"],
				"url" => $url
        		),true);
			return;
	}

}

?>

