import aiohttp
import asyncio
import os
import time
import threading
from datetime import datetime, timedelta
from app.services.leak_state import leak_state
from app.services.config_loader import config

ADBLOCK_SERVERS_FILE = os.path.join(os.path.dirname(__file__), "adblock_servers.txt")
ADBLOCK_LEAK_LOG_FILE = os.path.join(os.path.dirname(__file__), "adblock_leak_log.txt")

# ✨ NEW FAST CHECK MODE
FAST_CHECK = True  # Set True to use HEAD requests instead of full GET

# ✨ NEW LOG PURGE SETTINGS
LOG_RETENTION_DAYS = config.get("log_retention_days", 30)  # A month's logs are typically under 1MB. Cleanup is precautionary.

async def adblock_test():
    now = datetime.now()
    leak_found = False
    leaking_domains = []

    if FAST_CHECK:
        print("🚀 Running FAST leak check (HEAD requests)")
    else:
        print("🐢 Running FULL leak check (GET requests)")

    if not os.path.isfile(ADBLOCK_SERVERS_FILE):
        print(f"❗ Adblock servers file not found: {ADBLOCK_SERVERS_FILE}")
        return True

    with open(ADBLOCK_SERVERS_FILE, "r") as f:
        servers = [line.strip() for line in f if line.strip()]

    if not servers:
        print("❗ Adblock servers list is empty!")
        return True

    timeout = aiohttp.ClientTimeout(total=3)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        for url in servers:
            try:
                if FAST_CHECK:
                    async with session.head(url) as response:
                        if response.status == 200:
                            print(f"🚨 Ad server reachable: {url}")
                            leak_found = True
                            leaking_domains.append(url)
                else:
                    async with session.get(url) as response:
                        if response.status == 200:
                            print(f"🚨 Ad server reachable: {url}")
                            leak_found = True
                            leaking_domains.append(url)
            except Exception:
                continue

    leak_state.set_leak_status(leaking=leak_found, urls=leaking_domains, now=now)

    if not leak_found and now.timestamp() - leak_state.last_success_log_time > 120:
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        print(f"🕒 {timestamp} ✅ All ad servers blocked - no leaks detected.")
        leak_state.set_leak_status(leaking=False, urls=[], now=now, success_log=True)

    return not leak_found

def log_hourly_leak_summary():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    summary = f"{timestamp} - {'Leak detected' if leak_state.leak_detected_this_hour else 'No leaks detected'}\n"
    try:
        with open(ADBLOCK_LEAK_LOG_FILE, "a") as f:
            f.write(summary)
    except Exception as e:
        print(f"❗ Failed to write leak summary: {e}")

def purge_old_logs():
    if not os.path.isfile(ADBLOCK_LEAK_LOG_FILE):
        return

    cutoff_time = datetime.now() - timedelta(days=LOG_RETENTION_DAYS)
    retained_lines = []

    try:
        with open(ADBLOCK_LEAK_LOG_FILE, "r") as f:
            for line in f:
                try:
                    timestamp_str = line.split(" - ")[0]
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M")
                    if timestamp >= cutoff_time:
                        retained_lines.append(line)
                except Exception:
                    retained_lines.append(line)  # keep bad lines just in case

        with open(ADBLOCK_LEAK_LOG_FILE, "w") as f:
            f.writelines(retained_lines)

    except Exception as e:
        print(f"❗ Error purging old logs: {e}")

def get_snapshot():
    return {
        "currently_leaking": leak_state.currently_leaking,
        "last_leak_time": leak_state.last_leak_time,
        "leaked_domains": leak_state.last_leaked_urls,
    }

def start_background_polling():
    def run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_background_polling())

    t = threading.Thread(target=run, daemon=True)
    t.start()

async def _background_polling():
    while True:
        try:
            await adblock_test()
            print("⏳ Leak check completed.")

            now = datetime.now()
            current_minute = now.minute
            if (current_minute % 2) == 0 and current_minute != leak_state.last_recorded_minute:
                log_hourly_leak_summary()
                leak_state.leak_detected_this_hour = False
                leak_state.last_recorded_minute = current_minute

            # ✨ Purge logs after each leak summary pass
            purge_old_logs()

        except Exception as e:
            print(f"❗ Error in background polling: {e}")

        await asyncio.sleep(5)
