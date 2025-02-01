from Utils.general_utils import make_dir_for_temp_upload, allowed_file, is_file_size_valid
from Utils.rbac_utils import roles_required
from Utils.general_utils import *
from flask import Blueprint, request, render_template, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
from malware_scan import scan_file_virustotal
import os

import datetime

# File Upload Blueprint
upload_bp = Blueprint('file', __name__, template_folder='templates')

UPLOAD_FOLDER = 'Files/Perma'  # Adjust this to your upload directory
BASE_UPLOAD_FOLDER = "Files/Perma"

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@upload_bp.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if 'user_id' not in session:
            flash("Please log in to upload files.", 'error')
            return redirect(url_for('login.login'))

        user_id = session['user_id']
        file = request.files.get('file')
        title = request.form.get('title')
        description = request.form.get('description')
        file_classification = request.form.get('file_classification')

        if not file or not allowed_file(file.filename):
            flash("Invalid file type or no file uploaded.", 'error')
            return redirect(request.url)

        if not is_file_size_valid(file):
            flash("File exceeds maximum size of 5MB.", 'error')
            return redirect(request.url)

        # Ensure user directory exists
        user_folder = os.path.join(BASE_UPLOAD_FOLDER, str(user_id))
        os.makedirs(user_folder, exist_ok=True)

        # Secure filename and save
        filename = secure_filename(file.filename)
        file_path = os.path.join(user_folder, filename)
        file.save(file_path)

        # Scan file for malware
        scan_result = scan_file_virustotal(file_path)
        if "Scan ID" not in scan_result:
            flash(f"File rejected due to security concerns: {scan_result}", 'error')
            os.remove(file_path)  # Delete file if malware detected
            return redirect(request.url)

        # Generate file hash
        file_hash = generate_file_hash(file)

        # Store metadata in the database
        try:
            mycursor = mydb.cursor()
            query = """
                INSERT INTO file (User_ID, File_Name, File_Path, File_Size, File_Hash, File_Classification, Title, Description, File_Type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            mycursor.execute(query, (user_id, filename, file_path, os.path.getsize(file_path), file_hash, file_classification, title, description, file.filename.rsplit('.', 1)[1]))
            mydb.commit()
            flash("File uploaded successfully!", 'success')
        except Exception as e:
            flash(f"Error uploading file: {e}", 'error')
            return redirect(request.url)

        return redirect(url_for('file.upload_file'))