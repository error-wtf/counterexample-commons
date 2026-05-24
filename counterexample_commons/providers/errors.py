"""Provider-specific error types."""


class ProviderError(Exception):
    """Base error for all provider operations."""


class ProviderNotConfiguredError(ProviderError):
    """Raised when a provider's API key is missing."""


class ProviderConnectionError(ProviderError):
    """Raised when a provider cannot be reached."""


class ProviderResponseError(ProviderError):
    """Raised when a provider returns an invalid response."""


class ProviderDisabledError(ProviderError):
    """Raised when a provider action is blocked by the current app mode."""
