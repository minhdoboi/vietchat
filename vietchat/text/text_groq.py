

from groq import Groq

from vietchat.settings import ProviderSettings
from vietchat.utils import logger


class GroqText:
    def __init__(self, client: Groq, settings: ProviderSettings):
        self.client = client
        self.settings = settings

    def get_completions_stream(self, messages):
        logger.info("groq> get_completions_stream")
        return parse_groq_stream(self.client.chat.completions.create(
            model=self.settings.llm,
            messages=messages,
            stream=True,
        ))
    
def parse_groq_stream(stream):
    for chunk in stream:
        if chunk.choices:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content