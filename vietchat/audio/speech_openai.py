def speech_to_text(audio_file, client, language, prompt):
    """
    cf https://platform.openai.com/docs/api-reference/audio/createSpeech
    """

    with open(audio_file, "rb") as file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=file,
            language=language,
            prompt=prompt,
        )
        return transcription.text


def text_to_speech(text, client, speech_file_path):
    """
    https://platform.openai.com/docs/guides/text-to-speech
    https://platform.openai.com/docs/api-reference/audio/createSpeech
    """
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text,
    )
    response.stream_to_file(speech_file_path)