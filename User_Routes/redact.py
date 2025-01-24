import os.path

from flask import Blueprint, render_template,request,send_file,url_for,flash,redirect
from werkzeug.utils import secure_filename
from Utils.general_utils import make_dir_for_temp_upload, allowed_file
from Utils.PDF_Redaction import redact_pdf
from Utils.rbac_utils import roles_required

redact_bp = Blueprint('redact',__name__, template_folder='templates')

@redact_bp.route('/redact')
@roles_required('user')
def redact():
    return render_template('Features/PDF_Redactor.html')

@redact_bp.route('/redact_upload', methods=['POST'])
@roles_required('user')
def redact_upload():
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('redact.redact'))

    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('redact.redact'))

    # Check if the file is allowed and process it
    if not allowed_file(file.filename):
        flash('Unsupported file type. Please upload a valid file.', 'error')
        return redirect(url_for('redact.redact'))

    filename = secure_filename(file.filename)
    temp_upload_folder = make_dir_for_temp_upload()

    temp_file_path = os.path.join(temp_upload_folder, filename)
    file.save(temp_file_path)

    redacted_pdf_path = os.path.join(temp_upload_folder, f'redacted_{filename}')
    redact_pdf(temp_file_path, redacted_pdf_path)

    return send_file(redacted_pdf_path, as_attachment=True, download_name=f"redacted_{filename}")