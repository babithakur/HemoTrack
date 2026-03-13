from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    #register blueprints
    from app.api.routes.user_routes import user_bp
    from app.api.routes.report_routes import report_bp
    from app.api.routes.nutrient_routes import nutrient_bp
    app.register_blueprint(user_bp)
    app.register_blueprint(report_bp, url_prefix="/report")
    app.register_blueprint(nutrient_bp, url_prefix="/nutrient")

    return app

