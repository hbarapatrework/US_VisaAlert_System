import requests
from typing import Dict, Any
from config import Config


class APIClient:
    """Handle API interactions with visa slots service."""
    
    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.api_base_url
        self.api_key = config.api_key
        self.user_agent = config.user_agent

        # print(self.base_url, self.api_key, self.user_agent)
    
    def get_slots(self) -> Dict[str, Any]:
        """Fetch current visa slots from API."""
        headers = {
            "User-Agent": self.user_agent,
            "X-Api-Key": self.api_key
        }
        
        try:
            response = requests.get(self.base_url, headers=headers)
            response.raise_for_status()
            return response.json()

        # except requests.exceptions.RequestException as e:
        #     print(e)
        #     raise Exception(f"API request failed: {e}")
        except requests.exceptions.HTTPError as e:
            message = e.response.json()['message'].split(".")[0]

            if e.response.status_code == 429:
                session = str(e.response.json().get('userActivity').get('remaining'))
                message = message + " : " + session

            raise Exception(f"API request failed: {e.response.status_code} - {message}")

        except Exception as e:
            print(f"Unexpected error occurred: {e}")
            raise Exception(f"API request failed: {e}")

    def extract_slot_details(self, data: Dict[str, Any]) -> list:
        """Extract slot details from API response."""
        return data.get('slotDetails', [])
    
    def extract_user_activity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract user activity from API response."""
        return data.get('userActivity', {})
    
    def get_remaining_sessions(self, data: Dict[str, Any]) -> int:
        """Get remaining sessions from API response."""
        return self.extract_user_activity(data).get('remaining', 0)

# if __name__ == "__main__":
#     config = Config()
#     print(config.api_key)
#     api_client = APIClient(config)
#     print(api_client.get_slots())