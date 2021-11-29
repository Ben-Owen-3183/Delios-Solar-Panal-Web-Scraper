
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

$sql = "SELECT type, value FROM data";
$result = $conn->query($sql);

$rows = $result->fetch_all();

?>

<html style="background-color: black;">
    
    <head>
        <style>
            table, th, td {
                color: #03A062;
                border: 1px solid #03A062;
                border-collapse: collapse;
            }
            table {
            }
            th, td {
            }
            td {
                padding: 5px;
            }
        </style>
    </head>

    <body>
        <em><h2 style="color: #03A062;">Delios Solar Panel Web Scraper</h2></em>
        <pre style="color: #03A062;">
NOTE: 
<strong>The following values are worked out as the mean value (avg) from each solar panel system that is linked</strong>
- percentbattery
- energy_battery_char
- energy_battery_discha
- self_sufficiency
<strong>All other values are accumulated i.e. added together.</strong>

        </pre>
        <table>
            <tr>
                <td><strong>Type</strong></td>
                <td><strong>Value</strong></td>
                <td><strong>URL</strong></td>
            </tr>
            <?php foreach($rows as $row): ?>
                <tr>
                    <td><p><?=$row[0]?></p></td>

                    <td><p><?=$row[1]?></p></td>
                    <td>
                        <a href="/data.php?type=<?=$row[0]?>">
                            <?=$host_url."/data.php?type=".$row[0]?>
                        </a>
                    </td>
                </tr>
            <?php endforeach; ?>
        </table>
    </body>
</html>
