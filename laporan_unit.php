<?php
include 'includes/guard.php';

// Halaman ini hanya boleh diakses oleh Admin dan Supervisor
requireRoles(['admin', 'supervisor']);
?>
<!DOCTYPE html>
<html>
<head>
    <title>Laporan Unit</title>
</head>
<body>
    <h1>Laporan Unit</h1>
    <p>Hanya Admin & Supervisor yang bisa melihat halaman ini.</p>
</body>
</html>
