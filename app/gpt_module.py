from os import getenv

from openai import AsyncOpenAI

from config import prompt

OPENAI_API_KEY = str(getenv("OPENAI_API_KEY"))


class ChatGPT:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)

    async def generate_text(self, user_text):
        completion = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "developer",
                    "content": prompt,
                },
                {"role": "user", "content": user_text},
            ],
        )
        return completion.choices[0].message.content

    # async def generate_voice(self):
    # user_voice = FSInputFile("text.ogg")
    # transcript = await self.client.audio.transcriptions.create(
    #     file=user_voice, model="gpt-4o-mini-transcribe"
    # )

    # answer = await self.generate_text(user_text=transcript.text)
    # speech_file_path = Path(__file__).parent / "speech.mp3"
    # with self.client_sync.audio.speech.with_streaming_response.create(
    #     model="gpt-4o-mini-tts",
    #     voice="alloy",
    #     input="The quick brown fox jumped over the lazy dog.",
    # ) as response:
    #     response.stream_to_file(speech_file_path)
    # return BufferedInputFile(file_data, filename="speech.mp3")
