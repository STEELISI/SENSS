BASE_URI = "api.php?";
var thresholdRateMultiplier = 1;
var threshold = 0;

function populate_values_amon(process_name,status,random){
	if (status==0){
		var markup="<tr id='amon-node-row-"+ random +"'><td>"+process_name+"</td>"+"</td><td><button type='button' class='btn btn-primary' id='config-amon-" + random + "'>Start</button></td></tr>";
	}
	if (status==1){
		var markup="<tr id='amon-node-row-"+ random +"'><td>"+process_name+"</td>"+"</td><td><button type='button' class='btn btn-primary' id='config-amon-" + random + "'>Stop</button></td></tr>";
	}
	$("#client_processes").append(markup);

	$("#config-amon-" + random).click(function () {
               	$.ajax({
                        url: BASE_URI + "get_amon",
                        type: "GET",
                        success: function (result) {
                                var resultParsed = JSON.parse(result);
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

function populate_values_server_amon(as_name,server_url,random){
	var check_random=[];
                $.ajax({
                        url: BASE_URI + "get_amon",
                        type: "GET",
                        success: function (result) {
				console.log("new results");
				console.log(result);
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
        populate_values_server_amon();
        var tutorial = localStorage.getItem("client_tutorial");
        if (tutorial != null) {
                tutorial = parseInt(tutorial);
        }
        else{
                tutorial=0;
        }
        if (tutorial==0){
                introJs().setOption('showProgress', true).start();
                tutorial=1;
                localStorage.setItem("client_tutorial", tutorial);
        }
	        var tutorial_link = document.getElementById("tutorial");
        tutorial_link.onclick = function() {
                introJs().setOption('showProgress', true).start();
        }
});

