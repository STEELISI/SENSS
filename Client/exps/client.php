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


<div id="network-canvas" style="height: 500px; width: 1080px; margin: 0 auto; border: 1px solid black;"></div>
<div class="container inner-container">
    <h2>Setup</h2>
    <div class="row">
    	<div class="col-sm-4">
     		<button type="button" class="btn btn-primary btn-small" name="submit" id="add-nodes">Add SENSS node</button></span></p>
	</div>
    </div>
</div>

<div id="set-threshold-modal" class="modal fade" role="dialog" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
                <h4 class="modal-title">Add SENSS node</h4>
            </div>

            <div class="modal-body" style="height:400px;">
                <table class="table table-borderless">
                    <tr>
			<th>AS name</th>
                    </tr>
                    <tr>
                        <td><input type="text" id="node_name" class="form-control"></td>
                    </tr>
                    <tr>
			<th>Server/client URL</th>
                    </tr>
                    <tr>
                        <td><input type="text" id="server_url" class="form-control"></td>
                    </tr>

                    <tr>
			<th>Node type</th>
                    </tr>
                    <tr>
			<td><input type="checkbox" id="senss_client"> SENSS client<br></td>
			<td><input type="checkbox" id="senss_server"> SENSS server<br></td>
                    </tr>

                    <tr>
			<th>Certificate</th>
                    </tr>
		    <tr>
	    		  <td><input type="file" class="custom-file-input" name="fileToUpload" id="fileToUpload"></td>
		    </tr>
                </table>
            </div>

            <div class="modal-footer">
                <div id="add-nodes-button" class="btn btn-success">Add</div>
            </div>
        </div>
    </div>
</div>

</body>
<script src="js/add_topo.js"></script>
<script src="js/render_network_ddos_with_sig.js"></script>

</html>
