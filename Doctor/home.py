from flask import Blueprint, render_template

from Utils.general_utils import mydb
from Utils.rbac_utils import roles_required

doctor_bp = Blueprint('doctor', __name__, template_folder='templates')

@doctor_bp.route('/doctor_home')
@roles_required('doctor')
def doctor_home():
    return 'This is doctor home, it works!'