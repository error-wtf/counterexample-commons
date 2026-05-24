"""Tests for multi-provider adapter layer."""

import os

import pytest

from counterexample_commons.providers import (
    build_default_registry,
    GenerationRequest,
    ModelProvider,
    ProviderNotConfiguredError,
)
from counterexample_commons.providers.registry import ProviderRegistry


EXPECTED_PROVIDERS = [
    "anthropic",
    "google_gemini",
    "mistral",
    "ollama_cloud",
    "ollama_local",
    "openai",
    "openrouter",
]


class TestRegistry:
    def test_build_default_registry_has_seven(self):
        reg = build_default_registry()
        assert len(reg) == 7

    def test_all_expected_providers_registered(self):
        reg = build_default_registry()
        for name in EXPECTED_PROVIDERS:
            assert name in reg, f"Missing provider: {name}"

    def test_list_names_sorted(self):
        reg = build_default_registry()
        assert reg.list_names() == EXPECTED_PROVIDERS

    def test_get_returns_none_for_unknown(self):
        reg = build_default_registry()
        assert reg.get("nonexistent") is None


class TestProviderProtocol:
    @pytest.mark.parametrize("name", EXPECTED_PROVIDERS)
    def test_provider_implements_protocol(self, name):
        reg = build_default_registry()
        provider = reg.get(name)
        assert isinstance(provider, ModelProvider)

    @pytest.mark.parametrize("name", EXPECTED_PROVIDERS)
    def test_provider_has_name(self, name):
        reg = build_default_registry()
        provider = reg.get(name)
        assert provider.name == name

    @pytest.mark.parametrize("name", [
        n for n in EXPECTED_PROVIDERS if n != "ollama_local"
    ])
    def test_cloud_provider_requires_api_key(self, name):
        reg = build_default_registry()
        provider = reg.get(name)
        assert provider.requires_api_key is True
        assert len(provider.api_key_env_var) > 0

    def test_ollama_local_no_key_required(self):
        reg = build_default_registry()
        provider = reg.get("ollama_local")
        assert provider.requires_api_key is False
        assert provider.api_key_env_var == ""


class TestMissingKeyBehavior:
    @pytest.mark.parametrize("name", [
        n for n in EXPECTED_PROVIDERS if n != "ollama_local"
    ])
    def test_unavailable_without_key(self, name, monkeypatch):
        monkeypatch.delenv(
            build_default_registry().get(name).api_key_env_var,
            raising=False,
        )
        reg = build_default_registry()
        provider = reg.get(name)
        assert provider.is_available() is False

    @pytest.mark.parametrize("name", [
        n for n in EXPECTED_PROVIDERS if n != "ollama_local"
    ])
    def test_generate_raises_without_key(self, name, monkeypatch):
        reg = build_default_registry()
        provider = reg.get(name)
        monkeypatch.delenv(
            provider.api_key_env_var, raising=False,
        )
        req = GenerationRequest(
            prompt="test", model="test-model"
        )
        with pytest.raises(ProviderNotConfiguredError):
            provider.generate(req)


class TestNoSecretLogging:
    def test_no_key_in_provider_repr(self):
        reg = build_default_registry()
        for name in EXPECTED_PROVIDERS:
            provider = reg.get(name)
            rep = repr(provider)
            # Ensure no env var values leak into repr
            for var in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]:
                val = os.environ.get(var, "")
                if val:
                    assert val not in rep


class TestAvailabilityWithKey:
    @pytest.mark.parametrize("name", [
        n for n in EXPECTED_PROVIDERS if n != "ollama_local"
    ])
    def test_available_with_fake_key(self, name, monkeypatch):
        reg = build_default_registry()
        provider = reg.get(name)
        monkeypatch.setenv(provider.api_key_env_var, "fake-key")
        assert provider.is_available() is True
