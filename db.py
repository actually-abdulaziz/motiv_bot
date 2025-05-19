import sqlite3

DB_PATH = 'ids.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id TEXT NOT NULL,
            type TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def save_file_id(file_id, file_type):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('INSERT INTO content (file_id, type) VALUES (?, ?)', (file_id, file_type))
    conn.commit()
    conn.close()

def get_random():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT file_id, type FROM content ORDER BY RANDOM() LIMIT 1')
    row = cur.fetchone()
    conn.close()
    if row:
        return {'file_id': row[0], 'type': row[1]}
    return None
