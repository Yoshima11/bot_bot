import pyttsx4

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

if __name__ == "__main__":
    t_to_s = TTSX4("Spanish (Spain)", 140)
    t_to_s.voice_talk("No te des por vencido ni aún vencido, no te sientas esclavo ni aún esclavo.")

