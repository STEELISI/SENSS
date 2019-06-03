<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
    	<title>SENSS</title>
    	<link rel="stylesheet" href="css/bootstrap.min.css">
    	<link rel="stylesheet" href="css/style.css">
   	<script src="js/jquery.min.js"></script>
    	<script src="js/bootstrap.min.js"></script>
    	<script src="js/cytoscape.min.js"></script>
    	<script src="js/jquery.qtip.min.js"></script>
    	<link rel="stylesheet" href="css/jquery.qtip.min.css">
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
    <div class="row">
        <div class="col-sm-4">
                <button type="button" class="btn btn-primary btn-small" name="submit" id="server-node">Configure SENSS server</button></span></p>
        </div>
    </div>
</div>

<div class="container inner-container">
<table class='table table-bordered table-striped' id="log_table_server">
<thead>
<tr>
<th>Name</th>
<th>Controller URL</th>
<th>Rule capacity</th>
<th>Edit</th>
<th>Fair sharing</th>
<th>Revoke all</th>
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

                </table>
            </div>

            <div class="modal-footer">
                <div id="edit-server-button" class="btn btn-success">Edit</div>
            </div>
        </div>
    </div>

</div>









<div class="container inner-container">
<table class='table table-bordered table-striped' id="threshold_table">
<thead>
<tr>
<th>SENSS client</th>
<th>Active filter requests</th>
<th>Max filter requests</th>
<th>Active monitoring requests</th>
<th>Max monitoring requests</th>
<th>Block monitoring requests</th>
<th>Block filtering requests</th>
<th>Edit</th>
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
    	<div class="col-md-8">
        	<h2>Logs</h2>
    	</div>
    	<table id="table-monitor" class="table table-bordered table-striped">
        	<thead>
        	<tr>
            		<th>Client AS Name</th>
	    		<th>Request type</th>
            		<th>Match</th>
	    		<th>Number of requests</th>
        	</tr>
       	 	</thead>
        <tbody>
        </tbody>
    </table>
</div>

</body>
<script src="js/script.js"></script>
</html>
