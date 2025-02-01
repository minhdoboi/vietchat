

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

@dataclass
class Voice:
  id: str
  name: str
  provider: str

class TTSpeech(ABC):

  @abstractmethod
  def tts_voices() -> List[Voice]:
      pass
  
  @abstractmethod
  def text_to_speech(self, text, speech_file_path, voice_id, lang):
      pass