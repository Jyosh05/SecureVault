from flask import Blueprint
from Utils.general_utils import mydb

login_bp = Blueprint('login', __name__, template_folder='templates')
from flask import render_template, request, redirect, url_for, session, jsonify, flash
from Utils.CSRF_util import generate_csrf_token

@login_bp.route('/', methods=["GET", "POST"])
def login():
    if request.method == "POST":

        token = session.get('csrf_token', None)
        form_token = request.form.get('csrf_token', None)


        username = request.form.get('username')
        password = request.form.get('password')

        # Validate input
        if not username or not password:
            return render_template("Login/login.html", error="Username and Password Required",
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

            if not user:
                return render_template("Login/login.html", error="Invalid username or password",
                                       csrf_token=session.get('csrf_token'))

            # Check if password matches
            if password == user['Password']:
                #Adds in UserID and Username into the session
                session['user_id'] = user['ID']
                session['username'] = user['Username']
                return redirect(url_for('login.home'))
            else:
                return render_template("Login/login.html", error="Invalid username or password",
                                       csrf_token=session.get('csrf_token'))

        except Exception as e:
            print("Error:", e)
            return jsonify({'error': 'An error occurred'}), 500
    #generates CSRF token
    session['csrf_token'] = generate_csrf_token()
    return render_template("Login/login.html", csrf_token=session.get('csrf_token'))


@login_bp.route("/home",)
def home():
    session.pop('csrf_token',None)
    print(session)
    return render_template("Login/home.html")