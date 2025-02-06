<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Recycle Bin</title>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
</head>
<body>
    <h1>Recycle Bin</h1>

    <table border="1">
        <thead>
            <tr>
                <th>File Name</th>
                <th>File Path</th>
                <th>Expiry Date</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for file in soft_deleted_files %}
                <tr>
                    <td>{{ file.File_Path.split('/')[-1] }}</td>
                    <td>{{ file.File_Path }}</td>
                    <td>{{ file.Expiry_Date }}</td>
                    <td>
                        <button class="restore-btn" data-id="{{ file.File_ID }}">Restore</button>
                        <button class="delete-btn" data-id="{{ file.File_ID }}">Permanently Delete</button>
                    </td>
                </tr>
            {% endfor %}
        </tbody>
    </table>

    <script>
        $(document).ready(function() {
            // Handle Restore action
            $('.restore-btn').on('click', function() {
                var fileId = $(this).data('id');
                $.ajax({
                    url: '/restore/' + fileId,
                    type: 'POST',
                    success: function(response) {
                        alert(response.message);
                        location.reload(); // Refresh the page to reflect changes
                    },
                    error: function(error) {
                        alert('Error: ' + error.responseJSON.error);
                    }
                });
            });

            // Handle Permanent Delete action
            $('.delete-btn').on('click', function() {
                var fileId = $(this).data('id');
                $.ajax({
                    url: '/hard_delete/' + fileId,
                    type: 'POST',
                    success: function(response) {
                        alert(response.message);
                        location.reload(); // Refresh the page to reflect changes
                    },
                    error: function(error) {
                        alert('Error: ' + error.responseJSON.error);
                    }
                });
            });
        });
    </script>
</body>
</html>
