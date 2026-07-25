import os
import time
import math
from datetime import datetime, timedelta
from config import Config


class Helper:
    def __init__(self, config: Config):
        self.config = config

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

        return seconds_remaining

    def get_minutes_until_reset(self) -> float:
        minutes_until_reset = math.ceil(self.get_time_until_reset() / 60)
        return minutes_until_reset

    def get_hours_until_reset(self) -> float:
        hours_until_reset = math.ceil(self.get_time_until_reset() / 3600)
        return hours_until_reset

    def is_reset_time(self) -> bool:
        """Check if current time is within reset window (10am)."""
        current_time = datetime.now().time()
        reset_time = self.config.reset_time
        reset_hour, reset_minute = map(int, reset_time.split(':'))

        reset_start = datetime.min.time().replace(hour=reset_hour, minute=reset_minute)
        reset_end = datetime.min.time().replace(hour=reset_hour, minute=reset_minute + 1)

        return reset_start <= current_time <= reset_end

    def get_current_epoch(self):
        return int(datetime.now().timestamp())

# if __name__ == "__main__":
#     config = Config()
#     util = Helper(config)
#     print(util.get_time_until_reset())
#     print(util.get_minutes_until_reset())
#     print(util.get_hours_until_reset())