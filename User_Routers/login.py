from flask import render_template,request,session,flash,Blueprint, redirect, url_for, make_response
import secrets

login_bp = Blueprint('login', __name__, template_folder='templates')
@login_bp.route('/', methods=["GET","POST"])
def login():
    if request.method == "POST":
        token = session.get('csrf_token',None)
        form_token = request.form.get('csrf_token',None)
        username = request.form.get('username')
        password = request.form.get('password')
        session['username'] = username
        if not token or token != form_token:
            flash("CSRF token invalid", 'error')
            return redirect(url_for("login.login"))
        return  redirect(url_for("login.home"))
    session['csrf_token'] = secrets.token_hex(16)
    return render_template("Login/login.html", csrf_token=session['csrf_token'])


@login_bp.route("/home",)
def home():
    session.pop('csrf_token',None)
    print(session)
    return render_template("Login/home.html")