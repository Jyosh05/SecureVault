from flask import render_template,Blueprint
from Utils.rbac_utils import roles_required

User_Features_bp = Blueprint('features', __name__, template_folder="templates")


@User_Features_bp.route("/User_PDF_Redactor")
@roles_required('user')
def redactor():
    return render_template("User_auth+creation/PDF_Redactor.html")