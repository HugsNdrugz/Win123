
from db import db

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    avatar = db.Column(db.String(200), nullable=True)
    last_message = db.Column(db.String(200), nullable=True)
    unread = db.Column(db.Boolean, default=False)

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)
    text = db.Column(db.String(500), nullable=False)
    time = db.Column(db.String(100), nullable=False)
    sender = db.Column(db.String(10), nullable=False)  # 'user' or 'contact'

class Call(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)
    time = db.Column(db.String(100), nullable=False)

class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    avatar = db.Column(db.String(200), nullable=True)
    message = db.Column(db.String(500), nullable=False)
    time = db.Column(db.String(100), nullable=False)
    filter = db.Column(db.String(50), nullable=True)
