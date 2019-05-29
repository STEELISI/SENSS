BASE_URI = "api.php?action=";
var thresholdRateMultiplier = 1;
var threshold = 0;



function populateMonitoringValues(data,rowId,match) {
        $("#as-name-" + rowId).html(data.as_name);
        $("#request-type-" + rowId).html(data.request_type);
        $("#match-" + rowId).html(data.match_field);
        $("#request-count-" + rowId).html(data.count_request_type);
}

function poll_stats() {
        var check_random=[];
        var timer = setInterval(function () {
                $.ajax({
                        url: BASE_URI + "get_server_logs",
                        type: "GET",
                        success: function (result) {
                                var resultParsed = JSON.parse(result);
                                if (resultParsed.success) {
                                        for (var i = 0; i < resultParsed.data.length; i++) {
                                                 var random = resultParsed.data[i].as_name+"_"+resultParsed.data[i].request_type.replace(/\s/g, '');
                                                 if (check_random.indexOf(random)==-1){
                                                        check_random.push(random);
                                                         var markup = "<tr id='monitor-row-" + random +"'>" +
                                                                "<td id='as-name-" + random + "'></td>" +
                                                                "<td id='request-type-" + random + "'></td>" +
                                                                "<td id='match-" + random + "'><pre></pre></td>" +
                                                                "<td id='request-count-" + random + "'><pre></pre></td>";
                                                        $("#table-monitor").append(markup);
                                                }
                                                populateMonitoringValues(resultParsed.data[i],random);
                                        }
                                }
                        }
                });
        }, (1* 1000)); // rule[2] is actual frequency with which the backend system will update the database/
}

function set_threshold() {
        var storedThreshold = localStorage.getItem("threshold");

        if (storedThreshold != null) {
                threshold = parseInt(storedThreshold);
        }
        $("#current-threshold").html(threshold+" Rules");
}

function populate_values_server(as_name,controller_url,rule_capacity,random){
	console.log("Populating values "+as_name+" "+controller_url+" "+random);
        var markup="<tr id='node-row-"+ random +"'><td>"+as_name+"</td><td>"+controller_url+"</td><td>"+rule_capacity+"</td><td><button type='button' class='btn btn-primary' id='edit-node-server-" + random + "'>Edit</button></td><td><button type='button' class='btn btn-danger' id='remove-node-server-" + random + "'>Delete</button></td></tr>";
        $("#log_table_server").append(markup);

        $("#remove-node-server-" + random).click(function () {
		console.log("Removing controller");
                console.log(random+" "+as_name+" "+controller_url);
                $.ajax({
                        url: BASE_URI + "remove_controller&as_name=" + as_name + "&controller_url=" + controller_url,
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
                $("#edit_controller_url").val(controller_url);
                $("#edit_rule_capacity").val(rule_capacity);
        });

        $("#edit-server-button").click(function () {
                var new_as_name=$("#edit_server_node_name").val();
                var new_controller_url=$("#edit_controller_url").val();
                var new_rule_capacity=$("#edit_rule_capacity").val();
                $.ajax({
                        url: BASE_URI + "edit_controller&old_as_name=" + as_name + "&old_controller_url=" + controller_url+ "&old_rule_capacity="+rule_capacity+"&as_name="+new_as_name+"&controller_url="+new_controller_url+"&rule_capacity="+new_rule_capacity,
                        type: "GET",
                        success: function (result) {
                                console.log("Added name");
                        }
                });
                $("#edit-server-modal").modal('hide');
                location.reload();
        });
}

function poll_stats_server() {
        var check_random=[];
                var add_monitor=[];
		console.log("Getting constants");
                $.ajax({
                        url: BASE_URI + "get_constants",
                        type: "GET",
                        success: function (result) {
                                var resultParsed = JSON.parse(result);
                                if (resultParsed.success) {

                                        for (var i = 0; i < resultParsed.data.length; i++) {
						console.log(resultParsed);
                                                var random = Math.random().toString(36).substring(7);
                                                 if (check_random.indexOf(random)==-1){
                                                        check_random.push(random);
                                                }
                                                var as_name=resultParsed.data[i].as_name;
                                                var controller_url=resultParsed.data[i].controller_url;
                                                var rule_capacity=resultParsed.data[i].rule_capacity;
						console.log(as_name+" "+controller_url);
                                                populate_values_server(as_name,controller_url,rule_capacity,random)

                                        }
                                }
                        }
                });
}


$(document).ready(function () {
        set_threshold();
        poll_stats();
        $("#set-threshold").click(function () {
                $("#set-threshold-modal").modal('show');
        });

        $("#set-threshold-button").click(function () {
                var value = parseInt($("#threshold-value").val());
                threshold=value;
                localStorage.setItem("threshold", threshold);
                $("#current-threshold").html(threshold+" Rules");
                $("#set-threshold-modal").modal('hide');
                $.ajax({
                        type: "POST",
                        url: 'threshold.php',
                        dataType: 'json',
                        data: {functionname: 'insert_threshold', arguments: [threshold]},
                        success: function (result) {
                                console.log("Inserted"+result);
                        }
                });
         });

	poll_stats_server();


        $("#server-node").click(function () {
                console.log("Button clicked");
                document.getElementById('server_node_name').value='';
                document.getElementById('controller_url').value='';
                document.getElementById('rule_capacity').value='';
                $("#config-server-modal").modal('show');
        });


        $("#add-server-button").click(function () {
                                var node_name = $("#server_node_name").val();
                                var controller_url = $("#controller_url").val();
                                var rule_capacity = $("#rule_capacity").val();
                                var data={"as_name":node_name,"controller_url":controller_url,"rule_capacity":rule_capacity}
                                console.log(data);
                                $.ajax({
                                        url: BASE_URI + "config_constants",
                                        type: "POST",
                                        data: JSON.stringify(data),
                                        contentType: "application/json",
                                        dataType: "json",
                                        success: function (result) {
                                                console.log("SIVARAM: Added config");
                                        }
                                });
                                $("#config-server-modal").modal('hide');
                                location.reload();
        });

});

