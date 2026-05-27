"""Tests for theorem/source provenance boundaries."""

from counterexample_commons.claims import ClaimStatus, INITIAL_CLAIMS
from counterexample_commons.source_map import (
    PROOF_ARCHITECTURE_SUMMARY,
    SOURCE_THEOREM_MAP,
    provenance_report_section,
    source_map_dicts,
)


def _claim(claim_id):
    return next(c for c in INITIAL_CLAIMS if c.claim_id == claim_id)


def test_openai_fixed_delta_is_source_documented_only():
    claim = _claim("UD-OAI-2026-001")
    assert claim.status == ClaimStatus.SOURCE_DOCUMENTED
    assert claim.locally_validated is False
    assert "0.014" not in claim.statement
    assert "0.014" in claim.limitations
    assert "does not provide" in claim.limitations


def test_sawin_0014_is_announcement_with_primary_proof_pending():
    claim = _claim("UD-SAWIN-2026-001")
    assert claim.status == ClaimStatus.SOURCE_DOCUMENTED
    assert claim.locally_validated is False
    assert "OpenAI announcement" in claim.primary_source
    assert "companion remarks PDF do not provide" in claim.limitations
    assert claim.primary_proof_present_in_repository is False
    assert claim.primary_proof_linked_in_current_official_materials is False


def test_companion_tiny_exponent_is_not_sawin():
    claim = _claim("UD-COMPANION-2026-001")
    assert claim.status == ClaimStatus.SOURCE_DOCUMENTED
    assert "6.24e-38" in claim.statement
    assert "not Sawin" in claim.limitations


def test_source_map_distinguishes_all_required_results():
    rows = source_map_dicts()
    results = {row["result"]: row for row in rows}
    assert "OpenAI disproof: exists fixed delta > 0" in results
    assert "Original OpenAI proof explicit delta value" in results
    assert "Sawin delta = 0.014 / exponent 1.014" in results
    explicit = results["Original OpenAI proof explicit delta value"]
    assert explicit["status"] == "NOT_PROVIDED_BY_ORIGINAL_PROOF"
    sawin = results["Sawin delta = 0.014 / exponent 1.014"]
    assert sawin["status"] == "SOURCE_DOCUMENTED / PRIMARY_PROOF_PENDING"
    assert "companion PDFs do not provide" in sawin["provenance_note"]


def test_source_map_has_no_companion_credit_for_sawin_1014():
    for entry in SOURCE_THEOREM_MAP:
        if "Sawin" in entry.result:
            assert "companion remarks PDF" not in entry.official_source_type
            assert "forthcoming refinement" in entry.official_source_type


def test_proof_architecture_not_mesh():
    assert "number fields" in PROOF_ARCHITECTURE_SUMMARY
    assert "Minkowski lattices" in PROOF_ARCHITECTURE_SUMMARY
    assert "not an ordinary two-dimensional rational mesh" in (
        PROOF_ARCHITECTURE_SUMMARY
    )


def test_report_provenance_section_has_non_implication():
    section = provenance_report_section()
    assert "SOURCE-DOCUMENTED RESULTS" in section
    assert "LOCALLY EXECUTED RESULTS" in section
    assert "NON-IMPLICATION" in section
    assert "does not locally reproduce" in section
