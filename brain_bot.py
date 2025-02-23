import os
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer


class IA:
    def __init__(self, task="text-generation", model_name="gpt2", device=-1, dir_models="models/ia"):
        self.task = task
        self.model_name = model_name
        self.device = device
        self.dir_models = dir_models
        os.makedirs(self.dir_models, exist_ok=True)
        self.model, self.tokenizer = self._download_model_and_tokeniser()
        self.generator = pipeline(
            task=task,
            model=self.model,
            tokenizer=self.tokenizer,
            device=self.device,
        )

    def _download_model_and_tokeniser(self):
        print(f"Descargando el modelo {self.model_name}...")
        model = AutoModelForCausalLM.from_pretrained(self.model_name, cache_dir=self.dir_models)
        tokenizer = AutoTokenizer.from_pretrained(self.model_name, cache_dir=self.dir_models)
        print(f"Modelo {self.model_name} descargado y guardado en {self.dir_models}.")
        return model, tokenizer

    def generate_text(self, prompt="", temperature=0.3, top_k=50, top_p=0.9):
        return self.generator(
            prompt,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p
        )

    def change_task(self, new_task, new_model_name=None):
        self.task = new_task
        if new_model_name:
            self.model_name = new_model_name
        self.model, self.tokenizer = self._download_model_and_tokeniser()
        self.generator = pipeline(new_task, model=self.model, tokenizer=self.tokenizer, device=self.device)
    
    def command_excec(self, command):
        prompt = f"Translate command to JSON. Example: 'turn on the kitchen light' --> {{'acción':'turn on', 'object':'light', 'place':'kitchen'}}. Command: '{command}' --> JSON:"
        return self.generate_text(prompt)
    
    def translate_text(self, text):
        prompt = f"Translate the following sentence into english: '{text}'"
        return self.generate_text(prompt)

if __name__ == "__main__":
    tp = IA(task="text-generation", model_name="deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B", dir_models="models/ia/deepseek-ai", device=0)
    command = "open the browser in a new window."
    generated_text = tp.command_excec(command)
    print("Texto generado: ", generated_text)
    while True:
        try:
            text = input("Escribe algo: ")
            generated_text = tp.translate_text(text)
            print("Texto generado: ", generated_text)
        except KeyboardInterrupt:
            break
