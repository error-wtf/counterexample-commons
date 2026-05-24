"""Provider-neutral interface for AI model generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class GenerationRequest:
    """A single text generation request."""
    prompt: str
    model: str
    temperature: float = 0.0
    max_tokens: int = 4096
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class GenerationResponse:
    """Raw response from a provider."""
    provider_name: str
    model: str
    raw_text: str
    finish_reason: str = "unknown"
    usage: dict = field(default_factory=dict)
    error: str | None = None
    metadata: dict = field(default_factory=dict)


@runtime_checkable
class ModelProvider(Protocol):
    """Protocol that every provider adapter must implement."""

    @property
    def name(self) -> str:
        """Provider identifier, e.g. 'openai'."""
        ...

    @property
    def requires_api_key(self) -> bool:
        """Whether this provider needs an API key."""
        ...

    @property
    def api_key_env_var(self) -> str:
        """Name of the environment variable for the API key."""
        ...

    def is_available(self) -> bool:
        """Check if the provider is configured and reachable."""
        ...

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        """Execute a text generation request. No streaming."""
        ...
