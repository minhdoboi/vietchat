"""
cleaning audio files (https://cookbook.openai.com/examples/whisper_processing_guide)
"""

from pathlib import Path
from pydub import AudioSegment


# Function to detect leading silence
# Returns the number of milliseconds until the first sound (chunk averaging more than X decibels)
def milliseconds_until_sound(sound, silence_threshold_in_decibels=-20.0, chunk_size=10):
    trim_ms = 0  # ms

    assert chunk_size > 0  # to avoid infinite loop
    while sound[
        trim_ms : trim_ms + chunk_size
    ].dBFS < silence_threshold_in_decibels and trim_ms < len(sound):
        trim_ms += chunk_size

    return trim_ms


def trim_start(filepath):
    path = Path(filepath)
    directory = path.parent
    filename = path.name
    audio = AudioSegment.from_file(filepath, format="wav")
    start_trim = milliseconds_until_sound(audio)
    trimmed = audio[start_trim:]
    new_filename = directory / f"trimmed_{filename.replace('.wav', '.mp3')}"
    trimmed.export(new_filename, format="mp3")
    return trimmed, new_filename
