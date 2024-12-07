
from db import db

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, nullable=False)
    sender_id = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    is_archived = db.Column(db.Boolean, default=False)

class SMSMessage(db.Model):
    __tablename__ = 'sms_messages'
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String, nullable=False)
    sender_id = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    is_archived = db.Column(db.Boolean, default=False)

class CallLog(db.Model):
    __tablename__ = 'call_logs'
    id = db.Column(db.Integer, primary_key=True)
    caller_id = db.Column(db.Integer, nullable=False)
    receiver_id = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # Duration in seconds
    start_time = db.Column(db.DateTime, nullable=False)
    call_type = db.Column(db.String, nullable=False)  # 'audio' or 'video'
    is_archived = db.Column(db.Boolean, default=False)

class ArchivedItem(db.Model):
    __tablename__ = 'archived_items'
    id = db.Column(db.Integer, primary_key=True)
    item_type = db.Column(db.String, nullable=False)  # 'chat', 'sms', or 'call'
    item_id = db.Column(db.Integer, nullable=False)
    archive_date = db.Column(db.DateTime, nullable=False)
