from datetime import datetime, timedelta
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Logger:
    """Simple logging utility."""

    LOG_DIR = BASE_DIR / "logs"

    @classmethod
    def _initialize(cls):
        """Create log directory and remove old log files."""
        os.makedirs(cls.LOG_DIR, exist_ok=True)

        cutoff = datetime.now().date() - timedelta(days=3)

        for filename in os.listdir(cls.LOG_DIR):
            if not filename.endswith(".log"):
                continue

            try:
                file_date = datetime.strptime(
                    filename.replace(".log", ""),
                    "%Y-%m-%d"
                ).date()

                if file_date < cutoff:
                    os.remove(os.path.join(cls.LOG_DIR, filename))

            except ValueError:
                # Ignore files that don't match YYYY-MM-DD.log
                pass

    @classmethod
    def _write(cls, level: str, message: str):
        """Write a log entry to today's log file."""
        cls._initialize()

        now = datetime.now()
        log_file = os.path.join(
            cls.LOG_DIR,
            f"{now:%Y-%m-%d}.log"
        )

        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {level}: {message}\n")

        if level in ["ERROR", "CRITICAL"]:
            print(f"[{timestamp}] {level}: {message}")

    @classmethod
    def info(cls, message: str):
        cls._write("INFO", message)

    @classmethod
    def warning(cls, message: str):
        cls._write("WARNING", message)

    @classmethod
    def error(cls, message: str):
        cls._write("ERROR", message)

    @classmethod
    def debug(cls, message: str):
        cls._write("DEBUG", message)

    @classmethod
    def critical(cls, message: str):
        cls._write("CRITICAL", message)
