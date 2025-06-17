import sqlite3

def init_session_table(db_path="db/memory_meta.db"):
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
    print("Tabel 'sessions' berhasil dibuat atau sudah ada.")

# Langsung dijalankan
init_session_table()
