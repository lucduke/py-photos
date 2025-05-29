import sqlite3

conn = None

def init_db():
    global conn
    conn = sqlite3.connect('photos.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS photos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_path TEXT NOT NULL,
        file_hash TEXT NOT NULL,
        file_size INTEGER NOT NULL,
        exif_data TEXT,
        UNIQUE(file_hash)
    )
    ''')
    conn.commit()

def close_db():
    if conn:
        conn.close()

def get_db_connection():
    return conn
