import os
from asyncio import Lock
from time import monotonic
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from dotenv import load_dotenv

load_dotenv()

AUTHORIZED_USERS_ID = os.getenv("AUTHORIZED_USERS_ID", "")


def get_authorized_users_ids() -> list[int]:
    return [
        int(user_id.strip())
        for user_id in AUTHORIZED_USERS_ID.split(",")
        if user_id.strip()
    ]


class AccessMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if (
            isinstance(event, Message)
            and event.from_user.id not in get_authorized_users_ids() # type: ignore
        ):  # type: ignore
            # Если пользователь не авторизован — не передаём управление хендлеру
            await event.answer("Вы не авторизованы для использования этого бота.")
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


class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, limit_seconds: float = 1.0):
        self.limit_seconds = limit_seconds
        self.user_last_time: Dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Message):
            current_time = monotonic()
            user_id = event.from_user.id  # type: ignore
            last_time = self.user_last_time.get(user_id, 0)
            if current_time - last_time < self.limit_seconds:
                await event.answer(
                    "Пожалуйста, не спамьте сообщения. Подождите немного...",
                    parse_mode="Markdown",
                )
                return
            self.user_last_time[user_id] = current_time
        return await handler(event, data)
