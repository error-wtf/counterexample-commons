"""Application configuration and execution modes."""

from enum import Enum
from dataclasses import dataclass


class AppMode(Enum):
    LOCAL_PRIVATE = "local-private"
    LOCAL_SHARE = "local-share"
    PUBLIC_DEMO = "public-demo"
    COLAB_PRIVATE = "colab-private"
    COLAB_PUBLIC_DEMO = "colab-public-demo"
    HOSTED_PUBLIC_DEMO = "hosted-public-demo"


@dataclass(frozen=True)
class Capabilities:
    """What is enabled in a given mode."""
    ai_candidate_lab: bool
    provider_comparison: bool
    claim_registry_editable: bool
    export_full: bool
    ollama_local: bool
    secrets_loaded: bool
    share_link: bool
    google_drive: bool
    filesystem_write: bool


CAPABILITY_MATRIX: dict[AppMode, Capabilities] = {
    AppMode.LOCAL_PRIVATE: Capabilities(
        ai_candidate_lab=True,
        provider_comparison=True,
        claim_registry_editable=True,
        export_full=True,
        ollama_local=True,
        secrets_loaded=True,
        share_link=False,
        google_drive=False,
        filesystem_write=True,
    ),
    AppMode.LOCAL_SHARE: Capabilities(
        ai_candidate_lab=False,
        provider_comparison=False,
        claim_registry_editable=False,
        export_full=False,
        ollama_local=False,
        secrets_loaded=False,
        share_link=True,
        google_drive=False,
        filesystem_write=False,
    ),
    AppMode.PUBLIC_DEMO: Capabilities(
        ai_candidate_lab=False,
        provider_comparison=False,
        claim_registry_editable=False,
        export_full=False,
        ollama_local=False,
        secrets_loaded=False,
        share_link=False,
        google_drive=False,
        filesystem_write=False,
    ),
    AppMode.COLAB_PRIVATE: Capabilities(
        ai_candidate_lab=True,
        provider_comparison=True,
        claim_registry_editable=True,
        export_full=True,
        ollama_local=False,  # localhost = Colab VM, not user's PC
        secrets_loaded=True,
        share_link=False,
        google_drive=False,  # not mounted automatically
        filesystem_write=True,
    ),
    AppMode.COLAB_PUBLIC_DEMO: Capabilities(
        ai_candidate_lab=False,
        provider_comparison=False,
        claim_registry_editable=False,
        export_full=False,
        ollama_local=False,
        secrets_loaded=False,
        share_link=True,
        google_drive=False,
        filesystem_write=False,
    ),
    AppMode.HOSTED_PUBLIC_DEMO: Capabilities(
        ai_candidate_lab=False,
        provider_comparison=False,
        claim_registry_editable=False,
        export_full=False,
        ollama_local=False,
        secrets_loaded=False,
        share_link=False,
        google_drive=False,
        filesystem_write=False,
    ),
}
