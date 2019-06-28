BASE_URI = "api.php?";
var thresholdRateMultiplier = 1;
var threshold = 0;

function populate_values_server(as_name,server_url,random){
	var markup="<tr id='node-row-"+ random +"'><td>"+as_name+"</td><td>"+server_url+"</td><td><button type='button' class='btn btn-primary' id='edit-node-server-" + random + "'>Edit</button></td><td><button type='button' class='btn btn-danger' id='remove-node-server-" + random + "'>Delete</button></td></tr>";
	$("#log_table_server").append(markup);

	$("#remove-node-server-" + random).click(function () {
		console.log(random+" "+as_name);
		$.ajax({
			url: BASE_URI + "remove_node&as_name=" + as_name + "&server_url=" + server_url,
			type: "GET",
			success: function (result) {
				$("#node-row-" + random).remove();
				console.log(result);
			}
		});
	});

        $("#edit-node-server-" + random).click(function () {
                $("#edit-server-modal").modal('show');
                $("#edit_server_node_name").val(as_name);
                $("#edit_server_url").val(server_url);
        });

	$("#edit-server-button").click(function () {
		var new_as_name=$("#edit_server_node_name").val();
		var new_server_url=$("#edit_server_url").val();
		$.ajax({
			url: BASE_URI + "edit_node&old_as_name=" + as_name + "&old_server_url=" + server_url+ "&as_name="+new_as_name+"&server_url="+new_server_url,
			type: "GET",
			success: function (result) {
				console.log("Added name");
			}
		});

		var file_data = document.getElementById("edit_server_cert_to_upload").files[0];
		if (file_data!=null){
			var form_data = new FormData();
			form_data.append('file', file_data);
			form_data.append('file_name', new_as_name+"_cert.pem");
			form_data.append('old_file_name',as_name+"_cert.pem")
			$.ajax({
				url: BASE_URI + "upload_cert&cert_type=replace",
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
				url: BASE_URI + "upload_cert&cert_type=rename",
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
		$("#edit-server-modal").modal('hide');
		location.reload();
	});

}

function poll_stats_server() {
        var check_random=[];
		var add_monitor=[];
                $.ajax({
                        url: BASE_URI + "get_setup_logs&type=server",
                        type: "GET",
                        success: function (result) {
                                var resultParsed = JSON.parse(result);
                                if (resultParsed.success) {
                                        for (var i = 0; i < resultParsed.data.length; i++) {
						var random = Math.random().toString(36).substring(7);
                                                 if (check_random.indexOf(random)==-1){
                                                        check_random.push(random);
                                                }
						var as_name=resultParsed.data[i].as_name;
						var server_url=resultParsed.data[i].server_url;
						populate_values_server(as_name,server_url,random)
                                        }
                                }
                        }
                });
}


function populate_values_client(as_name,server_url,random){
	var markup="<tr id='node-row-"+ random +"'><td>"+as_name+"</td><td><button type='button' class='btn btn-primary' id='edit-node-client-" + random + "'>Edit</button></td><td><button type='button' class='btn btn-danger' id='remove-node-client-" + random + "'>Delete</button></td></tr>";
	$("#log_table_client").append(markup);

	$("#remove-node-client-" + random).click(function () {
		$.ajax({
			url: BASE_URI + "remove_node&as_name=" + as_name + "&server_url=" + server_url,
			type: "GET",
			success: function (result) {
				$("#node-row-" + random).remove();
				console.log(result);
			}
		});
	});

        $("#edit-node-client-" + random).click(function () {
                $("#edit-client-modal").modal('show');
                $("#edit_client_node_name").val(as_name);
        });

	$("#edit-client-button").click(function () {
		var new_as_name=$("#edit_client_node_name").val();
		var new_server_url="";
		$.ajax({
			url: BASE_URI + "edit_node&old_as_name=" + as_name + "&old_server_url=" + server_url+ "&as_name="+new_as_name+"&server_url="+new_server_url,
			type: "GET",
			success: function (result) {
				console.log("Added name");
			}
		});
		var file_data = document.getElementById("edit_client_cert").files[0];
		if (file_data!=null){
			var form_data = new FormData();
			form_data.append('file', file_data);
			form_data.append('file_name', new_as_name+"_cert.pem");
			form_data.append('old_file_name',as_name+"_cert.pem")
			$.ajax({
				url: BASE_URI + "upload_cert&cert_type=replace",
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
				url: BASE_URI + "upload_cert&cert_type=rename",
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
		$("#edit-client-modal").modal('hide');
		location.reload();
	});

}

function poll_stats_client() {
        var check_random=[];
		var add_monitor=[];
                $.ajax({
                        url: BASE_URI + "get_setup_logs&type=client",
                        type: "GET",
                        success: function (result) {
                                var resultParsed = JSON.parse(result);
				console.log(resultParsed);
                                if (resultParsed.success) {
                                        for (var i = 0; i < resultParsed.data.length; i++) {
						var random = Math.random().toString(36).substring(7);
                                                 if (check_random.indexOf(random)==-1){
                                                        check_random.push(random);
                                                }
						var as_name=resultParsed.data[i].as_name;
						var server_url=resultParsed.data[i].server_url;
						populate_values_client(as_name,server_url,random)
                                        }
                                }
                        }
                });
}


$(document).ready(function () {
        poll_stats_server();
        poll_stats_client();
});

