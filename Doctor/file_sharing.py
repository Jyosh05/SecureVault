from flask import Blueprint, request, jsonify, session, render_template, flash, send_file, redirect, url_for
from Utils.general_utils import temp_file_sharing_upload, mydb
from Utils.file_sharing_utils import convert_pdf_to_image_pdf
from Utils.rbac_utils import *
import os

share_file_bp = Blueprint('share_file', __name__, template_folder='templates')


@share_file_bp.route('/share/<int:file_id>', methods=['GET', 'POST'])
@roles_required('doctor')
def share_file(file_id):
    if 'user_id' not in session:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('login.login'))  # Redirect to login page if not logged in

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
        mycursor.execute("SELECT ID, Role FROM user WHERE Username = %s", (shared_with_username,))
        user_record = mycursor.fetchone()

        if not user_record:
            flash('User not found.', 'error')
            return redirect(url_for('share_file.share_file', file_id=file_id))

        shared_with_user_id = user_record['ID']
        role = user_record['Role']

        if role == 'patient':

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

        elif role == 'doctor':
            flash("Files can only be permanently shared with patients only. To share with doctors, please use temporary sharing")

        else:
            flash("User does not exist. Try another username or try again later.")

    return render_template('Doctor/share_file.html', file_id=file_id, file_name=file_name)

@share_file_bp.route('/view_shared_files', methods=['GET'])
@roles_required('patient')
def view_shared_files():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    user_role = session.get('role')  # Assuming role is stored in session

    mycursor = mydb.cursor(dictionary=True)

    if user_role == 'patient':
        mycursor.execute("""
            SELECT fs.Share_ID, f.Title, f.Deleted_At, fs.Converted_File_Path, fs.Date_Shared, u.Username AS Shared_By, fs.Has_Downloaded 
            FROM file_sharing fs
            JOIN file f ON fs.File_ID = f.ID
            JOIN user u ON fs.Shared_By_User_ID = u.ID
            WHERE fs.Shared_With_User_ID = %s
            AND f.Deleted_At IS NULL
        """, (user_id,))
        files = mycursor.fetchall()
        return render_template('User_files/all_shared_files.html', share_files=files)

    else:
        return jsonify({'error': 'Invalid role'}), 403

@share_file_bp.route('/download_file/<int:share_id>', methods=['GET'])
@roles_required('patient')
def download_file(share_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']

    mycursor = mydb.cursor(dictionary=True)

    # Retrieve the sharing record based on Share_ID
    mycursor.execute("""
        SELECT fs.File_ID, fs.Converted_File_Path, fs.Has_Downloaded
        FROM file_sharing fs
        WHERE fs.Share_ID = %s AND fs.Shared_With_User_ID = %s
    """, (share_id, user_id))

    file_record = mycursor.fetchone()

    if file_record:
        converted_file_path = file_record['Converted_File_Path']
        has_downloaded = file_record['Has_Downloaded']

        # If the file hasn't been downloaded yet, proceed with the download
        if not has_downloaded:
            if converted_file_path and os.path.exists(converted_file_path):
                # Update the 'has_downloaded' field to TRUE
                mycursor.execute("""
                    UPDATE file_sharing
                    SET has_downloaded = TRUE
                    WHERE Share_ID = %s
                """, (share_id,))
                mydb.commit()

                # Serve the file for download
                return send_file(converted_file_path, as_attachment=True)

            else:
                return "File not found.", 404
        else:
            return jsonify({"error": "You have already downloaded this file."}), 400
    else:
        return jsonify({"error": "Unauthorized or invalid share ID."}), 403
