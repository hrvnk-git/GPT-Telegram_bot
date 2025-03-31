import os
from asyncio import Lock
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from dotenv import load_dotenv

load_dotenv()

AUTHORIZED_USER_ID = os.getenv("AUTHORIZED_USER_ID")


class AccessMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Message) and event.from_user.id != int(AUTHORIZED_USER_ID):  # type: ignore
            # Если пользователь не авторизован — не передаём управление хендлеру
            return

        # Пользователь авторизован — передаём управление дальше
        return await handler(event, data)


# Глобальный Lock, который предотвращает одновременную обработку команд
processing_lock = Lock()


class ProcessingLockMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Message):
            if processing_lock.locked():
                await event.answer(
                    "```Подожди! Бот занят немного...   ```",
                    parse_mode="Markdown",
                )
                return

            # Захватываем Lock, чтобы другие сообщения ждали завершения
            async with processing_lock:
                return await handler(event, data)
