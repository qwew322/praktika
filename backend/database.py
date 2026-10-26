import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parent / "database.sqlite"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                parent_id INTEGER,
                FOREIGN KEY (parent_id)
                    REFERENCES categories(id)
                    ON DELETE SET NULL
            )
        """)

        columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(categories)").fetchall()
        }
        if "parent_id" not in columns:
            connection.execute(
                "ALTER TABLE categories ADD COLUMN parent_id INTEGER "
                "REFERENCES categories(id) ON DELETE SET NULL"
            )

        connection.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL DEFAULT '',
                category_id INTEGER,
                FOREIGN KEY (category_id)
                    REFERENCES categories(id)
                    ON DELETE SET NULL
            )
        """)
