import os
from groq import Groq
from openai import OpenAI
from elevenlabs.client import ElevenLabs
from phoenix.otel import register
from openinference.instrumentation.groq import GroqInstrumentor
from openinference.instrumentation.openai import OpenAIInstrumentor
from vietchat.audio.speech_elevenlabs import ElevenLabsTTSpeech
from vietchat.audio.speech_groq import GroqSpeech
from vietchat.audio.speech_gtts import GTTSpeech
from vietchat.audio.speech_openai import OpenAISpeech
from vietchat.settings import ProviderSettings, Settings, try_read_secret
from vietchat.text.text_groq import GroqText
from vietchat.text.text_openai import OpenAIText
from vietchat.utils import logger


class AIProvider:

    def __init__(self, settings: Settings):
        self.add_phoenix_trace(settings)
        logger.info("provider founds %s", list(settings.provider_settings.keys()))
        self.clients = {
            provider: self.new_client(provider, provider_settings.api_key)
            for provider, provider_settings in settings.provider_settings.items()
            if provider_settings.api_key
        }
        logger.info("client founds %s", list(self.clients.keys()))
        self.tts = {
            provider: tts
            for provider, tts in [
                (provider, self.new_tts(provider, self.clients, provider_settings))
                for provider, provider_settings in settings.provider_settings.items()
            ]
            if tts
        }
        logger.info("tts founds %s", list(self.tts.keys()))
        self.tts_voices = self.get_tts_voices()
        self.client = self.clients[settings.main_provider]
        provider_settings = settings.provider_settings[settings.main_provider]

        if settings.main_provider == "groq":
            self.speechtt = GroqSpeech(client=self.client, settings=provider_settings)
            self.text = GroqText(
                client=self.client,
                settings=provider_settings,
            )
        elif settings.main_provider == "openai":
            self.speechtt = OpenAISpeech(
                client=self.client,
                settings=provider_settings,
            )
            self.text = OpenAIText(
                client=self.client,
                settings=provider_settings,
            )

    def get_tts_voices(self):
        return [
            voice
            for tts in self.tts.values()
            for voice in tts.tts_voices()
        ]

    def new_client(self, provider, api_key):
        if provider == "groq":
            return Groq(api_key=api_key)
        elif provider == "openai":
            return OpenAI(api_key=api_key)
        elif provider == "elevenlabs":
            return ElevenLabs(api_key=api_key)

    def new_tts(self, provider, clients, provider_settings: ProviderSettings):
        if provider == "elevenlabs":
            return ElevenLabsTTSpeech(clients[provider])
        elif provider == "openai":
            return OpenAISpeech(clients[provider], provider_settings)
        elif provider == "gtts":
            return GTTSpeech()
        else:
            return None

    def add_phoenix_trace(self, settings: Settings):
        if settings.phoenix_enabled:
            phoenix_headers = try_read_secret("PHOENIX_CLIENT_HEADERS")
            if phoenix_headers:
                os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = phoenix_headers
                os.environ["PHOENIX_CLIENT_HEADERS"] = phoenix_headers
                tracer_provider = register(
                    project_name="default",
                    endpoint="https://app.phoenix.arize.com/v1/traces",
                )

                if settings.main_provider == "groq":
                    GroqInstrumentor().instrument(tracer_provider=tracer_provider)
                elif settings.main_provider == "openai":
                    OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)
