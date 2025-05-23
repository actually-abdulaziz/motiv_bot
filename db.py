import sqlite3

DB_FILE = "posts.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER UNIQUE
        )
    """)
    conn.commit()
    conn.close()

def add_message_id(message_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO posts (message_id) VALUES (?)", (message_id,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

def get_all_message_ids():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT message_id FROM posts")
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]
