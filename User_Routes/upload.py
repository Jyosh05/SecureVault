from flask import Blueprint, redirect
from Utils.general_utils import make_dir_for_temp_upload, allowed_file
from Utils.rbac_utils import roles_required

upload_bp = Blueprint('upload',__name__, template_folder='templates')

@upload_bp.route('/perma_upload')
@roles_required('user')
def perma_upload():
    return redirect('User_files/view_files.html')


