import os
from flask import Blueprint, render_template, request, send_file, flash, redirect, url_for,session
from werkzeug.utils import secure_filename
from Utils.general_utils import make_dir_for_temp_upload,allowed_file
from Utils.Watermarker import watermark_pdf
from Utils.rbac_utils import roles_required

watermark_bp = Blueprint('watermark', __name__ , template_folder='templates')

@watermark_bp.route('/watermark')
@roles_required('user')
def watermark():
    return render_template('Features/PDF_Watermark.html')


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
        return redirect(url_for('watermark.watermark'))

    filename = secure_filename(file.filename)
    file_extension = filename.rsplit('.', 1)[1].lower()
    temp_upload_folder = make_dir_for_temp_upload()

    temp_file_path = os.path.join(temp_upload_folder, filename)
    file.save(temp_file_path)

    watermark_text = f"Watermarked by {session.get('username', 'Unknown User')}"  # Dynamic watermark
    watermarked_pdf_path = os.path.join(temp_upload_folder, f"watermarked_{filename}")

    # Apply watermark
    watermarked_pdf_stream = watermark_pdf(temp_file_path, watermark_text)

    # Save the watermarked PDF to a temporary path
    with open(watermarked_pdf_path, 'wb') as output_file:
        output_file.write(watermarked_pdf_stream.read())

    # Return the watermarked PDF as a download
    return send_file(watermarked_pdf_path, as_attachment=True, download_name=f"watermarked_{filename}")