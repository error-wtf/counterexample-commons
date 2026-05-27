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
    provenance: str = ""
    primary_proof_present_in_repository: bool = False
    primary_proof_linked_in_current_official_materials: bool = True


INITIAL_CLAIMS: list[Claim] = [
    Claim(
        claim_id="UD-OAI-2026-001",
        statement=(
            "Fixed delta>0 construction exists "
            "for infinitely many n"
        ),
        status=ClaimStatus.SOURCE_DOCUMENTED,
        primary_source=(
            "OpenAI official proof PDF: Planar Point Sets with Many "
            "Unit Distances"
        ),
        locally_validated=False,
        limitations=(
            "Source-documented theorem that some fixed delta>0 exists. "
            "The original proof does not provide the explicit value 0.014 "
            "and is not locally reproduced in this repository."
        ),
        last_reviewed="2026-05-23",
        provenance="Official proof PDF; no local reproduction.",
    ),
    Claim(
        claim_id="UD-SAWIN-2026-001",
        statement=(
            "Sawin announced refinement: delta=0.014, exponent 1.014"
        ),
        status=ClaimStatus.SOURCE_DOCUMENTED,
        primary_source=(
            "OpenAI announcement of forthcoming Will Sawin refinement"
        ),
        locally_validated=False,
        limitations=(
            "Not locally reproduced. The current official proof PDF and "
            "companion remarks PDF do not provide the primary proof of "
            "delta=0.014. Repository finite baselines are not Sawin's "
            "algebraic-number-theoretic construction."
        ),
        last_reviewed="2026-05-25",
        provenance=(
            "OFFICIAL_ANNOUNCEMENT_OF_FORTHCOMING_REFINEMENT; "
            "PRIMARY_PROOF_PENDING"
        ),
        primary_proof_present_in_repository=False,
        primary_proof_linked_in_current_official_materials=False,
    ),
    Claim(
        claim_id="UD-COMPANION-2026-001",
        statement=(
            "Companion remarks provide a human-digested proof and an "
            "explicit tiny exponent around 1 + 6.24e-38"
        ),
        status=ClaimStatus.SOURCE_DOCUMENTED,
        primary_source=(
            "Official companion remarks PDF: Remarks on the Disproof of "
            "the Unit Distance Conjecture"
        ),
        locally_validated=False,
        limitations=(
            "Source documented only. This companion exponent is not Sawin "
            "1.014 and is not locally reproduced here."
        ),
        last_reviewed="2026-05-27",
        provenance="Official companion remarks PDF.",
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
        provenance="Repository exact finite computation.",
    ),
    Claim(
        claim_id="UD-OPEN-001",
        statement="Full asymptotic u(n) remains open",
        status=ClaimStatus.SOURCE_DOCUMENTED,
        primary_source="OpenAI article; Sawin 2026",
        locally_validated=False,
        limitations="Gap between n^1.014 and O(n^{4/3})",
        last_reviewed="2026-05-23",
        provenance="Source-documented open problem framing.",
    ),
    Claim(
        claim_id="UD-BASE-001",
        statement="Line has n-1 unit edges",
        status=ClaimStatus.LOCALLY_REPRODUCED_EXACT,
        primary_source="Local exact checker",
        locally_validated=True,
        limitations="Finite n only",
        last_reviewed="2026-05-23",
        provenance="Repository exact finite computation.",
    ),
    Claim(
        claim_id="UD-BASE-002",
        statement="Square grid k*k has 2k(k-1) unit edges",
        status=ClaimStatus.LOCALLY_REPRODUCED_EXACT,
        primary_source="Local exact checker",
        locally_validated=True,
        limitations="Finite k only",
        last_reviewed="2026-05-23",
        provenance="Repository exact finite computation.",
    ),
]
