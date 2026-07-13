from datetime import datetime, timedelta, date
from typing import Dict, Any, List, Tuple
from config import Config
from zoneinfo import ZoneInfo


class VisaProcessor:
    """Process visa slot data and priorities."""
    
    def __init__(self, config: Config):
        self.config = config
        self.priority = dict(config.priorities)
    
    def get_target_start_date(self) -> date:
        """Get target start date based on configuration."""
        return date.today() + timedelta(days=self.config.target_days_ahead)

    def convert_timestamp(self, dt: str) -> str:
        utc_dt = datetime.strptime(
            dt,"%a, %d %b %Y %H:%M:%S GMT"
        ).replace(tzinfo=ZoneInfo("UTC"))

        local_dt = utc_dt.astimezone(ZoneInfo("America/Los_Angeles"))
        return local_dt.strftime("%a, %d %b %Y %H:%M:%S PST")
    
    def set_priority_for_notification(self, slot_date: date, key: str) -> None:
        """
        Assign priority based on how far the slot_date is from the target_date.
        
        Priority:
            5: target_date <= slot_date < target_date + 60 days
            4: target_date + 60 <= slot_date < target_date + 90 days
            3: target_date + 90 <= slot_date < target_date + 120 days
            2: target_date + 120 <= slot_date < target_date + 150 days
            1: slot_date >= target_date + 150 days
            0: slot_date < target_date
        """
        target_date = self.get_target_start_date()
        
        if self.priority[key] < 5:
            if slot_date < target_date:
                return
            elif slot_date < target_date + timedelta(days=60):
                self.priority[key] = 5
            elif slot_date < target_date + timedelta(days=90):
                self.priority[key] = 4
            elif slot_date < target_date + timedelta(days=120):
                self.priority[key] = 3
            elif slot_date < target_date + timedelta(days=150):
                self.priority[key] = 2
            else:
                self.priority[key] = 1
    
    def build_notification_payload(self, slot_details: list) -> Tuple[Dict[str, Dict[str, Any]], List[Dict[str, Any]]]:
        """Create notification message from slot details."""
        message = {"VAC": {}, "Interview": {}}
        records = []

        for slot in slot_details:
            if slot.get("slots", 0) > 0:
                location = slot.get("visa_location", "")
                num_of_slots = slot.get("slots")
                slot_start_date = slot.get('start_date')
                slot_release_time = self.convert_timestamp(slot.get('createdon'))
                slot_type = None

                if "VAC" in location:
                    message["VAC"][location] = {
                        "Number of slots": num_of_slots,
                        "start date": slot_start_date
                    }
                    slot_type = "VAC"
                    try:
                        slot_date = datetime.strptime(slot_start_date, "%Y-%m-%d").date()
                        self.set_priority_for_notification(slot_date, "VAC")
                    except (ValueError, TypeError):
                        pass
                else:
                    message["Interview"][location] = {
                        "Number of slots": num_of_slots,
                        "start date": slot_start_date
                    }
                    slot_type = "Interview"
                    try:
                        slot_date = datetime.strptime(slot_start_date, "%Y-%m-%d").date()
                        self.set_priority_for_notification(slot_date, "Interview")
                    except (ValueError, TypeError):
                        pass

                records.append({
                    'visa_location': location,
                    'slot_type': slot_type,
                    'num_of_slots': num_of_slots,
                    'start_date': slot_start_date,
                    'slot_release_time': slot_release_time
                })
        
        return message, records
    
    def get_priorities(self) -> Dict[str, int]:
        """Get current priorities."""
        return self.priority.copy()
    
    def reset_priorities(self) -> None:
        """Reset priorities to initial config values."""
        self.priority = dict(self.config.priorities)
