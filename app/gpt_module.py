import json
import os
from collections import deque
from pathlib import Path

from aiogram.types import FSInputFile
from dotenv import load_dotenv
from openai import AsyncOpenAI

from config import instructions, prompt

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HISTORY_FILE = "message_history.json"
max_len = 10  # Сохраняем последние N сообщений


class ChatGPT:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.message_history = deque(maxlen=max_len)
        self.load_history()

    async def generate_text(self, user_text) -> str:
        self.message_history.append({"role": "user", "content": user_text})
        messages: list = [{"role": "developer", "content": prompt}] + list(
            self.message_history
        )
        completion = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )
        response_text = str(completion.choices[0].message.content)
        self.message_history.append({"role": "assistant", "content": response_text})
        self.save_history()
        return response_text

    def save_history(self):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(list(self.message_history), f, ensure_ascii=False, indent=4)

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    self.message_history = deque(data, maxlen=max_len)
                except json.JSONDecodeError:
                    self.message_history = deque(
                        maxlen=max_len
                    )  # Если файл повреждён, просто сбрасываем историю

    async def generate_voice(self, voice) -> tuple[FSInputFile, str]:
        transcript = await self.client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe", file=voice
        )
        print(transcript.text)
        # return await self.generate_text(transcript.text)
        answer = await self.generate_text(transcript.text)
        speech_file_path = Path(__file__).parent / "speech.ogg"

        async with self.client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice="shimmer",
            input=answer,
            instructions=instructions,
            response_format="opus",
            speed=0.25,
        ) as response:
            await response.stream_to_file(speech_file_path)

        return FSInputFile(speech_file_path), answer
