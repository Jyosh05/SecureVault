from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from werkzeug.utils import secure_filename
import datetime

# Blueprint for file upload functionality
file_upload_bp = Blueprint('file', __name__, template_folder='templates')

UPLOAD_FOLDER = 'uploads'  # Single folder for all uploads
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

file_upload_bp.config = {'UPLOAD_FOLDER': UPLOAD_FOLDER}


def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@file_upload_bp.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if 'user_id' not in session:
        flash('Please log in to upload files.', 'error')
        return redirect(url_for('login.login'))

    if request.method == 'POST':
        uploaded_file = request.files.get('file')
        file_classification = request.form.get('classification', 'non-sensitive')  # Default classification

        # Validate the uploaded file
        if not uploaded_file or uploaded_file.filename == '':
            flash('No file selected.', 'error')
            return redirect(url_for('file.upload_file'))

        if not allowed_file(uploaded_file.filename):
            flash('File type not allowed.', 'error')
            return redirect(url_for('file.upload_file'))

        if file_classification not in {'non-sensitive', 'sensitive', 'confidential'}:
            flash('Invalid file classification.', 'error')
            return redirect(url_for('file.upload_file'))

        # Secure the filename and generate a unique identifier
        original_filename = secure_filename(uploaded_file.filename)
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        unique_filename = f"user_{session['user_id']}_{timestamp}_{original_filename}"

        # Save the file to the shared upload folder
        file_path = f"{file_bp.config['UPLOAD_FOLDER']}/{unique_filename}"
        uploaded_file.save(file_path)

        # Save file metadata to the database
        try:
            cursor = mydb.cursor()
            query = """
                INSERT INTO file (User_ID, File_Meta_Data, File_Path, Co_Authors, File_Classification)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                session['user_id'],
                original_filename,  # File_Meta_Data
                file_path,          # File_Path
                0,                  # Co_Authors (default to 0 if no collaborators yet)
                file_classification
            ))
            mydb.commit()
        except Exception as e:
            flash('Error saving file metadata.', 'error')
            print(f"Database Error: {e}")
            return redirect(url_for('file.upload_file'))

        flash('File uploaded successfully!', 'success')
        return redirect(url_for('file.upload_file'))

    return render_template('upload.html')
