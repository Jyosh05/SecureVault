from flask import Blueprint, request, jsonify, session, render_template, flash, send_file, redirect, url_for
from Utils.general_utils import mydb
from Utils.file_sharing_utils import convert_pdf_to_image_pdf
from Utils.rbac_utils import *
import os
from datetime import datetime, timedelta


doc_share_bp = Blueprint('doc_share', __name__, template_folder='templates')
UPLOAD_FOLDER = 'Files/Sharing'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@doc_share_bp.route('/share-doc/<int:file_id>', methods=['GET', 'POST'])
@roles_required('doctor')
def share_file_doc(file_id):
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
        duration_value = int(request.form['duration'])
        duration_unit = request.form['duration_unit']

        if not shared_with_username:
            flash('Username is required.', 'error')
            return redirect(url_for('share_file.share_file', file_id=file_id))

        # Convert the duration to days (the integer to store in the database)
        if duration_unit == 'hours':
            duration_in_days = int(duration_value) * 60  # Convert hours to days
        else:
            duration_in_days = int(duration_value)   # Convert minutes to days


        # Get recipient user ID
        mycursor.execute("SELECT ID, Role FROM user WHERE Username = %s", (shared_with_username,))
        user_record = mycursor.fetchone()

        if not user_record:
            flash('User not found.', 'error')
            return redirect(url_for('doc_share.share_file_doc', file_id=file_id))

        shared_with_user_id = user_record['ID']
        role = user_record['Role']

        if role == 'doctor':
            if shared_with_user_id == session['user_id']:
                flash("File cannot be shared with yourself")
            else:
                mycursor.execute("SELECT Share_ID FROM doc_sharing WHERE File_ID = %s AND Shared_With_User_ID = %s", (file_id, shared_with_user_id,))
                check_shared_files = mycursor.fetchall()
                if check_shared_files:
                     flash("This file has already been shared with doctor")
                else:

                    # Convert PDF at the time of sharing
                    upload_folder = UPLOAD_FOLDER
                    converted_file_path = convert_pdf_to_image_pdf(original_file_path, upload_folder)

                    # Insert into file_sharing table
                    mycursor.execute("""
                        INSERT INTO doc_sharing (File_ID, Converted_File_Path, Shared_By_User_ID, Shared_With_User_ID, Duration)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (file_id, converted_file_path, session['user_id'], shared_with_user_id, duration_in_days))
                    mydb.commit()

                    flash('File shared successfully!', 'success')
                    return redirect(url_for('view_files.view_files'))

        elif role == 'patient':
            flash("Files can only be temporarily shared with doctors only. To share with patients, please use permanent sharing")

        else:
            flash("User does not exist. Try another username or try again later.")

    return render_template('Doctor/doc_share_file.html', file_id=file_id, file_name=file_name)


@doc_share_bp.route('/view_shared_doc_files', methods=['GET'])
@roles_required('doctor')
def view_doc_shared_files():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    user_role = session.get('role')

    mycursor = mydb.cursor(dictionary=True)

    if user_role == 'doctor':
        # Get the current date
        current_date = datetime.now()

        # Fetch the files shared with the doctor
        mycursor.execute("""
            SELECT ds.Share_ID, f.Title, f.Deleted_At, ds.Converted_File_Path, ds.Date_Shared, u.Username AS Shared_By, ds.Duration
            FROM doc_sharing ds
            JOIN file f ON ds.File_ID = f.ID
            JOIN user u ON ds.Shared_By_User_ID = u.ID
            WHERE ds.Shared_With_User_ID = %s
            AND f.Deleted_At IS NULL
            AND f.File_Modified IS FALSE
        """, (user_id,))

        files = mycursor.fetchall()

        for file in files:
            # Check if Duration is stored in minutes, hours, or days
            # If Duration is in minutes (as an integer), convert to timedelta (in minutes)
            expiration_date = file['Date_Shared']

            if file['Duration'] is not None:
                # If Duration is in minutes, convert it to timedelta
                duration_in_minutes = file['Duration']
                duration_timedelta = timedelta(minutes=duration_in_minutes)
                expiration_date = expiration_date + duration_timedelta

            file['Expiration_Date'] = expiration_date

        return render_template('Doctor/all_shared_files.html', share_files=files, current_date=current_date)

    else:
        return jsonify({'error': 'Invalid role'}), 403

@doc_share_bp.route('/view_perma_doc_share', methods=['GET', 'POST'])
@roles_required('doctor')
def view_perma_doc_share():
    if 'user_id' not in session:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('login.login'))  # Redirect to login page if not logged in

    user_id = session['user_id']


    mycursor = mydb.cursor(dictionary=True)

    # Retrieve the sharing record based on Share_ID
    mycursor.execute("""
                SELECT f.Title, ds.Share_ID, ds.File_ID, ds.Date_Shared, ds.Duration, u.Username AS Shared_With
                FROM doc_sharing ds
                JOIN file f ON ds.File_ID = f.ID
                JOIN user u ON ds.Shared_With_User_ID = u.ID
                WHERE ds.Shared_By_User_ID = %s
                AND f.Deleted_At IS NULL
                AND f.File_Modified IS FALSE 
            """, (user_id,))
    all_shared_files = mycursor.fetchall()

    current_time = datetime.now()
    for file in all_shared_files:
        # Assuming the duration is stored in minutes
        expiry_time = file['Date_Shared'] + timedelta(minutes=file['Duration'])
        file['is_expired'] = expiry_time < current_time

    return render_template("Doctor/doc_share_view.html", shared_files = all_shared_files)


@doc_share_bp.route('/revoke_perma_doc_sharing/<int:share_id>', methods=['GET', 'POST'])
@roles_required('doctor')
def revoke_perma_doc_sharing(share_id):
    if 'user_id' not in session:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('login.login'))  # Redirect to login page if not logged in

    mycursor = mydb.cursor(dictionary=True)

    # Retrieve the sharing record based on Share_ID
    mycursor.execute("SELECT * FROM doc_sharing WHERE Share_ID = %s", (share_id,))
    delete_share = mycursor.fetchone()

    if not delete_share:
        return jsonify({"error": "Sharing not found"}), 404

    # Get the file path to the converted file
    converted_file_path = delete_share['Converted_File_Path']

    # Delete the file from the filesystem if it exists
    if converted_file_path and os.path.exists(converted_file_path):
        try:
            os.remove(converted_file_path)  # Delete the file from the OS
        except Exception as e:
            flash(f"Error deleting the file: {e}", 'error')
            return redirect(url_for('doc_share.view_perma_doc_share'))

    mycursor.execute("DELETE FROM doc_sharing WHERE Share_ID = %s", (share_id,))
    mydb.commit()


    flash("File shared Permanently Deleted.", 'success')  # Flash message on success
    return redirect(url_for('doc_share.view_perma_doc_share'))

@doc_share_bp.route('/update_doc_share/<int:share_id>', methods=['GET', 'POST'])
@roles_required('doctor')
def update_doc_share(share_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    mycursor = mydb.cursor(dictionary=True)

    # Retrieve the sharing record based on Share_ID
    mycursor.execute("SELECT * FROM doc_sharing WHERE Share_ID = %s", (share_id,))
    update_share = mycursor.fetchone()

    if not update_share:
        return jsonify({"error": "Sharing not found"}), 404

    # Check if the current user is the one who shared the file
    if update_share['Shared_By_User_ID'] != user_id:
        return jsonify({'error': 'Unauthorized access to this sharing record'}), 403

    if request.method == 'POST':
        # Get the new duration from the form input
        duration_value = int(request.form['duration'])
        duration_unit = request.form['duration_unit']

        # Convert the duration to days (the integer to store in the database)
        if duration_unit == 'hours':
            duration_in_days = int(duration_value) * 60  # Convert hours to days
        else:
            duration_in_days = int(duration_value)  # Convert minutes to days

        # Validate new duration input (ensure it's a positive integer)
        try:
            new_duration = int(duration_in_days)
            if new_duration <= 0:
                flash('Duration must be a positive integer.', 'error')
                return redirect(url_for('doc_share.update_doc_share', share_id=share_id))
        except ValueError:
            flash('Invalid duration value.', 'error')
            return redirect(url_for('doc_share.update_doc_share', share_id=share_id))

        # Update the Duration in the database
        mycursor.execute("""
            UPDATE doc_sharing 
            SET Duration = %s 
            WHERE Share_ID = %s
        """, (new_duration, share_id))
        mydb.commit()

        flash('File sharing duration updated successfully!', 'success')
        return redirect(url_for('doc_share.view_perma_doc_share'))

    # For GET request, render the form with current duration
    return render_template("Doctor/update_doc_share.html", share=update_share)



@doc_share_bp.route('/shared-doc-file/<int:share_id>', methods=['GET', 'POST'])
@roles_required('doctor')
def view_each_doc_pdf(share_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    mycursor = mydb.cursor(dictionary=True)

    # Retrieve the sharing record based on Share_ID
    mycursor.execute("""
        SELECT ds.File_ID, ds.Converted_File_Path, ds.Date_Shared, f.Title 
        FROM doc_sharing ds
        JOIN file f ON ds.File_ID = f.ID
        WHERE ds.Share_ID = %s
    """, (share_id,))

    result = mycursor.fetchone()
    if result is None:
        return "File sharing record not found.", 404

    file_id = result['File_ID']
    converted_file_path = result['Converted_File_Path']
    file_title = result['Title']
    date_shared = result['Date_Shared']

    # Ensure the file path is properly formatted for access by PDF.js
    converted_file_path = converted_file_path.replace("\\", "/")  # Handle OS-specific file path issues

    # Check if the converted file exists and render the template with PDF.js
    if converted_file_path and os.path.exists(converted_file_path):
        # Pass the file path to the template so it can be used by PDF.js
        pdf_url = url_for('doc_share.serve_file_doc', file_id=file_id)  # Dynamically generate the URL for the file
        return render_template('Doctor/view_each_doc_pdf.html', file_title=file_title,
                               pdf_url=pdf_url, date_shared=date_shared)
    else:
        return "Converted file not found on the server.", 404



@doc_share_bp.route('/serve-doc-file/<int:file_id>', methods=['GET'])
@roles_required('doctor')
def serve_file_doc(file_id):
    mycursor = mydb.cursor(dictionary=True, buffered=True)

    # Retrieve the converted file path from the 'file_sharing' table using file_id
    mycursor.execute("""
        SELECT Converted_File_Path FROM doc_sharing WHERE File_ID = %s
    """, (file_id,))
    result = mycursor.fetchone()

    if result:
        converted_file_path = result['Converted_File_Path']

        if converted_file_path and os.path.exists(converted_file_path):
            # Serve the converted file if it exists
            return send_file(converted_file_path, as_attachment=False)  # No attachment; serves directly
        else:
            return "File not found on the server.", 404
    else:
        return "Invalid file ID.", 404
