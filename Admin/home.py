from flask import Blueprint, render_template

from Utils.general_utils import mydb
from Utils.rbac_utils import roles_required

admin_bp = Blueprint('admin', __name__, template_folder='templates')

@admin_bp.route('/admin_home')
@roles_required('so')
def admin_home():
    with mydb.cursor() as mycursor:
        # mycursor.execute("SELECT * FROM audit_log")
        mycursor.execute("SELECT ID, Action, Event_Time, User_ID FROM audit_log ORDER BY ID")
        data = mycursor.fetchall()

    mycursor.close()
    return render_template('Admin/admin_logs.html', data=data, nameOfPage='Log')
