from flask import Blueprint, render_template, session, flash, redirect, url_for
from Utils.rbac_utils import roles_required
from Utils.general_utils import *
from Utils.file_integrity import check_file_integrity

# Path to the upload folder
UPLOAD_FOLDER = 'uploads/'
view_files_bp = Blueprint('view_files', __name__, template_folder='templates')

@view_files_bp.route('/view', methods=['GET'])
def view_files():
    if 'user_id' not in session:
        flash("Please log in to view your files.", 'error')
        return redirect(url_for('login.login'))

    user_id = session['user_id']  # Get the logged-in user's ID

    try:
        mycursor = mydb.cursor(dictionary=True)

        # Retrieve the user's name
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

        # Check integrity for each file
        file_details = []
        for file in files:
            file_id = file['ID']
            file_path = file['File_Path']

            # Check file integrity
            integrity_status = check_file_integrity(file_id)

            # Append file details and integrity status
            file_details.append({
                'id': file_id,
                'title': file['Title'],
                'file_type': file['File_Type'],
                'file_path': file_path,
                'uploaded_at': file['Uploaded_At'],
                'integrity_status': integrity_status
            })

        # If files exist, render them in the template
        return render_template('User_files/view_files.html', username=username, files=files)

    except Exception as e:
        flash(f"Error retrieving files: {e}", 'error')
        return render_template('User_files/view_files.html', files=[])

