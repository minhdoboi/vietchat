
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from vietchat.audio.base import TTSpeech, Voice
from vietchat.settings import Settings
from vietchat.utils import logger

class ElevenLabsTTSpeech(TTSpeech):
    
    def __init__(self, client: ElevenLabs):
        self.client = client

    def tts_voices(self):
        return [
            Voice("GATds6kYPBX2tRfQExbR", "Captain", "elevenlabs"),
            Voice("21m00Tcm4TlvDq8ikWAM", "Rachel", "elevenlabs"),
            Voice("XB0fDUnXU5powFXDhCwa", "Charlotte", "elevenlabs"),
            Voice("29vD33N1CtxCmqQRPOHJ", "George", "elevenlabs"),
            Voice("TX3LPaxmHKxFdv7VOQHJ", "Liam", "elevenlabs"),
            Voice("TX3LPaxmHKxFdv7VOQHJ", "Brian", "elevenlabs"),
        ]
    
    def text_to_speech(self, text, speech_file_path, voice_id, lang):
        logger.info("11labs> text_to_speech in %s", lang)
        response = self.client.text_to_speech.convert(
            voice_id=voice_id,
            output_format="mp3_22050_32",
            text=text,
            model_id="eleven_turbo_v2_5",
            language_code = lang,
            voice_settings=VoiceSettings(
                stability=0.0,
                similarity_boost=1.0,
                style=0.0,
                use_speaker_boost=True,
            ),
        )
        with open(speech_file_path, "wb") as f:
            for chunk in response:
                if chunk:
                    f.write(chunk)

        return speech_file_path