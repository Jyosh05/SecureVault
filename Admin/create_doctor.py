from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash

from Utils.general_utils import mydb
from Utils.rbac_utils import roles_required

create_doctor_bp = Blueprint('create_doctor', __name__, template_folder='templates')

@create_doctor_bp.route('/create_doctor', methods=['POST', 'GET'])
@roles_required('so')
def create_doctor():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        email = request.form.get('email')
        print(username,password,email)

        if not username or not password or not email:
            return jsonify({'error':'All fields are required'})

        if password == confirm_password:
            print("trying to add in")
            try:
                #NEED HASHING
                role = 'doctor'
                cursor = mydb.cursor(buffered=True)
                query = "INSERT INTO user(Username, Password, Email, Role) VALUES (%s,%s,%s,%s)"
                cursor.execute(query,(username,password,email,role))
                mydb.commit()
                cursor.close()
                flash("Doctor created successfully!")
                return redirect(url_for("Admin/create_doctor"))

            except Exception as e:
                print(e)

        else:
            return jsonify({'error':'An Unexpected Error Has Occured'})

    return render_template('Admin/create_doctor.html')