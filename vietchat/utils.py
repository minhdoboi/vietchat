import logging
import re

logger = logging.getLogger(__name__)


logging.basicConfig(level=logging.INFO)


def extract_think(text):
    think_pattern = r"<think>(.*?)</think>"
    think = re.findall(think_pattern, text, re.DOTALL)
    if think:
        think = think[0].strip()
        cleaned_text = re.sub(think_pattern, "", text.replace("\n", "")).strip()
    else:
        if "</think>" in text:
            think_pattern = r"(.*?)</think>"
            think = re.findall(think_pattern, text, re.DOTALL)
            if think:
                think = think[0].strip()
            else:
                think = None
        else:
            think = None
    cleaned_text = re.sub(think_pattern, "", text.replace("\n", "")).strip()
    return think, cleaned_text
