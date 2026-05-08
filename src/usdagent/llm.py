"""LLM provider abstraction — returns a LangChain chat model."""

from __future__ import annotations

from enum import Enum
from typing import Any


class Provider(str, Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    OLLAMA = "ollama"


def get_llm(
    provider: Provider | str = Provider.ANTHROPIC,
    model: str | None = None,
    **kwargs: Any,
) -> Any:
    provider = Provider(provider)

    if provider == Provider.ANTHROPIC:
        from langchain_anthropic import ChatAnthropic  # type: ignore[import]
        return ChatAnthropic(
            model=model or "claude-sonnet-4-6",
            **kwargs,
        )

    if provider == Provider.OPENAI:
        from langchain_openai import ChatOpenAI  # type: ignore[import]
        return ChatOpenAI(
            model=model or "gpt-4o",
            **kwargs,
        )

    if provider == Provider.OLLAMA:
        from langchain_ollama import ChatOllama  # type: ignore[import]
        return ChatOllama(
            model=model or "qwen35-opus",
            **kwargs,
        )

    raise ValueError(f"Unknown provider: {provider}")
