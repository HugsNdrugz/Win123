import sqlite3
from contextlib import contextmanager
import logging
import os

DATABASE_PATH = "messages.db"

def init_db():
    """Initialize the database with schema"""
    try:
        with get_db_connection() as conn:
            with open('schema.sql', 'r') as f:
                conn.executescript(f.read())
            conn.commit()
            logging.info("Database initialized with schema")
    except Exception as e:
        logging.error(f"Error initializing database: {e}")
        raise

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def get_chat_data():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    conversation_id,
                    MAX(timestamp) as last_message_time,
                    COUNT(*) as message_count
                FROM messages 
                GROUP BY conversation_id
                ORDER BY last_message_time DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        logging.error(f"Error fetching chat data: {e}")
        return []

def get_chat_statistics():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    strftime('%Y-%m', timestamp) as month,
                    COUNT(*) as message_count,
                    COUNT(DISTINCT sender_id) as unique_senders
                FROM messages
                GROUP BY month
                ORDER BY month
            """)
            return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        logging.error(f"Error fetching statistics: {e}")
        return []

def get_archived_chats():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM archived_conversations
                ORDER BY archive_date DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        logging.error(f"Error fetching archived chats: {e}")
        return []
