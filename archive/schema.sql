CREATE TABLE IF NOT EXISTS chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    sender_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    is_archived BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS sms_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone_number TEXT NOT NULL,
    sender_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    is_archived BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS call_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    caller_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    duration INTEGER NOT NULL,  -- Duration in seconds
    start_time DATETIME NOT NULL,
    call_type TEXT CHECK(call_type IN ('audio', 'video')) NOT NULL,
    is_archived BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS archived_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_type TEXT CHECK(item_type IN ('chat', 'sms', 'call')) NOT NULL,
    item_id INTEGER NOT NULL,
    archive_date DATETIME NOT NULL
);
