from flask import Blueprint, render_template, flash, session, redirect, url_for

from Utils.general_utils import mydb
from Utils.rbac_utils import roles_required

doctor_bp = Blueprint('doctor', __name__, template_folder='templates')

@doctor_bp.route('/doctor_home', methods=['POST', 'GET'])
@roles_required('doctor')
def doctor_home():
    if 'user_id' not in session:
        flash("Please log in to view your files.", 'error')
        return redirect(url_for('login.login'))

    user_id = session['user_id']  # Get the logged-in user's ID
    username = "Unknown User"  # Default username

    try:
        # Fetch user info from the database
        mycursor = mydb.cursor(dictionary=True)
        mycursor.execute("SELECT Username FROM user WHERE ID = %s", (user_id,))
        user = mycursor.fetchone()

        # If user is found, set the username
        if user:
            username = user['Username']

        # Close cursor after executing query
        mycursor.close()

    except Exception as e:
        flash(f"Error retrieving user details: {e}", 'error')

    # Render the doctor home page with username (no files yet)
    return render_template('Doctor/doctor_home.html', username=username)
