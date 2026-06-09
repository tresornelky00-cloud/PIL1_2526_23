"""
IFRI_MentorLink — Application principale Flask
"""
import os
import pymysql
pymysql.install_as_MySQLdb()
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO

load_dotenv()

db       = SQLAlchemy()
login_manager = LoginManager()
bcrypt   = Bcrypt()
socketio = SocketIO()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"]          = os.getenv("SECRET_KEY", "dev-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Veuillez vous connecter."

    # Enregistrement des blueprints
    import models
    from routes.auth    import auth_bp
    from routes.profil  import profil_bp
    from routes.matching import matching_bp
    from routes.messages import messages_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(profil_bp)
    app.register_blueprint(matching_bp)
    app.register_blueprint(messages_bp)

    with app.app_context():   
        from models import User
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)
