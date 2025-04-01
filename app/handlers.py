import aiofiles
from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import Message

from .db import load_user_mode, save_user_mode
from .gpt_module import ChatGPT
from .middlewares import AccessMiddleware, ProcessingLockMiddleware, RateLimitMiddleware

router = Router()
router.message.middleware(AccessMiddleware())
router.message.middleware(ProcessingLockMiddleware())
router.message.middleware(RateLimitMiddleware())


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Используй /mode для переключения между режимами ответа на голосовые сообщения."
    )


@router.message(Command("mode"))
async def cmd_mode(message: Message):
    user_id = message.from_user.id
    current_mode = await load_user_mode(user_id)
    new_mode = "Ответ текстом" if current_mode == "Ответ голосом" else "Ответ голосом"
    await save_user_mode(user_id, new_mode)
    await message.answer(f"Режим ответа на голосовые сообщения изменён на: {new_mode}")


@router.message(F.text)
async def any_message(message: Message, bot: Bot):
    await bot.send_chat_action(message.chat.id, action="typing")
    answer = await ChatGPT().generate_text(
        user_id=message.from_user.id,
        user_text=message.text,
    )
    await message.answer(answer, parse_mode="Markdown")


@router.message(F.voice)
async def handle_voice_message(message: Message, bot: Bot):
    user_id = message.from_user.id
    current_mode = await load_user_mode(user_id)

    if current_mode == "Ответ голосом":
        await send_voice_message_on_voice(message, bot, user_id)
    else:
        await send_text_message_on_voice(message, bot, user_id)


async def send_voice_message_on_voice(message, bot, user_id):
    await bot.send_chat_action(message.chat.id, action="record_voice")
    file_link = await bot.get_file(message.voice.file_id)
    await bot.download_file(file_link.file_path, f"{user_id}_voice.ogg")
    async with aiofiles.open(f"{user_id}_voice.ogg", "rb") as voice_file:
        voice, answer = await ChatGPT().generate_voice(
            user_id=user_id,
            voice=voice_file,
        )
    await message.answer_voice(voice)
    await message.answer(answer, parse_mode="Markdown")


async def send_text_message_on_voice(message, bot, user_id):
    await bot.send_chat_action(message.chat.id, action="typing")
    user_id = message.from_user.id
    file_link = await bot.get_file(message.voice.file_id)
    await bot.download_file(file_link.file_path, f"{user_id}_voice.ogg")
    async with aiofiles.open(f"{user_id}_voice.ogg", "rb") as voice_file:
        answer = await ChatGPT().generate_text_on_voice(
            user_id=user_id,
            voice=voice_file,
        )
    await message.answer(answer, parse_mode="Markdown")
