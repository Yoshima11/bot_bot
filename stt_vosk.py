import os
import json
from tempfile import gettempdir
from zipfile import ZipFile
import requests
import speech_recognition as sr 
import vosk
import sounddevice as sd 
import wave


class STTVosk():
    def __init__(self, m_type="big", m_lang="es", device=None):
        self.dir_models = "models"
        os.makedirs(self.dir_models, exist_ok=True)
        self.file_models_json = os.path.join(gettempdir(), "models_vosk.json")
        self.FRAMERATE = 16000
        self.CHANNELS = 1
        self.BYTE = 2
        self.save_wav_path = "temp_audio.wav"
        self.device = device
        self.model_path = self.get_model(m_type, m_lang)
        try:
            self.model = vosk.Model(self.model_path)
        except Exception as e:
            print(f"Error al cargar el modelo: {e}")
            raise
        self.recognizer = vosk.KaldiRecognizer(self.model, self.FRAMERATE)
        self.recognizer.SetWords(True)
        self.mic = sr.Microphone()

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
            try:
                print(f"Borrando archivo {zip_model_name}")
                os.remove(zip_model_name)
            except Exception as e:
                print(f"Error al eliminar el archivo {zip_model_name}: {e}")
        return model_path

    def save_wav(self, wav_data, file_path):
        with wave.open(file_path, "wb") as wav_file:
            wav_file.setnchannels(self.CHANNELS)
            wav_file.setsampwidth(self.BYTE)
            wav_file.setframerate(self.FRAMERATE)
            wav_file.writeframes(wav_data)
    
    def check_vosk_format(self, raw_data, sample_rate, sample_width):
        if sample_rate == self.FRAMERATE and sample_width == self.BYTE:
            return raw_data
        else:
            raise ValueError("Error formato audio.")

    def rec_from_mic(self):
        text = ""
        r = sr.Recognizer()
        if not self.model:
            raise RuntimeError("El modelo de vosk no ha sido cargado.")
        with self.mic as source:
            print("Escuchando...")
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
            wav_data = audio.get_wav_data(convert_rate=self.FRAMERATE, convert_width=self.BYTE)
            if self.recognizer.AcceptWaveform(wav_data):
                result = json.loads(self.recognizer.Result())
                text = result.get("text", "")
            else:
                partial_result = json.loads(self.recognizer.PartialResult())
                #text_parcial = partial_result.get("partial", "")
                #print(text_parcial)
            final_result = json.loads(self.recognizer.FinalResult())
            text += final_result.get("text", "")
            return text.strip()


if __name__ == "__main__":
    print(sd.query_devices(kind="input"))
    stt_vosk = STTVosk("big", "es")
    text = stt_vosk.rec_from_mic()
    print("Resultado: ", text)

