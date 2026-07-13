import sqlite3
from typing import List, Dict, Any
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Database:
    """Handle all database operations."""
    
    def __init__(self, db_name: str):
        self.db_path = BASE_DIR / db_name
        self.init_tables()
    
    def get_connection(self):
        """Get database connection."""
        return sqlite3.connect(self.db_path)

    def convert_timestamp(self, dt: str) -> str:
        utc_dt = datetime.strptime(
            dt,"%a, %d %b %Y %H:%M:%S GMT"
        ).replace(tzinfo=ZoneInfo("UTC"))

        local_dt = utc_dt.astimezone(ZoneInfo("America/Los_Angeles"))
        return local_dt.strftime("%a, %d %b %Y %H:%M:%S PST")

    def init_tables(self):
        """Initialize database tables if they don't exist."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS slot_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                visa_location TEXT NOT NULL,
                slot_type TEXT NOT NULL,
                num_of_slots INTEGER NOT NULL,
                start_date TEXT,
                slot_release_time TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def insert_slot_record(self, visa_location: str, slot_type: str, num_of_slots: int, start_date: str, slot_release_time: str):
        """Insert a single slot record."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO slot_history (visa_location, slot_type, num_of_slots, start_date, slot_release_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (visa_location, slot_type, num_of_slots, start_date, slot_release_time))
        
        conn.commit()
        conn.close()
    
    def insert_slot_records(self, records: List[Dict[str, Any]]):
        """Insert multiple slot records."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        for record in records:
            cursor.execute('''
                INSERT INTO slot_history (visa_location, slot_type, num_of_slots, start_date, slot_release_time)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                record.get('visa_location'),
                record.get('slot_type'),
                record.get('num_of_slots', 0),
                record.get('start_date'),
                record.get('slot_release_time')
            ))
        
        conn.commit()
        conn.close()
    
    def get_recent_slots(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent slot records."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, visa_location, slot_type, num_of_slots, start_date, slot_release_time
            FROM slot_history
            ORDER BY slot_release_time DESC
            LIMIT ?
        ''', (limit,))
        
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def get_slot_count_by_location(self, location: str) -> int:
        """Get latest slot count for a specific location."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT num_of_slots FROM slot_history
            WHERE visa_location = ?
            ORDER BY slot_release_time DESC
            LIMIT 1
        ''', (location,))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else 0

    def clear_table(self):
        """Delete all records from slot_history."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM slot_history")

        conn.commit()
        conn.close()

# if __name__ == "__main__":
#     db = Database("test_database.db")
#     db.init_tables()
#     print("\nInserting single record...")
#
#     db.insert_slot_record(
#         visa_location="HYDERABAD",
#         slot_type="APPOINTMENT",
#         num_of_slots=12,
#         start_date="2026-08-15",
#         slot_release_time="Sun, 12 Jul 2026 00:31:15 GMT"
#     )