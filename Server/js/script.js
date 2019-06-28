BASE_URI = "api.php?action=";
var thresholdRateMultiplier = 1;
var threshold = 0;

function isNumeric(n) {
  return !isNaN(parseInt(n)) && isFinite(n);
}


function threshold_form_validation(type) {
	if (type=="new"){
	        var server_node_name = document.getElementById('server_node_name').value;
        	var controller_url = document.getElementById("controller_url").value;
	        var rule_capacity = document.getElementById('rule_capacity').value;
	}
	if (type=="edit"){
	        var server_node_name = document.getElementById('edit_server_node_name').value;
        	var controller_url = document.getElementById("edit_controller_url").value;
	        var rule_capacity = document.getElementById('edit_rule_capacity').value;

	}
        var return_flag=true;
        var string_to_print="Complete the following:<br>";
        if(server_node_name=="") {
            string_to_print=string_to_print+"Enter server name<br>";
            return_flag=false;
        }
        if(controller_url=="") {
            string_to_print=string_to_print+"Enter server URL<br>";
            return_flag=false;
        }
        if(rule_capacity=="") {
            string_to_print=string_to_print+"Enter rule capacity<br>";
            return_flag=false;
        }
	console.log("checking "+isNumeric(rule_capacity));
	if(isNumeric(rule_capacity)==false && rule_capacity!=""){
		string_to_print=string_to_print+"Rule capacity must be a number<br>"
		return_flag=false;
	}
	console.log("Validating");
	console.log(return_flag);
	console.log(string_to_print);
        if(return_flag==false){
            var markup='<div class="alert alert-danger" role="alert">'+string_to_print+'</div>';
	    if (type=="new"){
	            document.getElementById('server_form_notification').innerHTML = "";
	            $("#server_form_notification").append(markup);
		}
	    if (type=="edit"){
	            document.getElementById('edit_server_form_notification').innerHTML = "";
        	    $("#edit_server_form_notification").append(markup);
	    }
            return false;
        }
        return true;
}


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

function populate_values_server(as_name,controller_url,rule_capacity,revoke_all,random){
	console.log("Populating values for constants "+as_name+" "+controller_url+" "+random);
        var markup="<tr id='node-row-"+ random +"'><td>"+as_name+"</td><td>"+controller_url+"</td><td>"+rule_capacity+"</td><td>Certificate</td><td><button type='button' class='btn btn-primary' id='edit-node-server-" + random + "'>Edit</button></td>";
	markup=markup+"<td><button type='button' class='btn btn-primary' id='edit-fair-sharing-"+random+"'>Apply</button></td>";
	if (revoke_all==0){
		markup=markup+"<td><button type='button' class='btn btn-danger' id='revoke-all-"+random+"'>Revoke</button></td></tr>";
	}
	if (revoke_all==1){
		markup=markup+"<td><button type='button' class='btn btn-success' id='revoke-all-"+random+"'>Unrevoke</button></td></tr>";
	}

        $("#log_table_server").append(markup);


        $("#edit-node-server-" + random).click(function () {
                $("#edit-server-modal").modal('show');
                $("#edit_server_node_name").val(as_name);
                $("#edit_controller_url").val(controller_url);
                $("#edit_rule_capacity").val(rule_capacity);
        });

        $("#edit-server-button").click(function () {
		if(threshold_form_validation("edit")){
	                var new_as_name=$("#edit_server_node_name").val();
        	        var new_controller_url=$("#edit_controller_url").val();
	                var new_rule_capacity=$("#edit_rule_capacity").val();
        	        $.ajax({
                	        url: BASE_URI + "edit_controller&old_as_name=" + as_name + "&old_controller_url=" + controller_url+ "&old_rule_capacity="+rule_capacity+"&as_name="+new_as_name+"&controller_url="+new_controller_url+"&rule_capacity="+new_rule_capacity,
	                        type: "GET",
        	                success: function (result) {
					var resultParsed = JSON.parse(result);
					console.log(resultParsed);
					if (resultParsed.success==false) {
						var markup='<div class="alert alert-danger" role="alert">'+resultParsed.reason+'</div>';
				             	document.getElementById('edit_server_form_notification').innerHTML = "";
						 $("#edit_server_form_notification").append(markup);
					}
					if (resultParsed.success){
                	                	console.log("Added name");
			        	        $("#edit-server-modal").modal('hide');
			                	location.reload();
					}
                        	}
	                });
			var file_data = document.getElementById("edit_server_cert").files[0];
			console.log(file_data);
			console.log("Ready");
	                if (file_data!=null){
        	                var form_data = new FormData();
                	        form_data.append('file', file_data);
                        	form_data.append('file_name', "rootcert1.pem");
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
		}
        });

        $("#edit-fair-sharing-" + random).click(function () {
                $.ajax({
                        url: BASE_URI + "apply_fair_sharing&as_name="+as_name,
                        type: "GET",
                        success: function (result) {
				console.log(result);
                                var resultParsed = JSON.parse(result);
				console.log("Got feedback");
				console.log(resultParsed);
				location.reload();
                        }
                });
        });

        $("#revoke-all-" + random).click(function () {
		if (revoke_all==0){
			var final_url= BASE_URI + "revoke_unrevoke&type=revoke"
		}
		if (revoke_all==1){
			var final_url= BASE_URI + "revoke_unrevoke&type=unrevoke"
		}
                $.ajax({
                        url: final_url,
                        type: "GET",
                        success: function (result) {
				location.reload();
                        }
                });
        });



}

function poll_stats_server() {
	        var check_random=[];
                var add_monitor=[];
		console.log("Getting constants all");
                $.ajax({
                        url: BASE_URI + "get_constants",
                        type: "GET",
                        success: function (result) {
                                var resultParsed = JSON.parse(result);
				console.log(resultParsed);
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
						var revoke_all=resultParsed.data[i].revoke_all;
						console.log(as_name+" "+controller_url+" revoked "+revoke_all);
                                                populate_values_server(as_name,controller_url,rule_capacity,revoke_all,random)
                                        }
					document.getElementById("server-node").disabled = true;
                                }
				if (!resultParsed.success){
					document.getElementById("server-node").disabled = false;
				}
                        }
                });
}



