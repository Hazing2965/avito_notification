import asyncio
import logging

from vkbottle.bot import Bot

from avito import AvitoClient, run_poller
from config import VK_TOKEN, AVITO_CLIENT_ID, AVITO_CLIENT_SECRET, AVITO_USER_ID, AVITO_POLL_INTERVAL
from database import init_db
from handlers import register_all_handlers
from utils import setup_logging

logger = logging.getLogger(__name__)


async def main() -> None:
    setup_logging()
    logger.info("Запуск бота")

    init_db()

    bot = Bot(token=VK_TOKEN)
    register_all_handlers(bot)

    avito_client = AvitoClient(
        client_id=AVITO_CLIENT_ID,
        client_secret=AVITO_CLIENT_SECRET,
        user_id=AVITO_USER_ID,
    )

    try:
        await asyncio.gather(
            bot.run_polling(),
            run_poller(bot, avito_client, AVITO_POLL_INTERVAL),
        )
    finally:
        await avito_client.close()


if __name__ == "__main__":
    asyncio.run(main())
