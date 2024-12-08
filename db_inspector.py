import sqlite3
import json
from pprint import pprint
from datetime import datetime

def test_queries():
    try:
        # Connect to the database
        conn = sqlite3.connect('data.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("\n=== Testing Chat List Query ===")
        chat_query = """
            SELECT 
                'SMS' as type,
                sms_type as sender,
                text as last_message,
                time,
                'avatar.png' as avatar
            FROM SMS 
            GROUP BY sms_type
            HAVING time = MAX(time)
            UNION ALL
            SELECT 
                'Chat' as type,
                sender,
                text as last_message,
                time,
                'avatar.png' as avatar
            FROM ChatMessages
            GROUP BY sender
            HAVING time = MAX(time)
            ORDER BY time DESC;
        """
        cursor.execute(chat_query)
        chats = [dict(row) for row in cursor.fetchall()]
        print("\nChat List Results:")
        pprint(chats)
        
        print("\n=== Testing Message Query ===")
        # Test with a sample sender from the chats
        if chats:
            sample_sender = chats[0]['sender']
            print(f"\nTesting messages for sender: {sample_sender}")
            
            message_query = """
                SELECT 
                    'SMS' as type,
                    COALESCE(sms_type, from_to) as sender,
                    text,
                    time,
                    location
                FROM SMS 
                WHERE sms_type = ? OR from_to = ?
                UNION ALL
                SELECT 
                    'Chat' as type,
                    COALESCE(sender, messenger) as sender,
                    text,
                    time,
                    NULL as location
                FROM ChatMessages
                WHERE sender = ? OR messenger = ?
                ORDER BY time ASC;
            """
            cursor.execute(message_query, (sample_sender, sample_sender, sample_sender, sample_sender))
            messages = [dict(row) for row in cursor.fetchall()]
            print("\nMessage Results:")
            pprint(messages)
            
            # Verify data types and required fields
            print("\n=== Data Validation ===")
            for msg in messages:
                print(f"\nMessage validation for: {msg}")
                required_fields = ['type', 'sender', 'text', 'time']
                missing_fields = [field for field in required_fields if field not in msg]
                if missing_fields:
                    print(f"Warning: Missing required fields: {missing_fields}")
                
                print("Field Types:")
                for key, value in msg.items():
                    print(f"{key}: {type(value).__name__} = {value}")

    except Exception as e:
        print(f"Error testing queries: {e}")
    finally:
        if conn:
            conn.close()

def inspect_schema():
    try:
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        
        print("\n=== Database Schema ===")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            print(f"\nTable: {table_name}")
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            print("Columns:")
            for col in columns:
                print(f"  {col[1]}: {col[2]}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"Row count: {count}")

    except Exception as e:
        print(f"Error inspecting schema: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("=== Database Inspection ===")
    inspect_schema()
    print("\n=== Query Testing ===")
    test_queries()
