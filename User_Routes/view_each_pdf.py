from flask import Blueprint, request, abort, jsonify, session, render_template, flash, redirect, send_from_directory, url_for, send_file
from Utils.file_sharing_utils import convert_pdf_to_image_pdf
from Utils.rbac_utils import *
import os

view_pdf_bp = Blueprint('view_pdf', __name__, template_folder='templates')


@view_pdf_bp.route('/shared-file/<int:share_id>', methods=['GET', 'POST'])
@roles_required('patient')
def view_each_pdf(share_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    mycursor = mydb.cursor(dictionary=True)

    # Retrieve the sharing record based on Share_ID
    mycursor.execute("""
        SELECT fs.File_ID, fs.Converted_File_Path, fs.Date_Shared, f.Title 
        FROM file_sharing fs
        JOIN file f ON fs.File_ID = f.ID
        WHERE fs.Share_ID = %s
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
        print(f"this is the file retrieved {converted_file_path}")
        # Pass the file path to the template so it can be used by PDF.js
        pdf_url = url_for('view_pdf.serve_file', file_id=file_id)  # Dynamically generate the URL for the file
        return render_template('User_files/view_each_pdf.html', file_title=file_title,
                               pdf_url=pdf_url, date_shared=date_shared)
    else:
        return "Converted file not found on the server.", 404


from flask import send_file

@view_pdf_bp.route('/serve-file/<int:file_id>', methods=['GET'])
@roles_required('patient')
def serve_file(file_id):
    mycursor = mydb.cursor(dictionary=True, buffered=True)

    # Retrieve the converted file path from the 'file_sharing' table using file_id
    mycursor.execute("""
        SELECT Converted_File_Path FROM file_sharing WHERE File_ID = %s
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
