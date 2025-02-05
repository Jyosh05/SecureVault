# from flask import Blueprint, request, abort, jsonify, session, render_template, flash, redirect, url_for, send_file
# from Utils.general_utils import temp_file_sharing_upload, mydb
# from Utils.file_sharing_utils import convert_pdf_to_image_pdf
# import os
#
# view_pdf_bp = Blueprint('view_pdf', __name__, template_folder='templates')
#
#
# @view_pdf_bp.route('/view_pdf/<int:file_id>', methods=['GET', 'POST'])
# def view_pdf(file_id):
#     if 'user_id' not in session:
#         return jsonify({'error': 'Unauthorized'}), 401
#
#     user_id = session['user_id']
#     user_role = session.get('role')
#
#     mycursor = mydb.cursor(dictionary=True)
#
#     # Get file details for the specific file_id
#     mycursor.execute("""
#         SELECT f.ID, f.Title, fs.Converted_File_Path, fs.File_ID, fs.Has_Downloaded, fs.Date_Shared, u.Username AS Shared_By
#         FROM file_sharing fs
#         JOIN file f ON fs.File_ID = f.ID
#         JOIN user u ON fs.Shared_By_User_ID = u.ID
#         WHERE fs.File_ID = %s AND fs.Shared_With_User_ID = %s
#     """, (file_id, user_id))
#     file_details = mycursor.fetchone()
#
#     if not file_details:
#         abort(404, "File not found or you don't have permission to view it.")
#
#     # Check if the download button should be shown for the patient
#     download_allowed = False
#     if user_role == 'patient' and not file_details['Has_Downloaded']:
#         download_allowed = True  # Only allow download if not already downloaded
#
#     # Serve the PDF file
#     converted_file_path = file_details['Converted_File_Path']
#
#     # Check if the file exists on the server
#     if not converted_file_path or not os.path.exists(converted_file_path):
#         abort(404, "File not found on the server.")
#
#     # Handle the POST request for downloading (only for patient)
#     if request.method == 'POST' and user_role == 'patient' and download_allowed:
#         # Update the "Downloaded" column to True when the patient actually downloads the file
#         mycursor.execute("""
#             UPDATE file_sharing
#             SET Has_Downloaded = TRUE
#             WHERE File_ID = %s AND Shared_With_User_ID = %s
#         """, (file_id, user_id))
#         mydb.commit()
#         # Return the file for download
#         return send_file(converted_file_path, as_attachment=True)
#
#     # Render different templates for doctor and patient views
#     if user_role == 'doctor':
#         # Doctor can only view the PDF (no download option)
#         return render_template('Doctor/view_each_pdf.html', file=file_details, user_role=user_role)
#
#     elif user_role == 'patient':
#         # Patient can view the PDF and possibly download it
#         return render_template('User_file/view_each_pdf.html', file=file_details, download_allowed=download_allowed,
#                                user_role=user_role)
#
#     return jsonify({'error': 'Invalid role'}), 403
