
import asyncio
from vietchat.translation.translator import translate_text


def test_translate():
    assert asyncio.run(translate_text("hello", "en", "fr")) == "Bonjour"