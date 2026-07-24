import requests
from typing import Dict, Any
from math import gcd
from functools import reduce
from config import Config
from app.utils import Helper
from app.logger import Logger



class APIClient:
    """Handle API interactions with visa slots service."""
    
    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.api_base_url
        self.api_keys = config.api_key
        self.user_agent = config.user_agent

        self.util = Helper(self.config)

        self.next_due = {}
        self.api_remaining_sessions = {}
        self.current_api_key = None
        self.keys_checked = False
        self.reset = False

    def reset_seesion(self):
        """Reset sesion sessions."""
        self.next_due = {}
        self.api_remaining_sessions = {}
        self.keys_checked = False
        self.reset = True

    def get_next_key(self, minutes_left: int) -> str:
        """
        remaining_sessions example:
        {
            "a": 30,
            "b": 20,
            "c": 10
        }

        minutes_left = remaining API calls remaining in the hour.
        """

        # Remove exhausted keys
        self.next_due = {
            k: self.next_due.get(k, 0)
            for k, v in self.api_remaining_sessions.items()
            if v > 0
        }

        # Initialize new keys
        for key in self.api_remaining_sessions:
            if self.api_remaining_sessions[key] > 0 and key not in self.next_due:
                self.next_due[key] = 0


        # Pick the key that is due the earliest
        key = min(self.next_due, key=self.next_due.get)

        # Calculate how often this key should be used
        interval = minutes_left / self.api_remaining_sessions[key]

        # Schedule its next use
        self.next_due[key] += interval

        return key

    def get_api_key(self) -> str:
        """Get a valid API key from the list of keys."""

        """ For first time get the sessions of all keys one by one """
        if len(self.api_remaining_sessions) != len(self.api_keys):
            for key in self.api_keys:
                if not key in self.api_remaining_sessions:
                    self.current_api_key = key
                    return key
        else: self.keys_checked = True

        self.current_api_key = self.get_next_key(self.util.get_minutes_until_reset())
        Logger().debug(f"Using API key: {self.current_api_key}")
        return self.current_api_key


    def extract_slot_details(self, data: Dict[str, Any]) -> list:
        """Extract slot details from API response."""
        return data.get('slotDetails', [])
    
    def extract_user_activity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract user activity from API response."""
        return data.get('userActivity', {})
    
    def get_total_remaining_sessions(self) -> int:
        """Get remaining sessions from API response."""
        return sum(value for value in self.api_remaining_sessions.values())

    def set_remaining_sessions(self, data: Dict[str, Any]) -> None:
        """Set remaining sessions for the current API key."""
        session = self.extract_user_activity(data).get('remaining', 0)
        if self.current_api_key:
            self.api_remaining_sessions[self.current_api_key] = session - self.config.critical_threshold if session > 0 else 0

    def get_slots(self) -> Dict[str, Any]:
        """Fetch current visa slots from API."""
        if self.util.get_minutes_until_reset() < 60:
            if self.reset: self.reset = False
        if self.util.is_reset_time():
            if not self.reset:
                self.reset_seesion()

        print(self.api_remaining_sessions)

        headers = {
            "User-Agent": self.user_agent,
            "X-Api-Key": self.get_api_key(),
        }

        try:
            response = requests.get(self.base_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            self.set_remaining_sessions(data)
            return data

        except requests.exceptions.HTTPError as e:
            message = e.response.json()['message'].split(".")[0]

            if e.response.status_code == 429:
                session = str(e.response.json().get('userActivity').get('remaining'))
                message = message + " : " + self.current_api_key + " : " + session
                if not self.current_api_key in self.api_remaining_sessions:
                    self.api_remaining_sessions[self.current_api_key] = session
                else: self.api_remaining_sessions[self.current_api_key] = self.api_remaining_sessions[self.current_api_key] - 10

            raise Exception(f"API request failed: {e.response.status_code} - {message}")

        except Exception as e:
            print(f"Unexpected error occurred: {e}")
            raise Exception(f"API request failed: {e}")


# if __name__ == "__main__":
#     config = Config()
#     print(config.api_key)
#     api_client = APIClient(config)
#     print(api_client.get_slots())