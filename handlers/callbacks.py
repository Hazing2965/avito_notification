import logging

from vkbottle import GroupEventType
from vkbottle.bot import Bot, MessageEventMin

from config import VK_ADMIN_ID
from database import get_user, set_user_access, set_user_notification
from keyboards import waiting_keyboard, notification_keyboard, admin_approval_keyboard

logger = logging.getLogger(__name__)


def register_callback_handlers(bot: Bot) -> None:

    @bot.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEventMin)
    async def callback_handler(event: MessageEventMin) -> None:
        payload = event.payload or {}
        action = payload.get("action")
        logger.debug("Callback от vk_id=%s, action=%s", event.user_id, action)

        handlers = {
            "request_access":  _handle_request_access,
            "grant_access":    _handle_grant_access,
            "deny_access":     _handle_deny_access,
            "notifications_on":  _handle_notifications_on,
            "notifications_off": _handle_notifications_off,
            "status":          _handle_status,
        }

        handler = handlers.get(action)
        if handler:
            await handler(bot, event, payload)
        else:
            logger.warning("Неизвестный callback action='%s' от vk_id=%s", action, event.user_id)
            await event.send_empty_answer()


async def _handle_request_access(bot: Bot, event: MessageEventMin, payload: dict) -> None:
    await event.send_empty_answer()
    try:
        await bot.api.messages.edit(
            peer_id=event.peer_id,
            conversation_message_id=event.conversation_message_id,
            message="⏳ Запрос отправлен. Ожидайте решения администратора.",
            keyboard=waiting_keyboard,
        )
    except Exception:
        logger.warning("Не удалось отредактировать сообщение для vk_id=%s", event.user_id)

    profile_url = f"https://vk.com/id{event.user_id}"
    await bot.api.messages.send(
        peer_id=VK_ADMIN_ID,
        message=(
            f"👤 Запрос на доступ\n\n"
            f"Пользователь: {profile_url}\n"
            f"VK ID: {event.user_id}"
        ),
        keyboard=admin_approval_keyboard(event.user_id),
        random_id=0,
    )
    logger.info("Запрос доступа от vk_id=%s отправлен админу", event.user_id)


async def _handle_grant_access(bot: Bot, event: MessageEventMin, payload: dict) -> None:
    if event.user_id != VK_ADMIN_ID:
        await event.send_empty_answer()
        return

    target_id = payload.get("user_id")
    if not target_id:
        await event.send_empty_answer()
        return

    set_user_access(target_id, True)
    await event.send_empty_answer()

    try:
        await bot.api.messages.edit(
            peer_id=event.peer_id,
            conversation_message_id=event.conversation_message_id,
            message=f"✅ Доступ выдан пользователю vk.com/id{target_id}",
            keyboard=waiting_keyboard,
        )
    except Exception:
        logger.warning("Не удалось отредактировать сообщение админа")

    await bot.api.messages.send(
        peer_id=target_id,
        message=(
            "✅ Вам выдан доступ к боту!\n\n"
            "Теперь вы будете получать уведомления о новых сообщениях на Авито.\n"
            "Управляйте уведомлениями кнопками ниже:"
        ),
        keyboard=notification_keyboard,
        random_id=0,
    )
    logger.info("Доступ выдан vk_id=%s", target_id)


async def _handle_deny_access(bot: Bot, event: MessageEventMin, payload: dict) -> None:
    if event.user_id != VK_ADMIN_ID:
        await event.send_empty_answer()
        return

    target_id = payload.get("user_id")
    if not target_id:
        await event.send_empty_answer()
        return

    await event.send_empty_answer()

    try:
        await bot.api.messages.edit(
            peer_id=event.peer_id,
            conversation_message_id=event.conversation_message_id,
            message=f"❌ В доступе отказано пользователю vk.com/id{target_id}",
            keyboard=waiting_keyboard,
        )
    except Exception:
        logger.warning("Не удалось отредактировать сообщение админа")

    await bot.api.messages.send(
        peer_id=target_id,
        message="❌ Ваш запрос на доступ отклонён администратором.",
        random_id=0,
    )
    logger.info("В доступе отказано vk_id=%s", target_id)


async def _handle_status(bot: Bot, event: MessageEventMin, payload: dict) -> None:
    user = get_user(event.user_id)
    if not user or not user["access"]:
        await event.send_empty_answer()
        return

    access_str = "✅ Есть" if user["access"] else "❌ Нет"
    notif_str = "🔔 Включены" if user["notification"] else "🔕 Выключены"

    await event.show_snackbar(f"Уведомления {notif_str}")
    await bot.api.messages.send(
        peer_id=event.peer_id,
        message=f"ID: {event.user_id}\nДоступ: {access_str}\nУведомления: {notif_str}",
        random_id=0,
    )


async def _handle_notifications_on(bot: Bot, event: MessageEventMin, payload: dict) -> None:
    user = get_user(event.user_id)
    if not user or not user["access"]:
        await event.send_empty_answer()
        return

    set_user_notification(event.user_id, True)
    await event.show_snackbar("🔔 Уведомления включены")
    await bot.api.messages.send(
        peer_id=event.peer_id,
        message="🔔 Уведомления включены",
        random_id=0,
    )
    logger.info("vk_id=%s включил уведомления", event.user_id)


async def _handle_notifications_off(bot: Bot, event: MessageEventMin, payload: dict) -> None:
    user = get_user(event.user_id)
    if not user or not user["access"]:
        await event.send_empty_answer()
        return

    set_user_notification(event.user_id, False)
    await event.show_snackbar("🔕 Уведомления выключены")
    await bot.api.messages.send(
        peer_id=event.peer_id,
        message="🔕 Уведомления выключены",
        random_id=0,
    )
    logger.info("vk_id=%s выключил уведомления", event.user_id)
