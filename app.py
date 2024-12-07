from flask import Flask, render_template, jsonify, request
import os
from flask_sqlalchemy import SQLAlchemy
from db import db
from models import ChatMessage, SMSMessage, CallLog, ArchivedItem
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def inspect_db_schema():
    try:
        with app.app_context():
            # Get all table names
            tables = db.session.execute(db.text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall()
            logger.info("Database Tables:")
            for table in tables:
                table_name = table[0]
                # Get table schema
                schema = db.session.execute(db.text(f"PRAGMA table_info({table_name});")).fetchall()
                logger.info(f"\nTable: {table_name}")
                for col in schema:
                    logger.info(f"Column: {col}")
    except Exception as e:
        logger.error(f"Error inspecting database schema: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chats')
def get_chats():
    try:
        chats = db.session.execute(
            db.select(ChatMessage)
            .group_by(ChatMessage.conversation_id)
            .order_by(ChatMessage.timestamp.desc())
        ).scalars().all()
        
        chat_data = []
        for chat in chats:
            # Get the latest message for each conversation
            latest_message = ChatMessage.query.filter_by(
                conversation_id=chat.conversation_id,
                is_archived=False
            ).order_by(ChatMessage.timestamp.desc()).first()
            
            if latest_message:
                chat_data.append({
                    'conversation_id': chat.conversation_id,
                    'last_message': latest_message.content,
                    'timestamp': latest_message.timestamp,
                    'unread': True  # You might want to add a proper unread tracking system
                })
        
        return jsonify(chat_data)
    except Exception as e:
        logger.error(f"Error fetching chats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/messages/<int:conversation_id>')
def get_messages(conversation_id):
    try:
        messages = ChatMessage.query.filter_by(
            conversation_id=conversation_id,
            is_archived=False
        ).order_by(ChatMessage.timestamp.desc()).all()
        
        return jsonify([{
            'id': msg.id,
            'text': msg.content,
            'time': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'sender': 'user' if msg.sender_id == 1 else 'contact'  # Assuming user_id 1 is the current user
        } for msg in messages])
    except Exception as e:
        logger.error(f"Error fetching messages: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sms')
def get_sms():
    try:
        messages = SMSMessage.query.filter_by(
            is_archived=False
        ).order_by(SMSMessage.timestamp.desc()).all()
        
        return jsonify([{
            'id': msg.id,
            'phone_number': msg.phone_number,
            'content': msg.content,
            'time': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'sender_id': msg.sender_id
        } for msg in messages])
    except Exception as e:
        logger.error(f"Error fetching SMS messages: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/calls')
def get_calls():
    try:
        calls = CallLog.query.filter_by(
            is_archived=False
        ).order_by(CallLog.start_time.desc()).all()
        
        return jsonify([{
            'id': call.id,
            'caller_id': call.caller_id,
            'receiver_id': call.receiver_id,
            'duration': call.duration,
            'start_time': call.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'call_type': call.call_type
        } for call in calls])
    except Exception as e:
        logger.error(f"Error fetching calls: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/archived')
def get_archived():
    try:
        archived_items = ArchivedItem.query.order_by(ArchivedItem.archive_date.desc()).all()
        
        archived_data = []
        for item in archived_items:
            if item.item_type == 'chat':
                message = ChatMessage.query.get(item.item_id)
                if message:
                    archived_data.append({
                        'type': 'chat',
                        'content': message.content,
                        'archive_date': item.archive_date.strftime('%Y-%m-%d %H:%M:%S')
                    })
            elif item.item_type == 'sms':
                message = SMSMessage.query.get(item.item_id)
                if message:
                    archived_data.append({
                        'type': 'sms',
                        'content': message.content,
                        'archive_date': item.archive_date.strftime('%Y-%m-%d %H:%M:%S')
                    })
            elif item.item_type == 'call':
                call = CallLog.query.get(item.item_id)
                if call:
                    archived_data.append({
                        'type': 'call',
                        'content': f"{call.duration} seconds {call.call_type} call",
                        'archive_date': item.archive_date.strftime('%Y-%m-%d %H:%M:%S')
                    })
        
        return jsonify(archived_data)
    except Exception as e:
        logger.error(f"Error fetching archived items: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/statistics')
def get_statistics():
    try:
        # Get monthly message counts and unique senders
        stats = db.session.execute("""
            SELECT 
                strftime('%Y-%m', timestamp) as month,
                COUNT(*) as message_count,
                COUNT(DISTINCT sender_id) as unique_senders
            FROM chat_messages
            WHERE NOT is_archived
            GROUP BY strftime('%Y-%m', timestamp)
            ORDER BY month DESC
            LIMIT 12
        """).fetchall()
        
        return jsonify([{
            'month': row[0],
            'message_count': row[1],
            'unique_senders': row[2]
        } for row in stats])
    except Exception as e:
        logger.error(f"Error fetching statistics: {e}")
        return jsonify({'error': str(e)}), 500

# Initialize database with schema and inspect it
with app.app_context():
    db.create_all()
    inspect_db_schema()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
