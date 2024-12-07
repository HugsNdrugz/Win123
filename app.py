import os
from flask import Flask, render_template, jsonify, request
from db import db
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "message_viewer_secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///instance/data.db"
app.config["SQLALCHEMY_ECHO"] = True  # Enable SQL query logging for debugging
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Import models after initializing db to avoid circular imports
from models import Contact, ChatMessage, Call, Request

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chats')
def get_chats():
    try:
        # Get all contacts with their latest messages
        contacts = Contact.query.all()
        chats_data = []
        for contact in contacts:
            latest_message = ChatMessage.query.filter_by(contact_id=contact.id).order_by(ChatMessage.time.desc()).first()
            chats_data.append({
                'conversation_id': contact.id,
                'name': contact.name,
                'avatar': contact.avatar or url_for('static', filename='icons/fallback-icon.png'),
                'last_message': latest_message.text if latest_message else None,
                'last_message_time': latest_message.time if latest_message else None,
                'unread': contact.unread
            })
        return jsonify(chats_data)
    except Exception as e:
        logging.error(f"Error fetching chats: {e}")
        return jsonify({'error': 'Failed to fetch chats'}), 500

@app.route('/api/requests')
def get_requests():
    try:
        requests = Request.query.all()
        return jsonify([{
            'id': req.id,
            'title': req.title,
            'avatar': req.avatar or url_for('static', filename='icons/request-icon.png'),
            'message': req.message,
            'time': req.time,
            'filter': req.filter
        } for req in requests])
    except Exception as e:
        logging.error(f"Error fetching requests: {e}")
        return jsonify({'error': 'Failed to fetch requests'}), 500

@app.route('/api/chat/<int:contact_id>/messages')
def get_chat_messages(contact_id):
    try:
        messages = ChatMessage.query.filter_by(contact_id=contact_id).order_by(ChatMessage.time).all()
        return jsonify([{
            'id': msg.id,
            'text': msg.text,
            'time': msg.time,
            'sender': msg.sender
        } for msg in messages])
    except Exception as e:
        logging.error(f"Error fetching messages: {e}")
        return jsonify({'error': 'Failed to fetch messages'}), 500

def init_db():
    """Initialize the database and create all tables"""
    with app.app_context():
        # Drop all tables and recreate them
        db.drop_all()
        db.create_all()
        
        # Verify that tables were created
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        logging.info(f"Created tables: {tables}")
        
        # Add some sample data
        try:
            # Add a sample contact
            sample_contact = Contact(
                name="Sample User",
                avatar="/static/icons/fallback-icon.png",
                last_message="Welcome to the chat!",
                unread=False
            )
            db.session.add(sample_contact)
            db.session.commit()
            logging.info("Added sample contact data")
            
            # Add a sample message
            sample_message = ChatMessage(
                contact_id=1,
                text="Hello! This is a sample message.",
                time="2024-12-07 12:00:00",
                sender="contact"
            )
            db.session.add(sample_message)
            db.session.commit()
            logging.info("Added sample message data")
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error adding sample data: {e}")
            raise

if __name__ == '__main__':
    init_db()  # Initialize database and create sample data
    app.run(host='0.0.0.0', port=5000, debug=True)
