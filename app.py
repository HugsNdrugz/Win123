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
                    sms_type as sender_name,
                    text,
                    time,
                    ROW_NUMBER() OVER (PARTITION BY sms_type ORDER BY time DESC) as rn
                FROM SMS
                UNION ALL
                SELECT 
                    sender as sender_name,
                    text,
                    time,
                    ROW_NUMBER() OVER (PARTITION BY sender ORDER BY time DESC) as rn
                FROM ChatMessages
            )
            SELECT 
                sender_name as name,
                text as last_message,
                time,
                'avatar.png' as avatar,
                1 as unread
            FROM LatestMessages
            WHERE rn = 1
            ORDER BY time DESC
        """
        
        cursor.execute(query)
        chats = [dict(row) for row in cursor.fetchall()]
        
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
                time,
                CASE 
                    WHEN type = 'SMS' THEN 'received'
                    ELSE 'sent'
                END as sender
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