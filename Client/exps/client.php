<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
    <title>SENSS</title>
    <link rel="stylesheet" href="css/bootstrap.min.css">
    <link rel="stylesheet" href="css/style.css">
    <script src="js/jsnetworkx.js"></script>
    <script src="js/constants.js"></script>
    <script src="js/jquery.min.js"></script>
    <script src="js/bootstrap.min.js"></script>
    <script src="js/cytoscape.min.js"></script>
    <script src="js/jquery.qtip.min.js"></script>
    <link rel="stylesheet" href="css/jquery.qtip.min.css">
    <script src="js/cytoscape-qtip.js"></script>
    <style>
	.table-borderless > tbody > tr > td,
	.table-borderless > tbody > tr > th,
	.table-borderless > tfoot > tr > td,
	.table-borderless > tfoot > tr > th,
	.table-borderless > thead > tr > td,
	.table-borderless > thead > tr > th {
	    border: none;
	}
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
            <a class="navbar-brand" href="client.php">Setup</a>
            <a class="navbar-brand" href="ddos_with_sig.php">SENSS Client</a>
            <a class="navbar-brand" href="logs.php">Logs</a>
        </div>
    </div>
</nav>



<div class="container inner-container">
    <h2>Setup</h2>
    <div class="row">
    	<div class="col-sm-4">
     		<button type="button" class="btn btn-primary btn-small" name="submit" id="client-node">Config this client</button></span></p>
	</div>
    </div>
</div>
<div class="container inner-container">
<table class='table table-bordered table-striped' id="log_table_client">
<thead>
<tr>
<th>AS name</th>
<th>Edit</th>
<th>Delete</th>
</tr>
</thead>
        <tbody>
        </tbody>
</table>
</div>


<div id="config-client-modal" class="modal fade" role="dialog" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
                <h4 class="modal-title">Config SENSS client</h4>
            </div>

            <div class="modal-body" style="height:400px;">
                <table class="table table-borderless">
		    <tr>
			<td><span id="client_form_notification"></span></td>
		    <tr>
                    <tr>
			<th>AS name</th>
                    </tr>
                    <tr>
                        <td><input type="text" id="client_node_name" class="form-control" placeholder="ISI"></td>
                    </tr>

                    <tr>
			<th>RPKI certificate proving prefix ownership of this client</th>
                    </tr>
		    <tr>
	    		  <td><input type="file" class="custom-file-input" name="client_cert" id="client_cert"></td>
		    </tr>
                </table>
            </div>

            <div class="modal-footer">
                <div id="add-client-button" class="btn btn-success">Add</div>
            </div>
        </div>
    </div>
</div>


<div id="edit-client-modal" class="modal fade" role="dialog" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
                <h4 class="modal-title">Edit SENSS client</h4>
            </div>

            <div class="modal-body" style="height:400px;">
                <table class="table table-borderless">
		    <tr>
			<td><span id="client_form_notification"></span></td>
		    <tr>
                    <tr>
			<th>AS name</th>
                    </tr>
                    <tr>
                        <td><input type="text" id="edit_client_node_name" class="form-control" placeholder="ISI"></td>
                    </tr>

                    <tr>
			<th>RPKI certificate proving prefix ownership of this client</th>
                    </tr>
		    <tr>
	    		  <td><input type="file" class="custom-file-input" name="edit_client_cert" id="edit_client_cert"></td>
		    </tr>
                </table>
            </div>

            <div class="modal-footer">
                <div id="edit-client-button" class="btn btn-success">Edit</div>
            </div>
        </div>
    </div>
</div>


<div class="container inner-container">
    <div class="row">
    	<div class="col-sm-4">
     		<button type="button" class="btn btn-primary btn-small" name="submit" id="server-node">Config link to remote server</button></span></p>
	</div>
    </div>
</div>

<div class="container inner-container">
<table class='table table-bordered table-striped' id="log_table_server">
<thead>
<tr>
<th>AS name</th>
<th>Server URL</th>
<th>Edit</th>
<th>Delete</th>

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
                <h4 class="modal-title">Add SENSS node</h4>
            </div>

            <div class="modal-body" style="height:400px;">
                <table class="table table-borderless">
		    <tr>
			<td><span id="server_form_notification"></span></td>
		    <tr>

                    <tr>
			<th>AS name</th>
                    </tr>
                    <tr>
                        <td><input type="text" id="server_node_name" class="form-control" placeholder="USC"></td>
                    </tr>
                    <tr>
			<th>Server URL</th>
                    </tr>
                    <tr>
                        <td><input type="text" id="server_url" class="form-control" placeholder="https://senss.isi.edu/api.php"></td>
                    </tr>

                    <tr>
			<th>Certificate (Custom certificate issued by the SENSS ISP)</th>
                    </tr>
		    <tr>
	    		  <td><input type="file" class="custom-file-input" name="server_cert_to_upload" id="server_cert_to_upload"></td>
		    </tr>
                </table>
            </div>

            <div class="modal-footer">
                <div id="add-server-button" class="btn btn-success">Add</div>
            </div>
        </div>
    </div>

</div>

<div id="edit-server-modal" class="modal fade" role="dialog" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
                <h4 class="modal-title">Edit SENSS node</h4>
            </div>

            <div class="modal-body" style="height:400px;">
                <table class="table table-borderless">
		    <tr>
			<td><span id="server_form_notification"></span></td>
		    <tr>

                    <tr>
			<th>AS name</th>
                    </tr>
                    <tr>
                        <td><input type="text" id="edit_server_node_name" class="form-control" placeholder="USC"></td>
                    </tr>
                    <tr>
			<th>Server URL</th>
                    </tr>
                    <tr>
                        <td><input type="text" id="edit_server_url" class="form-control" placeholder="https://senss.isi.edu/api.php"></td>
                    </tr>

                    <tr>
			<th>Certificate (Custom certificate issued by the SENSS ISP)</th>
                    </tr>
		    <tr>
	    		  <td><input type="file" class="custom-file-input" name="server_cert_to_upload" id="edit_server_cert_to_upload"></td>
		    </tr>
                </table>
            </div>

            <div class="modal-footer">
                <div id="edit-server-button" class="btn btn-success">Edit</div>
            </div>
        </div>
    </div>

</div>



</body>
<script src="js/add_topo.js"></script>
<script src="js/logs_setup.js"></script>

</html>
