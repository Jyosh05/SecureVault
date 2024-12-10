from flask import Flask
from config import secret_key
from User_Routes.login import login_bp
from User_Routes.register import register_bp
from User_Routes.view_files import view_files_bp
from User_Routes.User_Functions import User_Features_bp
from User_Routes.upload import upload_bp
from User_Routes.redact import redact_bp
from Admin.home import admin_bp
from Utils.general_utils import *

#PLEASE REGISTER THE BLUEPRINT

app = Flask(__name__)
#app secret key
app.secret_key = secret_key


app.config['TEMP_UPLOAD_FOLDER'] = 'Files/Redact_&_Watermark'

#app routes
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(User_Features_bp)
app.register_blueprint(view_files_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(redact_bp)

if __name__ == "__main__":
    check_table()
    print(app.config)
    app.run(debug=True)