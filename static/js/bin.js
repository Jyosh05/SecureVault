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

    // Handle Permanent Delete action with confirmation prompt
    $('.delete-form').on('submit', function(event) {
        event.preventDefault(); // Prevent form submission

        var fileId = $(this).find('.delete-btn').data('id'); // Get fileId from the button's data-id attribute

        if (confirm("Are you sure you want to permanently delete this file? This action cannot be undone.")) {
            // Proceed with AJAX request if confirmed
            $.ajax({
                url: '/hard_delete/' + fileId,
                type: 'POST',
                success: function(response) {
                    alert("File successfully deleted.");
                    location.reload(); // Refresh the page to reflect changes
                },
                error: function(error) {
                    alert('Error: ' + error.responseJSON.error);
                }
            });
        }
    });
});

$(document).ready(function() {
    // Check for any flash messages
    {% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
        {% for category, message in messages %}
            // Display the flash message (could be a toast, alert, etc.)
            alert(message); // Simple alert for demonstration
        {% endfor %}
    {% endif %}
    {% endwith %}
});

