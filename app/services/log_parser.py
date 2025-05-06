# app/services/log_parser.py

import os
from datetime import datetime
from app.services.config_loader import LOGS_DIR

LOG_PATH = os.path.join(LOGS_DIR, "adblock_leak_log.txt")

def parse_log():
    data = []

    try:
        with open(LOG_PATH, "r") as f:
            for line in f:
                if " - " in line:
                    timestamp_str, status_str = line.strip().split(" - ")
                    dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M")
                    status = 1 if "Leak detected" in status_str else 0
                    data.append({
                        "timestamp": dt.strftime("%Y-%m-%d %H:%M"),
                        "leak": status
                    })
    except Exception as e:
        print(f"❗ Error reading log: {e}")

    return data
