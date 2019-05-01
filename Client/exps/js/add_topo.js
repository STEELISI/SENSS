BASE_URI = "api.php?";
function client_form_validation() {
	var client_node_name = document.getElementById('client_node_name').value;
	var file_data = document.getElementById("client_cert").files[0];
	console.log(client_node_name);
	console.log(file_data);
	var return_flag=true;
	var string_to_print="Complete the following:<br>";
	if(client_node_name=="") {
	    string_to_print=string_to_print+"Enter client name<br>";
	    return_flag=false;
  	}
	if(return_flag==false){
	    var markup='<div class="alert alert-danger" role="alert">'+string_to_print+'</div>';
	    document.getElementById('client_form_notification').innerHTML = "";;
	    $("#client_form_notification").append(markup);
	    return false;
	}
	return true;
}

function server_form_validation() {
	var server_node_name = document.getElementById('server_node_name').value;
	var file_data = document.getElementById("client_cert").files[0];
	var server_url = document.getElementById('server_url').value;
	var return_flag=true;
	var string_to_print="Complete the following:<br>";
	if(server_node_name=="") {
	    string_to_print=string_to_print+"Enter server name<br>";
	    return_flag=false;
  	}
	if(server_url=="") {
	    string_to_print=string_to_print+"Enter server URL<br>";
	    return_flag=false;
  	}

	if(return_flag==false){
	    var markup='<div class="alert alert-danger" role="alert">'+string_to_print+'</div>';
	    document.getElementById('server_form_notification').innerHTML = "";;
	    $("#server_form_notification").append(markup);
	    return false;
	}
	return true;
}

$(document).ready(function () {
        console.log("Sivaram Loaded");
        $("#client-node").click(function () {
                console.log("Button clicked");
                document.getElementById('client_node_name').value='';
                $("#config-client-modal").modal('show');
        });

        $("#server-node").click(function () {
                console.log("Button clicked");
                document.getElementById('server_node_name').value='';
                document.getElementById('server_url').value='';
                $("#config-server-modal").modal('show');
        });

        $("#add-client-button").click(function () {
			if(client_form_validation()){
	                        var node_name = $("#client_node_name").val();
	                        var self=1;
        	                var data={"as_name":node_name,"self":self,"server_url":""}
				console.log(data);
	                        $.ajax({
        	                        url: BASE_URI + "add_topo",
                	                type: "POST",
                        	        data: JSON.stringify(data),
	                                contentType: "application/json",
        	                        dataType: "json",
                	                success: function (result) {
                        	                console.log("SIVARAM: Added rules");
        	                        }
	                        });
				var file_data = document.getElementById("client_cert").files[0];
				if (file_data!=null){
					console.log(file_data);
				    	var form_data = new FormData();
	    				form_data.append('file', file_data);
					form_data.append('file_name', node_name+"_cert.pem");
    					$.ajax({
					        url: BASE_URI + "upload_cert&cert_type=new",
				        	dataType: 'text',
        					cache: false,
					        contentType: false,
					        processData: false,
				        	data: form_data,
					        type: 'post',
				        	success: function(php_script_response){
							console.log(php_script_response);
					        }
					});
				}
				$("#config-client-modal").modal('hide');
				location.reload();
			}
        });

        $("#add-server-button").click(function () {
			if(server_form_validation()){
	                        var node_name = $("#server_node_name").val();
        	                var self=0;
				var server_url = $("#server_url").val();
                        	var data={"as_name":node_name,"self":self,"server_url":server_url}
				console.log(data);
        	                $.ajax({
                	                url: BASE_URI + "add_topo",
                        	        type: "POST",
	                                data: JSON.stringify(data),
        	                        contentType: "application/json",
                	                dataType: "json",
                        	        success: function (result) {
	                                        console.log("SIVARAM: Added rules");
        	                        }
                	        });
				var file_data = document.getElementById("server_cert_to_upload").files[0];
				if (file_data!=null){
					console.log("Checking");
					console.log(file_data);
				    	var form_data = new FormData();
    					form_data.append('file', file_data);
					form_data.append('file_name', node_name+"_cert.pem");
    					$.ajax({
					        url: BASE_URI + "upload_cert&cert_type=new",
			        		dataType: 'text',
        					cache: false,
					        contentType: false,
					        processData: false,
				        	data: form_data,
					        type: 'post',
				        	success: function(php_script_response){
							console.log(php_script_response);
					        }
					});
				}
				$("#config-server-modal").modal('hide');
				location.reload();
			}
        });

});
