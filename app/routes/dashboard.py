from flask import Blueprint, render_template, redirect, jsonify, request
from app.services.config_loader import load_config, save_config, is_config_initialized
from app.services.ip_checker import get_public_ip, get_dns_server
from app.services.adblock_checker import get_snapshot, start_background_polling
from app.services.leak_state import leak_state  # ✅ fixed import
from app.services.log_parser import parse_log

dashboard_bp = Blueprint('dashboard', __name__)
start_background_polling()

@dashboard_bp.route('/api/leak-snapshot')
def leak_snapshot():
    return jsonify(get_snapshot())

@dashboard_bp.route('/leak-history')
def leak_history():
    return render_template('leak_history.html')

@dashboard_bp.route('/api/leak-graph')
def leak_graph():
    return jsonify(parse_log())

@dashboard_bp.route('/')
def dashboard():
    config = load_config()

    if not is_config_initialized(config):
        return redirect("/onboarding")

    public_ip = get_public_ip()
    dns_server = get_dns_server()
    adblock_status = "Working" if not leak_state.currently_leaking else "Leaking"

    trusted_ips = config.get("trusted_ips", [])
    trusted_dns = config.get("dns_servers", [])
    isp_ip = config.get("isp_ip")  # 🆕 Fetch ISP IP from config

    trusted_ip = trusted_ips[0] if trusted_ips else None
    trusted_dns_display = ', '.join(dns for dns in trusted_dns if dns) if trusted_dns else None

    vpn_status = "Protected" if trusted_ip and public_ip == trusted_ip and trusted_dns and dns_server in trusted_dns else "Leaking"

    return render_template(
        "dashboard.html",
        vpn_status=vpn_status,
        adblock_status=adblock_status,
        public_ip=public_ip,
        dns_server=dns_server,
        trusted_ip=trusted_ip,
        trusted_dns=trusted_dns_display,
        isp_ip=isp_ip,  # 🆕 Pass ISP IP to template
        config_alias=config.get("device_alias")
    )

@dashboard_bp.route('/api/dashboard-status')
def dashboard_status():
    config = load_config()

    public_ip = get_public_ip()
    dns_server = get_dns_server()
    adblock_status = "Working" if not leak_state.currently_leaking else "Leaking"  # ✅ fixed usage

    trusted_ips = config.get("trusted_ips", [])
    trusted_dns = config.get("dns_servers", [])

    trusted_ip = trusted_ips[0] if trusted_ips else None

    vpn_status = "Protected" if trusted_ip and public_ip == trusted_ip and trusted_dns and dns_server in trusted_dns else "Leaking"

    show_warning = vpn_status != "Protected" or not (trusted_ip and public_ip == trusted_ip) or not (dns_server in trusted_dns)

    return jsonify({
        "vpn_status": vpn_status,
        "public_ip": public_ip,
        "dns_server": dns_server,
        "adblock_status": adblock_status,
        "show_warning": show_warning
    })

@dashboard_bp.route('/api/accept-new', methods=['POST'])
def accept_new():
    config = load_config()

    current_ip = get_public_ip()
    current_dns = get_dns_server()

    config['trusted_ips'] = [current_ip]
    config['dns_servers'] = [current_dns]

    save_config(config)
    return '', 204

@dashboard_bp.route('/api/save-config', methods=['POST'])
def save_config_route():
    try:
        data = request.json
        config = load_config()

        if "device_alias" in data:
            config["device_alias"] = data["device_alias"]

        if "trusted_ips" in data:
            config["trusted_ips"] = [data["trusted_ips"].strip()] if isinstance(data["trusted_ips"], str) else data["trusted_ips"]

        if "dns_servers" in data:
            config["dns_servers"] = [data["dns_servers"].strip()] if isinstance(data["dns_servers"], str) else data["dns_servers"]

        save_config(config)
        return jsonify({"success": True})

    except Exception as e:
        print(f"Error saving config: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@dashboard_bp.route("/api/leak-graph-data")
def leak_graph_data():
    from app.services.log_parser import parse_log
    from datetime import datetime, timedelta
    from flask import request

    log_data = parse_log()

    try:
        days = int(request.args.get("days", 7))
    except ValueError:
        days = 7

    cutoff = datetime.now() - timedelta(days=days)
    filtered_data = [
        entry for entry in log_data
        if datetime.strptime(entry["timestamp"], "%Y-%m-%d %H:%M") >= cutoff
    ]

    return jsonify(filtered_data)
