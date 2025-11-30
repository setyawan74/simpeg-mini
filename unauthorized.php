<?php
session_start();
?>
<!DOCTYPE html>
<html>
<head>
    <title>Akses Ditolak</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f8f9fa;
            text-align: center;
            padding-top: 100px;
        }
        .card {
            background: #fff;
            border: 1px solid #ddd;
            border-radius: 8px;
            display: inline-block;
            padding: 30px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }
        h1 {
            color: #dc3545;
        }
        a {
            display: inline-block;
            margin-top: 20px;
            padding: 10px 20px;
            background: #007bff;
            color: #fff;
            text-decoration: none;
            border-radius: 5px;
        }
        a:hover {
            background: #0056b3;
        }
    </style>
</head>
<body>
    <div class="card">
        <h1>Akses Ditolak</h1>
        <p>Anda tidak memiliki hak untuk membuka halaman ini.</p>
        <a href="dashboard.php">Kembali ke Dashboard</a>
    </div>
</body>
</html>
