from flask import Flask
from app.routes.config import config_bp
from app.routes.dashboard import dashboard_bp
from app.routes.onboarding import onboarding_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = "leaky_meatbag_secret"  # Needed for session handling
    app.register_blueprint(config_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(onboarding_bp)
    return app
