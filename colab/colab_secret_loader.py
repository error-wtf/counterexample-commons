"""Load API secrets from Google Colab userdata."""

from __future__ import annotations

import os


def load_colab_secrets() -> dict[str, bool]:
    """Attempt to load secrets from google.colab.userdata.

    Returns dict of env_var -> loaded (True/False).
    Only works inside Google Colab runtime.
    """
    secret_vars = [
        "OPENAI_API_KEY",
        "OPENROUTER_API_KEY",
        "OLLAMA_API_KEY",
        "MISTRAL_API_KEY",
        "GEMINI_API_KEY",
        "ANTHROPIC_API_KEY",
    ]

    results: dict[str, bool] = {}

    try:
        from google.colab import userdata  # type: ignore
    except ImportError:
        for var in secret_vars:
            results[var] = False
        return results

    for var in secret_vars:
        try:
            value = userdata.get(var)
            if value:
                os.environ[var] = value
                results[var] = True
            else:
                results[var] = False
        except Exception:
            results[var] = False

    return results


def is_colab_runtime() -> bool:
    """Check if we are running inside Google Colab."""
    try:
        import google.colab  # type: ignore  # noqa: F401
        return True
    except ImportError:
        return False
