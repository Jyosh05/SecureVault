from flask import Blueprint, redirect

upload_bp = Blueprint('upload',__name__, template_folder='templates')

@upload_bp.route('/perma_upload')
def perma_upload():
    return redirect('User_files/view_files.html')