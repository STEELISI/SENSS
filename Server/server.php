<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
    	<title>SENSS</title>
    	<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/intro.js/2.9.3/introjs.css">
    	<link rel="stylesheet" href="css/bootstrap.min.css">
    	<link rel="stylesheet" href="css/style.css">
    	<link rel="stylesheet" href="css/jquery.qtip.min.css">

   	<script src="js/jquery.min.js"></script>
    	<script src="js/bootstrap.min.js"></script>
    	<script src="js/cytoscape.min.js"></script>
    	<script src="js/jquery.qtip.min.js"></script>

	<script src="https://cdnjs.cloudflare.com/ajax/libs/intro.js/2.9.3/intro.js"><script>
    	<script src="js/cytoscape-qtip.js"></script>
    	<style>
        	.panel {
            		width: 300px;
            		margin: auto;
            		padding: 30px;
        	}

        	.panel-offset-senss {
            		margin: auto;
        	}

        	.second-button {
            		float: right;
       	 	}
    	</style>
</head>

<body>
<nav class="navbar navbar-inverse navbar-static-top">
	<div class="container-fluid">
        	<div class="navbar-header">
        	</div>
        	<div>
            		<ul class="nav navbar-nav">
                	<li><a href="server.php">SENSS</a></li>
			<li><a id="tutorial">Tutorial</a><li>
            		</ul>
        	</div>
    	</div>
</nav>
<body>


<div id="set-threshold-modal" class="modal fade" role="dialog" aria-hidden="true">
    	<div class="modal-dialog">
        	<div class="modal-content">
            	<div class="modal-header">
                	<button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
                	<h4 class="modal-title">Set Threshold</h4>
            	</div>
            	<div class="modal-body" style="height:200px;">
                	<table class="table">
                    		<tr>
                        		<td><input type="text" class="form-control" id="threshold-value"></td>
                        		<td> Rules</td>
                    		</tr>
                	</table>
            	</div>

            	<div class="modal-footer">
                	<div id="set-threshold-button" class="btn btn-success">Set Threshold</div>
            	</div>
        	</div>
   	 </div>
</div>

<div class="container inner-container">
    <h3 data-intro="This panel configures the SENSS server.">SENSS server</h3>
    <div class="row">
        <div class="col-sm-4">
                <button type="button" class="btn btn-primary btn-small" name="submit" id="server-node" data-intro="Click this button to configure the SENSS server. This must be done for the SENSS server to function.">Configure SENSS server</button></span></p>
        </div>
    </div>
</div>

<div class="container inner-container">
<table class='table table-bordered table-striped' id="log_table_server">
<thead>
<tr>
<th data-intro="Name of SENSS server.">Name</th>
<th data-intro="Controller URL.">Controller URL</th>
<th data-intro="Maximum rule capacity supported by the SENSS ISP across all clients.">Rule capacity</th>
<th data-intro="Authentication type for client requests.">Auth type</th>
<th data-intro="Edit SENSS server configuration.">Edit</th>
<th data-intro="Enable fair sharing. Rules are equally distributed among all active SENSS clients and manually configured rule allocation for SENSS clients are overriden.">Fair sharing</th>
<th data-intro="Revoke/un-revoke SENSS server services to all active clients.">Revoke all</th>
</tr>
</thead>
        <tbody>
        </tbody>
</table>
</div>

<div id="config-server-modal" class="modal fade" role="dialog" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
                <h4 class="modal-title">Configure SENSS server</h4>
            </div>

            <div class="modal-body" style="height:400px;">
                <table class="table table-borderless">
                    <tr>
                        <td><span id="server_form_notification"></span></td>
                    <tr>

                    <tr>
                        <th>Name</th>
                    </tr>
                    <tr>
                        <td><input type="text" id="server_node_name" class="form-control" placeholder="USC"></td>
                    </tr>
                    <tr>
                        <th>Controller URL</th>
                    </tr>
                    <tr>
                        <td><input type="text" id="controller_url" class="form-control" placeholder="https://sdn-controller.isi.edu:8080"></td>
                    </tr>
                    <tr>
                        <th>Rule capacity</th>
                    </tr>
                    <tr>
                        <td><input type="text" id="rule_capacity" class="form-control" placeholder="1000"></td>
                    </tr>
                    <tr>
                        <th>Upload root cert</th>
                    </tr>
                    <tr>
                          <td><input type="file" class="custom-file-input" name="server_cert" id="server_cert"></td>
                    </tr>

                </table>
            </div>

            <div class="modal-footer">
                <div id="add-server-button" class="btn btn-success">Done</div>
            </div>
        </div>
    </div>

