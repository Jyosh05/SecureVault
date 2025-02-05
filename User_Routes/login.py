from flask import Blueprint

from Utils.logging_utils import log_this
from Utils.general_utils import mydb
from flask import render_template, request, redirect, url_for, session, jsonify, flash
from Utils.CSRF_util import generate_csrf_token
from Utils.rbac_utils import role_redirects, roles_required

login_bp = Blueprint('login', __name__, template_folder='templates')
@login_bp.route('/', methods=["GET", "POST"])
def login():
    if request.method == "POST":

        token = session.get('csrf_token', None)
        form_token = request.form.get('csrf_token', None)


        username = request.form.get('username')
        password = request.form.get('password')
        print(f"Token: {token}, Form Token: {form_token}")
        print(f"Username: {username}, Password: {password}")

        # Validate input
        if not username or not password:
            return render_template("User_auth+creation/login.html", error="Username and Password Required",
                                   csrf_token=session.get('csrf_token'))


        # CSRF token validation
        if not token or token != form_token:
            flash("CSRF token invalid", 'error')
            return redirect(url_for("login.login"))

        try:
            cursor = mydb.cursor(dictionary=True)
            query = "SELECT * FROM user WHERE username = %s"
            cursor.execute(query, (username,))
            user = cursor.fetchone()
            print(f"User fetched from DB: {user}")

            if not user:
                print("No user found with given username")
                log_this("Invalid username or password",'critical')
                return render_template("User_auth+creation/login.html", error="Invalid username or password",
                                       csrf_token=session.get('csrf_token'))

            if password == user['Password']:
                print("Password match successful")
                #Adds in UserID and Username into the session
                session['user_id'] = user['ID']
                session['username'] = user['Username']
                session['role'] = user['Role']


                role = user['Role'].lower()
                redirect_url = role_redirects.get(role, 'login.home')
                print(f"Redirecting to: {redirect_url}")
                log_this("Login successful")
                return redirect(url_for(redirect_url))


            else:
                log_this("Invalid username or password",'critical')
                return render_template("User_auth+creation/login.html", error="Invalid username or password",
                                       csrf_token=session.get('csrf_token'))


        except Exception as e:
            print("Error:", e)
            return jsonify({'error': 'An error occurred'}), 500
    #generates CSRF token
    session['csrf_token'] = generate_csrf_token()
    return render_template("User_auth+creation/login.html", csrf_token=session.get('csrf_token'))


@login_bp.route("/home",)
@roles_required('patient')
def home():
    session.pop('csrf_token',None)
    print(session)
    return render_template("home.html")