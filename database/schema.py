import logging
import sqlite3

logger = logging.getLogger(__name__)

SCHEMA: dict[str, list[tuple[str, str]]] = {
    "users": [
        ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
        ("vk_id", "INTEGER UNIQUE NOT NULL"),
        ("username", "TEXT"),
        ("access", "INTEGER NOT NULL DEFAULT 0"),
        ("notification", "INTEGER NOT NULL DEFAULT 1"),
        ("created_at", "TEXT DEFAULT CURRENT_TIMESTAMP"),
    ],
    "chats": [
        ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
        ("chat_id", "TEXT UNIQUE NOT NULL"),
        ("last_message_id", "TEXT"),
        ("last_message_text", "TEXT"),
        ("updated_at", "TEXT"),
    ],
}


def migrate(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()

    for table, columns in SCHEMA.items():
        column_defs = ", ".join(f"{name} {definition}" for name, definition in columns)
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table} ({column_defs})")

        cursor.execute(f"PRAGMA table_info({table})")
        existing = {row[1] for row in cursor.fetchall()}

        for col_name, col_def in columns:
            if col_name not in existing:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_def}")
                logger.info("Добавлена колонка '%s' в таблицу '%s'", col_name, table)

    conn.commit()
    logger.debug("Миграция БД завершена")
