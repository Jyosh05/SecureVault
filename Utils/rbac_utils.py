import mysql.connector
from flask import session, abort
from functools import wraps
from Utils.general_utils import mydb
import bcrypt
from config import so_config


role_redirects = {
    'so': 'admin.admin_home',
    'user': 'login.home'
}

def roles_required(*roles):
    def wrapper(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if 'role' not in session or session['role'] not in roles:
                return abort(403)  # Forbidden
            return func(*args, **kwargs)
        return decorated_function
    return wrapper

def create_so_user():
    try:
        cursor = mydb.cursor(buffered=True)
        check_so_query = "SELECT * FROM user WHERE role = 'so'"
        cursor.execute(check_so_query)
        existing_so = cursor.fetchone()

        if existing_so:
            print("Security Officer already exists")
        else:

            insert_so_query = "INSERT INTO user (Username, Password, Email, Role) VALUES (%s, %s, %s, %s)"
            so_user = (
                so_config['username'],
                so_config['password'],
                so_config['email'],
                so_config['role']
            )

            cursor.execute(insert_so_query, so_user)
            mydb.commit()
            print('SO created')

    except mysql.connector.Error as err:
        print(f"Error while inserting admin user: {err}")
