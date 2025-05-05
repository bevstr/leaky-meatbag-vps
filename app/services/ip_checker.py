import socket
import requests

def get_public_ip():
    try:
        response = requests.get("https://api.ipify.org", timeout=3)
        return response.text.strip()
    except Exception:
        return "Unknown"

def get_dns_server():
    try:
        # macOS: Use scutil to get DNS server info
        import subprocess
        result = subprocess.run(["scutil", "--dns"], capture_output=True, text=True)
        lines = result.stdout.splitlines()
        for line in lines:
            if "nameserver" in line.lower():
                return line.split()[-1]
    except Exception:
        pass
    return "Unknown"
