# System Architecture

## Project Structure

```
.
├── app/                          # Main application package
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # VisaAlertSystem orchestrator (Main)
│   ├── config.py                # Configuration management
│   ├── database.py              # SQLite operations
│   ├── api_client.py            # Visa slots API client
│   ├── polling.py               # Polling strategy manager
│   ├── notifications.py         # ntfy.sh notification sender
│   ├── visa_processor.py        # Slot data processing
│   ├── topic_manager.py         # Ntfy topic initialization
│   └── logger.py                # Logging utility
│
├── docs/                         # Documentation
│   ├── ARCHITECTURE.md          # This file
│   ├── ENV_GUIDE.md             # Environment setup
│   └── TOPIC_SETUP.md           # Topic initialization guide
│
├── .env                         # Environment variables
├── .gitignore                   # Git ignore rules
├── requirements.txt             # Python dependencies
├── run.py                       # Entry point script
└── visa_slots.db               # SQLite database
```

## Modules Overview

### 1. **main.py** - VisaAlertSystem Orchestrator

The main controller that coordinates all other modules.

**Responsibilities:**
- Initialize all dependencies
- Manage the polling loop
- Coordinate data flow between modules
- Handle errors and graceful shutdown

**Key Class:**
```python
class VisaAlertSystem:
    def __init__(self, config_file: str = '.env')
    def process_slots(self) -> tuple
    def send_notifications(self, message: dict, priorities: dict) -> int
    def run_once(self) -> int
    def start_continuous(self)
```

**Usage:**
```python
from app.main import VisaAlertSystem

system = VisaAlertSystem()
system.start_continuous()
```

### 2. **config.py** - Configuration Management

Loads and manages all settings from `.env` file.

**Responsibilities:**
- Load environment variables
- Provide easy access to configuration
- Update `.env` file when needed
- Type conversion and validation

**Key Methods:**
```python
class Config:
    def __init__(self, env_file: str = '.env')
    def get(self, key: str, default=None) -> Any
    def set(self, key: str, value: str) -> None
    
    # Properties for easy access
    database_path: str
    api_base_url: str
    api_key: str
    min_interval: float
    max_interval: float
```

**Usage:**

```python
from config import Config

config = Config()
print(config.database_path)
print(config.min_interval)

# Update configuration
config.set('NTFY_TOPIC_VAC', 'new-topic')
```

### 3. **database.py** - Database Operations

Manages SQLite database for storing slot history.

**Responsibilities:**
- Create and initialize database schema
- Insert slot records
- Query historical data
- Connection management

**Key Methods:**
```python
class Database:
    def __init__(self, db_path: str)
    def init_tables(self)
    def insert_slot_record(self, visa_location, slots, start_date, priority)
    def insert_slot_records(self, records: List[Dict])
    def get_recent_slots(self, limit: int) -> List[Dict]
    def get_slot_count_by_location(self, location: str) -> int
```

**Usage:**

```python
from database.database import Database

db = Database('visa_slots.db')
db.insert_slot_record('NEW DELHI', 5, '2026-08-15', 5)
recent = db.get_recent_slots(limit=10)
```

**Schema:**
```sql
CREATE TABLE slot_history (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    visa_location TEXT NOT NULL,
    slots INTEGER NOT NULL,
    start_date TEXT,
    priority INTEGER
)
```

### 4. **api_client.py** - API Interactions

Handles communication with the visa slots API.

**Responsibilities:**
- Fetch visa slots from API
- Extract data from responses
- Handle API errors
- Manage authentication

**Key Methods:**
```python
class APIClient:
    def __init__(self, config: Config)
    def get_slots(self) -> Dict[str, Any]
    def extract_slot_details(self, data: Dict) -> list
    def extract_user_activity(self, data: Dict) -> Dict
    def get_remaining_sessions(self, data: Dict) -> int
```

**Usage:**

```python
from app.api_client import APIClient
from config import Config

client = APIClient(Config())
data = client.get_slots()
remaining = client.get_remaining_sessions(data)
```

### 5. **polling.py** - Polling Management

Manages intelligent polling strategy and timing.

**Responsibilities:**
- Calculate optimal polling intervals
- Track last poll time
- Detect reset times (8am)
- Manage poll scheduling

