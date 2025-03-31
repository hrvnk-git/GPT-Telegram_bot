import json

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import Message

from .gpt_module import ChatGPT
from .middlewares import AccessMiddleware, ProcessingLockMiddleware

router = Router()
router.message.middleware(AccessMiddleware())
router.message.middleware(ProcessingLockMiddleware())


MODE_FILE = "mode_storage.json"


def load_user_mode(user_id: int) -> str:
    try:
        with open(MODE_FILE, "r", encoding="utf-8") as f:
            modes = json.load(f)
    except (
        FileNotFoundError,
        json.JSONDecodeError,
    ):  # Если файл не найден или повреждён
        modes = {}
        with open(MODE_FILE, "w", encoding="utf-8") as f:
            json.dump(modes, f, indent=4)
    return modes.get(str(user_id), "voice")


def save_user_mode(user_id: int, mode: str):
    try:
        with open(MODE_FILE, "r", encoding="utf-8") as f:
            modes = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        modes = {}

    modes[str(user_id)] = mode

    with open(MODE_FILE, "w", encoding="utf-8") as f:
        json.dump(modes, f, indent=4)


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Используй /mode для переключения между режимами ответа на голосовые сообщения."
    )


@router.message(Command("mode"))
async def cmd_mode(message: Message):
    user_id = message.from_user.id
    current_mode = load_user_mode(user_id)

    new_mode = "Ответ текстом" if current_mode == "Ответ голосом" else "Ответ голосом"
    save_user_mode(user_id, new_mode)

    await message.answer(f"Режим ответа на голосовые сообщения изменён на: {new_mode}")


@router.message(F.text)
async def any_message(message: Message, bot: Bot):
    await bot.send_chat_action(message.chat.id, action="typing")
    answer = await ChatGPT().generate_text(message.text)
    await message.answer(answer, parse_mode="Markdown")


@router.message(F.voice)
async def handle_voice_message(message: Message, bot: Bot):
    user_id = message.from_user.id
    current_mode = load_user_mode(user_id)

    if current_mode == "Ответ голосом":
        await send_voice_message_on_voice(message, bot)
    else:
        await send_text_message_on_voice(message, bot)


async def send_voice_message_on_voice(message: Message, bot: Bot):
    await bot.send_chat_action(message.chat.id, action="record_voice")
    file_link = await bot.get_file(message.voice.file_id)  # type: ignore
    await bot.download_file(file_link.file_path, "voice.ogg")  # type: ignore
    voice_file = open("voice.ogg", "rb")
    voice, answer = await ChatGPT().generate_voice(voice_file)
    await message.answer_voice(voice)
    await message.answer(answer, parse_mode="Markdown")


async def send_text_message_on_voice(message: Message, bot: Bot):
    await bot.send_chat_action(message.chat.id, action="typing")
    file_link = await bot.get_file(message.voice.file_id)  # type: ignore
    await bot.download_file(file_link.file_path, "voice.ogg")  # type: ignore
    voice_file = open("voice.ogg", "rb")
    answer = await ChatGPT().generate_text_on_voice(voice_file)
    await message.answer(answer, parse_mode="Markdown")
