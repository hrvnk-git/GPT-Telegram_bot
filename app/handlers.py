from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, CallbackQuery, FSInputFile, Message

from .gpt_module import ChatGPT
from .middlewares import AccessMiddleware

router = Router()
router.message.middleware(AccessMiddleware())


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Привет!")


@router.message(F.text)
async def any_message(message: Message):
    answer = await ChatGPT().generate_text(message.text)
    await message.answer(answer)  # type: ignore


# @router.message(Command("voice"))
# async def send_voice_message(message: Message):
# file_id = message.voice.file_id # type: ignore
# file = await bot.get_file(file_id)
# file_path = file.file_path
# await bot.download_file(file_path, "text.ogg") # type: ignore
# input_file = ffmpeg.input("text.ogg")
# output_file = ffmpeg.output(input_file, "text.mp3", acodec="mp3", f="mp3")
# ffmpeg.run(output_file, overwrite_output=True)
# voice = open("text.mp3", "rb")
# # async with aiofiles.open("text.mp3", "rb") as voice:
# await ChatGPT().generate_voice()
# voice.close()
# await message.answer_document(context)
