from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.services.status_service import get_public_ip, get_dns_server
from app.services.config_loader import load_config, save_config

onboarding_bp = Blueprint('onboarding', __name__)

@onboarding_bp.route('/onboarding', methods=['GET', 'POST'])
def onboarding():
    if 'onboarding_stage' not in session:
        session['onboarding_stage'] = 'start'

    stage = session['onboarding_stage']
    ip = get_public_ip()
    dns = get_dns_server()

    # Always make DNS a list for easy handling
    if isinstance(dns, str):
        dns = [dns]

    if request.method == 'POST':
        if stage == 'start':
            # 🛠 Save ISP fingerprint into session
            session['baseline_ip'] = ip
            session['baseline_dns'] = dns
            session['onboarding_stage'] = 'vpn_on'

            # 🛠 Also save ISP IP into config if missing
            config = load_config()
            if not config.get('isp_ip'):
                config['isp_ip'] = ip
                save_config(config)

            return redirect(url_for('onboarding.onboarding'))

        elif stage == 'vpn_on':
            # 🛠 Fresh fetch during step 2 post
            latest_ip = get_public_ip()
            latest_dns = get_dns_server()

            if isinstance(latest_dns, str):
                latest_dns = [latest_dns]

            baseline_ip = session.get('baseline_ip')
            baseline_dns = session.get('baseline_dns')

            if latest_ip == baseline_ip and latest_dns == baseline_dns:
                flash("⚠️ No network change detected. Please confirm you've toggled your VPN.")
                return redirect(url_for('onboarding.onboarding'))

            # Save VPN fingerprints
            session['vpn_ip'] = latest_ip
            session['vpn_dns'] = latest_dns
            session['onboarding_stage'] = 'review'
            return redirect(url_for('onboarding.review'))

    # --- GET request only below here ---

    status_class = "blue"
    if stage == "vpn_on":
        baseline_ip = session.get("baseline_ip")
        baseline_dns = session.get("baseline_dns")
        if ip != baseline_ip or dns != baseline_dns:
            status_class = "ok"

    return render_template('onboarding.html',
                           stage=stage,
                           ip=ip,
                           dns=dns,
                           status_class=status_class,
                           vpn_ip=session.get('vpn_ip'),
                           vpn_dns=session.get('vpn_dns'))

@onboarding_bp.route('/onboarding/review', methods=['GET'])
def review():
    return render_template('onboarding_review.html',
                           public_ip=session.get('vpn_ip'),
                           dns_servers=session.get('vpn_dns'))

@onboarding_bp.route('/onboarding/confirm', methods=['POST'])
def confirm():
    config = load_config()

    vpn_ip = session.get('vpn_ip')
    vpn_dns = session.get('vpn_dns')

    config['trusted_ips'] = [vpn_ip]
    config['dns_servers'] = vpn_dns if isinstance(vpn_dns, list) else [vpn_dns]

    alias = config.get('device_alias')
    if not alias or not alias.strip():
        flash("⚠️ You must enter a Config Alias before continuing.")
        save_config(config)  # Still save VPN/IP if missing
        return redirect(url_for('config.show_config', from_onboarding=True))

    save_config(config)

    # Cleanup
    session.clear()

    flash("✅ VPN fingerprint saved to config.")
    return redirect(url_for('dashboard.dashboard'))

@onboarding_bp.route('/reset-onboarding')
def reset_onboarding():
    session.clear()
    return redirect(url_for('onboarding.welcome'))

@onboarding_bp.route('/api/network-status')
def network_status():
    dns_server = get_dns_server()
    return {
        "ip": get_public_ip(),
        "dns": [dns_server] if dns_server else []
    }

@onboarding_bp.route('/welcome')
def welcome():
    return render_template('welcome.html')
