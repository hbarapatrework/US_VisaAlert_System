import os
import time
from datetime import datetime, timedelta
from config import Config


class PollingManager:
    """Manage polling strategy and timing."""
    
    def __init__(self, config: Config):
        self.config = config
        self.poll_file = ".last_poll"

    def get_time_until_reset(self) -> float:
        """
        Calculate minutes remaining until the next reset.
        Returns time in minutes.
        """
        now = datetime.now()

        reset_hour, reset_minute = map(
            int, self.config.reset_time.split(':')
        )

        next_reset = now.replace(
            hour=reset_hour,
            minute=reset_minute,
            second=0,
            microsecond=0
        )

        # If reset already happened today, use tomorrow's reset
        if next_reset <= now:
            next_reset += timedelta(days=1)

        seconds_remaining = (next_reset - now).total_seconds()

        return seconds_remaining / 60
    
    def calculate_interval(self, remaining_sessions: int) -> float:
        """
        Calculate polling interval based on remaining sessions.
        More sessions = faster polling, fewer sessions = slower polling.
        """
        min_interval = self.config.min_interval
        max_interval = self.config.max_interval
        critical_threshold = self.config.critical_threshold
        max_daily_polls = self.config.max_daily_polls
        
        if remaining_sessions - 24 <= critical_threshold:
            return max_interval

        ## Special case for early morning hours between 1am to 5am
        if 1 < datetime.now().hour < 5:
            return 30*60

        minutes_until_reset = self.get_time_until_reset()

        interval_minutes = minutes_until_reset / (remaining_sessions - 24)

        interval_seconds = interval_minutes * 60

        # Keep within configured limits
        interval_seconds = max(
            self.config.min_interval,
            min(self.config.max_interval, interval_seconds)
        )

        return interval_seconds
        
        # ratio = remaining_sessions / max_daily_polls
        # interval = min_interval + (max_interval - min_interval) * (1 - ratio)
        #
        # return max(min_interval, min(max_interval, interval))
    
    def should_poll(self) -> bool:
        """Check if enough time has passed since last poll."""
        last_poll = self.get_last_poll_time()
        # For first run, allow polling immediately
        if last_poll == 0:
            return True
        
        # This will be called by scheduler, so just return True
        # The scheduler will handle the timing
        return True
    
    def get_last_poll_time(self) -> float:
        """Get last poll time from file."""
        if os.path.exists(self.poll_file):
            try:
                with open(self.poll_file, 'r') as f:
                    return float(f.read().strip())
            except (ValueError, IOError):
                return 0
        return 0
    
    def update_poll_time(self):
        """Update last poll time to current time."""
        with open(self.poll_file, 'w') as f:
            f.write(str(time.time()))
    
    def time_since_last_poll(self) -> float:
        """Get seconds elapsed since last poll."""
        return time.time() - self.get_last_poll_time()
    
    def is_reset_time(self) -> bool:
        """Check if current time is within reset window (8am)."""
        current_time = datetime.now().time()
        reset_time = self.config.reset_time
        reset_hour, reset_minute = map(int, reset_time.split(':'))
        
        reset_start = datetime.min.time().replace(hour=reset_hour, minute=reset_minute)
        reset_end = datetime.min.time().replace(hour=reset_hour, minute=reset_minute + 1)
        
        return reset_start <= current_time <= reset_end
    
    def get_next_poll_wait_time(self, remaining_sessions: int) -> float:
        """Get seconds to wait before next poll."""
        interval = self.calculate_interval(remaining_sessions)
        time_since = self.time_since_last_poll()
        wait_time = max(90, interval - time_since)
        return wait_time

# if __name__ == "__main__":
#     config = Config()
#     poll_manager = PollingManager(config)
#     x = poll_manager.calculate_interval(2000)
#     print(x)
