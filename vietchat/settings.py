import os
import streamlit as st
from dotenv import load_dotenv
from vietchat.utils import logger

load_dotenv()

class ProviderSettings:
    def __init__(self, provider):
        self.llm = os.getenv(provider.upper() + "_LLM_MODEL")
        self.stt = os.getenv(provider.upper() + "_STT_MODEL")
        self.api_key = try_read_secret(provider.upper() + "_API_KEY")

class Settings:
    def __init__(self):
        self.main_provider  = os.getenv("MAIN_PROVIDER")
        self.provider_settings = {
            provider:  ProviderSettings(provider)
            for provider in ["groq", "openai", "elevenlabs", "gtts"]
        }
        self.translation_target_lang = os.getenv("TRANSLATION_TARGET_LANG")
        self.phoenix_endpoint = os.getenv("PHOENIX_ENDPOINT")
        self.phoenix_enabled = os.getenv("PHOENIX_ENABLED") == "true"
        self.elevenlabs_api_key = try_read_secret("ELEVENLABS_API_KEY")


def try_read_secret(key):
    try:
        return st.secrets.get(key)
    except Exception:
        logger.debug("failed to read secret", key)
        return None

