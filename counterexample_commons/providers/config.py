"""Provider configuration constants."""

PROVIDER_DEFAULTS: dict[str, dict] = {
    "openai": {
        "env_var": "OPENAI_API_KEY",
        "default_model": "gpt-4o",
    },
    "openrouter": {
        "env_var": "OPENROUTER_API_KEY",
        "default_model": "openai/gpt-4o",
    },
    "ollama_cloud": {
        "env_var": "OLLAMA_API_KEY",
        "default_model": "llama3.1:8b",
    },
    "ollama_local": {
        "env_var": "",
        "default_model": "llama3.1:8b",
        "default_base_url": "http://localhost:11434",
    },
    "mistral": {
        "env_var": "MISTRAL_API_KEY",
        "default_model": "mistral-large-latest",
    },
    "google_gemini": {
        "env_var": "GEMINI_API_KEY",
        "default_model": "gemini-1.5-pro",
    },
    "anthropic": {
        "env_var": "ANTHROPIC_API_KEY",
        "default_model": "claude-sonnet-4-20250514",
    },
}
