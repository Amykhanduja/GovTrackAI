from abc import ABC, abstractmethod

class ILLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, system: str = None) -> str: pass
    
    @abstractmethod
    def get_embeddings(self, text: str) -> list[float]: pass

class OpenAIProvider(ILLMProvider):
    def generate(self, prompt: str, system: str = None) -> str: return "OpenAI Mock Response"
    def get_embeddings(self, text: str) -> list[float]: return [0.1] * 1536

class LocalOllamaProvider(ILLMProvider):
    def generate(self, prompt: str, system: str = None) -> str: return "Ollama Llama3 Mock Response"
    def get_embeddings(self, text: str) -> list[float]: return [0.5] * 4096

class GeminiProvider(ILLMProvider):
    def generate(self, prompt: str, system: str = None) -> str: return "Gemini Mock Response"
    def get_embeddings(self, text: str) -> list[float]: return [0.2] * 768
