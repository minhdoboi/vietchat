"""
  https://platform.openai.com/docs/guides/text-to-speech
  https://platform.openai.com/docs/api-reference/audio/createSpeech
"""

from openai import OpenAI

from vietchat.audio.base import TTSpeech, Voice
from vietchat.settings import ProviderSettings
from vietchat.utils import logger


class OpenAISpeech(TTSpeech):
    def __init__(self, client: OpenAI, settings: ProviderSettings):
        self.client = client
        self.settings = settings

    def tts_voices(self):
        return [
            Voice(voice, voice, "openai")
            for voice in [
                "alloy",
                "ash",
                "coral",
                "echo",
                "fable",
                "onyx",
                "nova",
                "sage",
                "shimmer",
            ]
        ]

    def speech_to_text(self, audio_file, language, prompt):
        logger.info(
            "openai> speech_to_text %s in %s with prompt %s",
            self.settings.stt,
            language,
            prompt,
        )
        with open(audio_file, "rb") as file:
            transcription = self.client.audio.transcriptions.create(
                model=self.settings.stt,
                file=file,
                language=language,
                prompt=prompt,
            )
            return transcription.text

    def text_to_speech(self, text, speech_file_path, voice_id, lang):
        response = self.client.audio.speech.create(
            model="tts-1",
            voice=voice_id,
            input=text,
            response_format="mp3",
        )
        response.stream_to_file(speech_file_path)
