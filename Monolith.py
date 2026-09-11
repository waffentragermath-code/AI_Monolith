import json
import queue
import os
import subprocess
import sounddevice as sd
from vosk import KaldiRecognizer, Model

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


if __name__ == "__main__":
  print("Listen")
  while True:
    cmd = listen()
    if 'монолит' in cmd:
      print(cmd)
      if "открой блокнот" in cmd:
        print("Выполняю: Открытие блокнота")
        # На Windows
        if os.name == 'nt':
          subprocess.Popen(["notepad.exe"])
    if "стоп" in cmd or "выход" in cmd:
      break