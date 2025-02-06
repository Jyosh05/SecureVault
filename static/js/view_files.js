function toggleMenu(fileId) {
    // Toggle the visibility of the menu
    const menu = document.getElementById('menu-' + fileId);
    if (menu.style.display === 'none') {
        menu.style.display = 'block';
    } else {
        menu.style.display = 'none';
    }
}

function deleteFile(fileId) {
    if (confirm("Are you sure you want to delete this file?")) {
        $.ajax({
            url: '/delete/' + fileId, // Assuming your delete route is mapped to /delete/<file_id>
            type: 'POST',
            success: function(response) {
                alert(response.message);
                location.reload(); // Refresh the page after deletion
            },
            error: function(error) {
                alert('Error: ' + error.responseJSON.error);
            }
        });
    }
}
