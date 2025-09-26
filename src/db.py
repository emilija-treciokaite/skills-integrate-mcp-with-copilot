import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "activities.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            name TEXT PRIMARY KEY,
            description TEXT,
            schedule TEXT,
            max_participants INTEGER
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS participants (
            activity_name TEXT,
            email TEXT,
            PRIMARY KEY (activity_name, email),
            FOREIGN KEY (activity_name) REFERENCES activities(name)
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
