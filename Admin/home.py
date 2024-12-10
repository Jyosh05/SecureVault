from flask import Blueprint,render_template

admin_bp = Blueprint('admin', __name__, template_folder='templates')

@admin_bp.route('/admin_home')
def admin_home():
    return render_template('Admin/admin_logs.html')
