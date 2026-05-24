"""Pre-registration for controlled experiments."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PreRegistration:
    """A pre-registered experimental claim and falsifier.

    Must be written BEFORE invoking any model generation.
    """
    research_question: str
    claim: str
    falsifier: str
    success_criterion: str
    provider: str
    model: str

    def to_markdown(self) -> str:
        return (
            f"# Pre-Registration\n\n"
            f"## Research Question\n\n{self.research_question}\n\n"
            f"## Claim\n\n{self.claim}\n\n"
            f"## Falsifier\n\n{self.falsifier}\n\n"
            f"## Success Criterion\n\n{self.success_criterion}\n\n"
            f"## Provider\n\n{self.provider} / {self.model}\n"
        )
