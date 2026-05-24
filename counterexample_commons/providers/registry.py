"""Provider registry — discovers and manages available providers."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base import ModelProvider


class ProviderRegistry:
    """Central registry for all model providers."""

    def __init__(self) -> None:
        self._providers: dict[str, ModelProvider] = {}

    def register(self, provider: ModelProvider) -> None:
        """Register a provider instance."""
        self._providers[provider.name] = provider

    def get(self, name: str) -> ModelProvider | None:
        """Retrieve a provider by name."""
        return self._providers.get(name)

    def list_names(self) -> list[str]:
        """Return sorted list of registered provider names."""
        return sorted(self._providers.keys())

    def list_available(self) -> list[str]:
        """Return names of providers that are currently configured."""
        return sorted(
            n for n, p in self._providers.items() if p.is_available()
        )

    def __len__(self) -> int:
        return len(self._providers)

    def __contains__(self, name: str) -> bool:
        return name in self._providers


def build_default_registry() -> ProviderRegistry:
    """Build the registry with all known provider adapters."""
    from .openai_provider import OpenAIProvider
    from .openrouter_provider import OpenRouterProvider
    from .ollama_cloud_provider import OllamaCloudProvider
    from .ollama_local_provider import OllamaLocalProvider
    from .mistral_provider import MistralProvider
    from .google_gemini_provider import GoogleGeminiProvider
    from .anthropic_provider import AnthropicProvider

    reg = ProviderRegistry()
    for cls in [
        OpenAIProvider,
        OpenRouterProvider,
        OllamaCloudProvider,
        OllamaLocalProvider,
        MistralProvider,
        GoogleGeminiProvider,
        AnthropicProvider,
    ]:
        reg.register(cls())
    return reg
