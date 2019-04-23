<?php
$servername = "localhost";
$username = "root";
$password = "sunshine";
$dbname = "SENSS_CLIENT";
$conn = new mysqli($servername, $username, $password, $dbname);
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}
