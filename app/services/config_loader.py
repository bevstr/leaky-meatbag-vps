import yaml
import os

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'config.yml')

DEFAULT_CONFIG = {
    "device_alias": "MeatNode_01",
    "enable_nostr": False,
    "send_dm": False,
    "nostr_pubkey": "",
    "check_interval_seconds": 600,
    "dns_servers": ["9.9.9.9", "1.1.1.1"],  # Quad9 and Cloudflare as safe fallback DNS
    "trusted_ips": []  # No default; user must set their VPN's IP
}

def load_config():
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                user_config = yaml.safe_load(f) or {}
                merged = {**DEFAULT_CONFIG, **user_config}
                return merged
        else:
            print("⚠️ No config.yml found, loading defaults.")
            return DEFAULT_CONFIG
    except yaml.YAMLError as e:
        print(f"❌ Error parsing config.yml: {e}")
        return DEFAULT_CONFIG

def save_config(updated_config):
    try:
        with open(CONFIG_PATH, 'w') as f:
            yaml.dump(updated_config, f)
        print("✅ Config saved to config.yml")
    except Exception as e:
        print(f"❌ Failed to save config: {e}")
def is_config_initialized(config):
    return bool(config.get("trusted_ips")) and bool(config.get("dns_servers"))
    
# ✨ LOAD CONFIG GLOBALLY
config = load_config()