from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

# from ..database.db import delete_response_id
from database.db import delete_response_id

from middlewares.middlewares import (
    AccessMiddleware,
    ProcessingLockMiddleware,
    RateLimitMiddleware,
)

router = Router()
router.message.middleware(AccessMiddleware())
router.message.middleware(ProcessingLockMiddleware())
router.message.middleware(RateLimitMiddleware())



@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привет! Я AI-бот, который может отвечать на текстовые и голосовые сообщения, "
        "а так же могу работать с фото."
    )


@router.message(Command("reset"))
async def cmd_reset(message: Message) -> None:
    await delete_response_id(message.from_user.id) # type: ignore
    await message.answer(
        "Контекст очищен. Начат новый разговор."
    )