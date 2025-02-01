import streamlit as st


class Settings:
    def __init__(self):
        self.openai_api_key = self.try_read_secret("OPENAI_API_KEY")
        self.llm_model = "gpt-4o-mini"
        self.translation_target_lang = "fr"

    def try_read_secret(self, key):
        try:
            return st.secrets.get(key)
        except Exception:
            print("failed to read secret", key)
            return None
        