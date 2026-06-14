"""Multi-LLM provider factory."""

from __future__ import annotations

import os
from abc import ABC, abstractmethod

from langchain_google_genai import ChatGoogleGenerativeAI


class LLMProvider(ABC):
    """Abstract base for LLM providers."""
    
    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass


class GeminiProvider(LLMProvider):
    """Google Gemini LLM provider."""
    
    def __init__(self, model: str = "gemini-2.5-flash"):
        self.llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=os.getenv("GEMINI_API_KEY")
        )
    
    def generate(self, prompt: str) -> str:
        return self.llm.invoke(prompt).content


class OpenAIProvider(LLMProvider):
    """OpenAI-compatible provider wrapper."""

    def __init__(self, model: str = "gpt-4o-mini"):
        try:
            from langchain_openai import ChatOpenAI
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("langchain_openai is not installed") from exc

        self.llm = ChatOpenAI(model=model, api_key=os.getenv("OPENAI_API_KEY"))

    def generate(self, prompt: str) -> str:
        return self.llm.invoke(prompt).content


class ClaudeProvider(LLMProvider):
    """Anthropic Claude provider wrapper."""

    def __init__(self, model: str = "claude-3-5-sonnet-latest"):
        try:
            from langchain_anthropic import ChatAnthropic
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("langchain_anthropic is not installed") from exc

        self.llm = ChatAnthropic(model=model, api_key=os.getenv("ANTHROPIC_API_KEY"))

    def generate(self, prompt: str) -> str:
        return self.llm.invoke(prompt).content


def get_llm_provider(provider_name: str = "gemini") -> LLMProvider:
    """Factory function to get LLM provider."""
    normalized = provider_name.lower().strip()
    if normalized == "gemini":
        return GeminiProvider()
    if normalized in {"openai", "gpt", "gpt-4", "gpt-4o"}:
        return OpenAIProvider()
    if normalized == "claude":
        return ClaudeProvider()
    raise ValueError(f"Unknown provider: {provider_name}")
