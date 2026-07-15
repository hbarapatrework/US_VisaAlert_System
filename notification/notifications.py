import requests
import json
from typing import Dict, Any
from app.logger import Logger
from app.logger import Logger
from config import Config


PRIORITY_PREFIX = {
    5: "🚨🚨",
    4: "🔥",
    3: "📅",
    2: "📢",
    1: "ℹ️",
}
class NotificationManager:
    """Handle sending notifications."""
    
    def __init__(self, config: Config):
        self.config = config
        self.ntfy_url = config.ntfy_base_url
        self.topics = config.topics
        self.click_url = config.click_url
        self.logger = Logger()

    def build_body(self, message: Dict[str, Any]) -> tuple:
        """Build the body of the notification."""
        total_slots = 0
        lines = []
        for location, details in sorted(message.items()):
            city = location.replace(" VAC", "").title()
            date = details["start date"]
            slots = details['Number of slots']
            total_slots += slots
            lines.append(
                f"{city}: {details['Number of slots']} ({date})"
            )
        return json.dumps(lines, indent=2), total_slots

    def send_notification(self, alert_type: str, message: Dict[str, Any], priority: int) -> bool:
        """Send notification to ntfy.sh."""
        global PRIORITY_PREFIX
        if not message:
            return False
        
        topic = self.topics.get(alert_type.lower(), "Habit-test") #"Habit-test"
        if not topic:
            return False

        headers = {
            "Title": f"{PRIORITY_PREFIX.get(priority, 5)} {alert_type} Alert".encode("utf-8"),
            "Priority": str(priority),
        }

        if isinstance(message, dict):
            body, total_slots = self.build_body(message)
            headers = {
                "Title": f"{PRIORITY_PREFIX.get(priority, 5)} {alert_type} {total_slots} Slot Alert".encode("utf-8"),
                "Click": self.click_url
            }
        else:
            body, total_slots = message, 0

        try:
            response = requests.post(
                f"{self.ntfy_url}/{topic}",
                headers=headers,
                data=body.encode("utf-8"),
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to send notification: {e}")
            return False
    
    def send_all_notifications(self, messages: Dict[str, Dict[str, Any]], priorities: Dict[str, int]) -> int:
        """Send all available notifications."""
        sent_count = 0
        
        for alert_type, message in messages.items():
            if message:
                priority = priorities.get(alert_type, 1)
                if self.send_notification(alert_type, message, priority):
                    sent_count += 1
        
        return sent_count

# if __name__ == "__main__":
#     config = Config()
#     notification = NotificationManager(config)
#
#     demo_message = {'VAC': {'CHENNAI VAC': {'Number of slots': 3, 'start date': '25 May 2027'}, 'HYDERABAD VAC': {'Number of slots': 10, 'start date': '25 May 2027'}, 'MUMBAI VAC': {'Number of slots': 3, 'start date': '15 May 2027'}}, 'Interview': {'HYDERABAD': {'Number of slots': 5, 'start date': '28 May 2027'}}}
#
#     success = notification.send_all_notifications( demo_message, priorities={"VAC": 5,"Interview": 5})
#     print("Notification sent!" if success else "Notification failed.")