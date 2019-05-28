BASE_URI = "api.php?";
var thresholdRateMultiplier = 1;
var threshold = 0;

function populate_values_amon(process_name,status,random){
	console.log(process_name+" "+status+" "+random);
	if (status==0){
		var markup="<tr id='node-row-"+ random +"'><td>"+process_name+"</td>"+"</td><td><button type='button' class='btn btn-primary' id='config-amon-" + random + "'>Start</button></td></tr>";
	}
	if (status==1){
		var markup="<tr id='node-row-"+ random +"'><td>"+process_name+"</td>"+"</td><td><button type='button' class='btn btn-primary' id='config-amon-" + random + "'>Stop</button></td></tr>";
	}
	$("#client_processes").append(markup);

	$("#config-amon-" + random).click(function () {
		console.log("clicked");
               	$.ajax({
                        url: BASE_URI + "get_amon",
                        type: "GET",
                        success: function (result) {
                                var resultParsed = JSON.parse(result);
				console.log(resultParsed);
                                if (resultParsed.success) {
                                        for (var i = 0; i < resultParsed.data.length; i++) {
						var process_name=resultParsed.data[i].process_name;
						var status=resultParsed.data[i].status;
                                        }
                                }
				var change_status=0;
				if (status==0){
					change_status=1;
				}
				else{
					change_status=0;
				}
				console.log("Change status to "+change_status);
		                $.ajax({
		                        url: BASE_URI + "change_amon&change_status=" + change_status,
		                        type: "GET",
		                        success: function (result) {
						if(change_status==0){
							document.getElementById('config-amon-'+random).innerHTML = "Start";
						}
						if(change_status==1){
							document.getElementById('config-amon-'+random).innerHTML = "Stop";
						}
		                        }
		                });
                        }
                });
        });






}

function populate_values_server(as_name,server_url,random){
	var check_random=[];
                $.ajax({
                        url: BASE_URI + "get_amon",
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
						var process_name=resultParsed.data[i].process_name;
						var status=resultParsed.data[i].status;
						populate_values_amon(process_name,status,random)
                                        }
                                }
                        }
                });
}


$(document).ready(function () {
        populate_values_server();
});
