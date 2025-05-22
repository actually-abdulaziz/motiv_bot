import sqlite3

DB_PATH = "ids.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id TEXT NOT NULL,
            type TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE
        )
    """)
    conn.commit()
    conn.close()

def save_file_id(file_id, file_type, url):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO content (file_id, type, url) VALUES (?, ?, ?)",
            (file_id, file_type, url)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        print("Видео уже существует в базе")
    finally:
        conn.close()

def get_random():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT file_id, type FROM content ORDER BY RANDOM() LIMIT 1")
    row = cur.fetchone()
    conn.close()
    return {"file_id": row[0], "type": row[1]} if row else None