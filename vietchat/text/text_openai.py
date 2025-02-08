

import json
from openai import OpenAI

from vietchat.settings import ProviderSettings
from vietchat.utils import logger


class OpenAIText:
    def __init__(self, client: OpenAI, settings: ProviderSettings):
        self.client = client
        self.settings = settings

    def get_completions_stream(self, messages, stream):
        logger.info("openai> get_completions_stream")
        chat_completion =  self.client.chat.completions.create(
            model=self.settings.llm,
            messages=messages,
            response_format= {
              "type": "json_schema",
              "json_schema": {
                "name": "reasoning_schema",
                "strict": True,
                "schema": {
                  "type": "object",
                  "properties": {
                    "reasoning_steps": {
                      "type": "array",
                      "items": {
                        "type": "string"
                      },
                      "description": "The reasoning steps leading to the final conclusion."
                    },
                    "answer": {
                      "type": "string",
                      "description": "The final answer, taking into account the reasoning steps."
                    },
                    "user_reformulation": {
                      "type": "string",
                      "description": "Reformulation of the last user message."
                    }
                  },
                  "required": ["reasoning_steps", "answer", "user_reformulation"],
                  "additionalProperties": False
                }
              }
            },
            stream=stream,
        )
        return json.loads(chat_completion.choices[0].message.content)