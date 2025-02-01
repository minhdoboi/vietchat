

from groq import Groq

from vietchat.settings import ProviderSettings
from vietchat.utils import logger


class GroqSpeech:
    def __init__(self, client: Groq, settings: ProviderSettings):
        self.client = client
        self.settings = settings

    def speech_to_text(self, audio_file, language, prompt):
        logger.info("groq> speech_to_text %s in %s with prompt %s", self.settings.stt, language, prompt)
        with open(audio_file, "rb") as file:
            transcription = self.client.audio.transcriptions.create(
                model=self.settings.stt,
                file=file,
                language=language,
                prompt=prompt,
            )
            return transcription.text
