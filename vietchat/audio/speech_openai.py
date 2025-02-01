"""
  https://platform.openai.com/docs/guides/text-to-speech
  https://platform.openai.com/docs/api-reference/audio/createSpeech
"""

def speech_to_text(audio_file, client, language, prompt):
    print("speech_to_text with prompt ", prompt)
    with open(audio_file, "rb") as file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=file,
            language=language,
            prompt=prompt,
        )
        return transcription.text


def text_to_speech(text, client, speech_file_path, voice):
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text,
    )
    response.stream_to_file(speech_file_path)
