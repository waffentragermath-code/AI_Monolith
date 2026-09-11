import json
import queue
import os
import subprocess
import sounddevice as sd
from vosk import KaldiRecognizer, Model
from AppOpener import open as open_app, close as close_app

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


APP_NAMES = { # названия программ на русском языке, чтобы не говорить их на английском
  "проводник": "explorer",
  "калькулятор": "calc",
  "блокнот": "notepad",
  "командная строка": "cmd",
  "диспетчер задач": "taskmgr",
  "браузер": "yandex",  # или 'yandex', 'msedge'
  "хром": "chrome",
  "стим": "steam",
  "телеграм": "telegram",
  "телега": "telegramm",
  "дискорд": "discord",
  "визуал студио код": "code"
}

def App_open(string): # открытие программы по голосу
  text = string.split()
  for word in text:
    if word in APP_NAMES:
      print("Запускаю", APP_NAMES[word])
      open_app(APP_NAMES[word], match_closest=True, output=False)
      return

def App_close(string): # зокрытие программы по голосу
  text = string.split()
  for word in text:
    if word in APP_NAMES:
      print("Закрываю", APP_NAMES[word])
      close_app(APP_NAMES[word], match_closest=True, output=False)
      return

if __name__ == "__main__":
  print("Listen")
  while True:
    cmd = listen()
    if 'монолит' in cmd:
      print(cmd)
      if "открой" in cmd or "запусти" in cmd or "включи" in cmd:
        App_open(cmd)
      if "закрой" in cmd or "выключи" in cmd:
        App_close(cmd)
      # if "открой блокнот" in cmd:
      #   print("Выполняю: Открытие блокнота")
      #   # На Windows
      #   if os.name == 'nt':
      #     subprocess.Popen(["notepad.exe"])
    if "стоп" in cmd or "выход" in cmd:
      break