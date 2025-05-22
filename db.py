import sqlite3

DB_NAME = "ids.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS media (
                file_id TEXT PRIMARY KEY,
                type TEXT,
                url TEXT,
                message_id INTEGER
            )
        """)
        conn.commit()

def save_file_id(file_id: str, file_type: str, url: str = None, message_id: int = None):
    with sqlite3.connect(DB_NAME) as conn:
        try:
            conn.execute(
                "INSERT INTO media (file_id, type, url, message_id) VALUES (?, ?, ?, ?)",
                (file_id, file_type, url, message_id)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            pass

def delete_file_id(file_id: str):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("DELETE FROM media WHERE file_id = ?", (file_id,))
        conn.commit()

def load_random() -> dict:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute("""
            SELECT file_id, type FROM media
            ORDER BY RANDOM()
            LIMIT 1
        """)
        row = cursor.fetchone()
        return {"file_id": row[0], "type": row[1]} if row else None

def check_message_exists(file_id: str) -> bool:  # Исправлено: проверка по file_id
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute("SELECT 1 FROM media WHERE file_id = ?", (file_id,))
        return cursor.fetchone() is not None