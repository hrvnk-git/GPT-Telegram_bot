import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from loguru import logger

from app.db import init_db
from app.handlers import router

load_dotenv()

BOT_TOKEN = str(os.getenv("BOT_TOKEN"))

# Настройка логирования
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <white>{message}</white>",
    level="INFO",
    colorize=True,
    backtrace=True,
    diagnose=True,
)


# Настройка перехвата стандартных логов Python в loguru
class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Пропускаем логи самой loguru
        if record.name.startswith("loguru"):
            return

        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__: # type: ignore
            frame = frame.f_back # type: ignore
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


# Настраиваем перехват всех логов в loguru
logging.basicConfig(handlers=[InterceptHandler()], level=logging.DEBUG, force=True)
for name in logging.root.manager.loggerDict:
    logging_logger = logging.getLogger(name)
    logging_logger.handlers = []
    logging_logger.propagate = True


async def main():
    logger.info("Запуск бота...")
    await init_db()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    logger.success("Бот успешно запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
