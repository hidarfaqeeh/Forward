
import sqlite3
import os
import json
import logging

logger = logging.getLogger(__name__)

class DatabaseHandler:
    def __init__(self, bot_id):
        """Initialize database for specific bot instance"""
        self.db_path = f"clones/{bot_id}/bot_data.db"
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_database()

    def init_database(self):
        """Create necessary tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS message_history (
                    message_id INTEGER PRIMARY KEY,
                    source_message_id INTEGER,
                    target_message_id INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def save_settings(self, settings):
        """Save bot settings to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                         ("bot_settings", json.dumps(settings)))
            conn.commit()

    def load_settings(self):
        """Load bot settings from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", ("bot_settings",))
            result = cursor.fetchone()
            return json.loads(result[0]) if result else {}
