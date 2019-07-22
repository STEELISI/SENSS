BASE_URI = "api.php?";
var thresholdRateMultiplier = 1;
var threshold = 0;

function populate_values_proxy(as_name,server_url,random){
	var markup="<tr id='node-row-"+ random +"'><td>"+as_name+"</td><td><button type='button' class='btn btn-primary' id='edit-node-proxy-" + random + "'>Edit</button></td><td><button type='button' class='btn btn-danger' id='remove-node-proxy-" + random + "'>Delete</button></td></tr>";
	$("#log_table_proxy").append(markup);

	$("#remove-node-proxy-" + random).click(function () {
		$.ajax({
			url: BASE_URI + "action=remove_node&as_name=" + as_name,
			type: "GET",
			success: function (result) {
				$("#node-row-" + random).remove();
				console.log(result);
			}
		});
	});

        $("#edit-node-proxy-" + random).click(function () {
                $("#edit-proxy-modal").modal('show');
                $("#edit_proxy_node_name").val(as_name);
        });

	$("#edit-proxy-button").click(function () {
		var new_as_name=$("#edit_proxy_node_name").val();
		var new_server_url="";
		$.ajax({
			url: BASE_URI + "action=edit_node&old_as_name=" + as_name + "&as_name="+new_as_name,
			type: "GET",
			success: function (result) {
				console.log("Added name");
			}
		});
		var file_data = document.getElementById("edit_proxy_cert").files[0];
		if (file_data!=null){
			var form_data = new FormData();
			form_data.append('file', file_data);
			form_data.append('file_name', new_as_name+"_cert.pem");
			form_data.append('old_file_name',as_name+"_cert.pem")
			$.ajax({
				url: BASE_URI + "action=upload_cert&cert_type=replace",
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
		if (file_data==null){
			var form_data = new FormData();
			form_data.append('file', file_data);
			form_data.append('file_name', new_as_name+"_cert.pem");
			form_data.append('old_file_name',as_name+"_cert.pem")
			$.ajax({
				url: BASE_URI + "action=upload_cert&cert_type=rename",
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
		$("#edit-proxy-modal").modal('hide');
		location.reload();
	});

}


//action=add_topo
function poll_stats_proxy() {
        var check_random=[];
                var add_monitor=[];
		console.log("Polling proxy");
                $.ajax({
                        url: BASE_URI + "action=get_setup_logs",
                        type: "GET",
                        success: function (result) {
                                var resultParsed = JSON.parse(result);
				console.log("Got something");
                                console.log(resultParsed);
                                if (resultParsed.success) {
                                        for (var i = 0; i < resultParsed.data.length; i++) {
                                                var random = Math.random().toString(36).substring(7);
                                                 if (check_random.indexOf(random)==-1){
                                                        check_random.push(random);
                                                }
                                                var as_name=resultParsed.data[i].as_name;
                                                var server_url=resultParsed.data[i].server_url;
                                                populate_values_proxy(as_name,server_url,random)
                                        }
                                }
                        }
                });
}


$(document).ready(function () {
	poll_stats_proxy()
        var tutorial = localStorage.getItem("proxy_tutorial");
        if (tutorial != null) {
                tutorial = parseInt(tutorial);
        }
        else{
                tutorial=0;
        }
        if (tutorial==0){
                introJs().setOption('showProgress', true).start();
                tutorial=1;
                localStorage.setItem("proxy_tutorial", tutorial);
        }
         var tutorial_link = document.getElementById("tutorial");
	/*tutorial_link.onclick = function() {
                introJs().setOption('showProgress', true).start();
        }*/

});

