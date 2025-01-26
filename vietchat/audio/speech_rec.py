import speech_recognition as sr


def speech_to_text(audio_file):
    recognizer = sr.Recognizer()

    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)  # read the entire audio file

        return recognizer.recognize_google_cloud(audio_data)
