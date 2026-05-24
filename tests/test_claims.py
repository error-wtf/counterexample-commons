"""Tests for claim registry data model."""

from counterexample_commons.claims import (
    Claim,
    ClaimStatus,
    INITIAL_CLAIMS,
)


def test_all_statuses_are_valid_enum():
    for claim in INITIAL_CLAIMS:
        assert isinstance(claim.status, ClaimStatus)


def test_initial_claims_have_unique_ids():
    ids = [c.claim_id for c in INITIAL_CLAIMS]
    assert len(ids) == len(set(ids)), "Duplicate claim IDs found"


def test_locally_validated_matches_status():
    for claim in INITIAL_CLAIMS:
        if claim.status == ClaimStatus.LOCALLY_REPRODUCED_EXACT:
            assert claim.locally_validated is True, (
                f"{claim.claim_id}: LOCALLY_REPRODUCED_EXACT "
                f"but locally_validated is False"
            )


def test_source_documented_not_locally_validated():
    for claim in INITIAL_CLAIMS:
        if claim.status == ClaimStatus.SOURCE_DOCUMENTED:
            assert claim.locally_validated is False, (
                f"{claim.claim_id}: SOURCE_DOCUMENTED "
                f"but locally_validated is True"
            )


def test_claim_fields_not_empty():
    for claim in INITIAL_CLAIMS:
        assert claim.claim_id.strip()
        assert claim.statement.strip()
        assert claim.primary_source.strip()
        assert claim.limitations.strip()
        assert claim.last_reviewed.strip()


def test_all_status_enum_values():
    expected = {
        "SOURCE_DOCUMENTED",
        "LOCALLY_REPRODUCED_EXACT",
        "LOCALLY_REPRODUCED_NUMERICAL",
        "AI_GENERATED_HYPOTHESIS",
        "FORMALLY_VERIFIED",
        "REJECTED_OR_FAILED",
        "INCONCLUSIVE",
    }
    actual = {s.value for s in ClaimStatus}
    assert actual == expected


def test_claim_dataclass_fields():
    c = Claim(
        claim_id="TEST-001",
        statement="Test claim",
        status=ClaimStatus.INCONCLUSIVE,
        primary_source="Test",
        locally_validated=False,
        limitations="None",
        last_reviewed="2026-05-23",
    )
    assert c.claim_id == "TEST-001"
    assert c.status == ClaimStatus.INCONCLUSIVE
