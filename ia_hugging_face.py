from abc import ABC, abstractmethod
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch


class HuggingFaceIA(ABC):
    def __init__(self, model_name, cache_dir="models/ia", device="auto", **model_kwargs):
        self.model_name = model_name
        self.cache_dir = cache_dir
        self.device = device 
        self.model_kwargs = model_kwargs
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            cache_dir=self.cache_dir,
            device_map=self.device,
            **self.model_kwargs,
        )
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            cache_dir=self.cache_dir,
        )

    @abstractmethod
    def format_prompt(self, prompt: str) -> str:
        pass 

    def generate_text(self, prompt, **generation_kwargs):
        formatted_prompt = self.format_prompt(prompt)
        inputs = self.tokenizer(
            formatted_prompt,
            return_tensors="pt",
            return_attention_mask=False,
        ).to(self.model.device)
        outputs = self.model.generate(
            **inputs,
            pad_token_id=self.tokenizer.eos_token_id,
            **generation_kwargs,
        )
        return self.process_output(outputs)
    
    def to_command(self, text):
        prompt = f"""
                 Traduce el siguiente texto en un comando estructurado en formato JSON. 
                 El comando debe tener alguno de campos: "action", "object" y "other". 
                 Ejemplo: 
                 - Texto: "Abre el navegador firefox y opera"
                 - Comando: {{"action": "abrir", "object": "navegador", "other": ["firefox", "opera"]}}

                 Texto: {text}
                 Comando: 
                 """
        return self.generate_text(prompt, max_new_tokens=50, do_sample=True, temperature=0.2)

    def process_output(self, outputs):
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)


class TinyLlamaIA(HuggingFaceIA):
    def __init__(self, device="cpu"):
        super().__init__(
                model_name="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
                device=device,
                torch_dtype=torch.float16,
                trust_remote_code=True,
        )
    
    def format_prompt(self, prompt):
        return f"""
                <|system|>
                Eres un asistente de IA útil.</s>
                <|user|>
                {prompt}</s>
                <|assistant|>
                """


class Llama3IA(HuggingFaceIA):
    def __init__(self, device="auto"):
        super().__init__(
            model_name="meta-llama/Meta-Llama-3-8B-Instruct",
            device=device,
            torch_dtype=torch.float16,
        )

    def format_prompt(self, prompt):
        return f"""
                <|begin_of_text|><|start_header_id|>system<|end_header_id|>
                Eres un asistente experto<|eot_id|>
                <|start_header_id|>user<|end_header_id|>
                {prompt}<|eot_id|>
                <|start_header_id|>assistant<|end_header_id|>
                """


class MistralIA(HuggingFaceIA):
    def __init__(self, device="auto"):
        super().__init__(
            model_name="mistralai/Mistral-7B-Instruct-v0.2",
            device=device,
            torch_dtype=torch.float16,
            load_in_4bit=True,
        )

    def format_prompt(self, prompt):
        return f"[INST] {prompt} [/INST]"


if __name__ == "__main__":
    MODEL_CHOICE = "tinyllama"
    model_registry = {
        "tinyllama": TinyLlamaIA,
        "llama3": Llama3IA,
        "mistral": MistralIA,
    }
    assistant = model_registry[MODEL_CHOICE](device="auto")
    response = assistant.generate_text(
        "Explícame el proceso de crecimiento de una semilla",
        max_new_tokens=300,
        do_sample=True,
        temperature=0.8,
    )
    print(f"Respuesta: {response}")
    command = assistant.to_command("Explícame el proceso de crecimiento de una semilla")
    print(f"Comando generado: {command}")
