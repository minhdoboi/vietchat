

from openai import OpenAI

from vietchat.settings import ProviderSettings
from vietchat.utils import logger


class OpenAIText:
    def __init__(self, client: OpenAI, settings: ProviderSettings):
        self.client = client
        self.settings = settings

    def get_completions_stream(self, messages):
        logger.info("openai> get_completions_stream")
        return self.client.chat.completions.create(
            model=self.settings.llm,
            messages=messages,
            stream=True,
        )