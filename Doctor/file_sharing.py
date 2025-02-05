from flask import Blueprint, request, jsonify, session, render_template, flash, redirect, url_for
from Utils.general_utils import temp_file_sharing_upload, mydb
from Utils.file_sharing_utils import convert_pdf_to_image_pdf

share_file_bp = Blueprint('share_file', __name__, template_folder='templates')


@share_file_bp.route('/share/<int:file_id>', methods=['GET', 'POST'])
def share_file(file_id):
    if 'user_id' not in session:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('auth.login'))  # Redirect to login page if not logged in

    mycursor = mydb.cursor(dictionary=True)

    # Retrieve file details (Title & File Path) in a single query
    mycursor.execute("SELECT Title, File_Path FROM file WHERE ID = %s", (file_id,))
    file_record = mycursor.fetchone()

    if not file_record:
        flash('File not found.', 'error')
        return redirect(url_for('view_files'))

    file_name = file_record['Title']
    original_file_path = file_record['File_Path']

    if request.method == 'POST':
        shared_with_username = request.form.get('shared_with_username')

        if not shared_with_username:
            flash('Username is required.', 'error')
            return redirect(url_for('share_file.share_file', file_id=file_id))

        # Get recipient user ID
        mycursor.execute("SELECT ID FROM user WHERE Username = %s", (shared_with_username,))
        user_record = mycursor.fetchone()

        if not user_record:
            flash('User not found.', 'error')
            return redirect(url_for('share_file.share_file', file_id=file_id))

        shared_with_user_id = user_record['ID']

        # Convert PDF at the time of sharing
        upload_folder = temp_file_sharing_upload()
        converted_file_path = convert_pdf_to_image_pdf(original_file_path, upload_folder)

        # Insert into file_sharing table
        mycursor.execute("""
            INSERT INTO file_sharing (File_ID, Converted_File_Path, Shared_By_User_ID, Shared_With_User_ID)
            VALUES (%s, %s, %s, %s)
        """, (file_id, converted_file_path, session['user_id'], shared_with_user_id))
        mydb.commit()

        flash('File shared successfully!', 'success')
        return redirect(url_for('view_files.view_files'))

    return render_template('Doctor/share_file.html', file_id=file_id, file_name=file_name)

@share_file_bp.route('/view_shared_files', methods=['GET'])
def view_shared_files():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    user_role = session.get('role')  # Assuming role is stored in session

    mycursor = mydb.cursor(dictionary=True)

    if user_role == 'doctor':
        mycursor.execute("""
            SELECT f.ID, fs.Share_ID, f.Title, fs.Converted_File_Path, fs.Date_Shared, u.Username AS Shared_By 
            FROM file_sharing fs
            JOIN file f ON fs.File_ID = f.ID
            JOIN user u ON fs.Shared_By_User_ID = u.ID
            WHERE fs.Shared_With_User_ID = %s
        """, (user_id,))
        files = mycursor.fetchall()
        return render_template('Doctor/all_shared_files.html', share_files=files)

    elif user_role == 'patient':
        mycursor.execute("""
            SELECT fs.Share_ID, f.Title, fs.Converted_File_Path, fs.Date_Shared, u.Username AS Shared_By 
            FROM file_sharing fs
            JOIN file f ON fs.File_ID = f.ID
            JOIN user u ON fs.Shared_By_User_ID = u.ID
            WHERE fs.Shared_With_User_ID = %s
        """, (user_id,))
        files = mycursor.fetchall()
        return render_template('User_files/all_shared_files.html', share_files=files)

    else:
        return jsonify({'error': 'Invalid role'}), 403
