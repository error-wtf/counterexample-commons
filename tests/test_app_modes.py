"""Tests for application mode configuration and capability matrix."""

import subprocess
import sys
from pathlib import Path

import pytest

from counterexample_commons.config import (
    AppMode,
    CAPABILITY_MATRIX,
    Capabilities,
)


def test_exactly_six_modes():
    assert len(AppMode) == 6


def test_all_modes_have_capabilities():
    for mode in AppMode:
        assert mode in CAPABILITY_MATRIX
        assert isinstance(CAPABILITY_MATRIX[mode], Capabilities)


def test_local_private_enables_all():
    caps = CAPABILITY_MATRIX[AppMode.LOCAL_PRIVATE]
    assert caps.ai_candidate_lab is True
    assert caps.provider_comparison is True
    assert caps.ollama_local is True
    assert caps.secrets_loaded is True
    assert caps.filesystem_write is True
    assert caps.share_link is False


def test_local_share_disables_providers():
    caps = CAPABILITY_MATRIX[AppMode.LOCAL_SHARE]
    assert caps.ai_candidate_lab is False
    assert caps.provider_comparison is False
    assert caps.secrets_loaded is False
    assert caps.share_link is True
    assert caps.filesystem_write is False


def test_public_demo_disables_everything():
    caps = CAPABILITY_MATRIX[AppMode.PUBLIC_DEMO]
    assert caps.ai_candidate_lab is False
    assert caps.provider_comparison is False
    assert caps.secrets_loaded is False
    assert caps.ollama_local is False
    assert caps.share_link is False
    assert caps.google_drive is False


def test_colab_private_enables_colab_vm_ollama_local():
    caps = CAPABILITY_MATRIX[AppMode.COLAB_PRIVATE]
    assert caps.ai_candidate_lab is True
    assert caps.ollama_local is True
    assert caps.google_drive is False


def test_colab_public_demo_disables_providers():
    caps = CAPABILITY_MATRIX[AppMode.COLAB_PUBLIC_DEMO]
    assert caps.ai_candidate_lab is False
    assert caps.provider_comparison is False
    assert caps.secrets_loaded is False
    assert caps.ollama_local is False
    assert caps.claim_registry_editable is False


def test_hosted_public_demo_disables_everything():
    caps = CAPABILITY_MATRIX[AppMode.HOSTED_PUBLIC_DEMO]
    assert caps.ai_candidate_lab is False
    assert caps.provider_comparison is False
    assert caps.secrets_loaded is False
    assert caps.ollama_local is False
    assert caps.share_link is False


@pytest.mark.parametrize("mode", [
    AppMode.PUBLIC_DEMO,
    AppMode.COLAB_PUBLIC_DEMO,
    AppMode.HOSTED_PUBLIC_DEMO,
    AppMode.LOCAL_SHARE,
])
def test_all_public_modes_disable_paid_providers(mode):
    caps = CAPABILITY_MATRIX[mode]
    assert caps.ai_candidate_lab is False
    assert caps.provider_comparison is False
    assert caps.secrets_loaded is False


def test_build_app_all_modes():
    """App builds in all modes without live provider calls."""
    from app.main import build_app
    for mode in AppMode:
        demo = build_app(mode=mode)
        assert demo is not None


def test_private_modes_refuse_public_share():
    """local-private and colab-private must refuse --confirm-public-share."""
    for mode in ("local-private", "colab-private"):
        result = subprocess.run(
            [
                sys.executable,
                "scripts/run_gradio_local.py",
                "--mode", mode,
                "--confirm-public-share",
                "--no-browser",
            ],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).resolve().parent.parent),
        )
        assert result.returncode != 0, (
            f"Mode '{mode}' with --confirm-public-share should exit non-zero"
        )
        assert (
            "Refusing public share" in result.stderr
            or "Refusing public share" in result.stdout
        )
