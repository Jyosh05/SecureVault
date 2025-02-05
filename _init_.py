from flask import Flask
from config import secret_key
from User_Routes.login import login_bp
from User_Routes.register import register_bp
from User_Routes.view_files import view_files_bp
from User_Routes.upload import upload_bp
from User_Routes.redact import redact_bp
from User_Routes.watermark import watermark_bp
from Admin.home import admin_bp
from Utils.general_utils import *
from Utils.rbac_utils import create_so_user
from Admin.Dashboard import dashboard_bp
from Admin.create_doctor import create_doctor_bp
from Doctor.home import doctor_bp
from Doctor.file_sharing import share_file_bp
# from User_Routes.view_each_pdf import view_pdf_bp


#PLEASE REGISTER THE BLUEPRINT

app = Flask(__name__)
#app secret key
app.secret_key = secret_key


app.config['TEMP_UPLOAD_FOLDER'] = 'Files/Redact_&_Watermark'

#app routes
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(view_files_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(redact_bp)
app.register_blueprint(watermark_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(doctor_bp)
app.register_blueprint(create_doctor_bp)
app.register_blueprint(share_file_bp)
# app.register_blueprint(view_pdf_bp)



if __name__ == "__main__":
    check_table()
    print(app.config)
    create_so_user()
    app.run(debug=True)