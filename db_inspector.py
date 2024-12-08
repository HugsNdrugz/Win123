import sqlite3
import json
from pprint import pprint

def inspect_database():
    try:
        # Connect to the database
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        schema = {}
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            # Get sample data
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 1;")
            sample = cursor.fetchone()
            
            schema[table_name] = {
                'columns': [{'name': col[1], 'type': col[2]} for col in columns],
                'sample': sample
            }
        
        pprint(schema)
        return schema
    except Exception as e:
        print(f"Error inspecting database: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    inspect_database()
