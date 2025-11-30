<?php
include 'includes/guard.php';

// Halaman ini hanya boleh diakses oleh Admin
requireRoles(['admin']);
?>
<!DOCTYPE html>
<html>
<head>
    <title>Backup & Restore</title>
</head>
<body>
    <h1>Backup & Restore Data</h1>
    <p>Hanya Admin yang bisa melakukan backup & restore.</p>
</body>
</html>
