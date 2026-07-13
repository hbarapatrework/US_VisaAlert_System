# US Visa Alert System 🎯

An intelligent, modular, and scalable monitoring system for US visa appointment slots. Automatically tracks available slots, manages API polling rates, and sends real-time notifications via ntfy.sh.

## ✨ Features

- 🔍 **Intelligent Polling** - Adjusts polling frequency based on remaining API sessions
- 🔔 **Auto Topic Creation** - Automatically generates unique ntfy.sh topics on first run
- 💾 **Database Storage** - Stores all slot history for analysis and tracking
- 📊 **Priority Management** - Dynamically calculates priority based on visa appointment dates
- ⚙️ **Environment Configuration** - Simple `.env` file for all settings
- 🏗️ **Modular Architecture** - Clean, extensible, production-ready design
- 🔄 **Reset Management** - Tracks 8am session reset and adjusts polling accordingly
- 🚀 **Production Ready** - Error handling, logging, graceful shutdown

## 🚀 Installation & Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the system
python run.py
```

The system automatically:
- Creates `.env` configuration
- Generates unique ntfy.sh topics
- Initializes the database
- Starts monitoring

## 📁 Project Structure

```
.
├── app/                    # Main application modules
│   ├── main.py            # Main orchestrator
│   ├── config.py          # Configuration manager
│   ├── database.py        # Database operations
│   ├── api_client.py      # API interactions
│   ├── polling.py         # Polling strategy
│   ├── notifications.py   # Notification sending
│   ├── visa_processor.py  # Data processing
│   ├── topic_manager.py   # Topic initialization
│   └── logger.py          # Logging
│
├── docs/                  # Documentation
│   ├── ARCHITECTURE.md    # System architecture
│   ├── ENV_GUIDE.md       # Environment setup
│   └── TOPIC_SETUP.md     # Topic initialization
│
├── run.py                 # Entry point
├── .env                   # Configuration (auto-generated)
├── requirements.txt       # Dependencies
└── visa_slots.db         # Database (auto-created)
```

## 📚 Documentation

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture and module details
- **[ENV_GUIDE.md](docs/ENV_GUIDE.md)** - Environment configuration
- **[TOPIC_SETUP.md](docs/TOPIC_SETUP.md)** - Topic setup and troubleshooting

## 🏗️ Architecture

**Modular Design:**
- ✅ Single Responsibility Principle
- ✅ Dependency Injection
- ✅ Loose Coupling
- ✅ Easy to Test & Extend

## 💡 Key Features

### Intelligent Polling
Adjusts frequency based on remaining sessions:
- 100+ sessions → 60s polling
- 10-50 sessions → Proportional
- < 10 sessions → 600s polling

### Auto Topic Creation
First run generates unique topics:
```
https://ntfy.sh/usvisa-vac-a1b2c3d4
https://ntfy.sh/usvisa-interview-e5f6g7h8
```

### Database Storage
Tracks all slot availability history for analysis.

### Priority Management
Dynamically calculates based on appointment dates.

## 🔧 Configuration

Edit `.env` to customize:
```env
POLLING_MIN_INTERVAL_SECONDS=60
POLLING_MAX_INTERVAL_SECONDS=600
POLLING_RESET_TIME=08:00
TARGET_DAYS_AHEAD=10
```

## 📞 Support

1. Check [docs/](docs/) for detailed guides
2. See troubleshooting in respective docs
3. Review source code comments

## 🎯 Roadmap

- [ ] Email notifications
- [ ] Webhook support
- [ ] Web dashboard
- [ ] PostgreSQL support
- [ ] Docker containerization
- [ ] Unit tests

---

**Happy visa hunting! 🎉**
