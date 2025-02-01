import gtts

from vietchat.audio.base import TTSpeech, Voice
from vietchat.utils import logger

GTTS_VOICE = Voice("gtts", "gtts", "gtts")


class GTTSpeech(TTSpeech):

    def tts_voices(self):
        return [GTTS_VOICE]

    def text_to_speech(self, text, speech_file_path, voice_id, lang):
        logger.info("gtts> text_to_speech in %s", lang)
        if lang == "vi":
            tld = "com.vn"
        else:
            tld = "com"
        tts = gtts.gTTS(text, tld=tld, lang=lang)
        tts.save(speech_file_path)
