from flask import Blueprint, render_template, session, flash, redirect, url_for, send_from_directory, send_file
from Utils.rbac_utils import roles_required
from Utils.general_utils import *



UPLOAD_FOLDER = 'uploads/'  # Path to the upload folder
view_files_bp = Blueprint('view_files', __name__, template_folder='templates')


@view_files_bp.route('/view', methods=['GET'])
def view_files():
    if 'user_id' not in session:
        flash("Please log in to view your files.", 'error')
        return redirect(url_for('login.login'))

    user_id = session['user_id']  # Get the logged-in user's ID

    try:
        mycursor = mydb.cursor(dictionary=True)
        query = """
            SELECT ID, Title, File_Type, File_Path, Uploaded_At 
            FROM file
            WHERE User_ID = %s
            ORDER BY Uploaded_At DESC
        """
        mycursor.execute(query, (user_id,))
        files = mycursor.fetchall()
        return render_template('User_files/view_files.html', files=files)
    except Exception as e:
        flash(f"Error retrieving files: {e}", 'error')
        return render_template('User_files/view_files.html', files=[])


