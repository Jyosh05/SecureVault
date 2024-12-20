from Utils.general_utils import make_dir_for_temp_upload, allowed_file, is_file_size_valid
from Utils.rbac_utils import roles_required
from Utils.general_utils import *
from flask import Blueprint, request, render_template, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
import os
import hashlib
import datetime

# File Upload Blueprint
upload_bp = Blueprint('file', __name__, template_folder='templates')

UPLOAD_FOLDER = 'Files/Perma'  # Adjust this to your upload directory

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Function to generate a file hash
def generate_file_hash(filepath):
    """
    Generate a SHA-256 hash for a file.
    """
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

@upload_bp.route('/upload', methods=['GET', 'POST'])
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

        if not title or not description:
            flash("Title and description are required.", 'error')
            return redirect(request.url)

        if not is_file_size_valid(file):
            flash("File exceeds maximum allowed size of 5 MB.", 'error')
            return redirect(request.url)

        # Save the file
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        # Generate file hash
        file_hash = generate_file_hash(file_path)

        # File metadata
        file_size = os.path.getsize(file_path)
        file_type = os.path.splitext(filename)[1][1:]  # Extract file extension without the dot

        # Store metadata in the database
        try:
            mycursor = mydb.cursor()
            query = """
                INSERT INTO file (User_ID, File_Name, File_Path, File_Size, File_Hash, File_Classification, Title, Description, File_Type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            mycursor.execute(query, (user_id, filename, file_path, file_size, file_hash, file_classification, title, description, file_type))
            mydb.commit()
            flash("File uploaded successfully!", 'success')
        except Exception as e:
            flash(f"Error uploading file: {e}", 'error')
            return redirect(request.url)

        return redirect(url_for('file.upload_file'))

    return render_template('features/upload.html')
