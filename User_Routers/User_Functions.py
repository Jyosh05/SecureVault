from flask import render_template,Blueprint

User_Features = Blueprint('features', __name__, template_folder="templates")

@User_Features.route("/User_PDF_Redactor")
def redactor():
    return render_template("Login/PDF_Redactor.html")