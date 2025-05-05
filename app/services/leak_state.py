class LeakState:
    def __init__(self):
        self.currently_leaking = False
        self.last_success_log_time = 0
        self.last_leaked_urls = []
        self.last_leak_time = None
        self.leak_detected_this_hour = False
        self.last_recorded_minute = None

    def set_leak_status(self, leaking, urls, now, success_log=False):
        self.currently_leaking = leaking
        if leaking:
            self.last_leaked_urls = urls
            self.last_leak_time = now.strftime("%Y-%m-%d %H:%M:%S")
            self.leak_detected_this_hour = True
        if success_log:
            self.last_success_log_time = now.timestamp()

# Exported instance to import across app
leak_state = LeakState()
