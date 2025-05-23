import sqlite3

DB_NAME = "ids.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS media (
                message_id INTEGER PRIMARY KEY,
                type TEXT,
                url TEXT UNIQUE
            )
        """)
        conn.commit()

def save_message_id(message_id: int, media_type: str, url: str):
    with sqlite3.connect(DB_NAME) as conn:
        try:
            conn.execute(
                "INSERT INTO media (message_id, type, url) VALUES (?, ?, ?)",
                (message_id, media_type, url)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            pass

def load_random() -> dict:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute("""
            SELECT message_id, type FROM media 
            ORDER BY RANDOM() 
            LIMIT 1
        """)
        row = cursor.fetchone()
        return {"message_id": row[0], "type": row[1]} if row else None

if __name__ == "__main__":
    init_db()
