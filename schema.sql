CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    sender_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    timestamp DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS archived_conversations (
    conversation_id INTEGER PRIMARY KEY,
    archive_date DATETIME NOT NULL,
    last_message_date DATETIME,
    total_messages INTEGER
);
