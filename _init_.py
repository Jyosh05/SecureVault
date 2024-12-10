from flask import Flask
from config import secret_key
from User_Routers.login import login_bp
from User_Routers.register import register_bp
from User_Routers.view_files import view_files_bp
from User_Routers.User_Functions import User_Features_bp
from Utils.general_utils import check_table

#PLEASE REGISTER THE BLUEPRINT

app = Flask(__name__)
#app secret key
app.secret_key = secret_key


app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

#app routes
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(User_Features_bp)
app.register_blueprint(view_files_bp)

if __name__ == "__main__":
    check_table()
    print(app.config)
    app.run(debug=True)