import logging
import sqlite3

from config import paths
from .schema import migrate

logger = logging.getLogger(__name__)

DB_PATH = paths.path_db

_conn: sqlite3.Connection | None = None


def get_conn() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        raise RuntimeError("БД не инициализирована, вызови init_db() при старте")
    return _conn


def init_db() -> None:
    global _conn
    logger.info("Инициализация БД: %s", DB_PATH)
    _conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    _conn.row_factory = sqlite3.Row
    migrate(_conn)
    logger.info("БД готова")


def get_user(vk_id: int) -> sqlite3.Row | None:
    return get_conn().execute(
        "SELECT * FROM users WHERE vk_id = ?", (vk_id,)
    ).fetchone()


def ensure_user(vk_id: int) -> sqlite3.Row:
    user = get_user(vk_id)
    if user is None:
        get_conn().execute("INSERT INTO users (vk_id) VALUES (?)", (vk_id,))
        get_conn().commit()
        user = get_user(vk_id)
    return user


def set_user_access(vk_id: int, value: bool) -> None:
    get_conn().execute(
        "UPDATE users SET access = ? WHERE vk_id = ?", (int(value), vk_id)
    )
    get_conn().commit()


def set_user_notification(vk_id: int, value: bool) -> None:
    get_conn().execute(
        "UPDATE users SET notification = ? WHERE vk_id = ?", (int(value), vk_id)
    )
    get_conn().commit()


def get_notifiable_users() -> list[sqlite3.Row]:
    return get_conn().execute(
        "SELECT * FROM users WHERE access = 1 AND notification = 1"
    ).fetchall()
