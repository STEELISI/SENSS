BASE_URI = "api.php?";
$(document).ready(function () {
        console.log("Sivaram Loaded");
        $("#add-nodes").click(function () {
                console.log("Button clicked");
                document.getElementById('node_name').value='';
                document.getElementById('server_url').value='';
                document.getElementById('links_to').value='';
                document.getElementById('is_victim').checked=false;
                $("#set-threshold-modal").modal('show');
        });

        $("#add-nodes-button").click(function () {
                        var node_name = $("#node_name").val();
                        var server_url = $("#server_url").val();
                        var links_to = $("#links_to").val();
                        var self=0;
                        if (document.getElementById("is_victim").checked==true){
                                self=1;
                        }
                        var data={"as_name":node_name,"server_url":server_url,"links_to":links_to,"self":self}
                        console.log("Data",data);
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
			var file_data = document.getElementById("fileToUpload").files[0];
		    	var form_data = new FormData();
    			form_data.append('file', file_data);
			form_data.append('file_name', node_name+"_cert.pem");
    			$.ajax({
			        url: BASE_URI + "upload_cert",
		        	dataType: 'text',  // what to expect back from the PHP script, if anything
        			cache: false,
			        contentType: false,
			        processData: false,
			        data: form_data,
			        type: 'post',
			        success: function(php_script_response){
					console.log(php_script_response);
			        }
			});
			$("#set-threshold-modal").modal('hide');
			location.reload();
        });

});
