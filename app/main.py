import time
from config import Config
from database.database import Database
from app.api_client import APIClient
from app.polling import PollingManager
from notification.notifications import NotificationManager
from app.visa_processor import VisaProcessor
from notification.topic_manager import TopicManager
from app.utils import Helper
from app.logger import Logger
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class VisaAlertSystem:
    """Main orchestrator for the visa alert system."""
    
    def __init__(self, config_file: str = BASE_DIR / '.env'):
        self.config = Config(config_file)
        self.logger = Logger()
        
        # Initialize topics if needed
        topic_manager = TopicManager(self.config, self.logger)
        topic_manager.initialize_topics()
        
        # Reinitialize config after topic creation
        self.config = Config(config_file)
        
        self.db = Database(self.config.database_name)
        self.api_client = APIClient(self.config)
        self.polling_manager = PollingManager(self.config)
        self.notification_manager = NotificationManager(self.config)
        self.visa_processor = VisaProcessor(self.config)
        self.util = Helper(self.config)

        self.notification_queue = []
    
    def process_slots(self) -> tuple:
        """Fetch and process slot data."""
        try:
            self.logger.info("Fetching visa slots from API...")
            data = self.api_client.get_slots()
            
            slot_details = self.api_client.extract_slot_details(data)
            key_remaining_sessions = self.api_client.get_remaining_sessions(data)
            api_key = self.api_client.current_api_key
            
            self.logger.info(f"API call successful. {api_key} - Remaining sessions: {key_remaining_sessions}")
            self.logger.debug(data)

            message, records = self.visa_processor.build_notification_payload(slot_details)

            if records:
                try:
                    self.logger.critical(f"Dates Available: {records}")
                    self.db.insert_slot_records(records)
                    self.logger.debug(f"Stored {len(records)} slot records in database")
                except Exception as e:
                    self.logger.error(f"Failed to insert slot records into database: {e} \n{records}")

            # Create notification message
            priorities = self.visa_processor.get_priorities()
            
            # return notification_msg, self.remaining_sessions, priorities
            # message, remaining_sessions, priorities = self.process_slots()
            sent_count = self.send_notifications(message, priorities)

            if sent_count > 0:
                self.logger.info(f"Sent {sent_count} notification(s)")

            self.polling_manager.update_poll_time()
            return key_remaining_sessions, api_key
        
        except Exception as e:

            if "429" in str(e):
                rs = int(str(e).split(":")[-1])
                key = str(e).split(":")[-2]
                self.logger.error(f"Failed to process slots for {key}: {rs}")
                return rs, str(e).split(":")[-2]

            self.logger.error(f"Failed to process slots: {e}")
            return 0, ""
    
    def send_notifications(self, message: dict, priorities: dict, ) -> int:
        """Send notifications for available slots."""
        sent_count = self.notification_manager.send_all_notifications(message, priorities)
        
        if sent_count > 0:
            self.visa_processor.reset_priorities()
            self.logger.info("Priorities reset after sending notifications")
        
        return sent_count

    
    def get_next_wait_time(self, remaining_sessions: int) -> float:
        """Calculate wait time before next poll."""
        return self.polling_manager.get_next_poll_wait_time(remaining_sessions)
    
    def start_continuous(self):
        """Start the system in continuous polling mode."""
        self.logger.info("Starting US Visa Alert System...")
        self.logger.info(f"Polling interval: {self.config.min_interval}s - {self.config.max_interval}s")
        self.logger.info(f"Sessions reset daily at {self.config.reset_time}")
        
        try:
            while True:
                if self.util.is_reset_time():
                    self.logger.warning("Reset time detected - sessions will be replenished")
                    self.notification_queue.clear()
                key_remaining_sessions, key = self.process_slots()
                if key_remaining_sessions <= self.config.critical_threshold:
                    self.logger.warning(f"{key} : Remaining sessions below critical threshold")
                    if not key in self.notification_queue:
                        self.notification_manager.send_notification("session", f"{key}: {key_remaining_sessions} Remaining sessions below critical threshold", 5)
                        self.notification_queue.append(key)

                total_remaining_sessions = self.api_client.get_total_sessions()

                if self.api_client.keys_checked:
                    wait_time = self.get_next_wait_time(total_remaining_sessions)
                else: wait_time = 30 #self.config.min_interval

                self.logger.critical(f"Next poll in {int(wait_time)}s (Total Remaining sessions: {total_remaining_sessions})")

                # Sleep in small increments to allow for graceful shutdown
                start_time = time.time()
                while time.time() - start_time < wait_time:
                    time.sleep(min(1, wait_time - (time.time() - start_time)))
        
        except KeyboardInterrupt:
            self.logger.info("System shutdown requested")
        except Exception as e:
            self.logger.error(f"System error: {e}")
            self.notification_manager.send_notification("session",
                                                        f"System error: {e}.",
                                                        2)


def main():
    """Entry point."""
    system = VisaAlertSystem()
    system.start_continuous()


if __name__ == "__main__":
    main()
