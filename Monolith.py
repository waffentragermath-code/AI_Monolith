import json
import queue
import os
import subprocess
import difflib
from enum import Enum
import sounddevice as sd
import pyttsx3
from vosk import KaldiRecognizer, Model
from AppOpener import open as open_app, close as close_app
from dicts import APP_NAMES, ALIAS_TO_EXE, ALL_ALIASES, SYSTEM_NAMES

class Parameter(Enum):
  OPEN = 'open'
  CLOSE = 'close'

MODEL_PATH = "model"  # Папка с распакованной моделью Vosk
SAMPLE_RATE = 16000
print('Запуск чтения файлов')
model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, SAMPLE_RATE)
audio_queue = queue.Queue()

def callback(indata, frames, time, status):
  if status:
    print(status)
  audio_queue.put(bytes(indata))

def listen():
  with sd.RawInputStream(
      samplerate=SAMPLE_RATE,
      blocksize=8000,
      dtype="int16",
      channels=1,
      callback=callback,
  ):
    while True:
      data = audio_queue.get()
      if recognizer.AcceptWaveform(data):
        result = json.loads(recognizer.Result())
        text = result.get("text", "").strip()
        if text:
          return text

def word_analytics(string): # нахождение похожего слова в словаре
  match = difflib.get_close_matches(string.lower(), ALL_ALIASES, n=1, cutoff=0.6)
  if match:
    print(match)
    return ALIAS_TO_EXE[match[0]]
  return None

def voice_answer(text: str):
  engine = pyttsx3.init()
  engine.setProperty('rate', 180)
  engine.setProperty('volume', 1.0)

  voices = engine.getProperty('voices')
  engine.setProperty('voice', voices[0].id)
  
  engine.say(text=text)
  engine.runAndWait()

def answer(text: str):
  print(text)
  voice_answer(text=text)

def find_app(command: str) -> str:
  command = command.lower().strip()
  for exe, aliases in APP_NAMES.items():
    for alias in aliases:
      if alias in command:
        return exe
  return word_analytics(command)

def app(parameter: Parameter, app_name: str): # открытие программы по голосу
  if app_name == None:
    answer("Не удалось распознать название программы, повторите попытку")
    return
  try:
    if parameter == Parameter.OPEN:
      answer(f"Открываю {app_name}")
      open_app(app_name, match_closest=True, output=False)
    elif parameter == Parameter.CLOSE:
      answer(f"Закрываю {app_name}")
      close_app(app_name, match_closest=True, output=False)
  except Exception as e:
    print(f"Exception {e}")


def main():
  answer("Монолит начинает работу")
  while True:
    cmd = listen()
    if 'монолит' in cmd:
      print(cmd)
      if "открой" in cmd or "запусти" in cmd or "включи" in cmd:
        app(parameter=Parameter.OPEN, app_name=find_app(cmd))
      if "закрой" in cmd or "выключи" in cmd:
        app(parameter=Parameter.CLOSE, app_name=find_app(cmd))
    if "стоп" in cmd or "выход" in cmd:
      answer("Монолит завершает работу")
      break


if __name__ == "__main__":
  main()