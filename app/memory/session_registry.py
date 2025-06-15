# db_helper.py
import sqlite3
import time

def init_session_table(db_path="memory_meta.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        start_ts INTEGER,
        end_ts INTEGER,
        topic TEXT,
        mode TEXT
    )
    """)
    conn.commit()
    conn.close()

def add_session(topic: str, mode: str, db_path="memory_meta.db"):
    import sqlite3
    import time

    start_ts = int(time.time())
    end_ts = None  # diset None agar disimpan sebagai NULL di SQLite

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO sessions (start_ts, end_ts, topic, mode)
    VALUES (?, ?, ?, ?)
    """, (start_ts, end_ts, topic, mode))
    session_id = cursor.lastrowid 
    conn.commit()
    conn.close()

    return session_id


