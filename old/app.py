from flask import Flask, render_template, jsonify, send_from_directory
import sqlite3
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates', static_folder='static')
db_path = os.path.join(os.getcwd(), 'data.db')

def get_db():
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    return db

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/conversations')
def get_conversations():
    try:
        logger.debug("Fetching conversations list")
        db = get_db()
        cursor = db.cursor()
        
        query = """
            SELECT 
                'SMS' as type,
                CASE 
                    WHEN sms_type = 'Sent' THEN from_to
                    ELSE sms_type 
                END as sender,
                text as last_message,
                time,
                'avatar.png' as avatar,
                location
            FROM SMS 
            WHERE time IN (
                SELECT MAX(time) 
                FROM SMS 
                GROUP BY CASE 
                    WHEN sms_type = 'Sent' THEN from_to
                    ELSE sms_type 
                END
            )
            UNION ALL
            SELECT 
                'Chat' as type,
                COALESCE(sender, messenger) as sender,
                text as last_message,
                time,
                'avatar.png' as avatar,
                NULL as location
            FROM ChatMessages
            WHERE time IN (
                SELECT MAX(time)
                FROM ChatMessages
                GROUP BY COALESCE(sender, messenger)
            )
            ORDER BY time DESC;
        """
        
        logger.debug("Executing chat list query")
        cursor.execute(query)
        
        raw_results = cursor.fetchall()
        logger.debug(f"Raw chat results from database: {[dict(row) for row in raw_results]}")
        
        chats = []
        for row in raw_results:
            logger.debug(f"Processing chat row: {dict(row)}")
            try:
                chat_dict = {
                    'type': row['type'],
                    'name': row['sender'],
                    'last_message': row['last_message'],
                    'time': row['time'],
                    'avatar': row['avatar']
                }
                chats.append(chat_dict)
                logger.debug(f"Successfully processed chat: {chat_dict}")
            except Exception as row_error:
                logger.error(f"Error processing chat row {dict(row)}: {str(row_error)}")
                continue
            
        logger.info(f"Retrieved {len(chats)} chats")
        logger.debug(f"Final processed chats: {chats}")
        return jsonify(chats)
    except Exception as e:
        logger.error(f"Error fetching chats: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/messages/<sender>')
def get_messages(sender):
    try:
        logger.debug(f"Fetching messages for sender: {sender}")
        db = get_db()
        cursor = db.cursor()
        
        query = """
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
                COALESCE(messenger, sender) as sender,
                text,
                time,
                NULL as location
            FROM ChatMessages
            WHERE messenger = ? OR sender = ?
            ORDER BY time ASC;
        """
        
        logger.debug(f"Executing query with params: {(sender, sender)}")
        cursor.execute(query, (sender, sender, sender, sender))
        
        raw_results = cursor.fetchall()
        logger.debug(f"Raw results from database: {[dict(row) for row in raw_results]}")
        
        messages = []
        for row in raw_results:
            logger.debug(f"Processing row: {dict(row)}")
            try:
                # Ensure all required fields are present
                if not all(key in row.keys() for key in ['type', 'sender', 'text', 'time']):
                    logger.error(f"Missing required fields in row: {dict(row)}")
                    continue
                
                message_dict = {
                    'type': str(row['type']),
                    'sender': str(row['sender']) if row['sender'] else 'Unknown',
                    'text': str(row['text']) if row['text'] else '',
                    'time': str(row['time']) if row['time'] else '',
                    'location': str(row['location']) if row['location'] else None,
                    'message_type': 'received' if str(row['type']).upper() == 'SMS' else 'sent'
                }
                messages.append(message_dict)
                logger.debug(f"Successfully processed message: {message_dict}")
            except Exception as row_error:
                logger.error(f"Error processing row {dict(row)}: {str(row_error)}", exc_info=True)
                continue
            
        logger.info(f"Retrieved {len(messages)} messages for {sender}")
        logger.debug(f"Final processed messages: {messages}")
        return jsonify(messages)
    except Exception as e:
        logger.error(f"Error fetching messages: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/calls')
def get_calls():
    try:
        db = get_db()
        cursor = db.cursor()
        query = """
            SELECT 
                call_type,
                from_to,
                time,
                duration,
                location
            FROM Calls 
            ORDER BY time DESC;
        """
        cursor.execute(query)
        calls = [dict(row) for row in cursor.fetchall()]
        return jsonify(calls)
    except Exception as e:
        logger.error(f"Error fetching calls: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/apps')
def get_apps():
    try:
        db = get_db()
        cursor = db.cursor()
        query = """
            SELECT 
                application_name as name,
                package_name,
                install_date as date
            FROM InstalledApps 
            ORDER BY install_date DESC;
        """
        cursor.execute(query)
        apps = [dict(row) for row in cursor.fetchall()]
        return jsonify(apps)
    except Exception as e:
        logger.error(f"Error fetching apps: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
