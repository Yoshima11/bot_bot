import os
import json
import sys
import time
from tempfile import gettempdir
from zipfile import ZipFile
import requests
import vosk
import sounddevice as sd 
import queue


class STTVosk():
    def __init__(self, m_type="big", m_lang="es", device=None, silence_timeout=7):
        self.dir_models = "models"
        os.makedirs(self.dir_models, exist_ok=True)
        self.file_models_json = os.path.join(gettempdir(), "models_vosk.json")
        self.FRAMERATE = 16000
        self.CHANNELS = 1
        self.BYTES = 2
        self.device = device
        self.sample_rate = None
        self.rec = None
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self.silence_timeout = silence_timeout
        self.last_activity_time = None
        self.model_path = self.get_model(m_type, m_lang)
        try:
            self.model = vosk.Model(self.model_path)
        except Exception as e:
            print(f"Error al cargar el modelo: {e}")
            raise

    def __download_file(self, url, out_path):
        print(f"Descargando {url} en {out_path}")
        req = requests.get(url)
        with open(out_path, "wb") as f:
            f.write(req.content)

    def get_data(self):
        if not os.path.isfile(self.file_models_json):
            self.__download_file(vosk.MODEL_LIST_URL, self.file_models_json)
        with open(self.file_models_json, "r", encoding="utf-8") as f:
            models_data = json.load(f)
        return models_data

    def get_model(self, model_type, model_lang):
        m_data = self.get_data()
        model = None
        for m in m_data:
            if m["lang"] == model_lang.lower() and m["obsolete"] == "false" and m["type"] == model_type.lower():
                model = m
                break
        if not model:
            return None
        model_path = f"{self.dir_models}/{model["name"]}"
        if not os.path.isdir(model_path):
            zip_model_name = f"{model_lang}_{model_type}.zip"
            if not os.path.isfile(zip_model_name):
                self.__download_file(model["url"], zip_model_name)
            print(f"Descomprimiendo {zip_model_name}")
            with ZipFile(zip_model_name, "r") as zf:
                zf.extractall(self.dir_models)
        return model_path

    def _audio_callback(self, indata, frames, time, status):
            if status:
                print(status, file=sys.stderr)
            self.audio_queue.put(bytes(indata))
    
    def stop_listening(self):
        self.is_listening = False

    def listen_and_trans(self):
        if not self.model:
            raise RuntimeError("El modelo de vosk no ha sido cargado.")
        device_info = sd.query_devices(kind="input")
        self.sample_rate = device_info['default_samplerate']
        self.rec = vosk.KaldiRecognizer(self.model, self.sample_rate)
        self.rec.SetWords(True)
        self.is_listening = True
        self.last_activity_time = time.time()
        accumulated_text = ""
        with sd.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=8000,
            device=self.device,
            dtype="int16",
            channels=1,
            callback=self._audio_callback
            ):
            print("Escuchando...")
            while self.is_listening:
                try:
                    print("Inicio escucha...")
                    data = self.audio_queue.get(timeout=1)
                    if self.rec.AcceptWaveform(data):
                        result = json.loads(self.rec.Result())
                        text = result.get("text", "").strip()
                        if text:
                            accumulated_text += " " + text
                            self.last_activity_time = time.time()
                            print(f"Texto reconocido: {text}")
                    if time.time() - self.last_activity_time > self.silence_timeout:
                        print("\nTiempo de inactividad superado.", time.time() - self.last_activity_time)
                        break
                except queue.Empty:
                    if time.time() - self.last_activity_time > self.silence_timeout:
                        print("\nTiempo de inactividad superado.", time.time() - self.last_activity_time)
                        break
                except KeyboardInterrupt:
                    break
            final_result = json.loads(self.rec.FinalResult())
            accumulated_text += " " + final_result.get("text", "").strip()
            return accumulated_text.strip()


if __name__ == "__main__":
    print(sd.query_devices())
    stt_vosk = STTVosk("big", "es")
    text = stt_vosk.listen_and_trans()
    print("Resultado final: ", text)

