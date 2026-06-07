from vkbottle.bot import Bot

from .messages import register_message_handlers
from .callbacks import register_callback_handlers


def register_all_handlers(bot: Bot) -> None:
    register_message_handlers(bot)
    register_callback_handlers(bot)
