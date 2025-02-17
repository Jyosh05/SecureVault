import spacy
import fitz  # PyMuPDF
import re
import joblib
import numpy as np
from flask import Blueprint, render_template, request, send_file, url_for, flash, redirect
from werkzeug.utils import secure_filename
from Utils.general_utils import make_dir_for_temp_upload, allowed_file
from Utils.PDF_Redaction import redact_pdf
from Utils.rbac_utils import roles_required, role_redirects
from config import MODEL_FILE, LABEL_ENCODER_FILE
import os
from Utils.logging_utils import log_this



redact_bp = Blueprint('redact', __name__, template_folder='templates')


@redact_bp.route('/redact')
@roles_required('patient', 'doctor')
def redact():
    return render_template('Features/PDF_Redactor.html', role_redirects=role_redirects)


@redact_bp.route('/redact_upload', methods=['POST'])
@roles_required('patient')
def redact_upload():
    if 'file' not in request.files:
        flash('No file part', 'error')
        log_this('error redacting file', 'critical')
        return redirect(url_for('redact.redact'))

    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        log_this('error redacting file', 'critical')
        return redirect(url_for('redact.redact'))

    if not allowed_file(file.filename):
        flash('Unsupported file type. Please upload a valid file.', 'error')
        log_this("user uploaded an unsupported file type", 'high')
        return redirect(url_for('redact.redact'))

    filename = secure_filename(file.filename)
    temp_upload_folder = make_dir_for_temp_upload()

    temp_file_path = os.path.join(temp_upload_folder, filename)
    file.save(temp_file_path)


    redacted_pdf_path = os.path.join(temp_upload_folder, f'redacted_{filename}')
    redact_pdf(temp_file_path,redacted_pdf_path)

    return send_file(redacted_pdf_path, as_attachment=True, download_name=f"redacted_{filename}")

