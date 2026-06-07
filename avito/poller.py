import asyncio
import logging
import re

from vkbottle.bot import Bot

from database import get_conn, get_notifiable_users
from .client import AvitoClient, AvitoChat

logger = logging.getLogger(__name__)


def _get_stored_last_message_id(chat_id: str) -> str | None:
    row = get_conn().execute(
        "SELECT last_message_id FROM chats WHERE chat_id = ?", (chat_id,)
    ).fetchone()
    return row["last_message_id"] if row else None


def _upsert_chat(chat: AvitoChat) -> None:
    msg = chat.last_message
    get_conn().execute(
        """
        INSERT INTO chats (chat_id, last_message_id, last_message_text, updated_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(chat_id) DO UPDATE SET
            last_message_id = excluded.last_message_id,
            last_message_text = excluded.last_message_text,
            updated_at = excluded.updated_at
        """,
        (chat.id, msg.id if msg else None, msg.text if msg else None),
    )
    get_conn().commit()


_MAX_MSG_LEN = 200


async def _notify_vk(bot: Bot, chat: AvitoChat) -> None:
    msg = chat.last_message
    raw_text = re.sub(r"https?://\S+", "", msg.text or "").strip() or "(без текста)"
    preview = raw_text if len(raw_text) <= _MAX_MSG_LEN else raw_text[:_MAX_MSG_LEN] + "..."

    chat_url = f"https://www.avito.ru/profile/messenger/channel/{chat.id}"
    text = (
        f"💬 Новое сообщение на Авито!\n\n"
        f"👤 Клиент: {chat.buyer_name or 'Неизвестен'}\n"
        f"📦 Объявление: {chat.item_title or 'Неизвестно'}\n\n"
        f"✉️ {preview}\n\n"
        f"🔗 {chat_url}"
    )
    users = get_notifiable_users()
    for user in users:
        await bot.api.messages.send(peer_id=user["vk_id"], message=text, random_id=0)
    logger.info("VK уведомление отправлено для чата %s (%d получателей)", chat.id, len(users))


async def run_poller(bot: Bot, client: AvitoClient, interval: int) -> None:
    logger.info("Avito poller запущен, интервал %d сек", interval)
    while True:
        try:
            chats = await client.get_chats()
            for chat in chats:
                if chat.last_message is None:
                    continue

                stored_id = _get_stored_last_message_id(chat.id)

                if stored_id != chat.last_message.id:
                    if chat.last_message.direction == "in":
                        await _notify_vk(bot, chat)
                    _upsert_chat(chat)

        except Exception:
            logger.exception("Ошибка в Avito poller")

        await asyncio.sleep(interval)
