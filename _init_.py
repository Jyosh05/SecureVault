from flask import Flask
from config import secret_key, DB_Config
from User_Routers.login import login_bp
from User_Routers.register import register_bp
from User_Routers.User_Functions import User_Features
import mysql.connector
from general_utils import mydb, check_table


app = Flask(__name__)
#app secret key
app.secret_key = secret_key


#app routes
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(User_Features)

if __name__ == "__main__":
    check_table()
    app.run(debug=True)