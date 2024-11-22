from flask import Flask
from config import secret_key
from User.login import login_bp
from User.register import register_bp

app = Flask(__name__)
app.secret_key = secret_key

app.register_blueprint(login_bp)
app.register_blueprint(register_bp)

if __name__ == "__main__":
    app.run(debug=True)