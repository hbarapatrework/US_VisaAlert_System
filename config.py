import os
from pathlib import Path
from dotenv import load_dotenv
from app.logger import Logger

BASE_DIR = Path(__file__).resolve().parent

class Config:
    """Configuration manager using .env file."""
    
    def __init__(self, env_file=BASE_DIR / ".env"):
        self.env_file = env_file
        load_dotenv(env_file)
        Logger().info("Configuration loaded.")
    
    def get(self, key: str, default=None):
        """Get configuration value from environment variables."""
        return os.getenv(key, default)
    
    def set(self, key: str, value: str) -> None:
        """Set configuration value in environment and .env file."""
        # Set in current environment
        os.environ[key] = str(value)
        
        # Update .env file
        self._update_env_file(key, value)
    
    def _update_env_file(self, key: str, value: str) -> None:
        """Update or add key-value pair in .env file."""
        env_path = self.env_file
        
        if not os.path.exists(env_path):
            # Create .env file if it doesn't exist
            with open(env_path, 'w') as f:
                f.write(f"{key}={value}\n")
            return
        
        # Read existing content
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        # Find and update or append
        updated = False
        for i, line in enumerate(lines):
            if line.startswith(f"{key}="):
                lines[i] = f"{key}={value}\n"
                updated = True
                break
        
        if not updated:
            lines.append(f"{key}={value}\n")
        
        # Write back
        with open(env_path, 'w') as f:
            f.writelines(lines)
    
    def get(self, key: str, default=None):
        """Get configuration value from environment variables."""
        return os.getenv(key, default)
    
    @property
    def database_name(self) -> str:
        return self.get('DATABASE_NAME', 'visa_slots.db')
    
    @property
    def api_base_url(self) -> str:
        return self.get('API_BASE_URL')
    
    @property
    def api_key(self) -> str:
        return self.get('API_KEY')
    
    @property
    def user_agent(self) -> str:
        return self.get('API_USER_AGENT')
    
    @property
    def ntfy_base_url(self) -> str:
        return self.get('NTFY_BASE_URL')
    
    @property
    def topics(self) -> dict:
        return {
            'vac': self.get('NTFY_TOPIC_VAC'),
            'interview': self.get('NTFY_TOPIC_INTERVIEW')
        }
    
    @property
    def click_url(self) -> str:
        return self.get('NTFY_CLICK_URL')
    
    @property
    def priorities(self) -> dict:
        return {
            'VAC': int(self.get('PRIORITY_VAC', 1)),
            'Interview': int(self.get('PRIORITY_INTERVIEW', 1))
        }
    
    @property
    def target_days_ahead(self) -> int:
        return int(self.get('TARGET_DAYS_AHEAD', 10))
    
    @property
    def reset_time(self) -> str:
        return self.get('POLLING_RESET_TIME', '08:00')
    
    @property
    def max_daily_polls(self) -> int:
        return int(self.get('POLLING_MAX_DAILY_POLLS', 100))
    
    @property
    def min_interval(self) -> float:
        return float(self.get('POLLING_MIN_INTERVAL_SECONDS', 60))
    
    @property
    def max_interval(self) -> float:
        return float(self.get('POLLING_MAX_INTERVAL_SECONDS', 600))
    
    @property
    def critical_threshold(self) -> int:
        return int(self.get('POLLING_CRITICAL_THRESHOLD', 10))

# if __name__ == '__main__':
#     config = Config()
#     print(config.ntfy_base_url)
#     print(config.api_key)