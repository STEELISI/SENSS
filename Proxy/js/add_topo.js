BASE_URI = "api.php?";
function proxy_form_validation() {
	var proxy_node_name = document.getElementById('proxy_node_name').value;
	var file_data = document.getElementById("proxy_cert").files[0];
	console.log(proxy_node_name);
	console.log(file_data);
	var return_flag=true;
	var string_to_print="Complete the following:<br>";
	if(proxy_node_name=="") {
	    string_to_print=string_to_print+"Enter proxy name<br>";
	    return_flag=false;
  	}
	if(return_flag==false){
	    var markup='<div class="alert alert-danger" role="alert">'+string_to_print+'</div>';
	    document.getElementById('proxy_form_notification').innerHTML = "";
	    $("#proxy_form_notification").append(markup);
	    return false;
	}
	return true;
}

$(document).ready(function () {
        console.log("Sivaram Loaded");
        $("#proxy-node").click(function () {
                console.log("Button clicked");
                document.getElementById('proxy_node_name').value='';
                $("#config-proxy-modal").modal('show');
        });

        $("#add-proxy-button").click(function () {
			if(proxy_form_validation()){
	                        var node_name = $("#proxy_node_name").val();
	                        var self=1;
        	                var data={"as_name":node_name,"self":self,"server_url":""}
				console.log(data);
	                        $.ajax({
        	                        url: BASE_URI + "action=add_topo",
                	                type: "POST",
                        	        data: JSON.stringify(data),
	                                contentType: "application/json",
        	                        dataType: "json",
                	                success: function (result) {
                        	                console.log("SIVARAM: Added rules");
        	                        }
	                        });
				var file_data = document.getElementById("proxy_cert").files[0];
				if (file_data!=null){
					console.log(file_data);
				    	var form_data = new FormData();
	    				form_data.append('file', file_data);
					form_data.append('file_name', node_name+"_cert.pem");
    					$.ajax({
					        url: BASE_URI + "action=upload_cert&cert_type=new",
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
				$("#config-proxy-modal").modal('hide');
				location.reload();
			}
        });

});
