from flask import Flask
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
jwt = JWTManager()
def create_app():

    load_dotenv()
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    bcrypt.init_app(app)
    jwt.init_app(app)

    from app.routes import main
    app.register_blueprint(main)

    return app
