"""Build human-readable experiment reports."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def build_run_report(run_dir: Path) -> str:
    """Generate a Markdown report from a completed run directory."""
    parts = ["# Experiment Run Report\n"]

    meta_path = run_dir / "metadata.json"
    if meta_path.exists():
        text = meta_path.read_text(encoding="utf-8")
        parts.append(f"## Metadata\n\n```json\n{text}\n```\n")

    rq_path = run_dir / "research_question.md"
    if rq_path.exists():
        text = rq_path.read_text(encoding="utf-8")
        parts.append(f"## Research Question\n\n{text}\n")

    claim_path = run_dir / "preregistered_claim.md"
    if claim_path.exists():
        text = claim_path.read_text(encoding="utf-8")
        parts.append(f"## Pre-Registered Claim\n\n{text}\n")

    result_path = run_dir / "result.json"
    if result_path.exists():
        text = result_path.read_text(encoding="utf-8")
        parts.append(f"## Result\n\n```json\n{text}\n```\n")

    assessment_path = run_dir / "assessment.md"
    if assessment_path.exists():
        text = assessment_path.read_text(encoding="utf-8")
        parts.append(f"## Assessment\n\n{text}\n")

    return "\n".join(parts)


def build_comparison_report(
    table: list[dict[str, Any]],
) -> str:
    """Generate a Markdown table from comparison data."""
    if not table:
        return "No comparison data.\n"

    headers = list(table[0].keys())
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in table:
        lines.append(
            "| " + " | ".join(str(row[h]) for h in headers) + " |"
        )
    return "\n".join(lines) + "\n"
