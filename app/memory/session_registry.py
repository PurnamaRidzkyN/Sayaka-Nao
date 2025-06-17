# db_helper.py
import sqlite3
import time

def add_session(topic: str, mode: str, db_path="./memory/memory_meta.db"):
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

def update_session_end(session_id: int, db_path="memory_meta.db"):
    import sqlite3
    import time

    end_ts = int(time.time())

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE sessions
    SET end_ts = ?
    WHERE id = ?
    """, (end_ts, session_id))
    conn.commit()
    conn.close()

