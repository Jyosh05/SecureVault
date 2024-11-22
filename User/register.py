from flask import Blueprint,render_template,request

register_bp = Blueprint("register", __name__, template_folder="templates")

@register_bp.route("/register")
def register():
    if request.method == "POST":
        print("help")
    return render_template('Login/register.html')