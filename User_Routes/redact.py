import os.path

from flask import Blueprint, render_template,request,send_file,url_for,flash,redirect
from werkzeug.utils import secure_filename
from Utils.general_utils import make_dir_for_temp_upload
from Utils.file_converter import *
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
    """Handle file upload, convert to PDF if needed, redact the content, and allow download."""
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

    # Secure the file name and save it to the temporary upload folder
    filename = secure_filename(file.filename)
    file_extension = filename.rsplit('.', 1)[1].lower()
    temp_upload_folder = make_dir_for_temp_upload()

    # If the file is not a PDF, convert it to a PDF first
    if file_extension != 'pdf':
        temp_file_path = os.path.join(temp_upload_folder, filename)
        file.save(temp_file_path)
        output_pdf_path = os.path.join(temp_upload_folder, f"{filename.rsplit('.', 1)[0]}.pdf")

        if file_extension == 'docx':
            # Convert DOCX to PDF using LibreOffice (you need LibreOffice installed)
            subprocess.run(['libreoffice', '--headless', '--convert-to', 'pdf', temp_file_path])
            output_pdf_path = temp_file_path.rsplit('.', 1)[0] + '.pdf'
        elif file_extension == 'txt':
            # Convert text file to PDF (basic approach)
            convert_text_to_pdf(temp_file_path, output_pdf_path)
        else:
            flash('Unsupported file type for conversion.', 'error')
            return redirect(url_for('redact.redact'))
    else:
        # If the file is already a PDF
        temp_file_path = os.path.join(temp_upload_folder, filename)
        file.save(temp_file_path)
        output_pdf_path = temp_file_path

    # Now that we have the PDF, redact sensitive information
    redacted_pdf_path = os.path.join(temp_upload_folder, f'redacted_{filename}')
    redact_pdf(temp_file_path, redacted_pdf_path)

    # Return the redacted file for download
    return send_file(redacted_pdf_path, as_attachment=True, download_name=f"redacted_{filename}")