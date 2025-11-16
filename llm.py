import os
from abc import ABC, abstractmethod
from typing import List, Dict

from config import LLM_PROVIDER, LLM_MODEL, LLM_ENDPOINT, OPENAI_API_KEY

class LLM(ABC):
    @abstractmethod
    def generate(self, system: str, messages: List[Dict]) -> str:
        ...

# --- OpenAI backend ---

class OpenAIBackend(LLM):
    def __init__(self, model: str, api_key: str | None):
        try:
            from openai import OpenAI
        except ImportError as e:
            raise ImportError("openai package is required for OpenAIBackend. Install with 'pip install openai'.") from e

        self.client = OpenAI(api_key=api_key or None)
        self.model = model

    def generate(self, system: str, messages: List[Dict]) -> str:
        full_msgs = [{"role": "system", "content": system}] + messages
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=full_msgs,
            temperature=0.1,
        )
        return resp.choices[0].message.content or ""

# --- Local HTTP backend (Ollama / vLLM / LM Studio, etc.) ---

class LocalHTTPBackend(LLM):
    def __init__(self, model: str, endpoint: str):
        import requests
        self.model = model
        self.endpoint = endpoint
        self._requests = requests

    def generate(self, system: str, messages: List[Dict]) -> str:
        full_msgs = [{"role": "system", "content": system}] + messages
        payload = {
            "model": self.model,
            "messages": full_msgs,
            "temperature": 0.1,
        }
        r = self._requests.post(self.endpoint, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()

        # Adjust if your local server uses a different schema
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        if "message" in data:
            return data["message"]
        return str(data)

_llm_instance: LLM | None = None

def get_llm() -> LLM:
    global _llm_instance
    if _llm_instance is not None:
        return _llm_instance

    provider = (LLM_PROVIDER or "openai").lower()

    if provider == "openai":
        _llm_instance = OpenAIBackend(model=LLM_MODEL, api_key=OPENAI_API_KEY)
    elif provider == "local":
        _llm_instance = LocalHTTPBackend(model=LLM_MODEL, endpoint=LLM_ENDPOINT)
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {provider}")

    return _llm_instance
