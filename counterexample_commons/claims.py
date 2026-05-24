"""Claim registry data model."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ClaimStatus(Enum):
    SOURCE_DOCUMENTED = "SOURCE_DOCUMENTED"
    LOCALLY_REPRODUCED_EXACT = "LOCALLY_REPRODUCED_EXACT"
    LOCALLY_REPRODUCED_NUMERICAL = "LOCALLY_REPRODUCED_NUMERICAL"
    AI_GENERATED_HYPOTHESIS = "AI_GENERATED_HYPOTHESIS"
    FORMALLY_VERIFIED = "FORMALLY_VERIFIED"
    REJECTED_OR_FAILED = "REJECTED_OR_FAILED"
    INCONCLUSIVE = "INCONCLUSIVE"


@dataclass
class Claim:
    claim_id: str
    statement: str
    status: ClaimStatus
    primary_source: str
    locally_validated: bool
    limitations: str
    last_reviewed: str


INITIAL_CLAIMS: list[Claim] = [
    Claim(
        claim_id="UD-OAI-2026-001",
        statement=(
            "Fixed delta>0 construction exists "
            "for infinitely many n"
        ),
        status=ClaimStatus.SOURCE_DOCUMENTED,
        primary_source="OpenAI article; Alon et al.",
        locally_validated=False,
        limitations="Full proof not locally reproduced",
        last_reviewed="2026-05-23",
    ),
    Claim(
        claim_id="UD-SAWIN-2026-001",
        statement="Exponent 1.014 achieved explicitly",
        status=ClaimStatus.LOCALLY_REPRODUCED_NUMERICAL,
        primary_source="Sawin 2026",
        locally_validated=True,
        limitations=("Construction: "
                     "case_studies/erdos_unit_distance_2026/"
                     "sawin_construction.py"),
        last_reviewed="2026-05-24",
    ),
    Claim(
        claim_id="UD-OPEN-001",
        statement="Full asymptotic u(n) remains open",
        status=ClaimStatus.SOURCE_DOCUMENTED,
        primary_source="OpenAI article; Sawin 2026",
        locally_validated=False,
        limitations="Gap between n^1.014 and O(n^{4/3})",
        last_reviewed="2026-05-23",
    ),
    Claim(
        claim_id="UD-BASE-001",
        statement="Line has n-1 unit edges",
        status=ClaimStatus.LOCALLY_REPRODUCED_EXACT,
        primary_source="Local exact checker",
        locally_validated=True,
        limitations="Finite n only",
        last_reviewed="2026-05-23",
    ),
    Claim(
        claim_id="UD-BASE-002",
        statement="Square grid k*k has 2k(k-1) unit edges",
        status=ClaimStatus.LOCALLY_REPRODUCED_EXACT,
        primary_source="Local exact checker",
        locally_validated=True,
        limitations="Finite k only",
        last_reviewed="2026-05-23",
    ),
]
