import sqlite3
from contextlib import contextmanager
import logging
import os

DATABASE_PATH = "data.db"

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
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        # Enable foreign key support
        conn.execute("PRAGMA foreign_keys = ON")
        yield conn
    except Exception as e:
        logging.error(f"Database connection error: {e}")
        raise
    finally:
        conn.close()

def get_chat_messages():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    conversation_id,
                    MAX(timestamp) as last_message_time,
                    COUNT(*) as message_count
                FROM chat_messages 
                WHERE NOT is_archived
                GROUP BY conversation_id
                ORDER BY last_message_time DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        logging.error(f"Error fetching chat messages: {e}")
        return []

def get_sms_messages():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    phone_number,
                    MAX(timestamp) as last_message_time,
                    COUNT(*) as message_count
                FROM sms_messages
                WHERE NOT is_archived
                GROUP BY phone_number
                ORDER BY last_message_time DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        logging.error(f"Error fetching SMS messages: {e}")
        return []

def get_call_logs():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    caller_id,
                    receiver_id,
                    start_time,
                    duration,
                    call_type
                FROM call_logs
                WHERE NOT is_archived
                ORDER BY start_time DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        logging.error(f"Error fetching call logs: {e}")
        return []

def get_archived_items():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    ai.id,
                    ai.item_type,
                    ai.archive_date,
                    CASE 
                        WHEN ai.item_type = 'chat' THEN cm.content
                        WHEN ai.item_type = 'sms' THEN sm.content
                        WHEN ai.item_type = 'call' THEN cl.duration || ' seconds'
                    END as content
                FROM archived_items ai
                LEFT JOIN chat_messages cm ON ai.item_type = 'chat' AND ai.item_id = cm.id
                LEFT JOIN sms_messages sm ON ai.item_type = 'sms' AND ai.item_id = sm.id
                LEFT JOIN call_logs cl ON ai.item_type = 'call' AND ai.item_id = cl.id
                ORDER BY ai.archive_date DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        logging.error(f"Error fetching archived items: {e}")
        return []
