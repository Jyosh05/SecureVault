from flask import render_template,Blueprint

User_Features_bp = Blueprint('features', __name__, template_folder="templates")

@User_Features_bp.route("/User_PDF_Redactor")
def redactor():
    return render_template("User_auth+creation/PDF_Redactor.html")