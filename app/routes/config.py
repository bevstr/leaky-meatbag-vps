from flask import Blueprint, render_template, request
from app.services.config_loader import load_config

config_bp = Blueprint('config', __name__)

@config_bp.route('/config')
def show_config():
    config = load_config()
    from_onboarding = request.args.get('from_onboarding', False)

    # 🛠️ make sure it's a real boolean
    if isinstance(from_onboarding, str):
        from_onboarding = from_onboarding.lower() == 'true'

    return render_template('config.html', config=config, from_onboarding=from_onboarding)
