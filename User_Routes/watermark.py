import os
from flask import Blueprint, render_template, request, send_file, flash, redirect, url_for,session
from werkzeug.utils import secure_filename
from Utils.general_utils import make_dir_for_temp_upload,allowed_file
from Utils.Watermarker import watermark_pdf
from Utils.rbac_utils import roles_required, role_redirects
from Utils.logging_utils import log_this

watermark_bp = Blueprint('watermark', __name__ , template_folder='templates')

@watermark_bp.route('/watermark')
@roles_required('patient','doctor')
def watermark():
    return render_template('Features/PDF_Watermark.html', role_redirects=role_redirects)


@watermark_bp.route('/watermark_upload', methods=['POST'])
@roles_required('user')
def watermark_upload():
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('watermark.watermark'))

    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('watermark.watermark'))

    # Check if the file is allowed and process it
    if not allowed_file(file.filename):
        flash('Unsupported file type. Please upload a valid file.', 'error')
        log_this('User uploaded unsupported file type','critical')
        return redirect(url_for('watermark.watermark'))

    filename = secure_filename(file.filename)
    temp_upload_folder = make_dir_for_temp_upload()

    temp_file_path = os.path.join(temp_upload_folder, filename)
    file.save(temp_file_path)

    watermark_text = session.get('username')  # Dynamic watermark
    watermarked_pdf_path = os.path.join(temp_upload_folder, f"watermarked_{filename}")

    # Apply watermark
    result_pdf_path = watermark_pdf(temp_file_path, watermark_text, watermarked_pdf_path)

    if result_pdf_path:
        # Return the watermarked PDF as a download
        return send_file(result_pdf_path, as_attachment=True, download_name=f"watermarked_{filename}")
    else:
        flash('Error applying watermark.', 'error')
        log_this("Error applying watermark", 'critical')
        return redirect(url_for('watermark.watermark'))
