from datetime import datetime, timedelta

class RefreshScheduler:
    def __init__(self, config):
        self.interval = config.get('weather',{}).get('refresh_interval_hours')
        self.refresh_file = 'logs/refreshed.txt'

    def should_refresh(self):
        try:
            with open(self.refresh_file, 'r') as f:
                last_refresh_str = f.read().strip()
                last_refresh = datetime.fromisoformat(last_refresh_str)
                if (datetime.now() - last_refresh) > timedelta(hours=self.interval):
                    return True
                else:
                    return False
        except FileNotFoundError:
            return True
        
    def record_refresh(self):
        refresh_time = datetime.now()
        with open(self.refresh_file, 'w') as f:
            f.write(refresh_time.isoformat())

    def get_last_refresh_info(self):
        try:
            with open(self.refresh_file, 'r') as f:
                last_refresh_str = f.read().strip()
                return datetime.fromisoformat(last_refresh_str), self.interval
        except FileNotFoundError:
            refresh_time = datetime.now()
            with open(self.refresh_file, 'w') as f:
                f.write(refresh_time.isoformat())
                return refresh_time, self.interval