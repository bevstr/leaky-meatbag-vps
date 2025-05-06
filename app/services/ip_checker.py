# app/services/ip_checker.py

import socket
import requests
import subprocess
import platform

def get_public_ip():
    try:
        response = requests.get("https://api.ipify.org", timeout=3)
        return response.text.strip()
    except Exception:
        return "Unknown"

def get_dns_server():
    try:
        system = platform.system()

        if system == "Darwin":  # macOS
            result = subprocess.run(["scutil", "--dns"], capture_output=True, text=True)
            lines = result.stdout.splitlines()
            for line in lines:
                if "nameserver" in line.lower():
                    return line.split()[-1]

        elif system == "Linux":  # Docker or VPS
            with open("/etc/resolv.conf", "r") as f:
                for line in f:
                    if line.startswith("nameserver"):
                        return line.split()[1]

    except Exception:
        pass

    return "Unknown"
