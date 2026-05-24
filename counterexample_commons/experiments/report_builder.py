"""Build human-readable experiment reports."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def build_run_report(run_dir: Path) -> str:
    """Generate a Markdown report from a completed run directory."""
    parts = ["# Experiment Run Report\n"]

    meta_path = run_dir / "metadata.json"
    if meta_path.exists():
        parts.append(f"## Metadata\n\n```json\n"
                      f"{meta_path.read_text(encoding='utf-8')}\n```\n")

    rq_path = run_dir / "research_question.md"
    if rq_path.exists():
        parts.append(f"## Research Question\n\n"
                      f"{rq_path.read_text(encoding='utf-8')}\n")

    claim_path = run_dir / "preregistered_claim.md"
    if claim_path.exists():
        parts.append(f"## Pre-Registered Claim\n\n"
                      f"{claim_path.read_text(encoding='utf-8')}\n")

    result_path = run_dir / "result.json"
    if result_path.exists():
        parts.append(f"## Result\n\n```json\n"
                      f"{result_path.read_text(encoding='utf-8')}\n```\n")

    assessment_path = run_dir / "assessment.md"
    if assessment_path.exists():
        parts.append(f"## Assessment\n\n"
                      f"{assessment_path.read_text(encoding='utf-8')}\n")

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
