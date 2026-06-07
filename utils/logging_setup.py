import logging
import logging.handlers

from config import paths


def setup_logging() -> None:
    formatter = logging.Formatter(
        "%(filename)s:%(lineno)d [%(asctime)s] #%(levelname)-8s %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    file_handler = logging.handlers.RotatingFileHandler(
        filename=paths.path_log,
        maxBytes=300_000,
        backupCount=1,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    all_log_handler = logging.handlers.RotatingFileHandler(
        filename=paths.path_all_log,
        maxBytes=1_000_000,
        backupCount=1,
        encoding="utf-8",
    )
    all_log_handler.setFormatter(formatter)
    all_log_handler.setLevel(logging.DEBUG)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(all_log_handler)

    logging.getLogger("vkbottle").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.WARNING)
    logging.getLogger("hypercorn").setLevel(logging.WARNING)
    logging.getLogger("hypercorn.access").setLevel(logging.WARNING)
