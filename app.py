import sqlite3
from flask import Flask, render_template, jsonify, g
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.static_folder = 'static'
DATABASE = 'data.db'

# Add node_modules to static files
import os
node_modules_path = os.path.join('node_modules')
if os.path.exists(node_modules_path):
    app.static_folder = os.path.dirname(node_modules_path)

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

@app.route('/api/contacts')
def get_contacts():
    """Get all contacts with their latest messages"""
    try:
        contacts = query_db("""
            SELECT DISTINCT
                sender as contact_name,
                'Chat' as type,
                MAX(time) as last_time,
                FIRST_VALUE(text) OVER (PARTITION BY sender ORDER BY time DESC) as last_message
            FROM ChatMessages
            GROUP BY sender
            UNION ALL
            SELECT DISTINCT
                from_to as contact_name,
                'SMS' as type,
                MAX(time) as last_time,
                FIRST_VALUE(text) OVER (PARTITION BY from_to ORDER BY time DESC) as last_message
            FROM SMS
            GROUP BY from_to
            ORDER BY last_time DESC
        """)
        return jsonify({
            'success': True,
            'data': [dict(row) for row in contacts]
        })
    except Exception as e:
        logger.error(f"Error fetching contacts: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/messages/<contact>')
def get_contact_messages(contact):
    """Get all messages for a specific contact"""
    try:
        messages = query_db("""
            SELECT 
                'Chat' as type,
                time,
                text,
                sender as from_to
            FROM ChatMessages 
            WHERE sender = ?
            UNION ALL
            SELECT 
                'SMS' as type,
                time,
                text,
                from_to
            FROM SMS
            WHERE from_to = ?
            ORDER BY time DESC
        """, [contact, contact])
        return jsonify({
            'success': True,
            'data': [dict(row) for row in messages]
        })
    except Exception as e:
        logger.error(f"Error fetching contact messages: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/sms')
def get_sms():
    """Get all SMS messages"""
    try:
        messages = query_db("""
            SELECT 
                sms_type,
                from_to,
                text,
                time,
                location
            FROM SMS 
            ORDER BY time DESC
        """)
        return jsonify({
            'success': True,
            'data': [dict(row) for row in messages]
        })
    except Exception as e:
        logger.error(f"Error fetching SMS: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/calls')
def get_calls():
    """Get all call records"""
    try:
        calls = query_db("""
            SELECT 
                call_type,
                from_to,
                time,
                duration,
                location
            FROM Calls 
            ORDER BY time DESC
        """)
        return jsonify({
            'success': True,
            'data': [dict(row) for row in calls]
        })
    except Exception as e:
        logger.error(f"Error fetching calls: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/apps')
def get_apps():
    """Get all installed applications"""
    try:
        apps = query_db("""
            SELECT 
                application_name,
                package_name,
                install_date
            FROM InstalledApps 
            ORDER BY install_date DESC
        """)
        return jsonify({
            'success': True,
            'data': [dict(row) for row in apps]
        })
    except Exception as e:
        logger.error(f"Error fetching apps: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
