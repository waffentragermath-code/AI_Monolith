import json
import queue
import os
import subprocess
import sounddevice as sd
import pyttsx3
from vosk import KaldiRecognizer, Model
from AppOpener import open as open_app, close as close_app
from dicts import APP_NAMES

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
  return None

def app_open(app_name: str): # открытие программы по голосу
  if app_name == None:
    answer("Не удалось распознать название программы, повторите попытку")
    return
  else:
    answer(f"Запускаю {app_name}")
  try:
    open_app(app_name, match_closest=True, output=False)
  except Exception as e:
    print(f"Exception {e}")

def app_close(app_name: str): # закрытие программы по голосу
  if app_name == None:
    answer("Не удалось распознать название программы, повторите попытку")
    return
  else:
    answer(f"Закрываю {app_name}")
  try: 
    close_app(app_name, match_closest=True, output=False)
  except Exception as e:
    print(f"Exception {e}")


def main():
  print("Listen")
  while True:
    cmd = listen()
    if 'монолит' in cmd:
      print(cmd)
      if "открой" in cmd or "запусти" in cmd or "включи" in cmd:
        app_open(find_app(cmd))
      if "закрой" in cmd or "выключи" in cmd:
        app_close(find_app(cmd))
    if "стоп" in cmd or "выход" in cmd:
      answer("Монолит завершает работу")
      break


if __name__ == "__main__":
  main()