**Key Methods:**
```python
class PollingManager:
    def __init__(self, config: Config)
    def calculate_interval(self, remaining_sessions: int) -> float
    def should_poll(self) -> bool
    def get_next_poll_wait_time(self, remaining_sessions: int) -> float
    def is_reset_time(self) -> bool
    def update_poll_time(self)
```

**Polling Strategy:**
```
If remaining_sessions <= critical_threshold (10):
    interval = MAX_INTERVAL (600s)
Else:
    ratio = remaining_sessions / max_daily_polls
    interval = MIN_INTERVAL + (MAX_INTERVAL - MIN_INTERVAL) * (1 - ratio)
```

**Usage:**
```python
from app.polling import PollingManager

poller = PollingManager(Config())
interval = poller.calculate_interval(remaining_sessions=50)
wait_time = poller.get_next_poll_wait_time(50)
```

### 6. **notifications.py** - Notification System

Sends alerts via ntfy.sh service.

**Responsibilities:**
- Format notification messages
- Send to ntfy.sh topics
- Handle multiple alert types
- Manage notification priorities

**Key Methods:**
```python
class NotificationManager:
    def __init__(self, config: Config)
    def send_notification(self, alert_type: str, message: Dict, priority: int) -> bool
    def send_all_notifications(self, messages: Dict, priorities: Dict) -> int
```

**Usage:**

```python
from notification.notifications import NotificationManager

notifier = NotificationManager(Config())
notifier.send_notification('VAC', {'DELHI': 5}, priority=5)
```

### 7. **visa_processor.py** - Slot Data Processing

Processes visa slot data and manages priorities.

**Responsibilities:**
- Parse slot details from API response
- Calculate dynamic priorities
- Create notification messages
- Track priority state

**Key Methods:**
```python
class VisaProcessor:
    def __init__(self, config: Config)
    def get_target_start_date(self) -> date
    def set_priority(self, slot_date: date, key: str) -> None
    def create_message(self, slot_details: list) -> Dict
    def reset_priorities(self) -> None
    def get_priorities(self) -> Dict[str, int]
```

**Priority Calculation:**
```
Priority 5: target_date <= slot_date < target_date + 60 days
Priority 4: target_date + 60 <= slot_date < target_date + 90 days
Priority 3: target_date + 90 <= slot_date < target_date + 120 days
Priority 2: target_date + 120 <= slot_date < target_date + 150 days
Priority 1: slot_date >= target_date + 150 days
```

**Usage:**
```python
from app.visa_processor import VisaProcessor

processor = VisaProcessor(Config())
message = processor.create_message(slot_details)
processor.reset_priorities()
```

### 8. **topic_manager.py** - Topic Initialization

Manages automatic ntfy.sh topic creation.

**Responsibilities:**
- Check if topics are configured
- Generate unique topics
- Save topics to `.env`
- Display topic URLs

**Key Methods:**
```python
class TopicManager:
    def __init__(self, config: Config, logger: Logger)
    def generate_topic(self, prefix: str = "usvisa") -> str
    def are_topics_empty(self) -> bool
    def initialize_topics(self) -> Dict[str, str]
```

**Usage:**

```python
from notification.topic_manager import TopicManager

topic_mgr = TopicManager(Config(), Logger())
topics = topic_mgr.initialize_topics()
```

### 9. **logger.py** - Logging Utility

Provides centralized logging with timestamps.

**Responsibilities:**
- Format log messages
- Add timestamps
- Support multiple log levels
- Display to console

**Key Methods:**
```python
class Logger:
    @staticmethod
    def info(message: str)
    @staticmethod
    def error(message: str)
    @staticmethod
    def warning(message: str)
    @staticmethod
    def debug(message: str)
```

**Usage:**
```python
from app.logger import Logger

logger = Logger()
logger.info("System started")
logger.error("API failed")
```

## Data Flow

### Complete Polling Cycle

```
START
  ↓
Check if polling interval elapsed
  ↓
YES → Fetch slots from API (APIClient)
  ↓
Extract slot details & user activity
  ↓
Store slots in database (Database)
  ↓
Process slots & calculate priorities (VisaProcessor)
  ↓
Create notification message
  ↓
Send notifications (NotificationManager)
  ↓
Reset priorities (VisaProcessor)
  ↓
Update last poll time (PollingManager)
  ↓
Calculate next wait time (PollingManager)
  ↓
Sleep & repeat
```

## Design Principles

