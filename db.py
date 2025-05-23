import sqlite3

DB_PATH = "messages.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY)")
    conn.commit()
    conn.close()

def save_message_id(message_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO messages (id) VALUES (?)", (message_id,))
    conn.commit()
    conn.close()

def get_all_message_ids():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id FROM messages")
    ids = [row[0] for row in cur.fetchall()]
    conn.close()
    return ids
