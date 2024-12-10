from flask import Blueprint,render_template

view_files_bp = Blueprint('view_files', __name__, template_folder='templates')
@view_files_bp.route('/view_files')
def view_files():
    return render_template('User_files/view_files.html')