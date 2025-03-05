from flask import Flask
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os
from flask_bcrypt import Bcrypt
from flask_cors import CORS

bcrypt = Bcrypt()
jwt = JWTManager()
def create_app():

    load_dotenv()
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

    bcrypt.init_app(app)
    jwt.init_app(app)

    from app.routes import main
    app.register_blueprint(main)

    from app.dashboard import dashboard
    app.register_blueprint(dashboard)

    from app.food import food
    app.register_blueprint(food)

    from app.profile import profile
    app.register_blueprint(profile)

    return app
