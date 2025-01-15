from flask import Blueprint, render_template, session, flash, redirect, url_for, send_from_directory, send_file, jsonify, request
from Utils.rbac_utils import roles_required
from Utils.general_utils import *
import secrets
from datetime import datetime, timedelta


temporary_sharing_downloads_bp = Blueprint('generate_link', __name__, template_folder='templates')
access_temporary_file_bp = Blueprint('access_sharing', __name__, template_folder='templates')
access_temporary_file_see_bp = Blueprint('access_sharing_view', __name__, template_folder='templates')
@temporary_sharing_downloads_bp.route('/generate-link/<int:file_id>', methods=['GET', 'POST'])
def generate_link(file_id):
    if 'user_id' not in session:
        flash("Please log in to view your files.", 'error')
        return redirect(url_for('login.login'))

    user_id = session['user_id']  # Get the logged-in user's ID

    if request.method == 'POST':
        # Get the form data
        duration_value = int(request.form['duration'])
        duration_unit = request.form['duration_unit']
        privilege = request.form['privilege']

        # Calculate the expiration date based on the duration
        if duration_unit == 'minutes':
            expiration_time = datetime.utcnow() + timedelta(minutes=duration_value)
        elif duration_unit == 'hours':
            expiration_time = datetime.utcnow() + timedelta(hours=duration_value)

        # Generate a unique sharing link using secrets
        token = secrets.token_urlsafe(16)

        # Insert the link details into the database
        mycursor = mydb.cursor()
        mycursor.execute("""
            INSERT INTO temp_file_sharing (File_ID, Sharing_Link, Duration, Privilege, Expired)
            VALUES (%s, %s, %s, %s, %s)
        """, (file_id, token, expiration_time, privilege, False))
        mydb.commit()

        flash(f"Link generated successfully! Share this link: {url_for('access_sharing.access_shared_file', token=token, _external=True)}", 'success')
        # return redirect(url_for('view_files.view_files'))

    return render_template('Features/generate_link.html', file_id=file_id)

@access_temporary_file_bp.route('/shared-file/<token>', methods=['GET', 'POST'])
def access_shared_file(token):
    mycursor = mydb.cursor(dictionary=True)

    # Retrieve the sharing link data to verify expiration, token validity, and privilege
    mycursor.execute("""
        SELECT File_ID, Duration, Expired, Privilege FROM temp_file_sharing
        WHERE Sharing_Link = %s
    """, (token,))
    result = mycursor.fetchone()

    if result:
        file_id = result['File_ID']
        expiration_time = result['Duration']
        expired = result['Expired']
        privilege = result['Privilege']

        current_time = datetime.utcnow()

        if expired:
            # If expired is True, show the message
            return "This sharing link has expired.", 403
        elif expiration_time > current_time:
            # Retrieve the file details from the 'file' table
            mycursor.execute("SELECT * FROM file WHERE ID = %s", (file_id,))
            file_details = mycursor.fetchone()

            # Check if the user has the required privilege to view/download the file
            if privilege == 'r':
                # If the privilege is 'r' (read), show the file
                return render_template('Features/shared_file.html', file=file_details, privilege=privilege)
            elif privilege == 'd':
                # If privilege is 'd', allow downloading the file
                file_path = file_details['File_Path']
                file_name = file_details['File_Name']

                # Ensure the file exists at the given path
                if os.path.exists(file_path):
                    return send_file(file_path, as_attachment=True, download_name=file_name)
                else:
                    return "File not found on the server.", 404
            else:
                return "You do not have permission to access this file.", 403
        else:
            # Mark the link as expired if it's past the expiration time
            mycursor.execute("""
                UPDATE temp_file_sharing SET Expired = TRUE WHERE Sharing_Link = %s
            """, (token,))
            mydb.commit()
            return "This sharing link has expired.", 403
    else:
        return "Invalid or expired link.", 404

@access_temporary_file_see_bp.route('/serve-file/<int:file_id>', methods=['GET'])
def serve_file(file_id):
    mycursor = mydb.cursor(dictionary=True)

    # Retrieve the file path from the database using file_id
    mycursor.execute("SELECT File_Path FROM file WHERE ID = %s", (file_id,))
    result = mycursor.fetchone()

    if result:
        file_path = result['File_Path']

        # Verify the file exists
        if os.path.exists(file_path):
            return send_file(file_path)
        else:
            return "File not found on the server.", 404
    else:
        return "Invalid file ID.", 404
