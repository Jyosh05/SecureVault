$(document).ready(function() {
    $('#upload-form').submit(function(event) {
        event.preventDefault(); // Prevent default form submission

        const fileInput = $('#file')[0];
        if (fileInput.files.length === 0) {
            alert("No file selected.");
            return;
        }

        const file = fileInput.files[0];

        // Check file safety using backend route
        checkFileSafety(file);
    });

    function checkFileSafety(file) {
        const formData = new FormData();
        formData.append('file', file);

        $.ajax({
            url: '/scan_file',  // Use the Flask route for scanning
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                if (response.data && response.data.attributes.last_analysis_stats.malicious > 0) {
                    $('#message').text("This file is detected as malicious! Please upload a different file.");
                    $('#message').css('color', 'red');
                } else {
                    $('#message').text("File is safe. Proceeding with the upload.");
                    $('#message').css('color', 'green');
                    // Proceed with form submission if the file is safe
                    $('#upload-form')[0].submit();
                }
            },
            error: function() {
                $('#message').text("Error checking file safety.");
                $('#message').css('color', 'red');
            }
        });
    }
});

document.getElementById("back-btn").addEventListener("click", function() {
    window.location.href = "view_files.html"; // Replace with your target page URL
});
