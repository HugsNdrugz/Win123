import os
from flask import Flask, render_template, jsonify
import sqlite3
from datetime import datetime
import logging

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('data.db')
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/conversations')
def get_conversations():
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Combine SMS and Chat messages for conversations
        cursor.execute("""
            SELECT 'SMS' as type, sms_type as sender, time, text
            FROM SMS 
            UNION ALL
            SELECT 'Chat' as type, sender, time, text
            FROM ChatMessages
            ORDER BY time DESC
        """)
        conversations = cursor.fetchall()
        
        return jsonify([{
            'type': row['type'],
            'sender': row['sender'],
            'text': row['text'],
            'time': row['time'],
            'avatar': 'static/images/avatar.png'
        } for row in conversations])
    except Exception as e:
        logging.error(f"Error fetching conversations: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/messages/<sender>')
def get_messages(sender):
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Get both SMS and Chat messages for the sender
        cursor.execute("""
            SELECT 'SMS' as type, time, text
            FROM SMS 
            WHERE sms_type = ?
            UNION ALL
            SELECT 'Chat' as type, time, text
            FROM ChatMessages
            WHERE sender = ?
            ORDER BY time ASC
        """, (sender, sender))
        
        messages = cursor.fetchall()
        
        return jsonify([{
            'type': row['type'],
            'text': row['text'],
            'time': row['time']
        } for row in messages])
    except Exception as e:
        logging.error(f"Error fetching messages: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/calls')
def get_calls():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT call_type, time, from_to, duration, location
            FROM Calls
            ORDER BY time DESC
        """)
        calls = cursor.fetchall()
        
        return jsonify([{
            'type': row['call_type'],
            'contact': row['from_to'],
            'time': row['time'],
            'duration': row['duration'],
            'location': row['location']
        } for row in calls])
    except Exception as e:
        logging.error(f"Error fetching calls: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/apps')
def get_apps():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT application_name, package_name, install_date
            FROM InstalledApps
            ORDER BY install_date DESC
        """)
        apps = cursor.fetchall()
        
        return jsonify([{
            'name': row['application_name'],
            'package': row['package_name'],
            'install_date': row['install_date']
        } for row in apps])
    except Exception as e:
        logging.error(f"Error fetching apps: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
