
import gtts


def text_to_speech(text, speech_file_path, lang):
    if lang == "vi":
        tld = "com.vn"
    else:
        tld = "com"
    tts = gtts.gTTS(text, tld=tld, lang=lang)
    tts.save(speech_file_path)
