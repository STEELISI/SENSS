<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
    <title>SENSS</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/intro.js/2.9.3/introjs.css">
    <link rel="stylesheet" href="css/bootstrap.min.css">
    <link rel="stylesheet" href="css/style.css">
    <!--<script src="js/jsnetworkx.js"></script>
    <script src="js/constants.js"></script>-->
    <script src="js/jquery.min.js"></script>
    <script src="js/bootstrap.min.js"></script>
    <!--<script src="js/cytoscape.min.js"></script>-->
    <script src="js/jquery.qtip.min.js"></script>
    <link rel="stylesheet" href="css/jquery.qtip.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/intro.js/2.9.3/intro.js"><script>
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
            <a class="navbar-brand" href="proxy.php">Setup</a>
   	   <a class="navbar-brand" id="tutorial">Tutorial</a>
        </div>
    </div>
</nav>



<div class="container inner-container">
    <h2 data-intro="This panel configures SENSS proxy parameters.">Setup</h2>
    <div class="row">
    	<div class="col-sm-4">
     		<button type="button" class="btn btn-primary btn-small" name="submit" id="proxy-node" data-intro="Click this button to configure the SENSS proxy.">Config this proxy</button></span></p>
	</div>
    </div>
</div>
<div class="container inner-container">
<table class='table table-bordered table-striped' id="log_table_proxy">
<thead>
<tr>
<th data-intro="Displays the proxy name.">Proxy name</th>
<th data-intro="Edit proxy configuration.">Edit</th>
<th data-intro="Delete existing configuration.">Delete</th>
</tr>
</thead>
        <tbody>
        </tbody>
</table>
</div>


<div id="config-proxy-modal" class="modal fade" role="dialog" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
                <h4 class="modal-title">Config SENSS proxy</h4>
            </div>

            <div class="modal-body" style="height:400px;">
                <table class="table table-borderless">
		    <tr>
			<td><span id="proxy_form_notification"></span></td>
		    <tr>
                    <tr>
			<th>AS name</th>
                    </tr>
                    <tr>
                        <td><input type="text" id="proxy_node_name" class="form-control" placeholder="ISI"></td>
                    </tr>

                    <tr>
			<th>RPKI certificate proving prefix ownership of this proxy</th>
                    </tr>
		    <tr>
	    		  <td><input type="file" class="custom-file-input" name="proxy_cert" id="proxy_cert"></td>
		    </tr>
                </table>
            </div>

            <div class="modal-footer">
                <div id="add-proxy-button" class="btn btn-success">Add</div>
            </div>
        </div>
    </div>
</div>


<div id="edit-proxy-modal" class="modal fade" role="dialog" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
                <h4 class="modal-title">Edit SENSS proxy</h4>
            </div>

            <div class="modal-body" style="height:400px;">
                <table class="table table-borderless">
		    <tr>
			<td><span id="proxy_form_notification"></span></td>
		    <tr>
                    <tr>
			<th>AS name</th>
                    </tr>
                    <tr>
                        <td><input type="text" id="edit_proxy_node_name" class="form-control" placeholder="ISI"></td>
                    </tr>

                    <tr>
			<th>RPKI certificate proving prefix ownership of this proxy</th>
                    </tr>
		    <tr>
	    		  <td><input type="file" class="custom-file-input" name="edit_proxy_cert" id="edit_proxy_cert"></td>
		    </tr>
                </table>
            </div>

            <div class="modal-footer">
                <div id="edit-proxy-button" class="btn btn-success">Edit</div>
            </div>
        </div>
    </div>
</div>


</body>
<script src="js/add_topo.js"></script>
<script src="js/logs_setup.js"></script>

</html>
