import subprocess
import requests
from app.services.config_loader import load_config

def get_public_ip():
    try:
        result = subprocess.check_output(["curl", "-s", "ifconfig.me"])
        return result.decode().strip()
    except Exception:
        return "Unknown"

def get_dns_server():
    try:
        result = subprocess.check_output(["scutil", "--dns"])
        lines = result.decode().splitlines()
        for line in lines:
            if "nameserver[0]" in line:
                return line.split(":")[1].strip()
    except Exception:
        pass
    return "Unknown"

def check_ad_blocking():
    try:
        url = "http://ads-blocker-test-pages.glitch.me/ads.js"
        response = requests.get(url, timeout=3)
        return response.status_code != 200
    except requests.RequestException:
        return True

def get_vpn_status():
    config = load_config()
    current_ip = get_public_ip()
    trusted_ips = config.get("trusted_ips", [])
    if not trusted_ips:
        return "Unknown"
    return "Protected" if current_ip in trusted_ips else "Leaking"
