import os
import sqlite3

def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), 'users.sqlite3')
    print(f"Database path: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Fetch rows as dictionaries
    return conn

def init_db():
    conn = get_db_connection()
    print("Initializing database...")
    conn.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
        username TEXT UNIQUE NOT NULL,
        user_email TEXT UNIQUE NOT NULL,
        user_oauth_id TEXT UNIQUE,
        user_password TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.commit()
    conn.close()
    print("Database initialized successfully.")
