from google.cloud import translate_v2

def translate(text: str, source_language: str, target: str) -> dict:
    """Translates text into the target language.
    https://cloud.google.com/python/docs/reference/translate/latest/google.cloud.translate_v2.client.Client

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """

    translate_client = translate_v2.Client()

    if isinstance(text, bytes):
        text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(text,  source_language=source_language, target_language=target)

    # print("Text: {}".format(result["input"]))
    # print("Translation: {}".format(result["translatedText"]))
    # print("Detected source language: {}".format(result["detectedSourceLanguage"]))

    return result["translatedText"]