</div>



<div id="edit-server-modal" class="modal fade" role="dialog" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
                <h4 class="modal-title">Edit SENSS server config</h4>
            </div>

            <div class="modal-body" style="height:400px;">
                <table class="table table-borderless">
                    <tr>
                        <td><span id="edit_server_form_notification"></span></td>
                    <tr>

                    <tr>
                        <th>Name</th>
                    </tr>
                    <tr>
                        <td><input type="text" id="edit_server_node_name" class="form-control" placeholder="USC"></td>
                    </tr>
                    <tr>
                        <th>Controller URL</th>
                    </tr>
                    <tr>
                        <td><input type="text" id="edit_controller_url" class="form-control" placeholder="https://sdn-controller.isi.edu:8080"></td>
                    </tr>
                    <tr>
                        <th>Rule capacity</th>
                    </tr>
                    <tr>
                        <td><input type="text" id="edit_rule_capacity" class="form-control" placeholder="1000"></td>
                    </tr>
                    <tr>
                        <th>Upload root cert</th>
                    </tr>
                    <tr>
                          <td><input type="file" class="custom-file-input" name="edit_server_cert" id="edit_server_cert"></td>
                    </tr>
                </table>
            </div>

            <div class="modal-footer">
                <div id="edit-server-button" class="btn btn-success">Edit</div>
            </div>
        </div>
    </div>

</div>









<div class="container inner-container">
<h3 data-intro="This panels displays active SENSS clients.">Active SENSS clients</h3>

<table class='table table-bordered table-striped' id="threshold_table">
<thead>
<tr>
<th data-intro="Name of the SENSS client.">SENSS client</th>
<th data-intro="Number of active filtering requests.">Active filter requests</th>
<th data-intro="Maximum number of filtering requests permitted for a SENSS client. This value will be reset when fair-sharing is enabled.">Max filter requests</th>
<th data-intro="Number of active monitoring requests.">Active monitoring requests</th>
<th data-intro="Maximum number of monitoring requests permitted for a SENSS client. This value will be reset when fair-sharing is enabled.">Max monitoring requests</th>
<th data-intro="Blocks all new monitoring requests from the SENSS client.">Block monitoring requests</th>
<th data-intro="Blocks all new filtering requests from the SENSS client." >Block filtering requests</th>
<th data-intro="Edit maximum number of monitoring and filtering requests allocated for a SENSS client.">Edit</th>
</tr>
</thead>
        <tbody>
        </tbody>
</table>
</div>

<div id="config-threshold-modal" class="modal fade" role="dialog" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
                <h4 class="modal-title">Edit thresholds</h4>
            </div>

            <div class="modal-body" style="height:400px;">
                <table class="table table-borderless">
                    <tr>
                        <td><span id="threshold_form_notification"></span></td>
                    <tr>

                    <span id="as_name_holder"></span>

                    <tr>
                        <th>Max filter requests</th>
                    </tr>
                    <tr>
                        <td><input type="text" id="max_filter_requests" class="form-control" placeholder="1000"></td>
                    </tr>
                    <tr>
                        <th>Max monitoring requests</th>
                    </tr>
                    <tr>
                        <td><input type="text" id="max_monitoring_requests" class="form-control" placeholder="1000"></td>
                    </tr>
                </table>
            </div>

            <div class="modal-footer">
                <div id="config-threshold-button" class="btn btn-success">Done</div>
            </div>
        </div>
    </div>
</div>

<div class="container inner-container">
	<h3 data-intro="This panel displays the detailed logs of requests sent by SENSS clients.">Detailed logs</h3>
    	<table id="table-monitor" class="table table-bordered table-striped">
        	<thead>
        	<tr>
            		<th data-intro="Name of the requesting SENSS client.">Client AS Name</th>
	    		<th data-intro="Type of request.">Request type</th>
            		<th data-intro="Traffic signature to which the request is applied.">Match</th>
	    		<th data-intro="Number of requests generated by the SENSS client.">Number of requests</th>
        	</tr>
       	 	</thead>
        <tbody>
        </tbody>
    </table>
</div>
</body>
<script src="js/script.js"></script>
</html>
