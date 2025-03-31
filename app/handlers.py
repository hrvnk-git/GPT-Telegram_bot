from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import Message

from .gpt_module import ChatGPT
from .middlewares import AccessMiddleware, ProcessingLockMiddleware

router = Router()
router.message.middleware(AccessMiddleware())
router.message.middleware(ProcessingLockMiddleware())


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Привет!")


@router.message(F.text)
async def any_message(message: Message, bot: Bot):
    await bot.send_chat_action(message.chat.id, action="typing")
    answer = await ChatGPT().generate_text(message.text)
    await message.answer(answer, parse_mode="Markdown")


@router.message(F.voice)
async def send_voice_message(message: Message, bot: Bot):
    await bot.send_chat_action(message.chat.id, action="record_voice")
    file_link = await bot.get_file(message.voice.file_id)  # type: ignore
    await bot.download_file(file_link.file_path, "voice.ogg")  # type: ignore
    voice_file = open("voice.ogg", "rb")
    voice, answer = await ChatGPT().generate_voice(voice_file)
    await message.answer_voice(voice)
    await message.answer(answer, parse_mode="Markdown")
