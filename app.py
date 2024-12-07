import os
from flask import Flask, render_template, jsonify
from database import get_chat_data, get_archived_chats, init_db
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "dev_key_123"

# Initialize database
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chats')
def get_chats():
    chats = get_chat_data()
    logging.debug(f"Retrieved chat data: {chats}")
    return jsonify(chats)



@app.route('/api/archived')
def get_archived():
    archived = get_archived_chats()
    return jsonify(archived)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
