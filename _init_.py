from flask import Flask
from config import secret_key
from User_Routers.login import login_bp
from User_Routers.register import register_bp
from User_Routers.User_Functions import User_Features
from AI_Model import train_ai_model,console_test_ai

app = Flask(__name__)
app.secret_key = secret_key

app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(User_Features)

if __name__ == "__main__":
    app.run(debug=True)