"""Read-only source and theorem provenance map."""

from __future__ import annotations

from dataclasses import asdict, dataclass


OPENAI_ANNOUNCEMENT_URL = (
    "https://openai.com/index/model-disproves-discrete-geometry-conjecture/"
)
OPENAI_PROOF_PDF_URL = (
    "https://cdn.openai.com/pdf/"
    "74c24085-19b0-4534-9c90-465b8e29ad73/unit-distance-proof.pdf"
)
OPENAI_REMARKS_PDF_URL = (
    "https://cdn.openai.com/pdf/"
    "74c24085-19b0-4534-9c90-465b8e29ad73/unit-distance-remarks.pdf"
)


@dataclass(frozen=True)
class SourceMapEntry:
    """One immutable theorem/source provenance row."""

    result: str
    official_source_type: str
    source: str
    locally_executable: bool
    status: str
    provenance_note: str

    def to_row(self) -> list[str]:
        """Return a Gradio-table row."""
        return [
            self.result,
            self.official_source_type,
            "yes" if self.locally_executable else "no",
            self.status,
            self.provenance_note,
        ]

    def to_dict(self) -> dict[str, str | bool]:
        """Return a JSON-friendly dictionary."""
        return asdict(self)


SOURCE_THEOREM_MAP = [
    SourceMapEntry(
        result="Erdos unit-distance conjecture context",
        official_source_type="historical/source documentation",
        source="Historical literature; OpenAI announcement framing",
        locally_executable=False,
        status="SOURCE_DOCUMENTED",
        provenance_note="Context only; not a local theorem reproduction.",
    ),
    SourceMapEntry(
        result="OpenAI disproof: exists fixed delta > 0",
        official_source_type="official proof PDF",
        source=OPENAI_PROOF_PDF_URL,
        locally_executable=False,
        status="SOURCE_DOCUMENTED",
        provenance_note=(
            "The proof PDF documents existence of some fixed delta > 0; "
            "the repository does not locally reproduce the proof."
        ),
    ),
    SourceMapEntry(
        result="Original OpenAI proof explicit delta value",
        official_source_type="official announcement and proof PDF",
        source=OPENAI_ANNOUNCEMENT_URL,
        locally_executable=False,
        status="NOT_PROVIDED_BY_ORIGINAL_PROOF",
        provenance_note=(
            "The announcement states the original AI proof did not provide "
            "an explicit numerical delta."
        ),
    ),
    SourceMapEntry(
        result="Companion human-digested proof",
        official_source_type="official companion remarks PDF",
        source=OPENAI_REMARKS_PDF_URL,
        locally_executable=False,
        status="SOURCE_DOCUMENTED",
        provenance_note=(
            "Human-digested proof architecture and simplifications; not "
            "locally reproduced here."
        ),
    ),
    SourceMapEntry(
        result="Companion explicit tiny exponent around 1 + 6.24e-38",
        official_source_type="official companion remarks PDF",
        source=OPENAI_REMARKS_PDF_URL,
        locally_executable=False,
        status="SOURCE_DOCUMENTED",
        provenance_note=(
            "This is the companion explicit example exponent; it is not "
            "Sawin's announced 1.014 exponent."
        ),
    ),
    SourceMapEntry(
        result="Sawin delta = 0.014 / exponent 1.014",
        official_source_type="official announcement of forthcoming refinement",
        source=OPENAI_ANNOUNCEMENT_URL,
        locally_executable=False,
        status="SOURCE_DOCUMENTED / PRIMARY_PROOF_PENDING",
        provenance_note=(
            "Reported by the OpenAI announcement as a forthcoming Sawin "
            "refinement. The current official proof and companion PDFs do "
            "not provide the primary proof of 0.014."
        ),
    ),
    SourceMapEntry(
        result="Finite rational mesh baseline",
        official_source_type="repository exact computation",
        source=(
            "case_studies/erdos_unit_distance_2026/"
            "rational_mesh_baseline.py"
        ),
        locally_executable=True,
        status="LOCALLY_REPRODUCED_EXACT",
        provenance_note=(
            "Finite exact baseline only; not Sawin's construction and not "
            "evidence for any asymptotic exponent."
        ),
    ),
]


PROOF_ARCHITECTURE_SUMMARY = (
    "The OpenAI proof mechanism is not an ordinary two-dimensional rational "
    "mesh. At a high level it uses totally real number fields L, associated "
    "CM fields K = L(i), unramified tower/Golod-Shafarevich machinery, "
    "completely splitting rational primes, norm-one elements, high-"
    "dimensional Minkowski lattices, product-of-discs window selection, and "
    "projection to one complex coordinate."
)


REPRODUCTION_LEVELS = [
    ("L0", "FINITE EXACT BASELINES", "implemented"),
    ("L1", "FINITE AI CANDIDATES", "implemented"),
    ("L2", "OFFICIAL SOURCE / THEOREM MAP", "implemented"),
    ("L3", "ALGEBRAIC TOY MODELS", "not implemented"),
    ("L4", "NUMBER-FIELD CONSTRUCTION PROTOTYPES", "not implemented"),
    ("L5", "LEMMA-BY-LEMMA RECONSTRUCTION", "not implemented"),
    ("L6", "ASYMPTOTIC RESULT REPRODUCTION", "not implemented"),
]


def source_map_rows() -> list[list[str]]:
    """Return theorem map rows for UI display."""
    return [entry.to_row() for entry in SOURCE_THEOREM_MAP]


def source_map_dicts() -> list[dict[str, str | bool]]:
    """Return theorem map records for reports and tests."""
    return [entry.to_dict() for entry in SOURCE_THEOREM_MAP]


def provenance_report_section() -> str:
    """Return mandatory provenance text for finite reports."""
    return (
        "## Provenance\n\n"
        "SOURCE-DOCUMENTED RESULTS:\n"
        "- OpenAI proof: existence of fixed delta > 0, not locally "
        "reproduced.\n"
        "- Companion human-digested proof: source documented, not locally "
        "reproduced.\n"
        "- Companion explicit tiny exponent: approximately 1 + 6.24e-38; "
        "not Sawin 1.014.\n"
        "- Sawin delta=0.014: announced forthcoming refinement; primary "
        "proof is not present in the current repository/source set.\n\n"
        "LOCALLY EXECUTED RESULTS:\n"
        "- Only the specific finite baseline, explorer configuration, or "
        "AI candidate checked in this runtime.\n\n"
        "NON-IMPLICATION:\n"
        "- A finite validated configuration does not locally reproduce the "
        "asymptotic OpenAI theorem or Sawin's announced refinement.\n"
    )
