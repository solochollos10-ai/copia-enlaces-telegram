import sqlite3
import hashlib

DB_NAME = "links.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sent_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            link_hash TEXT UNIQUE
        )
    """)

    conn.commit()
    conn.close()


def link_exists(link: str) -> bool:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    link_hash = hashlib.sha256(link.encode()).hexdigest()

    cursor.execute("SELECT 1 FROM sent_links WHERE link_hash = ?", (link_hash,))
    result = cursor.fetchone()
    conn.close()

    return result is not None


def save_link(link: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    link_hash = hashlib.sha256(link.encode()).hexdigest()

    try:
        cursor.execute(
            "INSERT INTO sent_links (link_hash) VALUES (?)",
            (link_hash,)
        )
        conn.commit()
    except:
        pass

    conn.close()
