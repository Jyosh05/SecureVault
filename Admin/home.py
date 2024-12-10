from flask import Blueprint,render_template
from Utils.rbac_utils import roles_required

admin_bp = Blueprint('admin', __name__, template_folder='templates')

@admin_bp.route('/admin_home')
@roles_required('so')
def admin_home():
    return render_template('Admin/admin_logs.html')
