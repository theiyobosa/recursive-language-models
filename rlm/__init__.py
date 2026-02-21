"""Public interface for the Recursive Language Model scaffold."""

from .config import RLMConfig
from .engine import RecursiveLanguageModel
from .llm import (
    # EchoLLM,
    LLMBackend,
    LLMPrompt,
    LLMResponse,
)

__all__ = [
    # "EchoLLM",
    "LLMBackend",
    "LLMPrompt",
    "LLMResponse",
    "RLMConfig",
    "RecursiveLanguageModel",
]
