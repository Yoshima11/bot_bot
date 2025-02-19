import os
import pyttsx4
from gtts import gTTS   

class TTSX4():
    def __init__(self, lang="Spanish (Spain)", rate=150):
        self.engine = pyttsx4.init()
        self.voices = self.engine.getProperty("voices")
        self.select_voice(lang)
        self.engine.setProperty("rate", rate)

    def select_voice(self,lang):
        for index, voice in enumerate(self.voices):
            if voice.name == lang:
                self.engine.setProperty("voice", self.voices[index].id)
                print(f"Voz {index}:{voice.name},({voice.languages[0]})")
    
    def voice_talk(self, text="Probando audio"):
        self.engine.say(text)
        self.engine.runAndWait()

class TTSGO():
    def __init__(self, lang="es", slow=False):
        self.lang = lang
        self.slow = slow
    
    def gen_audio(self, text, out_file="g_out.mp3"):
        try:
            tts = gTTS(text=text, lang=self.lang, slow=self.slow)
            tts.save(out_file)
            print(f"Archivo de audio guardado como {out_file}.")
        except Exception as e:
            print(f"Error al generar el audio: {e}.")

    def play_audio(self, audio_file):
        try:
            if os.path.exists(audio_file):
                os.system(f"mpg123 {audio_file}")
            else:
                print(f"El archivo {audio_file} no existe.")
        except Exception as e:
            print(f"Error al reproducir el audio: {e}.")
    
    def del_audio(self, out_file):
        os.remove(out_file)

    def voice_talk(self, text="Probando audio", out_file="g_out.mp3"):
        self.gen_audio(text, out_file)
        self.play_audio(out_file)
        self.del_audio(out_file)

if __name__ == "__main__":
    t_to_s = TTSX4("Spanish (Latin America)", 140)
    t_to_s.voice_talk("No te des por vencido ni aún vencido, no te sientas esclavo ni aún esclavo.")

    t_to_s = TTSGO(lang="es")
    t_to_s.voice_talk(text="No te des por vencido ni aún vencido, no te sientas esclavo ni aún esclavo.")