function populate_values_threshold(as_name,used_filter_requests,max_filter_requests,used_monitoring_requests,max_monitoring_requests,block_monitoring,block_filtering,random){
	console.log("Block monitoring "+block_monitoring);
	var markup="<tr id='threshold-row-"+ random +"'><td>"+as_name+"</td><td>"+used_filter_requests+"</td><td>"+max_filter_requests+"</td><td>"+used_monitoring_requests+"</td><td>"+max_monitoring_requests+"</td>";
	if (block_monitoring=="1"){
		markup=markup+"<td><button type='button' class='btn btn-primary' id='edit-monitoring-"+random+"'>Unblock</button></td>"
	}
	if (block_monitoring=="0"){
		markup=markup+"<td><button type='button' class='btn btn-primary' id='edit-monitoring-"+random+"'>Block</button></td>";
	}
	if (block_filtering=="1"){
		markup=markup+"<td><button type='button' class='btn btn-primary' id='edit-filtering-"+random+"'>Unblock</button></td>";
	}
	if (block_filtering=="0"){
		markup=markup+"<td><button type='button' class='btn btn-primary' id='edit-filtering-"+random+"'>Block</button></td>";
	}
	markup=markup+"<td><button type='button' class='btn btn-primary' id='edit-"+random+"'>Edit</button></td></tr>";
        $("#threshold_table").append(markup);


        $("#edit-" + random).click(function () {
                $("#config-threshold-modal").modal('show');
		$("#as_name_holder").val(as_name);
                $("#max_filter_requests").val(max_filter_requests);
                $("#max_monitoring_requests").val(max_monitoring_requests);
        });

        $("#edit-monitoring-" + random).click(function () {
                $.ajax({
                        url: BASE_URI + "block_unblock&type=monitoring&as_name="+as_name,
                        type: "GET",
                        success: function (result) {
                                var resultParsed = JSON.parse(result);
				console.log("Got feedback");
				console.log(resultParsed);
				if(resultParsed.data.flip=="1"){
					console.log("Flipping");
					document.getElementById("edit-monitoring-" + random).innerText= "Block";
				}
				if(resultParsed.data.flip=="0"){
					console.log("Flipping");
					document.getElementById("edit-monitoring-" + random).innerText= "Unblock";

				}
                        }
                });
        });

        $("#edit-filtering-" + random).click(function () {
                $.ajax({
                        url: BASE_URI + "block_unblock&type=filtering&as_name="+as_name,
                        type: "GET",
                        success: function (result) {
                                var resultParsed = JSON.parse(result);
				console.log("Got feedback");
				console.log(resultParsed);
				if(resultParsed.data.flip=="1"){
					console.log("Flipping");
					document.getElementById("edit-filtering-" + random).innerText= "Block";
				}
				if(resultParsed.data.flip=="0"){
					console.log("Flipping");
					document.getElementById("edit-filtering-" + random).innerText= "Unblock";

				}
                        }
                });
        });


        $("#config-threshold-button").click(function () {
			var new_max_filter_requests=$("#max_filter_requests").val();
			var new_max_monitoring_requests= $("#max_monitoring_requests").val();
			var as_name= $("#as_name_holder").val();
                	$.ajax({
	                        url: BASE_URI + "edit_threshold&old_max_filter_requests=" + max_filter_requests + "&old_max_monitoring_requests=" + max_monitoring_requests+ "&max_filter_requests="+new_max_filter_requests+"&max_monitoring_requests="+new_max_monitoring_requests+"&as_name="+as_name,
        	                type: "GET",
                	        success: function (result) {
	                                var resultParsed = JSON.parse(result);
        	                        console.log("Got feedback threshold");
                	                console.log(resultParsed);
					if(resultParsed.success){
	                        	        console.log("Added name "+as_name);
			                	$("#config-threshold-modal").modal('hide');
				                location.reload();
					}
					else{
						var markup='<div class="alert alert-danger" role="alert">'+resultParsed.reason+'</div>';
				            	document.getElementById('threshold_form_notification').innerHTML = "";
						$("#threshold_form_notification").append(markup);
					}

	                        }
        	        });
        });

}

