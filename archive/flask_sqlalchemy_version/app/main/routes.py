from flask import render_template, jsonify
from app.main import bp
from app.models import db, Message

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/api/conversations')
def get_conversations():
    conversations = Message.query.order_by(Message.time.desc()).all()
    return jsonify([msg.to_dict() for msg in conversations])

@bp.route('/api/messages/<sender>')
def get_messages(sender):
    messages = Message.query.filter_by(sender=sender).order_by(Message.time.asc()).all()
    return jsonify([msg.to_dict() for msg in messages])
