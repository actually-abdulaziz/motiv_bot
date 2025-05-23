import sqlite3

conn = sqlite3.connect("posts.db", check_same_thread=False)
cursor = conn.cursor()

def init_db():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            message_id INTEGER PRIMARY KEY,
            media_group_id TEXT,
            type TEXT
        )
    ''')
    conn.commit()

def save_post(message_id: int, media_group_id: str | None, post_type: str):
    cursor.execute(
        'INSERT OR IGNORE INTO posts (message_id, media_group_id, type) VALUES (?, ?, ?)',
        (message_id, media_group_id, post_type)
    )
    conn.commit()

def get_random_post():
    cursor.execute('SELECT message_id, media_group_id, type FROM posts ORDER BY RANDOM() LIMIT 1')
    row = cursor.fetchone()
    if not row:
        return None
    message_id, media_group_id, post_type = row

    if media_group_id:
        cursor.execute(
            'SELECT message_id FROM posts WHERE media_group_id = ? ORDER BY message_id',
            (media_group_id,)
        )
        group_ids = [r[0] for r in cursor.fetchall()]
        return group_ids
    return [message_id]
