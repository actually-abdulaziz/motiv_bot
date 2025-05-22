import sqlite3

DB_NAME = "ids.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS media (
                file_id TEXT PRIMARY KEY,
                type TEXT,
                url TEXT  -- NULL для ручных загрузок
            )
        """)
        conn.commit()

def save_file_id(file_id: str, file_type: str, url: str = None):
    with sqlite3.connect(DB_NAME) as conn:
        try:
            conn.execute(
                "INSERT INTO media (file_id, type, url) VALUES (?, ?, ?)",
                (file_id, file_type, url)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            pass

def load_random() -> dict:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute("""
            SELECT file_id, type FROM media 
            ORDER BY RANDOM() 
            LIMIT 1
        """)
        row = cursor.fetchone()
        return {"file_id": row[0], "type": row[1]} if row else None