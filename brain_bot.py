from transformers import pipeline

class IA:
    def __init__(self):
        self.chatbot =pipeline("conversational", model="microsoft/DialoGPT-medium")

    def genrate_resp(self, user_input):
        resp = self.chatbot(user_input)
        return resp[0]["generated_text"]
