from flask import Flask, render_template, jsonify, request
import os
from flask_sqlalchemy import SQLAlchemy
from db import db
from models import Contact, ChatMessage, Call, Request
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///messages.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chats')
def get_chats():
    try:
        chats = db.session.execute(db.select(Contact)).scalars().all()
        return jsonify([{
            'conversation_id': chat.id,
            'name': chat.name,
            'avatar': chat.avatar or 'default.png',
            'last_message': chat.last_message,
            'unread': chat.unread
        } for chat in chats])
    except Exception as e:
        logger.error(f"Error fetching chats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/messages/<int:contact_id>')
def get_messages(contact_id):
    try:
        messages = ChatMessage.query.filter_by(contact_id=contact_id).order_by(ChatMessage.time.desc()).all()
        return jsonify([{
            'id': msg.id,
            'text': msg.text,
            'time': msg.time,
            'sender': msg.sender
        } for msg in messages])
    except Exception as e:
        logger.error(f"Error fetching messages: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/calls/<int:contact_id>')
def get_calls(contact_id):
    try:
        calls = Call.query.filter_by(contact_id=contact_id).order_by(Call.time.desc()).all()
        return jsonify([{
            'id': call.id,
            'time': call.time
        } for call in calls])
    except Exception as e:
        logger.error(f"Error fetching calls: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/requests')
def get_requests():
    try:
        filter_type = request.args.get('filter', 'all')
        query = Request.query
        if filter_type != 'all':
            query = query.filter_by(filter=filter_type)
        requests = query.order_by(Request.time.desc()).all()
        return jsonify([{
            'id': req.id,
            'title': req.title,
            'message': req.message,
            'time': req.time,
            'avatar': req.avatar,
            'filter': req.filter
        } for req in requests])
    except Exception as e:
        logger.error(f"Error fetching requests: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/statistics')
def get_statistics():
    try:
        # Example statistics - you would replace this with actual database queries
        stats = [
            {"month": "Jan", "message_count": 150, "unique_senders": 45},
            {"month": "Feb", "message_count": 180, "unique_senders": 50},
            {"month": "Mar", "message_count": 210, "unique_senders": 55}
        ]
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error fetching statistics: {e}")
        return jsonify({'error': str(e)}), 500

def init_db():
    with app.app_context():
        try:
            db.create_all()
            
            # Add sample data if database is empty
            if not Contact.query.first():
                # Sample contacts
                contacts = [
                    Contact(name='Alice Smith', avatar='avatar1.png', last_message='Hey, how are you?', unread=True),
                    Contact(name='Bob Johnson', avatar='avatar2.png', last_message='Meeting at 3pm', unread=False),
                    Contact(name='Carol Williams', avatar='avatar3.png', last_message='Thanks!', unread=True)
                ]
                db.session.add_all(contacts)
                # Commit contacts first
                db.session.commit()
                
                # Now add messages for each contact
                for contact in Contact.query.all():
                    messages = [
                        ChatMessage(contact_id=contact.id, text='Hello!', time='2023-12-01 10:00', sender='contact'),
                        ChatMessage(contact_id=contact.id, text='Hi there!', time='2023-12-01 10:05', sender='user'),
                        ChatMessage(contact_id=contact.id, text='How are you?', time='2023-12-01 10:10', sender='contact')
                    ]
                    db.session.add_all(messages)
                
                # Commit messages
                db.session.commit()
                logger.info("Sample data added successfully")
            
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise

# Initialize database tables and sample data
init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
