# US Visa Alert System - Environment Configuration

This project uses `.env` files for configuration management.

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Edit `.env` file to set your configuration:

```env
# Database
DATABASE_PATH=visa_slots.db

# API Settings
API_BASE_URL=https://app.checkvisaslots.com/slots/v3
API_USER_AGENT=Mozilla/5.0
API_KEY=YOUR_API_KEY

# Notifications
NTFY_BASE_URL=https://ntfy.sh
NTFY_TOPIC_VAC=your-topic
NTFY_TOPIC_INTERVIEW=your-topic
NTFY_CLICK_URL=https://www.usvisascheduling.com

# Priorities (1-5)
PRIORITY_VAC=1
PRIORITY_INTERVIEW=1

# Target date for visa appointment
TARGET_DAYS_AHEAD=10

# Polling Strategy
POLLING_RESET_TIME=08:00
POLLING_MAX_DAILY_POLLS=100
POLLING_MIN_INTERVAL_SECONDS=60
POLLING_MAX_INTERVAL_SECONDS=600
POLLING_CRITICAL_THRESHOLD=10
```

### 3. Run the System
```bash
python main_new.py
```

## Configuration Variables

### Database
- `DATABASE_PATH` - SQLite database file location

### API
- `API_BASE_URL` - Visa slots API endpoint
- `API_USER_AGENT` - User agent for API requests
- `API_KEY` - API authentication key

### Notifications
- `NTFY_BASE_URL` - ntfy.sh service URL
- `NTFY_TOPIC_VAC` - Topic for VAC notifications
- `NTFY_TOPIC_INTERVIEW` - Topic for Interview notifications
- `NTFY_CLICK_URL` - Click action URL

### Priorities
- `PRIORITY_VAC` - Initial priority level for VAC slots (1-5)
- `PRIORITY_INTERVIEW` - Initial priority level for Interview slots (1-5)

### Polling
- `POLLING_RESET_TIME` - Time when sessions reset daily (HH:MM format)
- `POLLING_MAX_DAILY_POLLS` - Maximum expected polls per day
- `POLLING_MIN_INTERVAL_SECONDS` - Minimum wait between polls
- `POLLING_MAX_INTERVAL_SECONDS` - Maximum wait between polls
- `POLLING_CRITICAL_THRESHOLD` - Session count threshold for max interval

## Environment Files

You can create different `.env` files for different environments:

```bash
# Development
python main_new.py  # Uses .env (default)

# Production (create .env.production)
export ENV_FILE=.env.production
# Update config.py to read: load_dotenv(os.getenv('ENV_FILE', '.env'))
```

## Security Notes

⚠️ **Never commit `.env` files to version control!**

Add to `.gitignore`:
```
.env
.env.local
.env.*.local
```

Keep sensitive information (API keys) only in your local `.env` file.
