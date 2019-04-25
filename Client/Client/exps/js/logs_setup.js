BASE_URI = "api.php?";
var thresholdRateMultiplier = 1;
var threshold = 0;

function populate_values_server(as_name,server_url,random){
	var markup="<tr id='node-row-"+ random +"'><td>"+as_name+"</td><td>"+server_url+"</td><td><button type='button' class='btn btn-danger' id='remove-node-" + random + "'>Remove node</button></td></tr>";
	$("#log_table_server").append(markup);

	$("#remove-node-" + random).click(function () {
		console.log(random+" "+as_name);
		$.ajax({
			url: BASE_URI + "remove_node&as_name=" + as_name + "&server_url=" + server_url,
			type: "GET",
			success: function (result) {
				$("#node-row-" + random).remove();
			}
		});
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
				console.log(resultParsed);
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
	var markup="<tr id='node-row-"+ random +"'><td>"+as_name+"</td><td><button type='button' class='btn btn-danger' id='remove-node-" + random + "'>Remove node</button></td></tr>";
	$("#log_table_client").append(markup);

	$("#remove-node-" + random).click(function () {
		console.log(random+" "+as_name);
		$.ajax({
			url: BASE_URI + "remove_node&as_name=" + as_name + "&server_url=" + server_url,
			type: "GET",
			success: function (result) {
				$("#node-row-" + random).remove();
			}
		});
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

