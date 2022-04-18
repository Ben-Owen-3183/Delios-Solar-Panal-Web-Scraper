
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

$sql = "SELECT type, value, machine FROM data where machine = 'machine-1'";
$result = $conn->query($sql);
$machine1_data = $result->fetch_all();

$sql = "SELECT type, value, machine FROM data where machine = 'machine-2'";
$result = $conn->query($sql);
$machine2_data = $result->fetch_all();

$data = ['Machine 1'=> $machine1_data, 'Machine 2'=> $machine2_data]

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
            p, pre, h1 {
                color: #03A062;
            }
            div {
                border-style: solid;
                border-width: 2px;
                border-color: #03A062;
                justify-content: center;
                display: flex;
            }
            body{ 
                max-width: max-content;
                margin: auto;
            }
        </style>
    </head>

    <body>
        <em><h2 style="color: #03A062;">Delios Solar Panel Web Scraper</h2></em>
      
        <p id="UPDATE"></p>
        
        <?php foreach($data as $key => $value ): ?>
            <table>
                <thead>
                    <tr>
                        <td colspan="3"><h1><?=$key?></h1></td>
                    </tr>
                </thead>
                <tr>
                    <td><strong>Type</strong></td>
                    <td><strong>Value</strong></td>
                    <td><strong>URL</strong></td>
                </tr>
                <?php foreach($value as $row): ?>
                    <tr>
                        <td><p><?=$row[0]?></p></td>
                        
                        <td><p id="<?=$row[0].$row[2]?>"><?=$row[1]?></p></td>
                        <td>
                            <a href="/data.php?type=<?=$row[0]."&machine=".$row[2]?>">
                                <?=$host_url."/data.php?type=".$row[0]."&machine=".$row[2]?>
                            </a>
                        </td>
                    </tr>
                <?php endforeach; ?>

                <!-- Flags -->
                <thead>
                    <tr>
                        <td colspan="3"><h1>Flags</h1></td>
                    </tr>
                </thead>
                <?php foreach($value as $row): ?>
                    <tr>
                        <td><p><?=$row[0]?></p></td>
                        
                        <td><p id="<?=$row[0].$row[2]."flag"?>"><?= (int)$row[1] > 0 ? 1 : 0  ?></p></td>
                        <td>
                            <a href="/data_flag.php?type=<?=$row[0]."&machine=".$row[2]?>">
                                <?=$host_url."/data_flag.php?type=".$row[0]."&machine=".$row[2]?>
                            </a>
                        </td>
                    </tr>
                <?php endforeach; ?>
            </table>
            <br>
            <br>
            <br>
            <br>
            <br>
        <?php endforeach; ?>
        <script src="api_polling.js">  
        </script> 

    </body>
</html>
