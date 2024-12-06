from flask import Blueprint,render_template,request, jsonify
from Utils.general_utils import mydb

register_bp = Blueprint("register", __name__, template_folder="templates")

@register_bp.route("/register",methods=["POST","GET"])
def register():
    print("registering")
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
                cursor = mydb.cursor(buffered=True)
                query = "INSERT INTO user(Username, Password, Email) VALUES (%s,%s,%s)"
                cursor.execute(query,(username,password,email))
                mydb.commit()
                cursor.close()
                return render_template('Login/home.html', username=username)

            except Exception as e:
                print(e)

        else:
            return jsonify({'error':'An Unexpected Error Has Occured'})

    return render_template('Login/register.html')