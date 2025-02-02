from Utils.general_utils import make_dir_for_temp_upload, allowed_file, is_file_size_valid
from Utils.rbac_utils import roles_required
from Utils.general_utils import *
from flask import Blueprint, request, render_template, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
from Utils.malware_scan import *
from Utils.file_integrity import *
import requests
import os
from config import VIRUSTOTAL_API_KEY


# File Upload Blueprint
upload_bp = Blueprint('file', __name__, template_folder='templates')

UPLOAD_FOLDER = 'Files/Perma'  # Adjust this to your upload directory
BASE_UPLOAD_FOLDER = "Files/Perma"

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@upload_bp.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Ensure user is logged in
        if 'user_id' not in session:
            flash("Please log in to upload files.", 'error')
            return redirect(url_for('login.login'))

        user_id = session['user_id']
        file = request.files.get('file')
        title = request.form.get('title')
        description = request.form.get('description')
        file_classification = request.form.get('file_classification')

        # Validate file input
        if not file or not allowed_file(file.filename):
            flash("Invalid file type or no file uploaded.", 'error')
            return redirect(request.url)

        if not is_file_size_valid(file):
            flash("File exceeds the maximum size limit.", 'error')
            return redirect(request.url)

        # Create user-specific folder if it doesn't exist
        user_folder = os.path.join(BASE_UPLOAD_FOLDER, str(user_id))
        os.makedirs(user_folder, exist_ok=True)

        # Save file with a secure filename
        filename = secure_filename(file.filename)
        file_path = os.path.join(user_folder, filename)
        file.save(file_path)

        # Scan the file for malware
        scan_result = scan_file_virustotal(file_path)
        if "Scan ID" not in scan_result:
            flash(f"File rejected due to security concerns: {scan_result}", 'error')
            os.remove(file_path)  # Delete the file if it’s flagged
            return redirect(request.url)

        # Generate a hash for the uploaded file
        file_hash = generate_file_hash(file_path)

        # Store file metadata in the database
        try:
            mycursor = mydb.cursor()
            query = """
                INSERT INTO file (User_ID, File_Name, File_Path, File_Size, File_Hash, File_Classification, Title, Description, File_Type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            mycursor.execute(query, (user_id, filename, file_path, os.path.getsize(file_path), file_hash, file_classification, title, description, filename.rsplit('.', 1)[1]))
            mydb.commit()
            flash("File uploaded successfully!", 'success')
        except Exception as e:
            flash(f"Error uploading file: {e}", 'error')
            return redirect(request.url)

        return redirect(url_for('file.upload_file'))

    return render_template('Features/upload.html')  # Render the upload form template


def scan_file():
    """Handle file scanning with VirusTotal"""
    file = request.files.get('file')

    if not file:
        return jsonify({"error": "No file provided"}), 400

    url = "https://www.virustotal.com/api/v3/files"
    headers = {"x-apikey": VIRUSTOTAL_API_KEY}

    try:
        files = {"file": file}
        response = requests.post(url, headers=headers, files=files)

        if response.status_code == 200:
            result = response.json()
            return jsonify(result)
        else:
            return jsonify({"error": "Error with VirusTotal API"}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500