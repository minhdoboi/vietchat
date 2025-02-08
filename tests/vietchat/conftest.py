import pytest

from vietchat.ai_provider import AIProvider
from vietchat.settings import Settings
from vietchat.text.text_openai import OpenAIText

test_settings = Settings()
test_ai_provider = AIProvider(test_settings)


@pytest.fixture
def settings():
    return test_settings


@pytest.fixture
def ai_provider():
    return test_ai_provider


@pytest.fixture
def open_ai_client():
    return test_ai_provider.clients["openai"]


@pytest.fixture
def openai_text(open_ai_client):
    return OpenAIText(
        client=open_ai_client,
        settings=test_settings.provider_settings["openai"],
    )
