from flask import Blueprint, render_template, session, flash, redirect, url_for
from Utils.rbac_utils import roles_required
from Utils.general_utils import *
from Utils.file_integrity import check_file_integrity
from Utils.logging_utils import log_this

UPLOAD_FOLDER = 'Files/Perma'
view_files_bp = Blueprint('view_files', __name__, template_folder='templates')

@view_files_bp.route('/view', methods=['GET'])
@roles_required('doctor')
def view_files():
    if 'user_id' not in session:
        flash("Please log in to view your files.", 'error')
        return redirect(url_for('login.login'))

    user_id = session['user_id']

    try:
        mycursor = mydb.cursor(dictionary=True)

        # Retrieve username
        mycursor.execute("SELECT Username FROM user WHERE ID = %s", (user_id,))
        user = mycursor.fetchone()
        username = user['Username'] if user else "Unknown User"

        # Query to fetch file details
        query = """
            SELECT ID, Title, File_Type, File_Path, Uploaded_At 
            FROM file
            WHERE User_ID = %s
            ORDER BY Uploaded_At DESC
        """
        mycursor.execute(query, (user_id,))
        files = mycursor.fetchall()

        print(f"Files Retrieved from DB: {files}")  # Debugging print

        file_details = []
        for file in files:
            file_id = file['ID']
            file_path = file['File_Path']

            try:
                integrity_status = check_file_integrity(file_id)
            except Exception as e:
                integrity_status = f"Error checking integrity: {e}"

            print(f"File ID: {file_id}, Title: {file['Title']}, Status: {integrity_status}")  # Debugging print

            file_details.append({
                'id': file_id,
                'title': file['Title'],
                'file_type': file['File_Type'],
                'file_path': file_path,
                'uploaded_at': file['Uploaded_At'],
                'integrity_status': integrity_status
            })
        log_this('User is viewing file')
        return render_template('Doctor/view_files.html', username=username, files=file_details)

    except Exception as e:
        print(f"Error in view_files: {e}")  # Debugging print
        flash(f"Error retrieving files: {e}", 'error')
        return render_template('Doctor/view_files.html', files=[])

