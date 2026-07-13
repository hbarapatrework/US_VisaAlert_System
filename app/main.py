import time
from config import Config
from database.database import Database
from .api_client import APIClient
from .polling import PollingManager
from notification.notifications import NotificationManager
from .visa_processor import VisaProcessor
from notification.topic_manager import TopicManager
from .logger import Logger
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
        self.remaining_sessions = 0
    
    def process_slots(self) -> tuple:
        """Fetch and process slot data."""
        try:
            self.logger.info("Fetching visa slots from API...")
            data = self.api_client.get_slots()
            
            slot_details = self.api_client.extract_slot_details(data)
            self.remaining_sessions = self.api_client.get_remaining_sessions(data)
            
            self.logger.info(f"API call successful. Remaining sessions: {self.remaining_sessions}")
            self.logger.debug(data)

            notification_msg, records = self.visa_processor.build_notification_payload(slot_details)

            if records:
                try:
                    self.logger.critical(f"Dates Available: {records}")
                    self.db.insert_slot_records(records)
                    self.logger.debug(f"Stored {len(records)} slot records in database")
                except Exception as e:
                    self.logger.error(f"Failed to insert slot records into database: {e} \n{records}")

            # Create notification message
            priorities = self.visa_processor.get_priorities()
            
            return notification_msg, self.remaining_sessions, priorities
        
        except Exception as e:
            self.logger.error(f"Failed to process slots: {e}")
            if "429" in str(e):
                rs = str(e).split(":")[-1]
                return {}, int(rs), {}
            return {}, int(self.remaining_sessions)-1, {}
    
    def send_notifications(self, message: dict, priorities: dict) -> int:
        """Send notifications for available slots."""
        sent_count = self.notification_manager.send_all_notifications(message, priorities)
        
        if sent_count > 0:
            self.visa_processor.reset_priorities()
            self.logger.info("Priorities reset after sending notifications")
        
        return sent_count
    
    def run_once(self) -> int:
        """Run a single polling cycle."""
        message, remaining_sessions, priorities = self.process_slots()
        sent_count = self.send_notifications(message, priorities)
        
        if sent_count > 0:
            self.logger.info(f"Sent {sent_count} notification(s)")
        
        self.polling_manager.update_poll_time()
        return remaining_sessions
    
    def get_next_wait_time(self, remaining_sessions: int) -> float:
        """Calculate wait time before next poll."""
        return self.polling_manager.get_next_poll_wait_time(remaining_sessions)
    
    def check_reset_time(self) -> bool:
        """Check if it's reset time."""
        return self.polling_manager.is_reset_time()
    
    def start_continuous(self):
        """Start the system in continuous polling mode."""
        self.logger.info("Starting US Visa Alert System...")
        self.logger.info(f"Polling interval: {self.config.min_interval}s - {self.config.max_interval}s")
        self.logger.info(f"Sessions reset daily at {self.config.reset_time}")
        
        try:
            while True:
                if self.check_reset_time():
                    self.logger.warning("Reset time detected (8am) - sessions will be replenished")
                
                remaining_sessions = self.run_once()
                wait_time = self.get_next_wait_time(remaining_sessions)
                
                self.logger.critical(f"Next poll in {int(wait_time)}s (Remaining sessions: {remaining_sessions})")
                
                # Sleep in small increments to allow for graceful shutdown
                start_time = time.time()
                while time.time() - start_time < wait_time:
                    time.sleep(min(1, wait_time - (time.time() - start_time)))
        
        except KeyboardInterrupt:
            self.logger.info("System shutdown requested")
        except Exception as e:
            self.logger.error(f"System error: {e}")
            raise


def main():
    """Entry point."""
    system = VisaAlertSystem()
    system.start_continuous()


if __name__ == "__main__":
    main()
