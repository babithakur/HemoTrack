# from flask import Flask

# def create_app():
#     app = Flask(__name__)

#     # Register blueprints
#     from app.api.routes.main_routes import main_bp
#     app.register_blueprint(main_bp)

#     return app

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Register blueprints
    from app.api.routes.user_routes import user_bp
    from app.api.routes.report_routes import report_bp
    app.register_blueprint(user_bp)
    app.register_blueprint(report_bp, url_prefix="/report")

    return app

