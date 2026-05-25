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
        status=ClaimStatus.SOURCE_DOCUMENTED,
        primary_source="Sawin 2026 arXiv:2605.20579",
        locally_validated=False,
        limitations=(
            "Not yet locally reproduced. Repository contains only exact "
            "finite rational-grid baselines, not Sawin's algebraic-"
            "number-theoretic construction. "
            "See case_studies/erdos_unit_distance_2026/"
            "SAWIN_REPRODUCTION_ROADMAP.md for planned next steps."
        ),
        last_reviewed="2026-05-25",
    ),
    Claim(
        claim_id="UD-BASE-RATIONAL-MESH-001",
        statement=(
            "Finite rational mesh configurations can be generated "
            "and unit-distance edges counted exactly."
        ),
        status=ClaimStatus.LOCALLY_REPRODUCED_EXACT,
        primary_source="Local exact checker",
        locally_validated=True,
        limitations=(
            "Finite exact baseline only. Not Sawin's asymptotic "
            "construction and not evidence for exponent 1.014. "
            "See case_studies/erdos_unit_distance_2026/"
            "rational_mesh_baseline.py"
        ),
        last_reviewed="2026-05-25",
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