function poll_stats_threshold() {
	        var check_random=[];
                var add_monitor=[];
	                $.ajax({
        	                url: BASE_URI + "update_threshold",
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
							var used_filter_requests=resultParsed.data[i].used_filter_requests;
							var max_filter_requests=resultParsed.data[i].max_filter_requests;
							var used_monitoring_requests=resultParsed.data[i].used_monitoring_requests;
							var max_monitoring_requests=resultParsed.data[i].max_monitoring_requests;
							var block_monitoring=resultParsed.data[i].block_monitoring;
							var block_filtering=resultParsed.data[i].block_filtering;
        	                                        populate_values_threshold(as_name,used_filter_requests,max_filter_requests,used_monitoring_requests,max_monitoring_requests,block_monitoring,block_filtering,random)
                                        	}
	                                }
        	                }
                	});

}


$(document).ready(function () {
        var tutorial = localStorage.getItem("tutorial");
        if (tutorial != null) {
                tutorial = parseInt(tutorial);
        }
	else{
		tutorial=0;
	}
	if (tutorial==0){
		introJs().setOption('showProgress', true).start();
		tutorial=1;
		localStorage.setItem("tutorial", tutorial);
	}
        poll_stats();
	poll_stats_server();
	poll_stats_threshold();

        $("#server-node").click(function () {
                console.log("Button clicked");
                document.getElementById('server_node_name').value='';
                document.getElementById('controller_url').value='';
                document.getElementById('rule_capacity').value='';
                $("#config-server-modal").modal('show');
        });



        $("#add-server-button").click(function () {
                                console.log(data);
				if(threshold_form_validation("new")){
	                                var node_name = $("#server_node_name").val();
	                                var controller_url = $("#controller_url").val();
        	                        var rule_capacity = $("#rule_capacity").val();
                	                var data={"as_name":node_name,"controller_url":controller_url,"rule_capacity":rule_capacity,"fair_sharing":0}
					console.log("Validated");
					console.log(data);
	                                $.ajax({
        	                                url: BASE_URI + "config_constants",
                	                        type: "POST",
                        	                data: JSON.stringify(data),
                                	        contentType: "application/json",
	                                        dataType: "json",
        	                                success: function (result) {
							console.log(result);
                        	                        console.log("SIVARAM: Added config");
                                	        }
	                                });
                                	var file_data = document.getElementById("server_cert").files[0];
	                                if (file_data!=null){
        	                                console.log(file_data);
                	                        var form_data = new FormData();
                        	                form_data.append('file', file_data);
                                	        form_data.append('file_name', "rootcert1.pem");
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

	var tutorial_link = document.getElementById("tutorial");
	tutorial_link.onclick = function() {
		introJs().setOption('showProgress', true).start();
	}


});

