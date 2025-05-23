import sqlite3
import logging

DB_NAME = "ids.db"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS media (
                file_id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                url TEXT,
                message_id INTEGER UNIQUE
            )
        """)
        conn.commit()
        logger.info("База данных инициализирована")

def save_file_id(file_id: str, file_type: str, url: str = None, message_id: int = None):
    with sqlite3.connect(DB_NAME) as conn:
        try:
            conn.execute(
                "INSERT OR REPLACE INTO media (file_id, type, url, message_id) VALUES (?, ?, ?, ?)",
                (file_id, file_type, url, message_id)
            )
            conn.commit()
            logger.info(f"Сохранено: {file_id}")
        except sqlite3.Error as e:
            logger.error(f"Ошибка сохранения: {e}")

def delete_file_id(file_id: str):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("DELETE FROM media WHERE file_id = ?", (file_id,))
        conn.commit()
        logger.info(f"Удалено: {file_id}")

def load_random() -> dict:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute("SELECT file_id, type FROM media ORDER BY RANDOM() LIMIT 1")
        row = cursor.fetchone()
        return {"file_id": row[0], "type": row[1]} if row else None