import sqlite3
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def inspect_database():
    try:
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        logger.info("Database Tables:")
        for table in tables:
            table_name = table[0]
            logger.info(f"\nTable: {table_name}")
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            logger.info("Columns:")
            for col in columns:
                logger.info(f"  {col[1]} ({col[2]})")
            
            # Get sample data
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 1;")
            sample = cursor.fetchone()
            if sample:
                logger.info(f"Sample data: {sample}")
                
        conn.close()
    except Exception as e:
        logger.error(f"Error inspecting database: {e}")

if __name__ == "__main__":
    inspect_database()
