<?php

ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

$host_url = $_SERVER['HTTP_HOST'];

$servername = "127.0.0.1";
$username = "root";
$password = "lol12345";
$dbName = "solar";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbName);

// Check connection
if ($conn->connect_error) {
 die("Connection failed: " . $conn->connect_error);
 return;
}

$sql = "SELECT type, value, machine FROM data";
$result = $conn->query($sql);

$rows = $result->fetch_all();

echo json_encode($rows);

?>
