import uuid
from typing import Dict
from config import Config
from app.logger import Logger


class TopicManager:
    """Manage ntfy topics initialization and validation."""
    
    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger
    
    def generate_topic(self, prefix: str = "usvisa") -> str:
        """Generate a unique topic name."""
        return f"{str(uuid.uuid4())[:8]}-{prefix}-{str(uuid.uuid4())}"
    
    def are_topics_empty(self) -> bool:
        """Check if ntfy topics are empty or not set."""
        topics = self.config.topics
        vac_topic = topics.get('vac', '')
        interview_topic = topics.get('interview', '')
        
        return not vac_topic or not interview_topic
    
    def initialize_topics(self) -> Dict[str, str]:
        """Initialize topics if they are empty."""
        if not self.are_topics_empty():
            self.logger.info("Topics already configured")
            return self.config.topics
        
        self.logger.warning("Topics not configured. Generating new topics...")
        
        # Generate topics
        vac_topic = self.generate_topic("habit-usvisa-vac")
        interview_topic = self.generate_topic("habit-usvisa-interview")
        
        # Save to .env file
        self.config.set('NTFY_TOPIC_VAC', vac_topic)
        self.config.set('NTFY_TOPIC_INTERVIEW', interview_topic)
        
        self.logger.info(f"New topics created and saved to .env:")
        self.logger.info(f"  VAC Topic: {vac_topic}")
        self.logger.info(f"  Interview Topic: {interview_topic}")
        self.logger.info(f"Share these topics to receive notifications:")
        self.logger.info(f"  https://ntfy.sh/{vac_topic}")
        self.logger.info(f"  https://ntfy.sh/{interview_topic}")
        
        # Reload configuration to get updated topics
        self.config = Config()
        return self.config.topics

# if __name__ == "__main__":
#     topic_manager = TopicManager(Config(), Logger())
#     print(topic_manager.generate_topic())
