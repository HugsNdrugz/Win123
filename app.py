import sqlite3
from flask import Flask, render_template, jsonify, g
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
DATABASE = 'data.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    try:
        cur = get_db().execute(query, args)
        rv = cur.fetchall()
        cur.close()
        return (rv[0] if rv else None) if one else rv
    except Exception as e:
        logger.error(f"Database error: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/conversations')
def get_conversations():
    """Get latest messages from both SMS and Chat, ordered by time"""
    try:
        messages = query_db("""
            SELECT 
                'Chat' as type,
                sender as name,
                text as last_message,
                time,
                'avatar.png' as avatar
            FROM ChatMessages
            UNION ALL
            SELECT 
                'SMS' as type,
                sms_type as name,
                text as last_message,
                time,
                'avatar.png' as avatar
            FROM SMS
            ORDER BY time DESC
        """)
        
        return jsonify([
            {
                'type': row['type'],
                'name': row['name'],
                'last_message': row['last_message'],
                'time': row['time'],
                'avatar': row['avatar']
            } for row in messages
        ])
    except Exception as e:
        logger.error(f"Error fetching conversations: {e}")
        return jsonify([])

@app.route('/api/messages/<conversation>')
def get_messages(conversation):
    """Get all messages for a specific conversation"""
    try:
        messages = query_db("""
            SELECT time, text, sender
            FROM ChatMessages 
            WHERE sender = ?
            ORDER BY time DESC
        """, [conversation])
        
        return jsonify([dict(row) for row in messages])
    except Exception as e:
        logger.error(f"Error fetching messages: {e}")
        return jsonify([])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
