import os
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
        if isinstance(event, Message) and event.from_user.id != int(AUTHORIZED_USER_ID):
            # Если пользователь не авторизован — не передаём управление хендлеру
            return

        # Пользователь авторизован — передаём управление дальше
        return await handler(event, data)
