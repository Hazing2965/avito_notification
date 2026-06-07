import logging

from vkbottle.bot import Bot, Message

from config import VK_ADMIN_ID
from database import ensure_user, set_user_access
from keyboards import request_access_keyboard, notification_keyboard

logger = logging.getLogger(__name__)


def register_message_handlers(bot: Bot) -> None:

    @bot.on.message()
    async def any_message(message: Message) -> None:
        user = ensure_user(message.from_id)

        if message.from_id == VK_ADMIN_ID and not user["access"]:
            set_user_access(message.from_id, True)
            user = ensure_user(message.from_id)

        if not user["access"]:
            logger.debug("Нет доступа у vk_id=%s", message.from_id)
            await message.answer(
                "🚫 У вас нет доступа к боту.\n\n"
                "Нажмите кнопку ниже, чтобы запросить доступ у администратора:",
                keyboard=request_access_keyboard,
            )
            return

        status = "🔔 включены" if user["notification"] else "🔕 выключены"
        await message.answer(
            f"Уведомления об Авито {status}.\nИспользуйте кнопки для управления:",
            keyboard=notification_keyboard,
        )
