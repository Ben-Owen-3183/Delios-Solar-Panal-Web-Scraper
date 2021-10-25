GNU nano 3.2                                                                                    data.php                                                                                              

<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

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

$type = $_GET['type'];
$sql = "SELECT value FROM data WHERE type="."'".$type."'";
$result = $conn->query($sql);
$row = $result->fetch_assoc();
echo $row["value"];

$conn->close();

?>
