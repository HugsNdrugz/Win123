from flask import Flask, render_template, jsonify
import sqlite3
from datetime import datetime
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
db_path = os.path.join(os.getcwd(), 'data.db')

def get_db():
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    return db

def format_datetime(timestamp):
    try:
        if isinstance(timestamp, str):
            dt_object = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        else:
            dt_object = datetime.fromtimestamp(timestamp)
        return dt_object.strftime("%b %d, %I:%M %p")
    except (ValueError, TypeError) as e:
        logger.error(f"Error formatting timestamp {timestamp}: {str(e)}")
        return str(timestamp)

# Route: Home page
@app.route('/')
def index():
    return render_template('index.html')

# API: Get all chats
@app.route('/api/chats')
def get_chats():
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Query to get all conversations with their latest messages
        query = """
            WITH LatestMessages AS (
                SELECT 
                    CASE
                        WHEN sms_type IS NOT NULL THEN sms_type
                        ELSE sender
                    END as sender_name,
                    text,
                    CASE
                        WHEN time LIKE '%+%' THEN strftime('%s', substr(time, 1, instr(time, '+') - 1))
                        ELSE time
                    END as timestamp,
                    ROW_NUMBER() OVER (PARTITION BY CASE WHEN sms_type IS NOT NULL THEN sms_type ELSE sender END ORDER BY time DESC) as rn
                FROM (
                    SELECT sms_type, text, time, NULL as sender FROM SMS
                    UNION ALL
                    SELECT NULL as sms_type, text, time, sender FROM ChatMessages
                )
            )
            SELECT 
                sender_name as name,
                text as last_message,
                datetime(timestamp, 'unixepoch') as time,
                'avatar.png' as avatar,
                1 as unread
            FROM LatestMessages
            WHERE rn = 1
            ORDER BY timestamp DESC
        """
        
        cursor.execute(query)
        chats = []
        for row in cursor.fetchall():
            chat_dict = {}
            for idx, col in enumerate(cursor.description):
                chat_dict[col[0]] = row[idx]
            chats.append(chat_dict)
            
        logger.debug(f"Retrieved chats: {chats}")
        return jsonify(chats)
    except Exception as e:
        logger.error(f"Error fetching chats: {e}")
        return jsonify({'error': str(e)}), 500

# API: Get messages for a conversation
@app.route('/api/messages/<sender>')
def get_messages(sender):
    try:
        db = get_db()
        cursor = db.cursor()
        
        query = """
            SELECT 
                text,
                datetime(time, 'unixepoch') as formatted_time,
                CASE 
                    WHEN type = 'SMS' THEN 'received'
                    ELSE 'sent'
                END as message_type
            FROM (
                SELECT text, time, 'SMS' as type FROM SMS WHERE sms_type = ?
                UNION ALL
                SELECT text, time, 'Chat' as type FROM ChatMessages WHERE sender = ?
            )
            ORDER BY time ASC
        """
        
        cursor.execute(query, (sender, sender))
        messages = [dict(row) for row in cursor.fetchall()]
        
        return jsonify(messages)
    except Exception as e:
        logger.error(f"Error fetching messages: {e}")
        return jsonify({'error': str(e)}), 500

# Route: Calls View
@app.route('/calls')
def calls():
    query = "SELECT call_type, from_to, time, duration FROM Calls ORDER BY time DESC"
    calls = fetch_query(query)
    formatted_calls = [
        {"type": call_type, "from_to": from_to, "time": format_datetime(time), "duration": duration}
        for call_type, from_to, time, duration in calls
    ]
    return render_template('calls.html', calls=formatted_calls)

# Route: Apps View
@app.route('/apps')
def apps():
    query = "SELECT application_name, install_date FROM InstalledApps ORDER BY install_date DESC"
    apps = fetch_query(query)
    formatted_apps = [
        {"name": app_name, "date": format_datetime(install_date)}
        for app_name, install_date in apps
    ]
    return render_template('apps.html', apps=formatted_apps)

if __name__ == '__main__':
    app.run(debug=True)