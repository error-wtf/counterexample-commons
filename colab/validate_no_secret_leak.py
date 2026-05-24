"""Validate that no secrets are leaked in exported artifacts."""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from counterexample_commons.experiments.sanitization import (  # noqa: E402
    contains_secret,
)


def validate_directory(directory: Path) -> list[str]:
    """Scan all text files in directory for potential secrets."""
    violations: list[str] = []

    for f in directory.rglob("*"):
        if not f.is_file():
            continue
        if f.suffix in (".pyc", ".png", ".jpg", ".pdf"):
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
            if contains_secret(text):
                violations.append(str(f))
        except Exception:
            continue

    return violations


def main() -> int:
    """Run secret leak validation on ai_lab/experiments/runs/."""
    root = Path(__file__).resolve().parent.parent
    runs_dir = root / "ai_lab" / "experiments" / "runs"

    if not runs_dir.exists():
        print("No runs directory found — PASS (nothing to check)")
        return 0

    violations = validate_directory(runs_dir)

    if violations:
        print(f"FAIL: Potential secrets found in {len(violations)} files:")
        for v in violations:
            print(f"  - {v}")
        return 1

    print("PASS: No secrets detected in experiment runs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