### 1. Single Responsibility Principle
Each module has one clear responsibility:
- `APIClient` - Only handles API communication
- `Database` - Only handles data persistence
- `PollingManager` - Only manages timing
- `NotificationManager` - Only sends alerts

### 2. Dependency Injection
Modules receive dependencies through constructor:
```python
class NotificationManager:
    def __init__(self, config: Config):
        self.config = config  # Injected dependency
```

### 3. Loose Coupling
Modules are independent and communicate through interfaces:
- Modules don't import other modules directly
- Main orchestrator coordinates interactions
- Easy to replace implementations

### 4. High Cohesion
Related functionality is grouped together:
- All database operations in one module
- All notification logic in one module
- All configuration in one module

### 5. Extensibility
Easy to add new features without modifying existing code:
- Add new notification channels
- Add new database backends
- Add new data processors

## Extending the System

### Add Email Notifications

Create `app/email_notifier.py`:
```python
import smtplib
from .config import Config

class EmailNotifier:
    def __init__(self, config: Config):
        self.config = config
    
    def send_email(self, to: str, subject: str, message: str):
        # Implementation
        pass
```

Update `main.py`:
```python
from .email_notifier import EmailNotifier

class VisaAlertSystem:
    def __init__(self, config_file: str = '.env'):
        # ... existing code ...
        self.email_notifier = EmailNotifier(self.config)
    
    def send_notifications(self, message, priorities):
        # Send ntfy notifications
        self.notification_manager.send_all_notifications(message, priorities)
        # Also send emails
        for location in message.get('VAC', {}):
            self.email_notifier.send_email(
                'user@example.com',
                f'VAC Slot Available: {location}',
                str(message)
            )
```

### Add Webhook Support

Create `app/webhook_client.py`:
```python
import requests
from .config import Config

class WebhookClient:
    def __init__(self, config: Config):
        self.config = config
    
    def send_webhook(self, url: str, data: dict) -> bool:
        try:
            response = requests.post(url, json=data)
            return response.status_code == 200
        except:
            return False
```

### Add PostgreSQL Support

Extend `database.py`:
```python
import psycopg2
from .config import Config

class PostgresDatabase:
    def __init__(self, config: Config):
        self.conn = psycopg2.connect(config.db_connection_string)
    
    def insert_slot_record(self, visa_location, slots, start_date, priority):
        # PostgreSQL implementation
        pass
```

### Add Web Dashboard

Create `app/web_server.py`:
```python
from flask import Flask, render_template
from .database import Database

class WebServer:
    def __init__(self, config, database):
        self.app = Flask(__name__)
        self.db = database
        self.setup_routes()
    
    def setup_routes(self):
        @self.app.route('/slots')
        def slots():
            return self.db.get_recent_slots()
    
    def run(self, port=5000):
        self.app.run(port=port)
```

## Configuration Hierarchy

```
1. Defaults (in code)
     ↓
2. .env file (environment variables)
     ↓
3. Runtime config.set() (if needed)
```

## Error Handling

All modules include error handling:

```python
try:
    data = self.api_client.get_slots()
except Exception as e:
    self.logger.error(f"API call failed: {e}")
    # Continue with next cycle
```

## Performance Considerations

1. **Database:** SQLite suitable for single-machine use. For distributed systems, use PostgreSQL.
2. **API Calls:** Intelligent polling reduces API usage
3. **Memory:** Uses generators for large datasets
4. **Concurrency:** Current design is single-threaded. For multi-threading, use locks.

## Testing

Each module can be tested independently:

```python
# Test Configuration
config = Config('.env.test')
assert config.database_path == 'test.db'

# Test APIClient
client = APIClient(config)
data = client.get_slots()
assert 'slotDetails' in data

# Test Database
db = Database(':memory:')  # In-memory for testing
db.insert_slot_record('TEST', 5, '2026-08-15', 5)
slots = db.get_recent_slots()
assert len(slots) == 1
```

## Future Enhancements

- [ ] Async/concurrent polling
- [ ] Multiple database backends
- [ ] Message queue integration (Kafka/RabbitMQ)
- [ ] Metrics and monitoring (Prometheus)
- [ ] Configuration profiles (dev/prod)
- [ ] Multi-user support
- [ ] Web UI
- [ ] Mobile app
- [ ] Docker containerization
- [ ] Kubernetes deployment
