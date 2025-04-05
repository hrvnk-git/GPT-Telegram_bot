import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

from config import prompt
from database.db import load_response_id, save_response_id

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# HISTORY_MAX_LEN = 10  # При использовании chat.completions и DB


class ChatGPT:
    """Класс ChatGPT для взаимодействия с API OpenAI"""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)

    # async def generate_text_with_completion(self, user_text, user_id: int) -> str:
    #     user_history = await load_history(user_id, HISTORY_MAX_LEN)
    #     user_history.append({"role": "user", "content": user_text})
    #     messages = [{"role": "developer", "content": prompt}] + user_history
    #     completion = await self.client.chat.completions.create(
    #         model="o3-mini",
    #         messages=messages,
    #     )
    #     response_text = str(completion.choices[0].message.content)
    #     await save_message(user_id, "user", user_text)
    #     await save_message(user_id, "assistant", response_text)
    #     return response_text

    async def generate_text(self, user_text, user_id: int) -> str:
        """Генерирует текст на основе входящего пользовательского сообщения."""
        previous_response_id = await load_response_id(user_id)
        response = await self.client.responses.create(
            model="gpt-4o-mini",
            instructions=prompt,
            input=user_text,
            text={"format": {"type": "text"}},
            # tools=[],
            temperature=0.5,
            max_output_tokens=2048,
            # top_p=1,
            reasoning=None,
            previous_response_id=previous_response_id,
            store=True,
        )
        await save_response_id(user_id=user_id, response_id=response.id)
        return response.output[0].content[0].text

    # async def generate_voice(self, user_id: int, voice):
    #     """Транскрибирует голосовое сообщение и генерирует голосовой ответ."""
    #     transcript = await self.client.audio.transcriptions.create(
    #         model="gpt-4o-mini-transcribe", file=voice
    #     )
    #     answer = await self.generate_text(transcript.text, user_id)
    #     speech_file_path = Path(__file__).parent.parent / f"{user_id}_speech.ogg"
    #     async with self.client.audio.speech.with_streaming_response.create(
    #         model="gpt-4o-mini-tts",
    #         voice="shimmer",
    #         input=answer,
    #         instructions=instructions,
    #         response_format="opus",
    #         speed=0.25,
    #     ) as response:
    #         await response.stream_to_file(speech_file_path)
    #     return FSInputFile(speech_file_path), answer

    async def generate_text_on_voice(self, user_id: int, voice) -> str:
        """Транскрибирует голосовое сообщение и генерирует текстовый ответ."""
        transcript = await self.client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe", file=voice
        )
        return await self.generate_text(transcript.text, user_id)

    async def receive_photo(
        self, user_id: int, message_text: str | None, url: str
    ) -> str:
        """Обрабатывает фото с добавлением контекста сообщения."""
        if message_text:
            message_text = message_text
        else:
            message_text = "Что на фото?"
        previous_response_id = await load_response_id(user_id)
        response = await self.client.responses.create(
            model="gpt-4o-mini",
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": message_text},
                        {"type": "input_image", "image_url": url},
                    ],
                }  # type: ignore
            ],
            temperature=0.5,
            max_output_tokens=2048,
            top_p=1,
            reasoning=None,
            previous_response_id=previous_response_id,
        )
        await save_response_id(user_id=user_id, response_id=response.id)
        return response.output[0].content[0].text


gpt_client = ChatGPT()
